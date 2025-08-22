# PPR_processor.py

import subprocess
import requests
import os
import json
import time
import logging
import pandas as pd

from datetime import datetime, timedelta
from http.cookiejar import MozillaCookieJar
from io import StringIO
from getpass import getuser
from typing import Dict, Any, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import each process-specific file:
from .PPR_PRU import process_PPR_PRU, CONFIG as PRU_CONFIG
from .PPR_Case_Receive import process_PPR_Case_Receive, CONFIG as CASE_REC_CONFIG
from .PPR_Cubiscan import process_PPR_Cubiscan, CONFIG as CUBISCAN_CONFIG
from .PPR_Each_Receive import process_PPR_Each_Receive, CONFIG as EACH_REC_CONFIG
from .PPR_LP_Receive import process_PPR_LP_Receive, CONFIG as LP_REC_CONFIG
from .PPR_Pallet_Receive import process_PPR_Pallet_Receive, CONFIG as PALLET_REC_CONFIG
from .PPR_Prep_Recorder import process_PPR_Prep_Recorder, CONFIG as PREP_REC_CONFIG
from .PPR_RC_Presort import process_PPR_RC_Presort, CONFIG as RC_PRESORT_CONFIG
from .PPR_RC_Sort import process_PPR_RC_Sort, CONFIG as RC_SORT_CONFIG
from .PPR_Receive_Dock import process_PPR_Receive_Dock, CONFIG as RCV_DOCK_CONFIG
from .PPR_Receive_Support import process_PPR_Receive_Support, CONFIG as RCV_SUPPORT_CONFIG
from .PPR_Transfer_Out import process_PPR_Transfer_Out, CONFIG as TO_CONFIG
from .PPR_Transfer_Out_Dock import process_PPR_Transfer_Out_Dock, CONFIG as TO_DOCK_CONFIG
from .PPR_RSR_Support import process_PPR_RSR_Support, CONFIG as RSR_SUPPORT_CONFIG

# Import PPR_Q as fallback
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PPR_Q.PPR_Q_processor import PPRQProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

class DataFetchError(Exception):
    """Custom exception for data fetching errors."""
    pass

class PPRProcessor:
    """
    A processor for handling PPR (Process Performance Reports) data fetching, cleaning, and processing.
    Now refactored to delegate each PPR process to its own file with enhanced error handling and PPR_Q fallback.
    """

    def __init__(self, site: str, sos_datetime: datetime, eos_datetime: datetime):
        """
        Initializes the PPRProcessor with site details and datetime range.

        Args:
            site (str): The warehouse site identifier.
            sos_datetime (datetime): Start of the shift datetime.
            eos_datetime (datetime): End of the shift datetime.
        """
        self.site = site
        self.sos_datetime = sos_datetime
        self.eos_datetime = eos_datetime
        self.cookie_file_path = f'C:/Users/{getuser()}/.midway/cookie'

        # Map each process key to the numeric process ID (if any)
        self.process_ids: Dict[str, str] = {
            "PPR_PRU": "",
            "PPR_Case_Receive": "1003025",
            "PPR_Cubiscan": "1002971",
            "PPR_Each_Receive": "1003027",
            "PPR_LP_Receive": "1003031",
            "PPR_Pallet_Receive": "1003032",
            "PPR_Prep_Recorder": "01003002",
            "PPR_RC_Presort": "1003008",
            "PPR_RC_Sort": "1003009",
            "PPR_Receive_Dock": "1003010",
            "PPR_Receive_Support": "1003033",
            "PPR_Transfer_Out": "1003021",
            "PPR_Transfer_Out_Dock": "1003022",
            "PPR_RSR_Support": "1003012",
        }

        # Define critical processes that should raise exceptions if they fail
        self.CRITICAL_PROCESSES = {
            "PPR_Pallet_Receive",  # This is the main process mentioned in the issue
            "PPR_Case_Receive",    # Also mentioned as affected
            "PPR_LP_Receive",      # Core receive process
        }

        # Our final PPR data structure
        self.PPR_JSON: Dict[str, Any] = {}

        # Track overall execution time
        self.start_time = time.time()

        # Load session cookies
        self.load_cookies()

        # A dictionary that ties each process key to:
        # - the process function
        # - the config dictionary
        # so we know how to handle each process specifically
        self.process_handlers: Dict[str, Dict[str, Any]] = {
            "PPR_PRU": {
                "function": process_PPR_PRU,
                "config": PRU_CONFIG
            },
            "PPR_Case_Receive": {
                "function": process_PPR_Case_Receive,
                "config": CASE_REC_CONFIG
            },
            "PPR_Cubiscan": {
                "function": process_PPR_Cubiscan,
                "config": CUBISCAN_CONFIG
            },
            "PPR_Each_Receive": {
                "function": process_PPR_Each_Receive,
                "config": EACH_REC_CONFIG
            },
            "PPR_LP_Receive": {
                "function": process_PPR_LP_Receive,
                "config": LP_REC_CONFIG
            },
            "PPR_Pallet_Receive": {
                "function": process_PPR_Pallet_Receive,
                "config": PALLET_REC_CONFIG
            },
            "PPR_Prep_Recorder": {
                "function": process_PPR_Prep_Recorder,
                "config": PREP_REC_CONFIG
            },
            "PPR_RC_Presort": {
                "function": process_PPR_RC_Presort,
                "config": RC_PRESORT_CONFIG
            },
            "PPR_RC_Sort": {
                "function": process_PPR_RC_Sort,
                "config": RC_SORT_CONFIG
            },
            "PPR_Receive_Dock": {
                "function": process_PPR_Receive_Dock,
                "config": RCV_DOCK_CONFIG
            },
            "PPR_Receive_Support": {
                "function": process_PPR_Receive_Support,
                "config": RCV_SUPPORT_CONFIG
            },
            "PPR_Transfer_Out": {
                "function": process_PPR_Transfer_Out,
                "config": TO_CONFIG
            },
            "PPR_Transfer_Out_Dock": {
                "function": process_PPR_Transfer_Out_Dock,
                "config": TO_DOCK_CONFIG
            },
            "PPR_RSR_Support": {
                "function": process_PPR_RSR_Support,
                "config": RSR_SUPPORT_CONFIG
            },
        }

    def load_cookies(self) -> None:
        """
        Loads cookies from the specified cookie file to maintain session.
        """
        logging.info('Loading cookies for PPR pulling...')
        self.cookie_jar = MozillaCookieJar(self.cookie_file_path)
        try:
            self.cookie_jar.load(ignore_discard=True, ignore_expires=True)
            for cookie in self.cookie_jar:
                if 'session' in cookie.name:
                    self.midway_session = f'session={cookie.value}'
                    logging.info('Session cookie loaded successfully.')
                    break
            else:
                logging.warning('Session cookie not found in the cookie file.')
        except FileNotFoundError:
            logging.error(f'Cookie file not found at {self.cookie_file_path}.')
        except Exception as e:
            logging.error(f'Error loading cookies: {e}')

    def build_url(self, process_key: str, process_id: str, shift: Dict[str, str]) -> str:
        """
        Constructs the URL for the API request based on process and shift details.
        """
        base_url = "https://fclm-portal.amazon.com/reports/"
        if not process_id:
            # For processes without a specific process_id
            url = (
                f"{base_url}processPathRollup?reportFormat=CSV&warehouseId={self.site}"
                f"&maxIntradayDays=1&spanType=Intraday&startDateIntraday={shift['start_year']}/"
                f"{shift['start_month']}/{shift['start_day']}&startHourIntraday={shift['start_hour']}"
                f"&startMinuteIntraday={shift['start_minute']}&endDateIntraday={shift['end_year']}/"
                f"{shift['end_month']}/{shift['end_day']}&endHourIntraday={shift['end_hour']}"
                f"&endMinuteIntraday={shift['end_minute']}&_adjustPlanHours=on&_hideEmptyLineItems=on"
                f"&employmentType=AllEmployees"
            )
        else:
            # For processes with a specific process_id
            url = (
                f"{base_url}functionRollup?reportFormat=CSV&warehouseId={self.site}"
                f"&processId={process_id}&maxIntradayDays=1&spanType=Intraday&startDateIntraday="
                f"{shift['start_year']}/{shift['start_month']}/{shift['start_day']}&startHourIntraday="
                f"{shift['start_hour']}&startMinuteIntraday={shift['start_minute']}&endDateIntraday="
                f"{shift['end_year']}/{shift['end_month']}/{shift['end_day']}&endHourIntraday="
                f"{shift['end_hour']}&endMinuteIntraday={shift['end_minute']}&_adjustPlanHours=on&_hideEmptyLineItems=on"
                f"&employmentType=AllEmployees"
            )
        logging.debug(f"Request URL for {process_key}: {url}")
        return url

    def get_shifts(self, weeks_back: int = 4) -> List[Dict[str, str]]:
        """
        Generates a list of shift dictionaries for the past 'weeks_back' weeks.
        """
        shifts = []
        for i in range(1, weeks_back + 1):
            shift_start = self.sos_datetime - timedelta(weeks=i)
            shift_end = self.eos_datetime - timedelta(weeks=i)
            shift = {
                'start_hour': shift_start.strftime("%H"),
                'start_minute': shift_start.strftime("%M").lstrip('0') or '0',
                'start_day': shift_start.strftime("%d"),
                'start_month': shift_start.strftime("%m"),
                'start_year': shift_start.strftime("%Y"),
                'end_hour': shift_end.strftime("%H"),
                'end_minute': shift_end.strftime("%M").lstrip('0') or '0',
                'end_day': shift_end.strftime("%d"),
                'end_month': shift_end.strftime("%m"),
                'end_year': shift_end.strftime("%Y")
            }
            shifts.append(shift)
            logging.debug(f"Generated shift {i}: {shift}")
        return shifts

    def fetch_process_data(self, process_key: str) -> pd.DataFrame:
        """
        Fetches data for a specific process across multiple shifts, returning a concatenated DataFrame.
        Enhanced with better error handling and CSV parsing fallbacks.
        """
        logging.info(f"Fetching data for process: {process_key}")
        process_id = self.process_ids.get(process_key, "")
        process_df = pd.DataFrame()
        shifts = self.get_shifts()

        for idx, shift in enumerate(shifts, 1):
            logging.info(f"Fetching data for week {idx}/{len(shifts)} for process {process_key}...")
            url = self.build_url(process_key, process_id, shift)
            try:
                response = requests.get(url, cookies=self.cookie_jar, verify=False, timeout=30)
                if response.status_code == 200:
                    logging.info(f"Data fetched successfully for week {idx} of process {process_key}.")
                    
                    # Try multiple CSV parsing strategies
                    df = None
                    parsing_strategies = [
                        # Strategy 1: Original approach
                        lambda: pd.read_csv(StringIO(response.text), delimiter=';', encoding='ISO-8859-1', on_bad_lines='skip'),
                        # Strategy 2: Try comma delimiter
                        lambda: pd.read_csv(StringIO(response.text), delimiter=',', encoding='ISO-8859-1', on_bad_lines='skip'),
                        # Strategy 3: Try tab delimiter
                        lambda: pd.read_csv(StringIO(response.text), delimiter='\t', encoding='ISO-8859-1', on_bad_lines='skip'),
                        # Strategy 4: Auto-detect delimiter
                        lambda: pd.read_csv(StringIO(response.text), encoding='ISO-8859-1', on_bad_lines='skip', engine='python')
                    ]
                    
                    for strategy_idx, strategy in enumerate(parsing_strategies, 1):
                        try:
                            df = strategy()
                            if not df.empty:
                                logging.info(f"CSV parsing strategy {strategy_idx} successful for week {idx} of process {process_key}.")
                                break
                        except Exception as e:
                            logging.debug(f"CSV parsing strategy {strategy_idx} failed for week {idx} of process {process_key}: {e}")
                            continue
                    
                    if df is not None and not df.empty:
                        process_df = pd.concat([process_df, df], ignore_index=True)
                        logging.debug(f"Appended data for week {idx} of process {process_key}.")
                    else:
                        logging.warning(f"Empty response for week {idx} of process {process_key}.")
                else:
                    logging.error(f"Failed to fetch data for week {idx} of process {process_key}: "
                                  f"Status Code {response.status_code}")
            except requests.exceptions.RequestException as e:
                logging.error(f"Request exception for process {process_key} week {idx}: {e}")

        return process_df

    def fetch_with_ppr_q_fallback(self, process_key: str) -> pd.DataFrame:
        """
        Attempts to fetch data using PPR, and falls back to PPR_Q if PPR fails.
        This implements the hybrid approach mentioned in the action plan.
        """
        logging.info(f"Attempting PPR fetch with PPR_Q fallback for process: {process_key}")
        
        # First, try PPR
        ppr_df = self.fetch_process_data(process_key)
        
        if not ppr_df.empty:
            logging.info(f"PPR fetch successful for {process_key} - {len(ppr_df)} rows")
            return ppr_df
        
        # If PPR failed, try PPR_Q as fallback
        logging.warning(f"PPR fetch failed for {process_key}, trying PPR_Q fallback...")
        try:
            ppr_q_processor = PPRQProcessor(self.site, self.sos_datetime, self.eos_datetime)
            ppr_q_df = ppr_q_processor.fetch_process_data(process_key)
            
            if not ppr_q_df.empty:
                logging.info(f"PPR_Q fallback successful for {process_key} - {len(ppr_q_df)} rows")
                return ppr_q_df
            else:
                logging.error(f"Both PPR and PPR_Q failed for {process_key}")
                return pd.DataFrame()
                
        except Exception as e:
            logging.error(f"PPR_Q fallback failed for {process_key}: {e}")
            return pd.DataFrame()

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the raw DataFrame by removing extra quotes and delimiters.
        """
        logging.info("Cleaning data...")
        try:
            csv_data = df.to_csv(index=False)
            rows_clean = [
                row.replace('""', '"').strip('"').replace(',,,', '').replace(',,', '')
                for row in csv_data.splitlines()
            ]
            csv_clean = "\n".join(rows_clean)
            cleaned_df = pd.read_csv(StringIO(csv_clean), delimiter=',', header=0)
            logging.info("Data cleaned successfully.")
            return cleaned_df
        except Exception as e:
            logging.error(f"Error during data cleaning: {e}")
            return pd.DataFrame()

    def process_all_processes(self) -> None:
        """
        Orchestrates fetch, clean, and process for all PPR processes concurrently.
        """
        max_workers = 4
        logging.info(f"Starting concurrent processing with {max_workers} workers...")

        process_keys = list(self.process_handlers.keys())

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {}
            for p_key in process_keys:
                future = executor.submit(self.handle_process, p_key)
                future_map[future] = p_key

            for future in as_completed(future_map):
                proc_key = future_map[future]
                try:
                    future.result()
                    logging.info(f"Process {proc_key} completed successfully.")
                except Exception as ex:
                    logging.error(f"Process {proc_key} generated an exception: {ex}")

        self.execution_time = time.time() - self.start_time
        logging.info(f"Total execution time: {self.execution_time:.2f} seconds")

    def handle_process(self, process_key: str) -> None:
        """
        Handles fetching, cleaning, and per-process logic for a given key.
        Enhanced with critical process error handling and PPR_Q fallback.
        """
        logging.info(f"Handling process: {process_key}")
        
        # 1) fetch data with PPR_Q fallback
        raw_df = self.fetch_with_ppr_q_fallback(process_key)
        
        if raw_df.empty:
            logging.warning(f"No data fetched for process {process_key}.")
            
            # Check if this is a critical process
            if process_key in self.CRITICAL_PROCESSES:
                error_msg = f"No data for critical process: {process_key}"
                logging.error(error_msg)
                raise DataFetchError(error_msg)
            else:
                logging.warning(f"Skipping non-critical process {process_key} due to no data.")
                return
        
        # 2) clean data
        cleaned_df = self.clean_data(raw_df)
        if cleaned_df.empty:
            logging.warning(f"Cleaned data is empty for process {process_key}.")
            
            # Check if this is a critical process
            if process_key in self.CRITICAL_PROCESSES:
                error_msg = f"Cleaned data is empty for critical process: {process_key}"
                logging.error(error_msg)
                raise DataFetchError(error_msg)
            else:
                logging.warning(f"Skipping non-critical process {process_key} due to empty cleaned data.")
                return
        
        # 3) run the process-specific function
        process_func = self.process_handlers[process_key]["function"]
        config = self.process_handlers[process_key]["config"]
        process_func(cleaned_df, self.generic_process, self.PPR_JSON, config)
        logging.info(f"Finished processing for process {process_key}.")

    def generic_process(
        self,
        df: pd.DataFrame,
        process_key: str,
        PPR_JSON: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """
        Generic method to process a DataFrame based on a config that defines
        'columns' to extract, 'sums' to compute, etc.
        """
        try:
            logging.info(f"Calculating metrics for {process_key}...")
            process_data = {}

            # 1) Extract specified columns
            for col_name, col_idx in config.get("columns", {}).items():
                process_data[col_name] = df.iloc[:, col_idx].fillna('NaN').tolist()

            # 2) Calculate sums based on conditions
            for sum_key, sum_config in config.get("sums", {}).items():
                total = 0.0
                if "conditions" in sum_config:
                    condition_mask = self.build_conditions(sum_config["conditions"], df)
                    total = df[condition_mask].iloc[:, sum_config["column"]].sum()
                elif "condition" in sum_config:
                    cond_col_idx, cond_val = sum_config["condition"]
                    total = df[df.iloc[:, cond_col_idx] == cond_val].iloc[:, sum_config["column"]].sum()

                if "divide_by" in sum_config:
                    divisor = sum_config["divide_by"]
                    if divisor != 0:
                        total /= divisor

                process_data[sum_key] = float(total)

            # Ensure the process_key exists in PPR_JSON
            if process_key not in PPR_JSON:
                PPR_JSON[process_key] = {}
            PPR_JSON[process_key].update(process_data)

            logging.info(f"Metrics calculated for {process_key}.")
        except Exception as e:
            logging.error(f"Error processing {process_key}: {e}")

    def build_conditions(self, conditions: List[tuple], df: pd.DataFrame) -> pd.Series:
        """
        Builds a boolean mask for multiple conditions: (col_idx, expected_value).
        Supports expected being a single value or a list of acceptable values (OR semantics).
        String comparisons are case-insensitive and trim whitespace.
        """
        mask = pd.Series([True] * len(df))
        for col_idx, expected in conditions:
            column_series = df.iloc[:, col_idx]

            # Normalize string columns for case-insensitive, trimmed matching
            def normalize_series(s: pd.Series) -> pd.Series:
                try:
                    return s.astype(str).str.strip().str.lower()
                except Exception:
                    return s

            def normalize_value(v: Any) -> Any:
                return v.strip().lower() if isinstance(v, str) else v

            if isinstance(expected, list):
                normalized_col = normalize_series(column_series)
                normalized_expected = [normalize_value(v) for v in expected]

                str_values = [v for v in normalized_expected if isinstance(v, str)]
                non_str_values = [v for v in normalized_expected if not isinstance(v, str)]

                part_mask = pd.Series([False] * len(df))
                if str_values:
                    part_mask |= normalized_col.isin(str_values)
                if non_str_values:
                    part_mask |= column_series.isin(non_str_values)

                mask &= part_mask
            else:
                if isinstance(expected, str):
                    mask &= (normalize_series(column_series) == normalize_value(expected))
                else:
                    mask &= (column_series == expected)
        return mask

    def run(self) -> Dict[str, Any]:
        """
        Executes the entire PPR processing workflow.
        """
        logging.info('Starting PPR processing...')
        self.process_all_processes()
        logging.info('PPR processing completed.')
        return self.PPR_JSON

# PPR_Q_processor.py

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

# Import each process-specific file from the existing PPR module:
import sys
import os
# Add the parent directory to the path so we can import PPR
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PPR.PPR_PRU import process_PPR_PRU, CONFIG as PRU_CONFIG
from PPR.PPR_Case_Receive import process_PPR_Case_Receive, CONFIG as CASE_REC_CONFIG
from PPR.PPR_Cubiscan import process_PPR_Cubiscan, CONFIG as CUBISCAN_CONFIG
from PPR.PPR_Each_Receive import process_PPR_Each_Receive, CONFIG as EACH_REC_CONFIG
from PPR.PPR_LP_Receive import process_PPR_LP_Receive, CONFIG as LP_REC_CONFIG
from PPR.PPR_Pallet_Receive import process_PPR_Pallet_Receive, CONFIG as PALLET_REC_CONFIG
from PPR.PPR_Prep_Recorder import process_PPR_Prep_Recorder, CONFIG as PREP_REC_CONFIG
from PPR.PPR_RC_Presort import process_PPR_RC_Presort, CONFIG as RC_PRESORT_CONFIG
from PPR.PPR_RC_Sort import process_PPR_RC_Sort, CONFIG as RC_SORT_CONFIG
from PPR.PPR_Receive_Dock import process_PPR_Receive_Dock, CONFIG as RCV_DOCK_CONFIG
from PPR.PPR_Receive_Support import process_PPR_Receive_Support, CONFIG as RCV_SUPPORT_CONFIG
from PPR.PPR_Transfer_Out import process_PPR_Transfer_Out, CONFIG as TO_CONFIG
from PPR.PPR_Transfer_Out_Dock import process_PPR_Transfer_Out_Dock, CONFIG as TO_DOCK_CONFIG
from PPR.PPR_RSR_Support import process_PPR_RSR_Support, CONFIG as RSR_SUPPORT_CONFIG


# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

class PPRQProcessor:
    """
    A processor for handling PPR Quarterly data fetching, cleaning, and processing.
    Uses ALL existing PPR process files but with flexible minute-level time ranges.
    """

    def __init__(self, site: str, sos_datetime: datetime, eos_datetime: datetime):
        """
        Initializes the PPRQProcessor with site details and shift datetime range.

        Args:
            site (str): The warehouse site identifier.
            sos_datetime (datetime): Start of shift datetime with minute precision.
            eos_datetime (datetime): End of shift datetime with minute precision.
        """
        self.site = site
        self.sos_datetime = sos_datetime
        self.eos_datetime = eos_datetime
        self.cookie_file_path = f'C:/Users/{getuser()}/.midway/cookie'

        # Use the EXACT SAME process IDs as PPR
        self.process_ids: Dict[str, str] = {
            "PPR_PRU": "",
            "PPR_Case_Receive": "1003025",
            "PPR_Cubiscan": "1002971",
            "PPR_Each_Receive": "01003027",
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

        # Our final PPR_Q data structure
        self.PPR_Q_JSON: Dict[str, Any] = {}
        
        # Store raw DataFrames for size-specific calculations
        self.raw_dataframes: Dict[str, pd.DataFrame] = {}

        # Track overall execution time
        self.start_time = time.time()

        # Load session cookies
        self.load_cookies()

        # Use the EXACT SAME process handlers as PPR
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
        EXACT SAME as PPR.
        """
        logging.info('Loading cookies for PPR_Q pulling...')
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

    def build_url(self, process_key: str, process_id: str, time_range: Dict[str, str]) -> str:
        """
        Constructs the URL for the API request based on process and time range details.
        Uses functionRollup when a process_id is provided, otherwise falls back to processPathRollup.
        This mirrors the exact logic used by the working PPR_processor.
        """
        base_url = "https://fclm-portal.amazon.com/reports/"
        start_date = f"{time_range['start_year']}/{time_range['start_month']}/{time_range['start_day']}"
        end_date = f"{time_range['end_year']}/{time_range['end_month']}/{time_range['end_day']}"

        if process_id:  # use functionRollup, same logic as PPR_processor
            url = (
                f"{base_url}functionRollup?reportFormat=CSV"
                f"&warehouseId={self.site}"
                f"&processId={process_id}"
                f"&maxIntradayDays=1&spanType=Intraday"
                f"&startDateIntraday={start_date}&startHourIntraday={time_range['start_hour']}&startMinuteIntraday={time_range['start_minute']}"
                f"&endDateIntraday={end_date}&endHourIntraday={time_range['end_hour']}&endMinuteIntraday={time_range['end_minute']}"
                f"&_adjustPlanHours=on&hideEmptyLineItems=true&_hideEmptyLineItems=on&_rememberViewForWarehouse=on&employmentType=AllEmployees"
            )
        else:  # no process ID – stick with processPathRollup
            url = (
                f"{base_url}processPathRollup?reportFormat=CSV"
                f"&warehouseId={self.site}"
                f"&maxIntradayDays=1&spanType=Intraday"
                f"&startDateIntraday={start_date}&startHourIntraday={time_range['start_hour']}&startMinuteIntraday={time_range['start_minute']}"
                f"&endDateIntraday={end_date}&endHourIntraday={time_range['end_hour']}&endMinuteIntraday={time_range['end_minute']}"
                f"&_adjustPlanHours=on&hideEmptyLineItems=true&_hideEmptyLineItems=on&_rememberViewForWarehouse=on&employmentType=AllEmployees"
            )
        
        logging.info(f"PPR_Q URL for {process_key} (process_id='{process_id}'): {url}")
        return url

    def get_time_range(self) -> Dict[str, str]:
        """
        Generates a time range for the exact shift period specified.
        Creates a single intraday URL covering the entire shift duration.
        """
        time_range = {
            'start_hour': self.sos_datetime.strftime("%H"),
            'start_minute': self.sos_datetime.strftime("%M").lstrip('0') or '0',
            'start_day': self.sos_datetime.strftime("%d"),
            'start_month': self.sos_datetime.strftime("%m"),
            'start_year': self.sos_datetime.strftime("%Y"),
            'end_hour': self.eos_datetime.strftime("%H"),
            'end_minute': self.eos_datetime.strftime("%M").lstrip('0') or '0',
            'end_day': self.eos_datetime.strftime("%d"),
            'end_month': self.eos_datetime.strftime("%m"),
            'end_year': self.eos_datetime.strftime("%Y")
        }
        logging.info(f"PPR_Q time range: {self.sos_datetime} to {self.eos_datetime}")
        logging.debug(f"Generated time range: {time_range}")
        return time_range





    def fetch_process_data(self, process_key: str) -> pd.DataFrame:
        """
        Fetches data for a specific process using a single intraday URL covering the exact time range.
        This follows the recommendation to avoid multi-strategy approaches and weekly loops.
        However, the API often ignores time ranges and returns much more data than requested,
        so we need to scale the results appropriately.
        """
        logging.info(f"Fetching data for process: {process_key}")
        process_id = self.process_ids.get(process_key, "")

        # Build single intraday URL for exact time range
        time_range = self.get_time_range()
        url = self.build_url(process_key, process_id, time_range)
        
        # Single API call per process covering the entire shift
        df = self._make_request(process_key, url)
        if not df.empty:
            logging.info(f"Successfully fetched {len(df)} rows for process {process_key}")
            
            # Scale the data to match the requested time range
            scaled_df = self._scale_data_to_time_range(df, process_key)
            return scaled_df
        else:
            logging.warning(f"No data returned for process {process_key}")
            return pd.DataFrame()

    def _scale_data_to_time_range(self, df: pd.DataFrame, process_key: str) -> pd.DataFrame:
        """
        DISABLED: No longer scales data to avoid magnitude issues.
        The PPR API returns data for the exact time range requested when using proper parameters.
        Scaling was causing values to be 2 orders of magnitude lower than expected.
        """
        if df.empty:
            return df

        # Calculate requested shift duration for logging only
        requested_hours = (self.eos_datetime - self.sos_datetime).total_seconds() / 3600
        
        # Log the time range but don't scale
        logging.info(f"Time range for {process_key}:")
        logging.info(f"  Requested: {requested_hours:.1f} hours")
        logging.info(f"  No scaling applied - using raw API data")
        
        return df



    def _make_request(self, process_key: str, url: str) -> pd.DataFrame:
        """
        Makes a single HTTP request and returns the parsed DataFrame.
        """
        try:
            response = requests.get(url, cookies=self.cookie_jar, verify=False, timeout=30)
            if response.status_code == 200:
                logging.info(f"Data fetched successfully for process {process_key}.")
                
                # Check if response is HTML (error page) instead of CSV
                if response.text.strip().startswith('<!DOCTYPE') or response.text.strip().startswith('<html'):
                    logging.error(f"API returned HTML error page for process {process_key}. URL may be invalid.")
                    logging.debug(f"Response preview: {response.text[:200]}...")
                    return pd.DataFrame()
                
                # Try multiple parsing strategies like the working PPR processor
                df = None
                parsing_strategies = [
                    # Strategy 1: Comma delimiter (most common for FCLM API)
                    lambda: pd.read_csv(StringIO(response.text), delimiter=',', encoding='ISO-8859-1', on_bad_lines='skip'),
                    # Strategy 2: Semicolon delimiter (fallback)
                    lambda: pd.read_csv(StringIO(response.text), delimiter=';', encoding='ISO-8859-1', on_bad_lines='skip'),
                    # Strategy 3: Auto-detect delimiter
                    lambda: pd.read_csv(StringIO(response.text), encoding='ISO-8859-1', on_bad_lines='skip', engine='python')
                ]
                
                for strategy_idx, strategy in enumerate(parsing_strategies, 1):
                    try:
                        df = strategy()
                        if not df.empty and df.shape[1] > 1:  # Must have multiple columns
                            logging.info(f"CSV parsing strategy {strategy_idx} successful for process {process_key}.")
                            break
                    except Exception as e:
                        logging.debug(f"CSV parsing strategy {strategy_idx} failed for process {process_key}: {e}")
                        continue
                if not df.empty:
                    logging.debug(f"Appended data for process {process_key}. Shape: {df.shape}")
                    # Log first few rows to debug
                    logging.debug(f"First 3 rows of data:\n{df.head(3)}")
                    return df
                else:
                    logging.warning(f"Empty response for process {process_key}.")
            else:
                logging.error(f"Failed to fetch data for process {process_key}: "
                            f"Status Code {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request exception for process {process_key}: {e}")
        except Exception as e:
            logging.error(f"Error parsing CSV for process {process_key}: {e}")
        
        return pd.DataFrame()



    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the raw DataFrame by removing extra quotes and delimiters.
        EXACT SAME as PPR.
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
        EXACT SAME as PPR.
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
        EXACT SAME as PPR.
        """
        logging.info(f"Handling process: {process_key}")
        # 1) fetch data
        raw_df = self.fetch_process_data(process_key)
        if raw_df.empty:
            logging.warning(f"No data fetched for process {process_key}. Skipping processing.")
            return
        # 2) clean data
        cleaned_df = self.clean_data(raw_df)
        if cleaned_df.empty:
            logging.warning(f"Cleaned data is empty for process {process_key}. Skipping processing.")
            return
        
        # Store raw DataFrame for size-specific calculations
        self.raw_dataframes[process_key] = cleaned_df.copy()
        
        # 3) run the process-specific function - EXACT SAME as PPR
        process_func = self.process_handlers[process_key]["function"]
        config = self.process_handlers[process_key]["config"]
        # Use our custom generic_process that doesn't divide by 4
        process_func(cleaned_df, self.generic_process, self.PPR_Q_JSON, config)
        logging.info(f"Finished processing for process {process_key}.")

    def generic_process(
        self,
        df: pd.DataFrame,
        process_key: str,
        PPR_JSON: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """
        PPR_Q specific generic_process with smart division logic.
        - For exact time ranges: No division (like original PPR_Q)
        - For historical fallback: Divide by number of weeks to get average
        """
        try:
            logging.info(f"Calculating metrics for {process_key}...")
            process_data = {}
            
            # DEBUG: Show DataFrame structure for rate debugging
            logging.info(f"[DEBUG] {process_key}: DataFrame shape = {df.shape}")
            logging.info(f"[DEBUG] {process_key}: Columns = {list(df.columns)}")
            if len(df) > 0:
                logging.info(f"[DEBUG] {process_key}: First row sample = {df.iloc[0].tolist()[:20]}")  # First 20 columns
            
            # 1) Extract columns based on config
            for col_key, col_idx in config.get("columns", {}).items():
                if col_idx < len(df.columns):
                    process_data[col_key] = df.iloc[:, col_idx].tolist()
                    # DEBUG: Show rate-related column data
                    if "Rate" in col_key:
                        sample_values = df.iloc[:5, col_idx].tolist() if len(df) > 0 else []
                        logging.info(f"[RATE] {process_key}: {col_key} (col {col_idx}) = {sample_values}")
                else:
                    logging.warning(f"Column index {col_idx} for {col_key} is out of bounds. DataFrame has {len(df.columns)} columns.")
                    process_data[col_key] = []
            
            # 2) Calculate sums based on conditions
            for sum_key, sum_config in config.get("sums", {}).items():
                total = 0.0
                if "conditions" in sum_config:
                    condition_mask = self.build_conditions(sum_config["conditions"], df)
                    total = df[condition_mask].iloc[:, sum_config["column"]].sum()
                elif "condition" in sum_config:
                    cond_col_idx, cond_val = sum_config["condition"]
                    matching_rows = df[df.iloc[:, cond_col_idx] == cond_val]
                    total = matching_rows.iloc[:, sum_config["column"]].sum()
                    
                    # DEBUG: Show rate calculation details
                    if "Rate" in sum_key or "rate" in sum_key.lower():
                        logging.info(f"[DEBUG] {process_key}: {sum_key} calculation:")
                        logging.info(f"   - Looking for '{cond_val}' in column {cond_col_idx}")
                        logging.info(f"   - Found {len(matching_rows)} matching rows")
                        if len(matching_rows) > 0:
                            sample_data = matching_rows.iloc[:3, sum_config["column"]].tolist()
                            logging.info(f"   - Sample values from column {sum_config['column']}: {sample_data}")
                        logging.info(f"   - Total before division: {total}")
                        if "divide_by" in sum_config:
                            logging.info(f"   - Will divide by: {sum_config['divide_by']}")
                        logging.info(f"   - Final result: {total / sum_config.get('divide_by', 1) if 'divide_by' in sum_config else total}")
            
                # Store the raw total before any division (this is the actual volume/hours)
                raw_total = total
                
                # For PPR_PRU, ALWAYS extract and store the actual volumes and hours from the data
                if process_key == "PPR_PRU" and ("Rate" in sum_key or "rate" in sum_key.lower()):
                    # Get the condition to find the matching row
                    cond_col_idx, cond_val = sum_config["condition"]
                    matching_rows = df[df.iloc[:, cond_col_idx] == cond_val]
                    
                    if len(matching_rows) > 0:
                        # Extract actual volume from column 7 and hours from column 8
                        actual_volume = matching_rows.iloc[0, 7] if len(matching_rows.columns) > 7 else 0
                        actual_hours = matching_rows.iloc[0, 8] if len(matching_rows.columns) > 8 else 0
                        
                        # Store the actual values
                        base_key = sum_key.replace("PRU_", "").replace("Rate", "").replace("rate", "")
                        volume_key = f"PRU_{base_key}_Volume"
                        hours_key = f"PRU_{base_key}_Hours"
                        
                        process_data[volume_key] = float(actual_volume)
                        process_data[hours_key] = float(actual_hours)
                        
                        logging.info(f"PPR_Q: Stored actual values for {sum_key}:")
                        logging.info(f"   - {volume_key} = {actual_volume}")
                        logging.info(f"   - {hours_key} = {actual_hours}")
                        logging.info(f"   - Current total = {total}")
                        
                        # For PPR_PRU, we should use the actual rate from column 9, not divide by anything
                        actual_rate = matching_rows.iloc[0, 9] if len(matching_rows.columns) > 9 else total
                        total = float(actual_rate)
                        
                        logging.info(f"   - Using actual rate from column 9: {actual_rate}")
                        
                        # Verify the calculation: rate should equal volume/hours
                        if actual_hours > 0:
                            calculated_rate = actual_volume / actual_hours
                            logging.info(f"   - Verification: {actual_volume} / {actual_hours} = {calculated_rate}")
                            if abs(calculated_rate - total) > 0.01:  # Allow small rounding differences
                                logging.warning(f"   - Rate mismatch! Expected {calculated_rate}, got {total}")
                
                # Apply divide_by logic ONLY for non-PPR_PRU processes
                elif "divide_by" in sum_config:
                    divisor = sum_config["divide_by"]
                    if divisor != 0:
                        total /= divisor
                        logging.info(f"PPR_Q: Applied divide_by {divisor} for {sum_key}: {total}")
                else:
                    # For rates without divide_by, calculate as volume/hours if we have both
                    if "Rate" in sum_key or "rate" in sum_key.lower():
                        # Try to find corresponding volume and hours
                        volume_key = sum_key.replace("Rate", "Volume").replace("rate", "Volume")
                        hours_key = sum_key.replace("Rate", "Hours").replace("rate", "Hours")
                        
                        if volume_key in process_data and hours_key in process_data:
                            volume = process_data[volume_key]
                            hours = process_data[hours_key]
                            if hours > 0:
                                total = volume / hours
                                logging.info(f"PPR_Q: Calculated rate {sum_key} = {volume} / {hours} = {total}")

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
        Executes the entire PPR_Q processing workflow.
        """
        logging.info('Starting PPR_Q processing...')
        logging.info(f'Site: {self.site}')
        logging.info(f'Time range: {self.sos_datetime} to {self.eos_datetime}')
        
        self.process_all_processes()
        
        # Calculate comprehensive target metrics
        self._calculate_comprehensive_metrics()
        
        # Add metadata about the run
        self.PPR_Q_JSON['_metadata'] = {
            'site': self.site,
            'sos_datetime': self.sos_datetime.isoformat(),
            'eos_datetime': self.eos_datetime.isoformat(),
            'execution_time_seconds': self.execution_time
        }
        
        logging.info('PPR_Q processing completed.')
        return self.PPR_Q_JSON
    
    def _calculate_comprehensive_metrics(self):
        """
        Calculate ALL target metrics using the modular calculators.
        """
        # Import the modular calculators
        from .metrics_calculator import enhance_ppr_q_with_all_metrics
        from .size_calculator import add_size_metrics_to_ppr_q
        
        logging.info("Calculating comprehensive target metrics...")
        
        # Add all target metrics
        self.PPR_Q_JSON = enhance_ppr_q_with_all_metrics(self.PPR_Q_JSON)
        
        # Add size-specific metrics using raw DataFrames
        self.PPR_Q_JSON = add_size_metrics_to_ppr_q(self.PPR_Q_JSON, self.raw_dataframes)
        
        # Clean up NaN values before returning
        self._clean_nan_values()
    
    def _clean_nan_values(self):
        """
        Recursively clean NaN values from the PPR_Q_JSON, replacing them with empty strings.
        """
        import math
        import numpy as np
        
        def clean_value(value):
            """Clean a single value, converting NaN to empty string."""
            if isinstance(value, float) and (math.isnan(value) or np.isnan(value)):
                return ""
            elif isinstance(value, str) and value == "NaN":
                return ""
            elif isinstance(value, dict):
                return {k: clean_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [clean_value(item) for item in value]
            else:
                return value
        
        logging.info("Cleaning NaN values from PPR_Q output...")
        self.PPR_Q_JSON = clean_value(self.PPR_Q_JSON)
        logging.info("NaN cleanup completed.")
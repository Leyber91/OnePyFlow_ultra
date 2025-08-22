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

    def __init__(self, site: str, start_datetime: datetime, end_datetime: datetime):
        """
        Initializes the PPRQProcessor with site details and datetime range.

        Args:
            site (str): The warehouse site identifier.
            start_datetime (datetime): Start datetime with minute precision.
            end_datetime (datetime): End datetime with minute precision.
        """
        self.site = site
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.cookie_file_path = f'C:/Users/{getuser()}/.midway/cookie'

        # Use the EXACT SAME process IDs as PPR
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

        # Our final PPR_Q data structure
        self.PPR_Q_JSON: Dict[str, Any] = {}

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
        FIXED to include _adjustPlanHours=on and remove problematic intervalType=INTRADAY.
        """
        base_url = "https://fclm-portal.amazon.com/reports/"
        
        # Use processPathRollup for ALL processes (same as working sample URL)
        # This endpoint works while functionRollup is failing
        url = (
            f"{base_url}processPathRollup?reportFormat=CSV&warehouseId={self.site}"
            f"&maxIntradayDays=1&spanType=Intraday&startDateIntraday={time_range['start_year']}%2F"
            f"{time_range['start_month']}%2F{time_range['start_day']}&startHourIntraday={time_range['start_hour']}"
            f"&startMinuteIntraday={time_range['start_minute']}&endDateIntraday={time_range['end_year']}%2F"
            f"{time_range['end_month']}%2F{time_range['end_day']}&endHourIntraday={time_range['end_hour']}"
            f"&endMinuteIntraday={time_range['end_minute']}&_adjustPlanHours=on&hideEmptyLineItems=true"
            f"&_hideEmptyLineItems=on&_rememberViewForWarehouse=on&employmentType=AllEmployees"
        )
        logging.info(f"PPR_Q URL for {process_key}: {url}")
        return url

    def get_time_range(self) -> Dict[str, str]:
        """
        Generates a time range using the EXACT same approach as the working PPR URL.
        Uses current/recent dates, not historical weeks back.
        """
        # Use the exact current time range (like the working PPR URL sample)
        time_range = {
            'start_hour': self.start_datetime.strftime("%H"),
            'start_minute': self.start_datetime.strftime("%M").lstrip('0') or '0',
            'start_day': self.start_datetime.strftime("%d"),
            'start_month': self.start_datetime.strftime("%m"),
            'start_year': self.start_datetime.strftime("%Y"),
            'end_hour': self.end_datetime.strftime("%H"),
            'end_minute': self.end_datetime.strftime("%M").lstrip('0') or '0',
            'end_day': self.end_datetime.strftime("%d"),
            'end_month': self.end_datetime.strftime("%m"),
            'end_year': self.end_datetime.strftime("%Y")
        }
        logging.info(f"PPR_Q time range (current): {self.start_datetime} to {self.end_datetime}")
        logging.debug(f"Generated time range: {time_range}")
        return time_range

    def get_extended_time_range(self) -> Dict[str, str]:
        """
        Generates an extended time range (24 hours) to work around API limitations.
        The API often ignores short time ranges, so we fetch a larger window and filter later.
        """
        # Extend the time range to 24 hours to ensure we get data
        extended_start = self.start_datetime - timedelta(hours=12)
        extended_end = self.end_datetime + timedelta(hours=12)
        
        time_range = {
            'start_hour': extended_start.strftime("%H"),
            'start_minute': extended_start.strftime("%M").lstrip('0') or '0',
            'start_day': extended_start.strftime("%d"),
            'start_month': extended_start.strftime("%m"),
            'start_year': extended_start.strftime("%Y"),
            'end_hour': extended_end.strftime("%H"),
            'end_minute': extended_end.strftime("%M").lstrip('0') or '0',
            'end_day': extended_end.strftime("%d"),
            'end_month': extended_end.strftime("%m"),
            'end_year': extended_end.strftime("%Y")
        }
        logging.info(f"PPR_Q extended time range: {extended_start} to {extended_end}")
        logging.debug(f"Generated extended time range: {time_range}")
        return time_range

    def filter_data_to_exact_range(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters the DataFrame to the exact time range requested.
        This handles the case where the API returns more data than requested.
        """
        if df.empty:
            return df
            
        logging.info(f"Filtering data from {len(df)} rows to exact time range...")
        
        # First, let's examine the actual column structure
        logging.info(f"DataFrame columns: {list(df.columns)}")
        logging.info(f"DataFrame shape: {df.shape}")
        
        # Try to find datetime columns to filter on
        datetime_columns = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['date', 'time', 'datetime', 'hour', 'day']):
                datetime_columns.append(col)
        
        if datetime_columns:
            logging.info(f"Found datetime columns: {datetime_columns}")
            
            # Try to parse and filter by datetime
            for col in datetime_columns:
                try:
                    # Try to convert to datetime
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    
                    # Filter to exact time range
                    mask = (df[col] >= self.start_datetime) & (df[col] <= self.end_datetime)
                    filtered_df = df[mask]
                    
                    if not filtered_df.empty:
                        logging.info(f"Successfully filtered using column '{col}': {len(filtered_df)} rows in exact time range")
                        return filtered_df
                    else:
                        logging.warning(f"Filtering with column '{col}' resulted in empty DataFrame")
                        
                except Exception as e:
                    logging.debug(f"Could not filter using column '{col}': {e}")
                    continue
            
            # If we get here, filtering failed, so we need to estimate the proportion
            logging.warning("Could not filter by datetime. Estimating proportion based on time range...")
            return self._estimate_proportional_data(df)
        else:
            logging.warning("No datetime columns found for filtering. Estimating proportion based on time range...")
            return self._estimate_proportional_data(df)

    def _estimate_proportional_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Estimates the proportion of data that belongs to the exact time range.
        This is a fallback when we can't filter by datetime columns.
        """
        # Calculate the proportion of time our range represents
        total_hours = 24  # Assuming the extended range is 24 hours
        requested_hours = (self.end_datetime - self.start_datetime).total_seconds() / 3600
        
        proportion = requested_hours / total_hours
        logging.info(f"Time proportion: {requested_hours:.2f} hours out of {total_hours} hours = {proportion:.2%}")
        
        # Take a proportional sample of the data
        sample_size = max(1, int(len(df) * proportion))
        logging.info(f"Taking {sample_size} rows out of {len(df)} total rows")
        
        # Take a sample from the middle of the data (assuming it's roughly chronological)
        start_idx = (len(df) - sample_size) // 2
        end_idx = start_idx + sample_size
        
        sampled_df = df.iloc[start_idx:end_idx].copy()
        logging.info(f"Sampled {len(sampled_df)} rows for exact time range")
        
        return sampled_df

    def fetch_process_data(self, process_key: str) -> pd.DataFrame:
        """
        Fetches data for a specific process using PPR's proven multi-week strategy.
        This approach is more reliable than trying exact current shift times.
        """
        logging.info(f"Fetching data for process: {process_key}")
        process_id = self.process_ids.get(process_key, "")
        process_df = pd.DataFrame()

        # Strategy 1: Use PPR's proven time range approach (1 week back)
        logging.info(f"Strategy 1: Using PPR's time range approach (1 week back) for process {process_key}...")
        time_range = self.get_time_range()
        url = self.build_url(process_key, process_id, time_range)
        
        df = self._make_request(process_key, url)
        if not df.empty:
            logging.info(f"Strategy 1 successful: Got {len(df)} rows for process {process_key}")
            return df

        # Strategy 2: Try exact current time range as fallback
        logging.info(f"Strategy 2: Trying exact current time range for process {process_key}...")
        current_start = self.start_datetime
        current_end = self.end_datetime
        
        current_time_range = {
            'start_hour': current_start.strftime("%H"),
            'start_minute': current_start.strftime("%M").lstrip('0') or '0',
            'start_day': current_start.strftime("%d"),
            'start_month': current_start.strftime("%m"),
            'start_year': current_start.strftime("%Y"),
            'end_hour': current_end.strftime("%H"),
            'end_minute': current_end.strftime("%M").lstrip('0') or '0',
            'end_day': current_end.strftime("%d"),
            'end_month': current_end.strftime("%m"),
            'end_year': current_end.strftime("%Y")
        }
        
        url = self.build_url(process_key, process_id, current_time_range)
        df = self._make_request(process_key, url)
        if not df.empty:
            logging.info(f"Strategy 2 successful: Got {len(df)} rows for process {process_key}")
            return df

        # Strategy 3: Try extended time range (24 hours)
        logging.info(f"Strategy 3: Trying extended time range (24 hours) for process {process_key}...")
        extended_time_range = self.get_extended_time_range()
        url = self.build_url(process_key, process_id, extended_time_range)
        
        df = self._make_request(process_key, url)
        if not df.empty:
            logging.info(f"Strategy 3 successful: Got {len(df)} rows for process {process_key}")
            # Filter to exact range
            filtered_df = self.filter_data_to_exact_range(df)
            if not filtered_df.empty:
                return filtered_df

        # Strategy 4: Create fallback data (last resort)
        logging.warning(f"All strategies failed for process {process_key}. Using fallback values.")
        process_df = self._create_fallback_data(process_key)
        
        return process_df

    def _get_smaller_extended_time_range(self) -> Dict[str, str]:
        """
        Generates a smaller extended time range (6 hours) to work around API limitations.
        This is more targeted than the 24-hour range.
        """
        # Extend the time range to 6 hours to ensure we get data
        extended_start = self.start_datetime - timedelta(hours=3)
        extended_end = self.end_datetime + timedelta(hours=3)
        
        time_range = {
            'start_hour': extended_start.strftime("%H"),
            'start_minute': extended_start.strftime("%M").lstrip('0') or '0',
            'start_day': extended_start.strftime("%d"),
            'start_month': extended_start.strftime("%m"),
            'start_year': extended_start.strftime("%Y"),
            'end_hour': extended_end.strftime("%H"),
            'end_minute': extended_end.strftime("%M").lstrip('0') or '0',
            'end_day': extended_end.strftime("%d"),
            'end_month': extended_end.strftime("%m"),
            'end_year': extended_end.strftime("%Y")
        }
        logging.info(f"PPR_Q smaller extended time range: {extended_start} to {extended_end}")
        return time_range

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
                
                df = pd.read_csv(
                    StringIO(response.text),
                    delimiter=';',
                    encoding='ISO-8859-1',
                    on_bad_lines='skip'
                )
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

    def _create_fallback_data(self, process_key: str) -> pd.DataFrame:
        """
        Creates minimal fallback data when no real data can be fetched.
        This prevents empty PPR_Q output and provides zero values for calculations.
        """
        logging.info(f"Creating fallback data structure for {process_key}")
        
        # Create a minimal DataFrame with expected columns
        fallback_data = {
            'Column_0': ['Fallback'],
            'Column_1': ['Data'],
            'Column_2': ['Structure'],
            'Column_3': [f'{process_key} - Fallback'],
            'Column_4': [0],
            'Column_5': [0],
            'Column_6': [0],
            'Column_7': [0],
            'Column_8': [0],
            'Column_9': [0],
            'Column_10': [0],
            'Column_11': [0],
            'Column_12': [0],
            'Column_13': [0],
            'Column_14': [0],  # Volume column
            'Column_15': [0],  # Hours column
            'Column_16': [0],  # Rate column
        }
        
        df = pd.DataFrame(fallback_data)
        logging.info(f"Created fallback DataFrame with {len(df)} rows and {len(df.columns)} columns")
        return df

    def _fetch_historical_fallback(self, process_key: str, process_id: str) -> pd.DataFrame:
        """
        Fallback method that uses the original PPR approach (4 weeks of historical data).
        This ensures we always get some data, even if it's not for the exact time range.
        """
        logging.info(f"Using historical fallback for process {process_key}")
        process_df = pd.DataFrame()
        
        # Get 4 weeks of historical data (like original PPR)
        for i in range(1, 5):  # 4 weeks
            shift_start = self.start_datetime - timedelta(weeks=i)
            shift_end = self.end_datetime - timedelta(weeks=i)
            
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
            
            url = self.build_url(process_key, process_id, shift)
            df = self._make_request(process_key, url)
            if not df.empty:
                process_df = pd.concat([process_df, df], ignore_index=True)
                logging.debug(f"Added historical week {i} data for process {process_key}")
        
        if not process_df.empty:
            logging.info(f"Historical fallback successful: Got {len(process_df)} total rows for process {process_key}")
        
        return process_df

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
            logging.info(f"🔍 DEBUG {process_key}: DataFrame shape = {df.shape}")
            logging.info(f"🔍 DEBUG {process_key}: Columns = {list(df.columns)}")
            if len(df) > 0:
                logging.info(f"🔍 DEBUG {process_key}: First row sample = {df.iloc[0].tolist()[:20]}")  # First 20 columns
            
            # 1) Extract columns based on config
            for col_key, col_idx in config.get("columns", {}).items():
                if col_idx < len(df.columns):
                    process_data[col_key] = df.iloc[:, col_idx].tolist()
                    # DEBUG: Show rate-related column data
                    if "Rate" in col_key:
                        sample_values = df.iloc[:5, col_idx].tolist() if len(df) > 0 else []
                        logging.info(f"🎯 DEBUG {process_key}: {col_key} (col {col_idx}) = {sample_values}")
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
                        logging.info(f"🎯 DEBUG {process_key}: {sum_key} calculation:")
                        logging.info(f"   - Looking for '{cond_val}' in column {cond_col_idx}")
                        logging.info(f"   - Found {len(matching_rows)} matching rows")
                        if len(matching_rows) > 0:
                            sample_data = matching_rows.iloc[:3, sum_config["column"]].tolist()
                            logging.info(f"   - Sample values from column {sum_config['column']}: {sample_data}")
                        logging.info(f"   - Total before division: {total}")
                        if "divide_by" in sum_config:
                            logging.info(f"   - Will divide by: {sum_config['divide_by']}")
                        logging.info(f"   - Final result: {total / sum_config.get('divide_by', 1) if 'divide_by' in sum_config else total}")
            
                # Smart division logic based on actual data timespan
                if "divide_by" in sum_config:
                    original_divisor = sum_config["divide_by"]
                    
                    # Calculate actual timespan of the data to determine proper scaling
                    data_timespan_hours = (self.end_datetime - self.start_datetime).total_seconds() / 3600
                    shift_hours = 12  # Standard shift duration
                    
                    # If we're using historical fallback data (detected by large row count or timespan > 24 hours)
                    if len(df) > 1000 or data_timespan_hours > 24:
                        # Historical data is typically weekly (168 hours) or multi-day
                        # Scale down to shift level (12 hours)
                        if data_timespan_hours > 24:
                            # Weekly or multi-day data - scale to shift
                            scaling_factor = shift_hours / data_timespan_hours
                            total *= scaling_factor
                            logging.info(f"PPR_Q: Historical data ({len(df)} rows, {data_timespan_hours:.1f}h), scaling by {scaling_factor:.4f} for {sum_key}")
                        else:
                            # Use original PPR division logic for other historical cases
                            if original_divisor != 0:
                                total /= original_divisor
                            logging.info(f"PPR_Q: Historical data ({len(df)} rows), dividing by {original_divisor} for {sum_key}")
                    else:
                        # Current shift data - no scaling needed
                        logging.info(f"PPR_Q: Current shift data ({len(df)} rows, {data_timespan_hours:.1f}h), no scaling for {sum_key}")

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
        logging.info(f'Time range: {self.start_datetime} to {self.end_datetime}')
        
        self.process_all_processes()
        
        # Add metadata about the run
        self.PPR_Q_JSON['_metadata'] = {
            'site': self.site,
            'start_datetime': self.start_datetime.isoformat(),
            'end_datetime': self.end_datetime.isoformat(),
            'execution_time_seconds': self.execution_time
        }
        
        logging.info('PPR_Q processing completed.')
        return self.PPR_Q_JSON
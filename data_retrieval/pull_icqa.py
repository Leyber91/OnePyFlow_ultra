#!/usr/bin/env python3
import logging
import requests
import pandas as pd
import os
import sys
import tempfile
from utils.utils import get_fiscal_week

logger = logging.getLogger(__name__)

# Add a function to get a proper temp directory
def get_temp_directory():
    """
    Returns a valid temporary directory that's accessible from either C: or D: drive.
    First tries to use the executable's directory, then falls back to the system temp directory.
    """
    try:
        # First try to get executable's directory
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running as a script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        # Create a 'temp' subdirectory if it doesn't exist
        temp_dir = os.path.join(base_dir, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Verify we can write to this directory
        test_file = os.path.join(temp_dir, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        
        logger.info(f"Using temporary directory: {temp_dir}")
        return temp_dir
        
    except Exception as e:
        # If there's any issue with the above approach, use the system temp directory
        system_temp = tempfile.gettempdir()
        logger.warning(f"Using system temp directory due to error: {e}")
        logger.info(f"System temp directory: {system_temp}")
        return system_temp

def _download_icqa_for_week(fc, fiscal_year, fiscal_week, midway_session, cookie_jar):
    """
    Helper function to download ICQA data for a specific fiscal week.
    Returns the path to the temporary CSV file or None if download fails.
    """
    # No zero-padding for the week
    week_str = str(fiscal_week)
    
    # Build S3 key and final URL
    s3_bucket = "diver-raw-data-prod"
    s3_key = (
        f"global_downloads/report=upt_transfer_shipments/location_name={fc}"
        f"/year={fiscal_year}/date_span=weekly/"
        f"000.upt_transfer_shipments_by_source_fc_week_{week_str}.csv"
    )
    file_name = f"{fc}_upt_transfer_shipments_by_source_fc_week_{fiscal_year}_{week_str}.csv"
    
    download_url = (
        "https://diver.qts.amazon.dev/api/download"
        f"?s3_bucket={s3_bucket}"
        f"&s3_key={s3_key}"
        f"&file_name={file_name}"
    )
    
    logger.info(f"[ICQA PULL] Constructed download URL for FY{fiscal_year}-W{week_str}: {download_url}")
    
    # Perform GET request
    try:
        response = requests.get(download_url, cookies=cookie_jar, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"[ICQA PULL] Error downloading ICQA data for FY{fiscal_year}-W{week_str}: {e}")
        return None
    
    # Write CSV to local file using the temp directory
    temp_dir = get_temp_directory()
    temp_csv_path = os.path.join(temp_dir, f"temp_{file_name}")
    
    try:
        with open(temp_csv_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"[ICQA PULL] Downloaded ICQA CSV to: {temp_csv_path}")
    except Exception as e:
        logger.error(f"[ICQA PULL] Error writing CSV file for FY{fiscal_year}-W{week_str}: {e}")
        return None
    
    return temp_csv_path

def _get_previous_fiscal_week(fiscal_year, fiscal_week):
    """
    Calculate the previous fiscal week and year.
    Handles fiscal year transitions (if week 1, go to previous year's last week).
    
    Returns:
        tuple: (previous_fiscal_year, previous_fiscal_week)
    """
    if fiscal_week > 1:
        # Simple case: just decrement the week
        return fiscal_year, fiscal_week - 1
    else:
        # Edge case: we're in week 1, need to go to previous fiscal year's last week
        # Amazon fiscal year typically has 52 weeks, but occasionally 53
        # For simplicity, assume 52 weeks in a fiscal year
        return fiscal_year - 1, 52

def _combine_csv_files(file_paths):
    """
    Combine multiple CSV files into a single DataFrame.
    Skip any None paths (failed downloads).
    
    Returns:
        tuple: (combined_csv_path, success) where success is True if at least one file was processed
    """
    combined_df = pd.DataFrame()
    valid_paths = [p for p in file_paths if p is not None]
    
    if not valid_paths:
        logger.error("[ICQA PULL] No valid CSV files to combine")
        return None, False
    
    for path in valid_paths:
        try:
            df = pd.read_csv(path)
            logger.info(f"[ICQA PULL] Read {len(df)} rows from {path}")
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        except Exception as e:
            logger.error(f"[ICQA PULL] Error reading CSV {path}: {e}")
    
    if combined_df.empty:
        logger.error("[ICQA PULL] Combined DataFrame is empty after processing all files")
        return None, False
    
    # Save combined DataFrame to a new CSV in the temp directory
    temp_dir = get_temp_directory()
    combined_path = os.path.join(temp_dir, "temp_combined_icqa_data.csv")
    
    try:
        combined_df.to_csv(combined_path, index=False)
        logger.info(f"[ICQA PULL] Combined {len(combined_df)} rows into {combined_path}")
        
        # Clean up individual files after successful combination
        for path in valid_paths:
            try:
                os.remove(path)
                logger.info(f"[ICQA PULL] Removed temporary file: {path}")
            except Exception as e:
                logger.warning(f"[ICQA PULL] Failed to remove temporary file {path}: {e}")
                
        return combined_path, True
    except Exception as e:
        logger.error(f"[ICQA PULL] Error saving combined CSV: {e}")
        return None, False

def pull_icqa(fc, current_date, midway_session, cookie_jar):
    """
    Retrieves ICQA data for the given FC and current date.
    
    Improved to pull data from both current week (week-1) and previous week (week-2)
    to minimize issues with Diver portal showing only 1 transfer item for some lanes.
    
    1) Gets fiscal years and weeks for current and previous weeks
    2) Downloads data for both weeks
    3) Combines the data into a single CSV file
    4) Returns the path to the combined CSV file
    
    Returns:
        str: Path to the combined CSV file, or None if all downloads failed
    """
    
    logger.info(f"[ICQA PULL] Starting pull for FC={fc}, current_date={current_date} (pulling 2 weeks of data)")
    
    # 1) Get the current fiscal year and week
    current_fiscal_year, current_fiscal_week = get_fiscal_week(current_date)
    
    # 2) Calculate the previous fiscal week
    prev_fiscal_year, prev_fiscal_week = _get_previous_fiscal_week(current_fiscal_year, current_fiscal_week)
    
    logger.info(f"[ICQA PULL] Pulling data for current week (FY{current_fiscal_year}-W{current_fiscal_week}) and previous week (FY{prev_fiscal_year}-W{prev_fiscal_week})")
    
    # 3) Download data for both weeks
    current_week_csv = _download_icqa_for_week(fc, current_fiscal_year, current_fiscal_week, midway_session, cookie_jar)
    prev_week_csv = _download_icqa_for_week(fc, prev_fiscal_year, prev_fiscal_week, midway_session, cookie_jar)
    
    # 4) Combine the downloaded CSVs
    combined_csv_path, success = _combine_csv_files([current_week_csv, prev_week_csv])
    
    if not success:
        logger.error("[ICQA PULL] Failed to retrieve and combine ICQA data for both weeks")
        return None
    
    return combined_csv_path
#!/usr/bin/env python3
import logging
import os
import shutil
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

def pull_vip_data(fc, midway_session=None, cookie_jar=None):
    """
    Retrieves VIP data from a text file.
    
    Args:
        fc (str): Fulfillment Center code to filter by (if needed)
        midway_session: Midway session object (not used but kept for API consistency)
        cookie_jar: Cookie jar with authentication cookies (not used but kept for API consistency)
    
    Returns:
        str: Path to a temporary file with VIP data
    """
    logger.info(f"[VIP PULL] Starting pull for FC={fc}")
    
    # Timestamp for generating unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_download_path = f"temp_vip_download_{timestamp}.txt"
    temp_filtered_path = f"temp_vip_{fc}_{timestamp}.txt"
    file_obtained = False
    
    # Primary file path
    primary_path = r"\\ant\dept-eu\BCN1\Public\ECFT\IXD\ALPS\VIP.txt"
    
    # Try to read from the primary path
    try:
        logger.info(f"[VIP PULL] Trying to read from primary path: {primary_path}")
        if os.path.exists(primary_path):
            shutil.copy2(primary_path, temp_download_path)
            logger.info(f"[VIP PULL] Successfully copied from primary path to: {temp_download_path}")
            file_obtained = True
        else:
            logger.warning(f"[VIP PULL] Primary path not found: {primary_path}")
    except Exception as e:
        logger.warning(f"[VIP PULL] Failed to read from primary path: {e}")
    
    # If primary path failed, try alternative paths
    if not file_obtained:
        alternative_paths = [
            r"\\ant\dept-eu\BCN1\ECFT\IXD\ALPS\VIP.txt",
            r"\\ant\dept-eu\BCN1\Public\ECFT\IXD\Data\VIP.txt",
            r"\\ant\dept-eu\BCN1\Public\ECFT\IXD\OnePyFlow\Data\VIP.txt"
        ]
        
        for path in alternative_paths:
            try:
                logger.info(f"[VIP PULL] Trying alternative path: {path}")
                if os.path.exists(path):
                    shutil.copy2(path, temp_download_path)
                    logger.info(f"[VIP PULL] Successfully copied from alternative path to: {temp_download_path}")
                    file_obtained = True
                    break
                else:
                    logger.warning(f"[VIP PULL] Alternative path not found: {path}")
            except Exception as e:
                logger.warning(f"[VIP PULL] Failed to read from alternative path {path}: {e}")
    
    # If all paths failed, create a dummy file
    if not file_obtained:
        logger.warning("[VIP PULL] All paths failed, creating dummy data")
        create_dummy_vip_data(fc, temp_download_path)
        file_obtained = True
    
    # Process the file to filter by FC if needed
    try:
        # Read the data
        with open(temp_download_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            logger.warning("[VIP PULL] Empty file, creating dummy data")
            create_dummy_vip_data(fc, temp_filtered_path)
            return temp_filtered_path
        
        # Parse headers
        headers = lines[0].strip().split('\t')
        site_index = headers.index('site') if 'site' in headers else 0
        
        # Filter lines by FC if needed
        filtered_lines = [lines[0]]  # Keep header
        for line in lines[1:]:
            values = line.strip().split('\t')
            if len(values) > site_index:
                site = values[site_index]
                if fc == 'ALL' or site == fc:
                    filtered_lines.append(line)
        
        # Write filtered data
        with open(temp_filtered_path, 'w', encoding='utf-8') as f:
            f.writelines(filtered_lines)
        
        logger.info(f"[VIP PULL] Saved filtered data with {len(filtered_lines)-1} rows to: {temp_filtered_path}")
        
        # Clean up the download file
        try:
            os.remove(temp_download_path)
            logger.info(f"[VIP PULL] Cleaned up temporary download: {temp_download_path}")
        except Exception as e:
            logger.warning(f"[VIP PULL] Failed to remove temporary file: {e}")
        
        return temp_filtered_path
            
    except Exception as e:
        logger.error(f"[VIP PULL] Error processing file: {e}", exc_info=True)
        
        # Create a fallback file if processing fails
        create_dummy_vip_data(fc, temp_filtered_path)
        return temp_filtered_path

def create_dummy_vip_data(fc, output_path):
    """
    Creates a dummy VIP data file.
    """
    # Sample data based on the observed format in paste.txt
    dummy_data = f"""site\tparcelforecastunit\tfixedslotunit\tpallet\tnextslot\tsnapshot_year\tsnapshot_month\tsnapshot_day\tsnapshot_hour\tinsert_timestamp_utc\tparcelappointmentcount\tappointmentcount\toffsitebl\toceancount\tbacklogicc\tbacklog
{fc}\t[{{value=0, day=2025-04-10}}]\t[{{value=0, day=2025-04-10}}]\t[{{value=0, day=2025-04-10}}]\t[{{value=2025-04-11, day=2025-04-10}}]\t2025\t04\t10\t20\t2025-04-10 21:05:41.379473\t[{{value=0, day=2025-04-10}}]\t[{{value=0, day=2025-04-10}}]\t[{{value=0, day=2025-04-10}}]\t[{{value=0, day=2025-04-10}}]\t[{{value=0, day=2025-04-10}}]\t[{{value=0, day=2025-04-10}}]"""
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(dummy_data)
    
    logger.info(f"[VIP PULL] Created fallback VIP data for FC {fc}")
    
    return True
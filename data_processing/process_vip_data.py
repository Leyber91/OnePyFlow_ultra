#!/usr/bin/env python3
import logging
import os
from datetime import datetime
import re

logger = logging.getLogger(__name__)

def process_vip_data(file_path):
    """
    Processes the VIP data from a text file.
    
    Args:
        file_path (str): Path to the text file containing VIP data
        
    Returns:
        dict: Dictionary containing VIP data and metadata
    """
    logger.info(f"[VIP PROCESS] Processing VIP data from: {file_path}")
    
    try:
        # Read the text file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            logger.warning("[VIP PROCESS] Empty file")
            return create_empty_result()
        
        # Parse headers and data
        headers = lines[0].strip().split('\t')
        site_data = {}
        
        for line in lines[1:]:
            values = line.strip().split('\t')
            if len(values) != len(headers):
                logger.warning(f"[VIP PROCESS] Skipping invalid line: {line}")
                continue
            
            site = values[0]
            site_values = {}
            
            for i, header in enumerate(headers):
                if i == 0:  # Skip site column
                    continue
                
                value = values[i]
                # Parse arrays like [{value=0, day=2025-04-10}]
                if value.startswith('[{') and value.endswith('}]'):
                    try:
                        # Extract array items
                        array_items = []
                        # Extract each {value=X, day=Y} pair
                        pattern = r'\{value=(.*?), day=(.*?)\}'
                        matches = re.findall(pattern, value)
                        
                        for match in matches:
                            item = {
                                "value": match[0],
                                "day": match[1]
                            }
                            array_items.append(item)
                        
                        site_values[header] = array_items
                    except Exception as e:
                        logger.warning(f"[VIP PROCESS] Error parsing array {value}: {e}")
                        site_values[header] = value
                else:
                    site_values[header] = value
            
            site_data[site] = site_values
        
        # Extract metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "site_count": len(site_data),
            "sites": list(site_data.keys()),
            "row_count": len(lines) - 1
        }
        
        # Create result dictionary with both data and metadata
        result = {
            "vip_data": site_data,
            "metadata": metadata
        }
        
        # Delete the temporary file
        try:
            os.remove(file_path)
            logger.info(f"[VIP PROCESS] Removed temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"[VIP PROCESS] Failed to remove temporary file {file_path}: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"[VIP PROCESS] Error processing VIP data: {e}", exc_info=True)
        
        # Try to delete the temporary file even if processing failed
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"[VIP PROCESS] Removed temporary file after error: {file_path}")
        except Exception as rm_error:
            logger.warning(f"[VIP PROCESS] Failed to remove temporary file: {rm_error}")
            
        # Return empty result with error information
        return create_empty_result(str(e))

def create_empty_result(error=None):
    """
    Creates an empty result structure.
    
    Args:
        error (str, optional): Error message to include in metadata
        
    Returns:
        dict: Empty result structure
    """
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "site_count": 0,
        "sites": [],
        "row_count": 0
    }
    
    if error:
        metadata["error"] = error
    
    return {
        "vip_data": {},
        "metadata": metadata
    }
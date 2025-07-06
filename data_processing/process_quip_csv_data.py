#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: process_quip_csv_data.py
Description: Processes raw Quip CSV data (a list of lists) into a list of dictionaries.
             This enhanced function cleans header names, pads rows if needed, and strips whitespace.
             If no data rows are present, it returns None.
"""

import logging

logger = logging.getLogger(__name__)

def transform_quip_data(rows):
    """
    Transforms raw CSV data into a list of dictionaries with enhanced cleaning.
    
    Parameters:
        rows (list of lists): The raw CSV data with the first row as headers.
        
    Returns:
        list of dict or None: The transformed CSV records, or None if input is insufficient.
    """
    if not rows or len(rows) < 2:
        logger.warning("[QuipCSV] No rows or only header. Returning None.")
        return None
    
    # Clean header: strip each header cell.
    header = rows[0]
    data_rows = rows[1:]
    
    # Build a list of tuples (index, cleaned_header) for non-empty headers.
    header_index = []
    for i, col_name in enumerate(header):
        col_stripped = col_name.strip()
        if col_stripped:
            header_index.append((i, col_stripped))
    
    final_list = []
    for row in data_rows:
        # Pad the row with empty strings if it is shorter than the header.
        while len(row) < len(header):
            row.append("")
        # Build a dictionary mapping header to cell (stripping extra whitespace from each cell).
        row_dict = {}
        for (col_idx, col_name) in header_index:
            if col_idx < len(row):  # Safety check to prevent index errors
                row_dict[col_name] = row[col_idx].strip()
            else:
                row_dict[col_name] = ""  # Pad with empty string if row is too short
        final_list.append(row_dict)
    
    logger.info(f"[QuipCSV] Transformed into {len(final_list)} dict rows.")
    return final_list

def process_quip_csv_data(raw_csv):
    """
    A wrapper that processes raw CSV data by invoking transform_quip_data.
    
    Parameters:
        raw_csv (list of lists): The raw CSV data.
        
    Returns:
        list of dict or None: The processed CSV records or None if input is invalid.
    """
    if raw_csv is None:
        logger.warning("[QuipCSV] Received None as input. Returning None.")
        return None
    
    try:
        return transform_quip_data(raw_csv)
    except Exception as e:
        logger.error(f"[QuipCSV] Error processing CSV data: {e}")
        return None
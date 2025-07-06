#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module: process_rc_sort_data.py
Description: Processes raw RC Sort data into a structured format suitable for JSON.
             This function transforms keys of the format "60_63_2_189_2_2_2025" into sequential
             date keys starting from "2024-12-29", with each subsequent key incremented by 7 days.
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def process_rc_sort_data(rc_sort_raw_data):
    """
    Processes raw RC Sort data into a dictionary with keys in "YYYY-MM-DD" format.
    
    Args:
        rc_sort_raw_data (dict): Raw RC Sort data extracted from HTML.
    
    Returns:
        dict: Processed RC Sort data with sequential date keys.
        
    Example:
        Given raw data:
        {
            "60_63_2_189_2_2_2025": "",
            "60_63_2_189_2_9_2025": "0.48000",
            "60_63_2_189_2_16_2025": "0.48990",
            ...
        }
        The output will be:
        {
            "2024-12-29": "",
            "2025-01-05": "0.48000",
            "2025-01-12": "0.48990",
            ...
        }
    """
    logger.info("Processing RC Sort data.")

    if not isinstance(rc_sort_raw_data, dict):
        logger.error("Expected raw RC Sort data to be a dictionary.")
        return None

    try:
        # Set the base date from which to start assigning new date keys.
        base_date = datetime.strptime("2024-12-29", "%Y-%m-%d")

        def sort_key(cell_id):
            parts = cell_id.split('_')
            try:
                # Expected format: "60_63_2_189_2_2_2025"
                # Use the 5th and 6th parts (indexes 4 and 5) for sorting.
                week = int(parts[4])
                day = int(parts[5])
                return (week, day)
            except Exception as e:
                logger.warning(f"Error parsing key '{cell_id}': {e}")
                return (0, 0)

        sorted_keys = sorted(rc_sort_raw_data.keys(), key=sort_key)

        processed_data = {}
        for i, key in enumerate(sorted_keys):
            new_date = base_date + timedelta(weeks=i)
            new_key = new_date.strftime("%Y-%m-%d")
            processed_data[new_key] = rc_sort_raw_data[key]

        logger.info("RC Sort data processed successfully.")
        return processed_data

    except Exception as e:
        logger.error(f"Error processing RC Sort data: {e}", exc_info=True)
        return None


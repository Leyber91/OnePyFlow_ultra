# utils/calculate_percentages.py

import logging
import pandas as pd

logger = logging.getLogger(__name__)

def calculate_percentages(df):
    """
    Calculate percentages for specific line items.

    Parameters:
    - df (pd.DataFrame): DataFrame containing 'LineItem' and 'Value' columns.

    Returns:
    - dict: Dictionary with line items as keys and their corresponding percentages as values.
    """
    try:
        # Check if 'LineItem' column exists
        if 'LineItem' not in df.columns:
            logger.error("'LineItem' column not found in DataFrame")
            return {}

        # Check if 'Value' column exists
        if 'Value' not in df.columns:
            logger.error("'Value' column not found in DataFrame")
            return {}

        # Convert 'Value' column to numeric, replacing any non-numeric values with 0
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce').fillna(0)

        total_row = df[df['LineItem'] == 'Receive - Total']
        if total_row.empty:
            logger.error("'Receive - Total' row not found in DataFrame")
            return {}

        total = total_row['Value'].iloc[0]
        if total == 0:
            logger.error("'Receive - Total' value is zero, cannot calculate percentages")
            return {}

        # Items to calculate percentages for
        items_to_calculate = [
            'Each Receive - Total',
            'LP Receive',
            'Pallet Receive',
            'Case Receive',
            'Cubiscan',
            'Prep Recorder - Total',
            'RC Sort - Total'
        ]

        percentages = {}
        for item in items_to_calculate:
            item_row = df[df['LineItem'] == item]
            if not item_row.empty:
                value = item_row['Value'].iloc[0]
                percentages[item.replace(" - ", " ")] = (value / total) * 100
            else:
                logger.warning(f"'{item}' not found in DataFrame")
                percentages[item.replace(" - ", " ")] = 0

        return percentages
    except Exception as e:
        logger.error(f"Error in calculate_percentages: {e}")
        return {}

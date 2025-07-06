import logging
import pandas as pd

logger = logging.getLogger(__name__)


def process_galaxy2_data(raw_data):
    """
    Processes Galaxy2 data and returns JSON.
    """
    try:
        df = pd.json_normalize(raw_data)

        # Map the JSON column names to our desired column names
        column_mapping = {
            'lineItem': 'LineItem',
            'date': 'date',
            'weekNumber': 'weekNumber',
            'value': 'Value'
        }

        # Create a new DataFrame with only the columns we need
        new_df = pd.DataFrame()
        for json_col, our_col in column_mapping.items():
            if json_col in df.columns:
                new_df[our_col] = df[json_col]
            else:
                new_df[our_col] = None
                logger.warning(f"Column '{json_col}' not found in Galaxy2 data. Adding with None values.")

        # Extract values for specific items
        numeric_items = [
            "Receive Dock",
            "Each Receive - Total",
            "LP Receive",
            "Pallet Receive",
            "Receive Support",
            "Case Receive",
            "Cubiscan",
            "Prep - Total",
            "Prep Recorder - Total",
            "Prep - Pallet",
            "Prep Support",
            "RSR Support",
            "IB Lead/PA",
            "IB Problem Solve",
            "RC Sort - Total",
            "Transfer Out",
            "Merge/Fusion",
            "Fluid load",
            "Manual palletize",
            "Transfer Out Dock",
            "TO Lead/PA",
            "TO Problem Solve"
        ]

        galaxy2_values = {}
        for item in numeric_items:
            item_row = new_df[new_df['LineItem'] == item]
            galaxy2_values[item] = float(item_row['Value'].iloc[0]) if not item_row.empty else 0.0

        logger.info("Galaxy2 data processed successfully.")
        
        # Convert processed DataFrame and galaxy2_values to JSON
        return (new_df, galaxy2_values)

    except Exception as e:
        logger.error(f"Error processing Galaxy2 data: {e}")
        return None
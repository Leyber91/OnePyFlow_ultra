
import logging
import pandas as pd

from utils.utils import calculate_percentages

logger = logging.getLogger(__name__)

def process_galaxy_data(raw_data):
    """
    Processes Galaxy data and returns JSON.
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
                logger.warning(f"Column '{json_col}' not found in Galaxy data. Adding with None values.")

        # Calculate percentages
        percentages = calculate_percentages(new_df)

        logger.info("Galaxy data processed successfully.")
        
        # Convert processed DataFrame and percentages to JSON
        return (new_df, percentages)

    except Exception as e:
        logger.error(f"Error processing Galaxy data: {e}")
        return None
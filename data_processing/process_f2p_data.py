import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def process_f2p_data(df_f2p):
    """
    Processes the F2P data and returns a nested structure with headers and contents.
    FIXED: Preserves original date columns instead of overwriting them with today+N.
    """
    try:
        if df_f2p is None or df_f2p.empty:
            logger.error("No F2P data to process or DataFrame is empty.")
            return None

        # Make a copy to avoid modifying the original
        df_processed = df_f2p.copy()

        # Remove any row where the first column is purely numeric or 0
        df_processed = df_processed[~df_processed.iloc[:, 0].astype(str).str.match(r'^\d*\.?\d*$')]

        # Replace '->' with '_' in the Arc column (first column)
        df_processed.iloc[:, 0] = df_processed.iloc[:, 0].str.replace('->', '_')

        # FIXED: Keep the original column names (dates) from the pivot table
        # We only make sure the first column is named 'Arc'
        if df_processed.columns[0] != 'Arc':
            df_processed.rename(columns={df_processed.columns[0]: 'Arc'}, inplace=True)

        # Log the actual date columns we're keeping for debugging
        date_columns = [col for col in df_processed.columns if col != 'Arc']
        logger.info(f"Preserving original date columns from F2P_DICE.txt: {date_columns}")

        # Sort by the first date column descending if we have date columns
        if len(date_columns) > 0:
            df_processed = df_processed.sort_values(by=date_columns[0], ascending=False)

        # Replace empty or missing values with 0
        df_processed.fillna(0, inplace=True)

        # -------------------------------------------------------------------
        # Remove any row that has Arc == 0 before converting to dictionary
        df_processed = df_processed[df_processed['Arc'] != 0]
        # -------------------------------------------------------------------

        # Convert to desired JSON structure
        headers = df_processed.columns.tolist()
        contents = df_processed.to_dict(orient='records')

        result = {
            "headers": headers,
            "contents": contents
        }

        logger.info("F2P data processed successfully with original dates preserved.")
        return result

    except Exception as e:
        logger.error(f"Error processing F2P data: {e}", exc_info=True)
        return None
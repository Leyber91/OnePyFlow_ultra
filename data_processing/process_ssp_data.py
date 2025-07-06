import logging

# Configure logging
logger = logging.getLogger(__name__)


def process_ssp_data(retrieval_result):
    """
    Processes the SSPPull retrieved data.

    Parameters:
    - retrieval_result (dict): Dictionary containing the DataFrame and timestamp.

    Returns:
    - pd.DataFrame: Processed DataFrame ready for output.
    """
    # Handle case where no data was retrieved
    if retrieval_result is None:
        logger.warning("No SSP data retrieved to process.")
        return None
    
    try:
        df = retrieval_result['dataframe']
        timestamp = retrieval_result['timestamp']

        # Additional processing if needed
        # For instance, calculating total containers
        df['Total_Containers'] = df['Totes'] + df['Cartons']

        logger.info(f"Processed SSPPull data with timestamp {timestamp}.")
        return df
    except Exception as e:
        logger.error(f"Error processing SSPPull data: {e}")
        logger.debug("Exception details:", exc_info=True)
        return None
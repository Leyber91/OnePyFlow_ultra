# utils/add_calculations_to_galaxy.py

import logging
from datetime import datetime

from utils.calculate_percentages import calculate_percentages

logger = logging.getLogger(__name__)

def add_calculations_to_galaxy(ws, df):
    """Add calculations to the Galaxy worksheet"""
    try:
        percentages = calculate_percentages(df)
        if not percentages:
            logger.warning("No percentages calculated. Skipping addition to Galaxy worksheet.")
            return

        # Use current date instead of Sunday's date
        current_date = datetime.now().strftime("%Y-%m-%d")
        ws.cell(row=1, column=13, value=current_date)  # Cell M1
        ws.cell(row=1, column=14, value=df['weekNumber'].iloc[0])  # Cell N1

        # Clean calculation items (remove slashes)
        calculation_items = [
            "Each Receive Total", "LP Receive", "Pallet Receive", "Receive Support",
            "Case Receive", "Cubiscan", "Prep Recorder Total", "RC Sort Total"
        ]

        for idx, item in enumerate(calculation_items, start=4):
            ws.cell(row=idx, column=13, value=item)
            # Get percentage value without slash in the key
            clean_item = item.replace(" - ", " ").replace("Receive Support", "Receive Support")
            ws.cell(row=idx, column=14, value=percentages.get(clean_item, 0) / 100)
            ws.cell(row=idx, column=14).number_format = '0.00%'

        logger.info("Calculations added to Galaxy worksheet successfully.")
    except Exception as e:
        logger.error(f"Error in add_calculations_to_galaxy: {e}")

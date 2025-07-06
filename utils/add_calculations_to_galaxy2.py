# utils/add_calculations_to_galaxy2.py

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def add_calculations_to_galaxy2(ws, df):
    """Add calculations to the Galaxy2 worksheet"""
    try:
        # Updated calculation items list to include all numeric values
        calculation_items = [
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

        # Use current date instead of Sunday's date
        current_date = datetime.now().strftime("%Y-%m-%d")
        ws.cell(row=1, column=11, value=current_date)  # Cell K1
        ws.cell(row=1, column=12, value=df['weekNumber'].iloc[0])  # Cell L1

        for idx, item in enumerate(calculation_items, start=1):
            ws.cell(row=idx, column=11, value=item)
            item_row = df[df['LineItem'] == item]
            # Default to 0 if the item is not found
            value = item_row['Value'].iloc[0] if not item_row.empty else 0
            ws.cell(row=idx, column=12, value=value)
            ws.cell(row=idx, column=12).number_format = '#,##0'

        logger.info("Calculations added to Galaxy2 worksheet successfully.")
    except Exception as e:
        logger.error(f"Error in add_calculations_to_galaxy2: {e}")

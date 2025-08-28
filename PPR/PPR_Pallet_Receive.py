# PPR_Pallet_Receive.py

import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

CONFIG: Dict[str, Any] = {
    "columns": {
        "Pallet_Receive_function_name": 1,
        "Pallet_Receive_paid_hours_total": 10,
        "Pallet_Receive_unit_type": 14,
        "Pallet_Receive_Size": 15,
        "Pallet_Receive_Units": 16
    },
    "sums": {
        "PalletPrEditor_LP_TotalUnits": {
            "conditions": [
                (15, "Total"),
                (14, "EACH"),
                (1, "PalletPrEditor-LP")
            ],
            "column": 16
        },
        "PalletPrEditorManual_TotalUnits": {
            "conditions": [
                (15, "Total"),
                (14, "EACH"),
                (1, "PalletPrEditorManual")
            ],
            "column": 16
        },
        "PalletPrEditorManual_TotalHours": {
            "conditions": [
                (15, "Total"),
                (14, "EACH"),
                (1, "PalletPrEditorManual")
            ],
            "column": 10
        },
        "Pallet_Receive_TotalCases": {
            "conditions": [
                (14, "Case"),
                (15, "Total")
            ],
            "column": 16
        },
        "Pallet_Receive_TotalPallets": {
            "conditions": [
                (14, "Pallet"),
                (15, "Total")
            ],
            "column": 16
        },
        "SmallsTotal": {
            "conditions": [
                (15, "Small")
            ],
            "column": 16
        },
        "Total": {
            "conditions": [
                (15, "Total"),
                (14, "EACH")
            ],
            "column": 16
        },
        # Missing metrics from table
        "PalletPrEditor_LP_TotalHours": {
            "conditions": [
                (15, "Total"),
                (14, "EACH"),
                (1, "PalletPrEditor-LP")
            ],
            "column": 10
        },
        "PalletPrEditor_LP_TotalJobs": {
            "conditions": [
                (15, "Total"),
                (14, "Pallet"),
                (1, "PalletPrEditor-LP")
            ],
            "column": 12
        },
        "PalletPrEditorManual_TotalJobs": {
            "conditions": [
                (15, "Total"),
                (14, "Pallet"),
                (1, "PalletPrEditorManual")
            ],
            "column": 12
        },
        "TotalHours": {
            "conditions": [
                (15, "Total"),
                (14, "EACH")
            ],
            "column": 10
        },
        "TotalJobs": {
            "conditions": [
                (15, "Total"),
                (14, "Pallet")
            ],
            "column": 12
        }
    }
}

def process_PPR_Pallet_Receive(df: DataFrame,
                               generic_process,
                               PPR_JSON: Dict[str, Any],
                               config: Dict[str, Any]) -> None:
    """
    Handles custom logic for PPR_Pallet_Receive. After generic processing,
    we compute 'MonoAsinUPP' = (PalletPrEditorManual_TotalUnits / Pallet_Receive_TotalPallets).
    """
    logging.info("Processing PPR_Pallet_Receive...")
    if "PPR_Pallet_Receive" not in PPR_JSON:
        PPR_JSON["PPR_Pallet_Receive"] = {}

    # 1) Perform the generic processing
    generic_process(df, "PPR_Pallet_Receive", PPR_JSON, config)

    # 2) Retrieve the dictionary for "PPR_Pallet_Receive"
    pallet_data = PPR_JSON.get("PPR_Pallet_Receive", {})

    # 3) Extract needed values (defaults to 0.0 if missing)
    pallet_pr_editor_manual_units = pallet_data.get("PalletPrEditorManual_TotalUnits", 0.0)
    pallet_receive_total_pallets = pallet_data.get("Pallet_Receive_TotalPallets", 0.0)

    # 4) Compute the new metric (avoid div-by-zero)
    if pallet_receive_total_pallets != 0.0:
        mono_asin_upp = pallet_pr_editor_manual_units / pallet_receive_total_pallets
    else:
        mono_asin_upp = 0.0

    # 5) Store it
    pallet_data["MonoAsinUPP"] = mono_asin_upp
    
    # 6) Calculate overall rate (PPH - Pallets Per Hour) for metrics validation
    total_pallets = pallet_data.get("Pallet_Receive_TotalPallets", 0.0)
    total_hours = pallet_data.get("TotalHours", 0.0)
    if total_hours > 0:
        overall_rate = total_pallets / total_hours
        pallet_data["OverallUPH"] = overall_rate
        logging.info(f"Calculated OverallUPH (PPH): {overall_rate:.2f} ({total_pallets} pallets / {total_hours} hours)")
    else:
        pallet_data["OverallUPH"] = 0.0

    # 7) Update self.PPR_JSON
    PPR_JSON["PPR_Pallet_Receive"] = pallet_data

    logging.info(f"Added MonoAsinUPP metric to PPR_Pallet_Receive: {mono_asin_upp:.2f}")
    logging.info("Finished PPR_Pallet_Receive.")

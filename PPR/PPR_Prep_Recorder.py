# PPR_Prep_Recorder.py

import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

CONFIG: Dict[str, Any] = {
    "columns": {
        "Prep_Recorder_paid_hours_total": 10,
        "Prep_Recorder_job_action": 11,
        "Prep_Recorder_unit_type": 14,
        "Prep_Recorder_Size": 15,
        "Prep_Recorder_Units": 16
    },
    "sums": {
        "EachReceived_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (11, "EachReceived")],
            "column": 16
        },
        "ItemPrepped_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (11, "ItemPrepped")],
            "column": 16
        },
        "ItemPrepped_TotalHours": {
            "conditions": [(15, "Total"), (14, "EACH"), (11, "ItemPrepped")],
            "column": 10
        },
        "PrepAssortment_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (11, "PrepAssortment")],
            "column": 16
        },
        "PrepAssortment_TotalHours": {
            "conditions": [(15, "Total"), (14, "EACH"), (11, "PrepAssortment")],
            "column": 10
        },
        "PalletReceived_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (11, "PalletReceived")],
            "column": 16
        },
        "SmallsTotal": {
            "conditions": [(15, "Small")],
            "column": 16
        },
        "Total": {
            "conditions": [(15, "Total")],
            "column": 16
        }
    }
}

def process_PPR_Prep_Recorder(df: DataFrame,
                              generic_process,
                              PPR_JSON: Dict[str, Any],
                              config: Dict[str, Any]) -> None:
    """
    Custom logic for PPR_Prep_Recorder. After generic processing, 
    we compute a new rate: ItemPrepped_Rate = ItemPrepped_TotalUnits / ItemPrepped_TotalHours.
    """
    logging.info("Processing PPR_Prep_Recorder...")
    if "PPR_Prep_Recorder" not in PPR_JSON:
        PPR_JSON["PPR_Prep_Recorder"] = {}

    # 1) Perform generic config-based processing
    generic_process(df, "PPR_Prep_Recorder", PPR_JSON, config)

    # 2) Additional rate computation
    prep_data = PPR_JSON.get("PPR_Prep_Recorder", {})
    item_prepped_units = prep_data.get("ItemPrepped_TotalUnits", 0.0)
    item_prepped_hours = prep_data.get("ItemPrepped_TotalHours", 0.0)

    if item_prepped_hours != 0:
        prep_data["ItemPrepped_Rate"] = item_prepped_units / item_prepped_hours
    else:
        prep_data["ItemPrepped_Rate"] = 0.0

    PPR_JSON["PPR_Prep_Recorder"] = prep_data
    logging.info("Finished PPR_Prep_Recorder.")

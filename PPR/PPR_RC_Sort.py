# PPR_RC_Sort.py

import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

CONFIG: Dict[str, Any] = {
    "columns": {
        "RC_Sort_function_name": 1,
        "RC_Sort_paid_hours_total": 10,
        "RC_Sort_unit_type": 14,
        "RC_Sort_size": 15,
        "RC_Sort_units": 16
    },
    "sums": {
        "RC_Sort_Primary_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "RC Sort Primary")],
            "column": 16
        },
        "RC_Sort_Primary_TotalHours": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "RC Sort Primary")],
            "column": 10
        },
        "UIS_5lb_Induct_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "UIS_5lb_Induct")],
            "column": 16
        },
        "UIS_5lb_Induct_TotalHours": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "UIS_5lb_Induct")],
            "column": 10
        },
        "UIS_20lb_Induct_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "UIS_20lb_Induct")],
            "column": 16
        },
        "UIS_20lb_Induct_TotalHours": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "UIS_20lb_Induct")],
            "column": 10
        },
        "Small_Units_Manual": {
            "conditions": [(15, "Small"), (14, "EACH"), (1, "RC Sort Primary")],
            "column": 16
        },
        "Small_Units_UIS5": {
            "conditions": [(15, "Small"), (14, "EACH"), (1, "UIS_5lb_Induct")],
            "column": 16
        },
        "Small_Units_UIS20": {
            "conditions": [(15, "Small"), (14, "EACH"), (1, "UIS_20lb_Induct")],
            "column": 16
        }
    }
}

def process_PPR_RC_Sort(df: DataFrame,
                        generic_process,
                        PPR_JSON: Dict[str, Any],
                        config: Dict[str, Any]) -> None:
    logging.info("Processing PPR_RC_Sort...")
    if "PPR_RC_Sort" not in PPR_JSON:
        PPR_JSON["PPR_RC_Sort"] = {}

    generic_process(df, "PPR_RC_Sort", PPR_JSON, config)
    logging.info("Finished PPR_RC_Sort.")

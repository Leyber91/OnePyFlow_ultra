# PPR_Cubiscan.py

import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

CONFIG: Dict[str, Any] = {
    "columns": {
        "Cubiscan_Function_Name": 1,
        "Cubiscan_Unit_Type": 14,
        "Cubiscan_Size": 15,
        "Cubiscan_Units": 16
    },
    "sums": {
        "ATACEgress_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "ATAC Egress")],
            "column": 16
        },
        "ATACEgress_TotalCases": {
            "conditions": [(15, "Total"), (14, "Bin"), (1, "ATAC Egress")],
            "column": 16
        },
        "Cubiscan_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "Cubiscan")],
            "column": 16
        },
        "Cubiscan_TotalCases": {
            "conditions": [(15, "Total"), (14, "Bin"), (1, "Cubiscan")],
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

def process_PPR_Cubiscan(df: DataFrame,
                         generic_process,
                         PPR_JSON: Dict[str, Any],
                         config: Dict[str, Any]) -> None:
    logging.info("Processing PPR_Cubiscan...")
    if "PPR_Cubiscan" not in PPR_JSON:
        PPR_JSON["PPR_Cubiscan"] = {}

    generic_process(df, "PPR_Cubiscan", PPR_JSON, config)

    logging.info("Finished PPR_Cubiscan.")

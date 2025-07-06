# PPR_Transfer_Out_Dock.py

import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

CONFIG: Dict[str, Any] = {
    "columns": {
        "Transfer_Out_Dock_job_action": 11,
        "Transfer_Out_Dock_unit_type": 14,
        "Transfer_Out_Dock_Size": 15,
        "Transfer_Out_Dock_Units": 16
    },
    "sums": {
        "Fluid_Load_Tote": {
            "conditions": [(15, "Total"), (14, "EACH"), (11, "FluidLoadTote")],
            "column": 16
        },
        "Fluid_Load_Case": {
            "conditions": [(15, "Total"), (14, "EACH"), (11, "FluidLoadCase")],
            "column": 16
        }
    }
}

def process_PPR_Transfer_Out_Dock(df: DataFrame,
                                  generic_process,
                                  PPR_JSON: Dict[str, Any],
                                  config: Dict[str, Any]) -> None:
    logging.info("Processing PPR_Transfer_Out_Dock...")
    if "PPR_Transfer_Out_Dock" not in PPR_JSON:
        PPR_JSON["PPR_Transfer_Out_Dock"] = {}

    generic_process(df, "PPR_Transfer_Out_Dock", PPR_JSON, config)
    logging.info("Finished PPR_Transfer_Out_Dock.")

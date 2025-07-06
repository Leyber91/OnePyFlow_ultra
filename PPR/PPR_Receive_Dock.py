# PPR_Receive_Dock.py

import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

CONFIG: Dict[str, Any] = {
    "columns": {},
    "sums": {}
}

def process_PPR_Receive_Dock(df: DataFrame,
                             generic_process,
                             PPR_JSON: Dict[str, Any],
                             config: Dict[str, Any]) -> None:
    """
    No calculations needed for Receive Dock, so just store a placeholder.
    """
    logging.info("Processing PPR_Receive_Dock...")
    PPR_JSON["PPR_Receive_Dock"] = "No data required"
    logging.info("Finished PPR_Receive_Dock.")

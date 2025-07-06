# PPR_RC_Presort.py

import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

CONFIG: Dict[str, Any] = {
    "columns": {},
    "sums": {
        "RC_Presort_size": {"conditions": [(15, "Total")], "column": 16},
        "RC_Presort_units": {"conditions": [(15, "Total")], "column": 16},
        "Total": {"conditions": [(15, "Total")], "column": 16}
    }
}

def process_PPR_RC_Presort(df: DataFrame,
                           generic_process,
                           PPR_JSON: Dict[str, Any],
                           config: Dict[str, Any]) -> None:
    logging.info("Processing PPR_RC_Presort...")
    if "PPR_RC_Presort" not in PPR_JSON:
        PPR_JSON["PPR_RC_Presort"] = {}

    generic_process(df, "PPR_RC_Presort", PPR_JSON, config)
    logging.info("Finished PPR_RC_Presort.")

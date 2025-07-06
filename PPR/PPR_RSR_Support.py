###############################################################################
# PPR_RSR_Support.py
###############################################################################
import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

###############################################################################
# CONFIG Dictionary
###############################################################################
# We point to the 4 columns we need:
#   - column 1  => RSR_Support_function_name
#   - column 14 => RSR_Support_unit_type
#   - column 15 => RSR_Support_size
#   - column 16 => RSR_Support_units
#
# Then we define a sum replicating:
#   =SUMIFS(Q:Q, B:B, "Decant", P:P, "Total", O:O, "Each")
# In uppercase form: DECANT, TOTAL, EACH
###############################################################################
CONFIG: Dict[str, Any] = {
    "columns": {
        "RSR_Support_function_name": 1,   # B => "Decant"
        "RSR_Support_unit_type": 14,      # O => "Each"
        "RSR_Support_size": 15,           # P => "Total"
        "RSR_Support_units": 16           # Q => sum
    },
    "sums": {
        "Decant_Each_Total": {
            "conditions": [
                (1, "DECANT"),  # RSR_Support_function_name column => "DECANT"
                (15, "TOTAL"),  # RSR_Support_size          => "TOTAL"
                (14, "EACH")    # RSR_Support_unit_type     => "EACH"
            ],
            "column": 16  # RSR_Support_units => sum of that column
        }
    }
}


def process_PPR_RSR_Support(
    df: DataFrame,
    generic_process,                 # The shared function from PPR_processor
    PPR_JSON: Dict[str, Any],
    config: Dict[str, Any]
) -> None:
    """
    1) Normalizes text in the relevant columns (uppercase/strip).
    2) Uses generic_process() to replicate the Excel formula:
       =SUMIFS(Q:Q,B:B,"Decant", P:P,"Total", O:O,"Each")
       in uppercase form: "DECANT", "TOTAL", "EACH".
    3) Places the result in PPR_JSON["PPR_RSR_Support"]["Decant_Each_Total"].
    """

    logging.info("Processing PPR_RSR_Support...")

    # Make sure the sub-dict in PPR_JSON exists
    if "PPR_RSR_Support" not in PPR_JSON:
        PPR_JSON["PPR_RSR_Support"] = {}

    # -------------------------------------------------------------------------
    # 1) Normalize text in the relevant columns so matching doesn't fail
    #    because of case or trailing spaces.
    # -------------------------------------------------------------------------
    fn_col = config["columns"]["RSR_Support_function_name"]  # typically 1
    ut_col = config["columns"]["RSR_Support_unit_type"]      # 14
    sz_col = config["columns"]["RSR_Support_size"]           # 15

    # Convert to string, strip, uppercase
    df.iloc[:, fn_col] = df.iloc[:, fn_col].astype(str).str.strip().str.upper()
    df.iloc[:, ut_col] = df.iloc[:, ut_col].astype(str).str.strip().str.upper()
    df.iloc[:, sz_col] = df.iloc[:, sz_col].astype(str).str.strip().str.upper()

    # -------------------------------------------------------------------------
    # 2) Adjust conditions in config to uppercase so they match
    # -------------------------------------------------------------------------
    # Note: If your config currently has "Decant", "Total", "Each",
    #       we need to change them to "DECANT", "TOTAL", "EACH":
    for condition_tuple in config["sums"]["Decant_Each_Total"]["conditions"]:
        col_idx, expected_val = condition_tuple
        # Convert expected_val to uppercase if it's a string
        if isinstance(expected_val, str):
            new_val = expected_val.strip().upper()
            # We'll replace in-place
            config["sums"]["Decant_Each_Total"]["conditions"] = [
                (cidx, new_val if (cidx == col_idx and val == expected_val) else val)
                for (cidx, val) in config["sums"]["Decant_Each_Total"]["conditions"]
            ]

    # -------------------------------------------------------------------------
    # 3) Use generic_process to do the sum
    # -------------------------------------------------------------------------
    generic_process(df, "PPR_RSR_Support", PPR_JSON, config)

    # The sum is now stored in:
    # PPR_JSON["PPR_RSR_Support"]["Decant_Each_Total"]

    # Log the final value
    final_val = PPR_JSON["PPR_RSR_Support"].get("Decant_Each_Total", 0.0)
    logging.info(f"Decant_Each_Total => {final_val}")

    logging.info("Finished PPR_RSR_Support.")

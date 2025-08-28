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
        "RSR_Support_job_action": 11,     # Job Action column
        "RSR_Support_jobs": 12,           # Jobs column
        "RSR_Support_unit_type": 14,      # O => "Each"
        "RSR_Support_size": 15,           # P => "Total"
        "RSR_Support_units": 16,          # Q => sum
        "RSR_Support_paid_hours": 10      # Paid Hours Total column
    },
    "sums": {
        "Decant_Each_Total": {
            "conditions": [
                (1, "DECANT"),  # RSR_Support_function_name column => "DECANT"
                (15, "TOTAL"),  # RSR_Support_size          => "TOTAL"
                (14, "EACH")    # RSR_Support_unit_type     => "EACH"
            ],
            "column": 16  # RSR_Support_units => sum of that column
        },
        "Decant_Small_Units": {
            "conditions": [
                (1, "DECANT"),
                (15, "SMALL"),
                (14, "EACH")
            ],
            "column": 16
        },
        "Decant_Medium_Units": {
            "conditions": [
                (1, "DECANT"),
                (15, "MEDIUM"),
                (14, "EACH")
            ],
            "column": 16
        },
        "Decant_Large_Units": {
            "conditions": [
                (1, "DECANT"),
                (15, "LARGE"),
                (14, "EACH")
            ],
            "column": 16
        },
        "Decant_HeavyBulky_Units": {
            "conditions": [
                (1, "DECANT"),
                (15, "HEAVYBULKY"),
                (14, "EACH")
            ],
            "column": 16
        },
        "EachToted_Total": {
            "conditions": [
                (11, "EACHTOTED"),
                (15, "TOTAL")
            ],
            "column": 16
        },
        "EachToted_Small": {
            "conditions": [
                (11, "EACHTOTED"),
                (15, "SMALL")
            ],
            "column": 16
        },
        "EachToted_Medium": {
            "conditions": [
                (11, "EACHTOTED"),
                (15, "MEDIUM")
            ],
            "column": 16
        },
        "EachToted_Large": {
            "conditions": [
                (11, "EACHTOTED"),
                (15, "LARGE")
            ],
            "column": 16
        },
        "Jobs_Total": {
            "conditions": [
                (15, "TOTAL")
            ],
            "column": 12  # Jobs column
        },
        "SmallsTotal": {
            "conditions": [
                (15, "SMALL")
            ],
            "column": 16
        },
        "Total": {
            "conditions": [
                (15, "TOTAL")
            ],
            "column": 16
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
    Enhanced PPR_RSR_Support processing with comprehensive metrics:
    1) Normalizes text in the relevant columns (uppercase/strip).
    2) Uses generic_process() to calculate multiple metrics including:
       - Size-specific Decant metrics (Small, Medium, Large, HeavyBulky)
       - EachToted metrics by size
       - Total jobs and units
    3) Calculates additional rates and totals for completeness.
    """

    logging.info("Processing PPR_RSR_Support...")

    # Make sure the sub-dict in PPR_JSON exists
    if "PPR_RSR_Support" not in PPR_JSON:
        PPR_JSON["PPR_RSR_Support"] = {}

    # -------------------------------------------------------------------------
    # 1) Normalize text in the relevant columns so matching doesn't fail
    # -------------------------------------------------------------------------
    fn_col = config["columns"]["RSR_Support_function_name"]  # typically 1
    ja_col = config["columns"]["RSR_Support_job_action"]     # 11
    ut_col = config["columns"]["RSR_Support_unit_type"]      # 14
    sz_col = config["columns"]["RSR_Support_size"]           # 15

    # Convert to string, strip, uppercase
    df.iloc[:, fn_col] = df.iloc[:, fn_col].astype(str).str.strip().str.upper()
    df.iloc[:, ja_col] = df.iloc[:, ja_col].astype(str).str.strip().str.upper()
    df.iloc[:, ut_col] = df.iloc[:, ut_col].astype(str).str.strip().str.upper()
    df.iloc[:, sz_col] = df.iloc[:, sz_col].astype(str).str.strip().str.upper()

    # -------------------------------------------------------------------------
    # 2) Use generic_process to calculate all metrics
    # -------------------------------------------------------------------------
    generic_process(df, "PPR_RSR_Support", PPR_JSON, config)

    # -------------------------------------------------------------------------
    # 3) Calculate additional derived metrics
    # -------------------------------------------------------------------------
    rsr_data = PPR_JSON["PPR_RSR_Support"]
    
    # Calculate total hours for Decant function
    decant_hours = 0.0
    paid_hours_col = config["columns"]["RSR_Support_paid_hours"]
    
    # Sum paid hours for Decant rows with Total size
    for idx, row in df.iterrows():
        if (str(row.iloc[fn_col]).upper() == "DECANT" and 
            str(row.iloc[sz_col]).upper() == "TOTAL"):
            try:
                decant_hours += float(row.iloc[paid_hours_col])
            except (ValueError, TypeError):
                pass
    
    rsr_data["Decant_TotalHours"] = decant_hours
    
    # Calculate Decant rate (units per hour)
    decant_total = rsr_data.get("Decant_Each_Total", 0.0)
    if decant_hours > 0:
        rsr_data["Decant_Rate"] = decant_total / decant_hours
    else:
        rsr_data["Decant_Rate"] = 0.0
    
    # Calculate EachToted rate if we have hours data
    eachtoted_total = rsr_data.get("EachToted_Total", 0.0)
    if decant_hours > 0 and eachtoted_total > 0:
        rsr_data["EachToted_Rate"] = eachtoted_total / decant_hours
    else:
        rsr_data["EachToted_Rate"] = 0.0

    # Log key metrics
    logging.info(f"Decant_Each_Total => {decant_total}")
    logging.info(f"Decant_TotalHours => {decant_hours}")
    logging.info(f"Decant_Rate => {rsr_data.get('Decant_Rate', 0.0):.2f}")
    logging.info(f"EachToted_Total => {eachtoted_total}")
    logging.info(f"SmallsTotal => {rsr_data.get('SmallsTotal', 0.0)}")
    logging.info(f"Total => {rsr_data.get('Total', 0.0)}")

    logging.info("Finished PPR_RSR_Support.")

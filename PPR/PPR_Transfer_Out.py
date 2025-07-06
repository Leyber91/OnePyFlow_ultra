###############################################################################
# PPR_Transfer_Out.py
###############################################################################
import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

###############################################################################
# CONFIG Dictionary
###############################################################################
# Adjust these column indices to match how your DataFrame is actually structured.
# The 'sums' section defines which rows to sum for each key (e.g. "Fluid_Load_Tote")
# based on multiple conditions (like Size="Total", UnitType="EACH", etc.).
###############################################################################
CONFIG: Dict[str, Any] = {
    "columns": {
        # Example mapping: if df.columns[2] is the site code
        # and df.columns[10] is paid hours, etc., then set them here.
        "Site": 2,  
        "Transfer_Out_paid_hours_total": 10,     
        "Transfer_Out_paid_job_action": 11,      
        "Transfer_Out_unit_type": 14,            
        "Transfer_Out_Size": 15,                 
        "Transfer_Out_Units": 16                 
    },

    "sums": {
        # -----------------------------------------------------------------------
        # Fluid Loading (Tote/Case)
        # -----------------------------------------------------------------------
        "Fluid_Load_Tote": {
            "conditions": [
                (15, "Total"),        # Size
                (14, "EACH"),         # Unit Type
                (11, "FluidLoadTote") # Job Action
            ],
            "column": 16  # Summation column (Units)
        },
        "Fluid_Load_Case": {
            "conditions": [
                (15, "Total"), 
                (14, "EACH"), 
                (11, "FluidLoadCase")
            ],
            "column": 16
        },

        # -----------------------------------------------------------------------
        # Misc (LPReceived, Merged_Container, etc.)
        # -----------------------------------------------------------------------
        "LP_Received": {
            "conditions": [
                (15, "Total"), 
                (14, "EACH"), 
                (11, "LPReceived")
            ],
            "column": 16
        },
        "Merged_Container": {
            "conditions": [
                (15, "Total"), 
                (14, "EACH"), 
                (11, "MergeContainer")
            ],
            "column": 16
        },
        "Pallet_Checkin": {
            "conditions": [
                (15, "Total"), 
                (14, "EACH"), 
                (11, "PalletCheckin")
            ],
            "column": 16
        },
        "Presort_Item_Scanned": {
            "conditions": [
                (15, "Total"), 
                (14, "EACH"), 
                (11, "PresortItemScanned")
            ],
            "column": 16
        },

        # -----------------------------------------------------------------------
        # Scanning & Palletizing (ScanCaseToPallet, ScanToteToPallet, etc.)
        # -----------------------------------------------------------------------
        "Scan_Case_To_Pallet": {
            "conditions": [
                (15, "Total"), 
                (14, "EACH"), 
                (11, "ScanCaseToPallet")
            ],
            "column": 16
        },
        "Scan_Tote_To_Pallet": {
            "conditions": [
                (15, "Total"), 
                (14, "EACH"), 
                (11, "ScanToteToPallet")
            ],
            "column": 16
        },
        "Transship_Pallet_Verified": {
            "conditions": [
                (15, "Total"), 
                (14, "EACH"), 
                (11, "TransshipPalletVerified")
            ],
            "column": 16
        },

        # -----------------------------------------------------------------------
        # Robot vs. Manual
        # -----------------------------------------------------------------------
        "Palletized_Robot": {
            "conditions": [
                (4, "Anonymous"),            # If you only want site "AB1"
                (14, "EACH"), 
                (15, "Total"), 
                (11, "ScanToteToPallet")
            ],
            "column": 16
        },
        "Palletized_Cases": {
            "conditions": [
                (14, "EACH"), 
                (15, "Total"), 
                (11, "ScanCaseToPallet")
            ],
            "column": 16
        },
        "Fluid_Totes": {
            "conditions": [
                (15, "Total"), 
                (14, "EACH"), 
                (11, "FluidLoadTote")
            ],
            "column": 16
        },
        "Fluid_Cases": {
            "conditions": [
                (15, "Total"), 
                (14, "EACH"), 
                (11, "FluidLoadCase")
            ],
            "column": 16
        },
        "Totes_Robot_Palletized": {
            "conditions": [
                (4, "Anonymous"), 
                (14, "Tote"), 
                (15, "Total"), 
                (11, "ScanToteToPallet")
            ],
            "column": 16
        },
        "Totes_Totales_Palletized": {
            "conditions": [
                (14, "Tote"), 
                (15, "Total"), 
                (11, "ScanToteToPallet")
            ],
            "column": 16
        },
        "Cajas_Manual": {
            "conditions": [
                (14, "Case"), 
                (15, "Total"), 
                (11, "ScanCaseToPallet")
            ],
            "column": 16
        },

        # -----------------------------------------------------------------------
        # Containers (Fluids) 
        # -----------------------------------------------------------------------
        "Containers_Fluids_Totes": {
            "conditions": [
                (14, "Tote"), 
                (15, "Total"), 
                (11, "FluidLoadTote")
            ],
            "column": 16
        },
        "Containers_Fluids_Cases": {
            "conditions": [
                (14, "Case"), 
                (15, "Total"), 
                (11, "FluidLoadCase")
            ],
            "column": 16
        },

        # -----------------------------------------------------------------------
        # Hours (WallBuilder, Palletizing, Merging, etc.)
        # -----------------------------------------------------------------------
        "Wall_Builder_Hours": {
            "conditions": [
                (1, "Wall Builder")
            ],
            "column": 10
        },
        "Palletized_Cases_Hours": {
            "conditions": [
                (1, "Palletize - Case"),
                (11, "ScanCaseToPallet"), 
                (14, "EACH"), 
                (15, "Total")
            ],
            "column": 10
        },
        "Units_Merged": {
            "conditions": [
                (14, "EACH"), 
                (15, "Total"), 
                (11, "MergeContainer")
            ],
            "column": 16
        },
        "Containers_Merged": {
            "conditions": [
                (14, "Container"), 
                (15, "Total"), 
                (11, "MergeContainer")
            ],
            "column": 16
        },
        "Merge_Hours": {
            "conditions": [
                (14, "EACH"), 
                (15, "Total"), 
                (11, "MergeContainer")
            ],
            "column": 10
        },
        "Palletized_Totes_Manual": {
            "conditions": [
                (3, ">0"), 
                (14, "EACH"), 
                (15, "Total"), 
                (11, "ScanToteToPallet")
            ],
            "column": 16
        }
    }
}


###############################################################################
# process_PPR_Transfer_Out
###############################################################################
# This is the main function that:
#  1) Invokes generic_process(...) to fill PPR_JSON["PPR_Transfer_Out"] 
#     with standard sums (Fluid_Load_Tote, Fluid_Load_Case, etc.).
#  2) Reads "Fluid_Totes" + "Fluid_Cases" from the sums to get total fluid units.
#  3) Reproduces Excel-like SUMIFS logic to sum fluid hours from df **including** 
#     "Wall Builder" if your logic says so.
#  4) Divides fluid units by fluid hours => "Fluids" rate. 
#  5) Stores "Fluids" in PPR_JSON["PPR_Transfer_Out"] so it shows up in final results.
###############################################################################
def process_PPR_Transfer_Out(
    df: DataFrame,
    generic_process,
    PPR_JSON: Dict[str, Any],
    config: Dict[str, Any]
) -> None:
    logging.info("Processing PPR_Transfer_Out...")

    # Ensure the dictionary key is present
    if "PPR_Transfer_Out" not in PPR_JSON:
        PPR_JSON["PPR_Transfer_Out"] = {}

    # 1) Run the standard sums
    generic_process(df, "PPR_Transfer_Out", PPR_JSON, config)

    # 2) Summation from the dictionary
    t_out_data = PPR_JSON["PPR_Transfer_Out"]
    fluid_totes = t_out_data.get("Fluid_Totes", 0.0)
    fluid_cases = t_out_data.get("Fluid_Cases", 0.0)
    total_fluids_units = fluid_totes + fluid_cases

    # 3) Build a mask that replicates your “Excel SUMIFS” for fluid hours
    site_idx   = config["columns"]["Site"]                           
    hours_idx  = config["columns"]["Transfer_Out_paid_hours_total"]  
    job_idx    = config["columns"]["Transfer_Out_paid_job_action"]   
    unit_idx   = config["columns"]["Transfer_Out_unit_type"]         
    size_idx   = config["columns"]["Transfer_Out_Size"]              

    #  
    # If you want to include "Wall Builder" in the same hours as FluidLoadCase / FluidLoadTote,
    # add it to the .isin(...) list below. For example:
    #
    #   (df.iloc[:, job_idx].isin(["FluidLoadCase", "FluidLoadTote", "Wall Builder"]))
    #
    # Then "Wall Builder" hours are aggregated into fluid_hours. If that is your desired logic,
    # uncomment the "Wall Builder" below:
    #
    # fluid_actions = ["FluidLoadCase", "FluidLoadTote", "Wall Builder"]
    # 
    # If you do NOT want "Wall Builder" to be included, remove it from the list.
    # Adjust "size" in `.isin([...])` if you want "Small", "Medium", etc. included as well.
    #

    fluid_actions = ["FluidLoadCase", "FluidLoadTote", "Wall Builder"]  # <--- INCLUDE "Wall Builder"
    fluid_sizes   = ["Total", "Case", "Tote"]                          # or ["Total","Case","Tote","Small","Medium", etc.]

    fluid_mask = (
        (df.iloc[:, site_idx] == "AB1") &
        (df.iloc[:, job_idx].isin(fluid_actions)) &
        (df.iloc[:, unit_idx] == "EACH") &
        (df.iloc[:, size_idx].isin(fluid_sizes))
    )
    fluid_hours = df.iloc[fluid_mask, hours_idx].sum()

    # 4) Compute the fluids rate
    if fluid_hours > 0:
        fluid_rate = total_fluids_units / fluid_hours
    else:
        fluid_rate = 0.0
        logging.warning("No fluid hours found or zero => fluid_rate=0.0")

    # 5) Save "Fluids" in PPR_JSON
    t_out_data["Fluids"] = round(fluid_rate, 2)

    # (Optional) debug logs 
    logging.info(f"Fluid Totes = {fluid_totes}, Fluid Cases = {fluid_cases}, Sum = {total_fluids_units}")
    logging.info(f"Fluid Hours = {fluid_hours} => Fluids Rate = {fluid_rate:.2f}")

    PPR_JSON["PPR_Transfer_Out"] = t_out_data
    logging.info("Finished PPR_Transfer_Out.")

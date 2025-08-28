# PPR_Transfer_Out_Dock.py

import logging
import pandas as pd
from typing import Dict, Any
from pandas import DataFrame

CONFIG: Dict[str, Any] = {
    "columns": {
        "Transfer_Out_Dock_function_name": 1,
        "Transfer_Out_Dock_paid_hours": 10,
        "Transfer_Out_Dock_job_action": 11,
        "Transfer_Out_Dock_jobs": 12,
        "Transfer_Out_Dock_unit_type": 14,
        "Transfer_Out_Dock_Size": 15,
        "Transfer_Out_Dock_Units": 16
    },
    "sums": {
        "DockPalletLoader_TotalUnits": {
            "conditions": [(1, "Dock Pallet Loader"), (15, "Total"), (11, "PalletLoaded")],
            "column": 16
        },
        "DockPalletLoader_Small_Units": {
            "conditions": [(1, "Dock Pallet Loader"), (15, "Small"), (11, "PalletLoaded")],
            "column": 16
        },
        "DockPalletLoader_TotalHours": {
            "conditions": [(1, "Dock Pallet Loader"), (15, "Total")],
            "column": 10
        },
        "DockPalletLoader_TotalJobs": {
            "conditions": [(1, "Dock Pallet Loader"), (15, "Total"), (11, "PalletLoaded")],
            "column": 12
        },
        "PalletMovement_TotalUnits": {
            "conditions": [(1, "Pallet Movement"), (15, "Total"), (11, "StackingToStaging")],
            "column": 16
        },
        "PalletMovement_Small_Units": {
            "conditions": [(1, "Pallet Movement"), (15, "Small"), (11, "StackingToStaging")],
            "column": 16
        },
        "PalletMovement_TotalHours": {
            "conditions": [(1, "Pallet Movement"), (15, "Total")],
            "column": 10
        },
        "PalletMovement_TotalJobs": {
            "conditions": [(1, "Pallet Movement"), (15, "Total"), (11, "StackingToStaging")],
            "column": 12
        },
        "ShipClerk_TotalHours": {
            "conditions": [(1, "Ship Clerk"), (15, "Total")],
            "column": 10
        },
        "TransferOutDockCrew_TotalUnits": {
            "conditions": [(1, "TransferOut DockCrew"), (15, "Total"), (11, "CaseReceived")],
            "column": 16
        },
        "TransferOutDockCrew_TotalHours": {
            "conditions": [(1, "TransferOut DockCrew"), (15, "Total")],
            "column": 10
        },
        "TransferOutDockCrew_TotalJobs": {
            "conditions": [(1, "TransferOut DockCrew"), (15, "Total"), (11, "CaseReceived")],
            "column": 12
        },
        "TruckLoader_TotalHours": {
            "conditions": [(1, "Truck Loader"), (15, "Total")],
            "column": 10
        },
        "PalletLoaded_TotalUnits": {
            "conditions": [(11, "PalletLoaded"), (15, "Total")],
            "column": 16
        },
        "StackingToStaging_TotalUnits": {
            "conditions": [(11, "StackingToStaging"), (15, "Total")],
            "column": 16
        },
        "CaseReceived_TotalUnits": {
            "conditions": [(11, "CaseReceived"), (15, "Total")],
            "column": 16
        },
        "SmallsTotal": {
            "conditions": [(15, "Small")],
            "column": 16
        },
        "Total": {
            "conditions": [(15, "Total")],
            "column": 16
        },
        "TotalHours": {
            "conditions": [(15, "Total")],
            "column": 10
        },
        "TotalJobs": {
            "conditions": [(15, "Total")],
            "column": 12
        }
    }
}

def process_PPR_Transfer_Out_Dock(df: DataFrame,
                                  generic_process,
                                  PPR_JSON: Dict[str, Any],
                                  config: Dict[str, Any]) -> None:
    """
    Enhanced PPR_Transfer_Out_Dock processing with comprehensive metrics:
    - Function-specific metrics (Dock Pallet Loader, Pallet Movement, etc.)
    - Job action metrics (PalletLoaded, StackingToStaging, CaseReceived)
    - Size-specific breakdowns
    - Rate calculations (UPH, JPH)
    """
    logging.info("Processing PPR_Transfer_Out_Dock...")
    if "PPR_Transfer_Out_Dock" not in PPR_JSON:
        PPR_JSON["PPR_Transfer_Out_Dock"] = {}

    # Process all metrics using generic function
    generic_process(df, "PPR_Transfer_Out_Dock", PPR_JSON, config)
    
    # Calculate derived metrics and rates
    dock_data = PPR_JSON["PPR_Transfer_Out_Dock"]
    
    # Calculate Dock Pallet Loader rate (UPH)
    dock_loader_units = dock_data.get("DockPalletLoader_TotalUnits", 0.0)
    dock_loader_hours = dock_data.get("DockPalletLoader_TotalHours", 0.0)
    if dock_loader_hours > 0:
        dock_data["DockPalletLoader_Rate"] = dock_loader_units / dock_loader_hours
    else:
        dock_data["DockPalletLoader_Rate"] = 0.0
    
    # Calculate Pallet Movement rate (UPH)
    pallet_movement_units = dock_data.get("PalletMovement_TotalUnits", 0.0)
    pallet_movement_hours = dock_data.get("PalletMovement_TotalHours", 0.0)
    if pallet_movement_hours > 0:
        dock_data["PalletMovement_Rate"] = pallet_movement_units / pallet_movement_hours
    else:
        dock_data["PalletMovement_Rate"] = 0.0
    
    # Calculate TransferOut DockCrew rate (UPH)
    dockcrew_units = dock_data.get("TransferOutDockCrew_TotalUnits", 0.0)
    dockcrew_hours = dock_data.get("TransferOutDockCrew_TotalHours", 0.0)
    if dockcrew_hours > 0:
        dock_data["TransferOutDockCrew_Rate"] = dockcrew_units / dockcrew_hours
    else:
        dock_data["TransferOutDockCrew_Rate"] = 0.0
    
    # Calculate overall Transfer Out Dock rate
    total_units = dock_data.get("Total", 0.0)
    total_hours = dock_data.get("TotalHours", 0.0)
    if total_hours > 0:
        dock_data["TransferOutDock_OverallRate"] = total_units / total_hours
    else:
        dock_data["TransferOutDock_OverallRate"] = 0.0
    
    # Log key metrics
    logging.info(f"DockPalletLoader_TotalUnits: {dock_loader_units}")
    logging.info(f"DockPalletLoader_Rate: {dock_data.get('DockPalletLoader_Rate', 0.0):.2f} UPH")
    logging.info(f"PalletMovement_TotalUnits: {pallet_movement_units}")
    logging.info(f"PalletMovement_Rate: {dock_data.get('PalletMovement_Rate', 0.0):.2f} UPH")
    logging.info(f"TransferOutDockCrew_TotalUnits: {dockcrew_units}")
    logging.info(f"Total Transfer Out Dock Units: {total_units}")
    logging.info(f"Total Transfer Out Dock Hours: {total_hours}")
    logging.info(f"Overall Transfer Out Dock Rate: {dock_data.get('TransferOutDock_OverallRate', 0.0):.2f} UPH")
    
    logging.info("Finished PPR_Transfer_Out_Dock.")

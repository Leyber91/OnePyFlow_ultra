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
        # ATAC Egress metrics
        "ATACEgress_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "ATAC Egress")],
            "column": 16
        },
        "ATACEgress_TotalCases": {
            "conditions": [(15, "Total"), (14, "Bin"), (1, "ATAC Egress")],
            "column": 16
        },
        "ATACEgress_TotalHours": {
            "conditions": [(15, "Total"), (1, "ATAC Egress")],
            "column": 10
        },
        
        # ATAC Ingress metrics (MISSING - this is why we lost 760 units)
        "ATACIngress_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "ATAC Ingress")],
            "column": 16
        },
        "ATACIngress_TotalCases": {
            "conditions": [(15, "Total"), (14, "Bin"), (1, "ATAC Ingress")],
            "column": 16
        },
        "ATACIngress_TotalHours": {
            "conditions": [(15, "Total"), (1, "ATAC Ingress")],
            "column": 10
        },
        
        # Cubiscan metrics
        "Cubiscan_TotalUnits": {
            "conditions": [(15, "Total"), (14, "EACH"), (1, "Cubiscan")],
            "column": 16
        },
        "Cubiscan_TotalCases": {
            "conditions": [(15, "Total"), (14, "Bin"), (1, "Cubiscan")],
            "column": 16
        },
        "Cubiscan_TotalHours": {
            "conditions": [(15, "Total"), (1, "Cubiscan")],
            "column": 10
        },
        
        # Size breakdowns
        "SmallsTotal": {
            "conditions": [(15, "Small")],
            "column": 16
        },
        "Total": {
            "conditions": [(15, "Total")],
            "column": 16
        },
        
        # Individual size metrics for ATAC Egress
        "ATACEgress_Small_Units": {
            "conditions": [(15, "Small"), (14, "EACH"), (1, "ATAC Egress")],
            "column": 16
        },
        "ATACEgress_Medium_Units": {
            "conditions": [(15, "Medium"), (14, "EACH"), (1, "ATAC Egress")],
            "column": 16
        },
        "ATACEgress_Large_Units": {
            "conditions": [(15, "Large"), (14, "EACH"), (1, "ATAC Egress")],
            "column": 16
        },
        
        # Individual size metrics for ATAC Ingress
        "ATACIngress_Small_Units": {
            "conditions": [(15, "Small"), (14, "EACH"), (1, "ATAC Ingress")],
            "column": 16
        },
        "ATACIngress_Medium_Units": {
            "conditions": [(15, "Medium"), (14, "EACH"), (1, "ATAC Ingress")],
            "column": 16
        },
        "ATACIngress_Large_Units": {
            "conditions": [(15, "Large"), (14, "EACH"), (1, "ATAC Ingress")],
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

    # DEBUG: Log all unique function names found in the data
    if not df.empty and len(df.columns) > 1:
        unique_functions = df.iloc[:, 1].unique() if len(df.columns) > 1 else []
        logging.info(f"[DEBUG] Unique Function Names: {list(unique_functions)}")
        for func_name in sorted(unique_functions):
            logging.info(f"   - '{func_name}'")
        
        # DEBUG: Log all unique unit types
        if len(df.columns) > 14:
            unique_unit_types = df.iloc[:, 14].unique()
            logging.info(f"[DEBUG] Unique Unit Types: {list(unique_unit_types)}")
            for unit_type in sorted(unique_unit_types):
                logging.info(f"   - '{unit_type}'")
        
        # DEBUG: Log all unique sizes
        if len(df.columns) > 15:
            unique_sizes = df.iloc[:, 15].unique()
            logging.info(f"[DEBUG] Unique Sizes: {list(unique_sizes)}")
            for size in sorted(unique_sizes):
                logging.info(f"   - '{size}'")

    generic_process(df, "PPR_Cubiscan", PPR_JSON, config)

    logging.info("Finished PPR_Cubiscan.")

"""
PPR_Q Size-Specific Calculator
Handles size-specific breakdowns (Small, Medium, Large) for various processes.
"""

import logging
from typing import Dict, Any, List, Tuple
import pandas as pd


class SizeSpecificCalculator:
    """
    Calculates size-specific metrics by filtering raw DataFrames.
    Handles Each Receive, Prep Recorder, and RC Sort size breakdowns.
    """
    
    def __init__(self, process_dataframes: Dict[str, pd.DataFrame]):
        self.dataframes = process_dataframes
        self.size_metrics = {}
    
    def calculate_all_size_metrics(self) -> Dict[str, float]:
        """
        Calculate all size-specific metrics from raw DataFrames.
        """
        logging.info("Calculating size-specific metrics from raw data...")
        
        # Each Receive size breakdowns
        self._calculate_each_receive_by_size()
        
        # Prep Recorder size breakdowns
        self._calculate_prep_recorder_by_size()
        
        # RC Sort size breakdowns  
        self._calculate_rc_sort_by_size()
        
        return self.size_metrics
    
    def _calculate_each_receive_by_size(self):
        """Calculate Each Receive rates by size (Small, Medium, Large)."""
        if "PPR_Each_Receive" not in self.dataframes:
            logging.warning("PPR_Each_Receive DataFrame not available for size calculations")
            return
        
        df = self.dataframes["PPR_Each_Receive"]
        
        if df.empty:
            logging.warning("PPR_Each_Receive DataFrame is empty")
            return
        
        # Column indices for Each Receive (based on existing config)
        size_col = 15  # Size column
        units_col = 16  # Units column  
        hours_col = 10  # Paid Hours Total column
        
        sizes = ["Small", "Medium", "Large"]
        
        for size in sizes:
            try:
                # Filter by size
                size_mask = df.iloc[:, size_col].astype(str).str.strip().str.lower() == size.lower()
                size_df = df[size_mask]
                
                if not size_df.empty:
                    # Sum units and hours for this size
                    total_units = size_df.iloc[:, units_col].sum()
                    total_hours = size_df.iloc[:, hours_col].sum()
                    
                    if total_hours > 0:
                        rate = total_units / total_hours
                        metric_name = f"Each_Receive_{size}"
                        self.size_metrics[metric_name] = rate
                        
                        logging.info(f"[OK] {metric_name}: {total_units:,.0f} units / {total_hours:.2f} hours = {rate:.2f} u/h")
                    else:
                        logging.warning(f"[ERROR] Each_Receive_{size}: Zero hours")
                else:
                    logging.warning(f"[ERROR] Each_Receive_{size}: No data for size")
                    
            except Exception as e:
                logging.error(f"Error calculating Each_Receive_{size}: {e}")
    
    def _calculate_prep_recorder_by_size(self):
        """Calculate Prep Recorder rates by size (Small, Medium, Large)."""
        if "PPR_Prep_Recorder" not in self.dataframes:
            logging.warning("PPR_Prep_Recorder DataFrame not available for size calculations")
            return
        
        df = self.dataframes["PPR_Prep_Recorder"]
        
        if df.empty:
            logging.warning("PPR_Prep_Recorder DataFrame is empty")
            return
        
        # Column indices for Prep Recorder
        size_col = 15  # Size column
        units_col = 16  # Units column
        hours_col = 10  # Paid Hours Total column
        
        sizes = ["Small", "Medium", "Large"]
        
        for size in sizes:
            try:
                # Filter by size
                size_mask = df.iloc[:, size_col].astype(str).str.strip().str.lower() == size.lower()
                size_df = df[size_mask]
                
                if not size_df.empty:
                    # Sum units and hours for this size
                    total_units = size_df.iloc[:, units_col].sum()
                    total_hours = size_df.iloc[:, hours_col].sum()
                    
                    if total_hours > 0:
                        rate = total_units / total_hours
                        metric_name = f"Prep_Recorder_{size}"
                        self.size_metrics[metric_name] = rate
                        
                        logging.info(f"[OK] {metric_name}: {total_units:,.0f} units / {total_hours:.2f} hours = {rate:.2f} u/h")
                    else:
                        logging.warning(f"❌ Prep_Recorder_{size}: Zero hours")
                else:
                    logging.warning(f"❌ Prep_Recorder_{size}: No data for size")
                    
            except Exception as e:
                logging.error(f"Error calculating Prep_Recorder_{size}: {e}")
    
    def _calculate_rc_sort_by_size(self):
        """Calculate RC Sort rates by size (Small, Medium, Large)."""
        if "PPR_RC_Sort" not in self.dataframes:
            logging.warning("PPR_RC_Sort DataFrame not available for size calculations")
            return
        
        df = self.dataframes["PPR_RC_Sort"]
        
        if df.empty:
            logging.warning("PPR_RC_Sort DataFrame is empty")
            return
        
        # Column indices for RC Sort
        size_col = 15  # Size column
        units_col = 16  # Units column
        hours_col = 10  # Paid Hours Total column
        
        sizes = ["Small", "Medium", "Large"]
        
        for size in sizes:
            try:
                # Filter by size
                size_mask = df.iloc[:, size_col].astype(str).str.strip().str.lower() == size.lower()
                size_df = df[size_mask]
                
                if not size_df.empty:
                    # Sum units and hours for this size
                    total_units = size_df.iloc[:, units_col].sum()
                    total_hours = size_df.iloc[:, hours_col].sum()
                    
                    if total_hours > 0:
                        rate = total_units / total_hours
                        metric_name = f"RC_Sort_{size}"
                        self.size_metrics[metric_name] = rate
                        
                        logging.info(f"[OK] {metric_name}: {total_units:,.0f} units / {total_hours:.2f} hours = {rate:.2f} u/h")
                    else:
                        logging.warning(f"❌ RC_Sort_{size}: Zero hours")
                else:
                    logging.warning(f"❌ RC_Sort_{size}: No data for size")
                    
            except Exception as e:
                logging.error(f"Error calculating RC_Sort_{size}: {e}")
    
    def get_size_breakdown_summary(self) -> str:
        """Get a summary of all calculated size breakdowns."""
        summary = "\n📊 SIZE-SPECIFIC METRICS SUMMARY:\n"
        summary += "-" * 50 + "\n"
        
        # Group by process
        processes = ["Each_Receive", "Prep_Recorder", "RC_Sort"]
        
        for process in processes:
            summary += f"\n🔹 {process}:\n"
            process_metrics = {k: v for k, v in self.size_metrics.items() if k.startswith(process)}
            
            if process_metrics:
                for metric, rate in process_metrics.items():
                    size = metric.split("_")[-1]
                    summary += f"   {size}: {rate:,.2f} u/h\n"
            else:
                summary += "   No size metrics calculated\n"
        
        return summary


def add_size_metrics_to_ppr_q(ppr_q_data: Dict[str, Any], raw_dataframes: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Add size-specific metrics to PPR_Q data using raw DataFrames.
    """
    calculator = SizeSpecificCalculator(raw_dataframes)
    size_metrics = calculator.calculate_all_size_metrics()
    
    # Add size metrics to the target metrics section
    if "_target_metrics" not in ppr_q_data:
        ppr_q_data["_target_metrics"] = {}
    
    ppr_q_data["_target_metrics"].update(size_metrics)
    
    # Add summary
    ppr_q_data["_size_breakdown_summary"] = calculator.get_size_breakdown_summary()
    
    return ppr_q_data

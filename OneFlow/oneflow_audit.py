import os
import csv
import json
import time
from datetime import datetime
import logging
import sys

logger = logging.getLogger(__name__)

def record_execution_time(Site, plan_type, shift, exec_time, user_login, module_exec_times=None, module_statuses=None, error_list=None):
    """
    Records detailed execution data to a comprehensive CSV file and maintains legacy format.
    
    Args:
        Site (str): Site code
        plan_type (str): Plan type
        shift (str): Shift code
        exec_time (float): Total execution time in seconds
        user_login (str): User login
        module_exec_times (dict): Dictionary mapping module names to execution times
        module_statuses (dict): Dictionary mapping module names to execution status
        error_list (list): List of errors encountered during execution
    """
    # Import config values
    from OneFlow.oneflow_config import CSV_OUTPUT_DIR, LEGACY_CSV_FILENAME, DETAILED_CSV_FILENAME
    
    # Create timestamp for this execution
    exec_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    exec_date = datetime.now().strftime('%Y-%m-%d')
    exec_time_minutes = exec_time / 60
    
    # Ensure output directory exists
    try:
        os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)
        logger.info(f"Using CSV output directory: {CSV_OUTPUT_DIR}")
    except Exception as e:
        logger.error(f"Error creating CSV output directory: {e}")
        # Fall back to local directory
        CSV_OUTPUT_DIR = os.getcwd()
        logger.info(f"Falling back to current directory: {CSV_OUTPUT_DIR}")
    
    # Define paths for both CSV files
    detailed_csv_path = os.path.join(CSV_OUTPUT_DIR, DETAILED_CSV_FILENAME)
    legacy_csv_path = os.path.join(CSV_OUTPUT_DIR, LEGACY_CSV_FILENAME)
    
    # Skip modules that should be excluded from reporting
    skip_modules = ["PHC", "HCTool", "BackLog"]
    
    # Count successful vs failed modules
    successful_modules = 0
    failed_modules = 0
    timeout_modules = 0
    
    if module_statuses:
        for mod_name, status in module_statuses.items():
            if mod_name in skip_modules:
                continue
            if "success" in status.lower():
                successful_modules += 1
            elif "timeout" in status.lower():
                timeout_modules += 1
                failed_modules += 1
            elif "fail" in status.lower() or "error" in status.lower():
                failed_modules += 1
    
    # Extract error count and details
    error_count = len(error_list) if error_list else 0
    error_types = {}
    if error_list:
        for error in error_list:
            error_type = error.get("ErrorType", "Unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
    
    # Create rows for the detailed CSV - one row per executed module
    rows_to_write = []
    
    # Does the file already exist? Check if we need to write headers
    write_detailed_header = not os.path.exists(detailed_csv_path) or os.path.getsize(detailed_csv_path) == 0
    
    # Define all the fields we want to capture
    detailed_header = [
        # Basic execution info
        'ExecutionTimestamp', 'ExecutionDate', 'Site', 'PlanType', 'Shift', 'UserLogin',
        
        # Overall execution metrics
        'TotalExecutionTime_Seconds', 'TotalExecutionTime_Minutes',
        'TotalModulesAttempted', 'SuccessfulModules', 'FailedModules', 'TimeoutModules',
        'TotalErrorCount',
        
        # Per-module details
        'ModuleName', 'ModuleExecutionTime', 'ModuleStatus',
        'ModuleErrorCount', 'ModuleErrorDetails',
        
        # Additional context
        'ExecutableName', 'ExecutionMode', 'RunID'
    ]
    
    # Generate a unique run ID for this execution
    run_id = f"{Site}_{exec_date.replace('-', '')}_{int(time.time())}"
    
    # Get executable information
    executable_name = get_executable_name()
    execution_mode = 'compiled' if getattr(sys, 'frozen', False) else 'script'
    
    if module_exec_times:
        # Create one row per module with all the context data
        for mod_name, mod_time in module_exec_times.items():
            # Skip excluded modules
            if mod_name in skip_modules:
                continue
                
            # Get module-specific data
            mod_status = module_statuses.get(mod_name, "Unknown") if module_statuses else "Unknown"
            
            # Get module-specific errors
            mod_errors = [err for err in error_list if err.get("Function") == mod_name] if error_list else []
            mod_error_count = len(mod_errors)
            mod_error_details = "; ".join([err.get("ErrorName", "Unknown Error") for err in mod_errors]) if mod_errors else ""
            
            # Create the full data row
            row = [
                # Basic execution info
                exec_datetime, exec_date, Site, plan_type, shift, user_login,
                
                # Overall execution metrics
                f"{exec_time:.4f}", f"{exec_time_minutes:.4f}",
                len([m for m in module_exec_times if m not in skip_modules]), 
                successful_modules, failed_modules, timeout_modules,
                error_count,
                
                # Per-module details
                mod_name, f"{mod_time:.4f}", mod_status,
                mod_error_count, mod_error_details,
                
                # Additional context
                executable_name, execution_mode, run_id
            ]
            
            rows_to_write.append(row)
    else:
        # If no module details, just write a single summary row
        row = [
            # Basic execution info
            exec_datetime, exec_date, Site, plan_type, shift, user_login,
            
            # Overall execution metrics
            f"{exec_time:.4f}", f"{exec_time_minutes:.4f}",
            0, 0, 0, 0, error_count,
            
            # Per-module details (empty)
            "SUMMARY", "", "",
            0, "",
            
            # Additional context
            executable_name, execution_mode, run_id
        ]
        rows_to_write.append(row)
    
    # 1. Write to the detailed CSV file
    try:
        with open(detailed_csv_path, mode='a', newline='') as f:
            writer = csv.writer(f)
            if write_detailed_header:
                writer.writerow(detailed_header)
            
            # Write all rows
            for row in rows_to_write:
                writer.writerow(row)
                
        logger.info(f"Module performance metrics recorded to CSV: {detailed_csv_path} ({len(rows_to_write)} rows)")
        
    except Exception as e:
        logger.error(f"Failed to write to detailed CSV: {e}", exc_info=True)
    
    # 2. Also write to the legacy format CSV for backward compatibility
    try:
        write_legacy_header = not os.path.exists(legacy_csv_path) or os.path.getsize(legacy_csv_path) == 0
        
        with open(legacy_csv_path, mode='a', newline='') as f:
            writer = csv.writer(f)
            if write_legacy_header:
                writer.writerow([
                    'Datetime', 'Site', 'PlanType', 'Shift',
                    'TotalExecutionTime (seconds)',
                    'TotalExecutionTime (minutes)', 'UserLogin'
                ])
            writer.writerow([
                exec_datetime, Site, plan_type, shift,
                f"{exec_time:.4f}", f"{exec_time_minutes:.4f}", user_login
            ])
        
        logger.info(f"Legacy execution time recorded to CSV: {legacy_csv_path}")
    except Exception as e:
        logger.error(f"Failed to write to legacy CSV: {e}", exc_info=True)


def get_executable_name():
    """
    Retrieve the name of the executable or script currently running.

    Returns:
    - For compiled executables: filename of the .exe
    - For scripts: filename of the .py script
    """
    try:
        if getattr(sys, 'frozen', False):
            # Running as a compiled executable (PyInstaller)
            return os.path.basename(sys.executable)
        else:
            # Running as a regular Python script
            return os.path.basename(sys.argv[0])
    except Exception as e:
        logger.error(f"Error retrieving executable name: {e}")
        return "unknown_executable"


def generate_module_status_report(site, module_exec_times, module_statuses, error_list):
    """
    Generates a detailed module status report in JSON format and saves it
    to the CSV_OUTPUT_DIR with timestamp and site information.
    
    Args:
        site (str): Site code for the report
        module_exec_times (dict): Dictionary of module execution times
        module_statuses (dict): Dictionary of module execution statuses
        error_list (list): List of error dictionaries from processing
        
    Returns:
        str: Path to the saved report file
    """
    from OneFlow.oneflow_config import CSV_OUTPUT_DIR
    
    report_time = datetime.now()
    report_timestamp = report_time.strftime("%Y%m%d_%H%M%S")
    report_filename = f"{site}_module_report_{report_timestamp}.json"
    report_path = os.path.join(CSV_OUTPUT_DIR, report_filename)
    
    # Build the report structure
    report = {
        "site": site,
        "timestamp": report_time.isoformat(),
        "modules": {},
        "summary": {
            "total_modules": len(module_exec_times),
            "successful_modules": sum(1 for status in module_statuses.values() if "success" in status.lower()),
            "failed_modules": sum(1 for status in module_statuses.values() if "fail" in status.lower() or "error" in status.lower()),
            "total_execution_time": sum(module_exec_times.values()),
            "error_count": len(error_list)
        }
    }
    
    # Add module-specific details
    for mod_name, exec_time in module_exec_times.items():
        report["modules"][mod_name] = {
            "execution_time_seconds": exec_time,
            "status": module_statuses.get(mod_name, "Unknown"),
        }
        
        # Add any errors associated with this module
        module_errors = [err for err in error_list if err.get("Function") == mod_name]
        if module_errors:
            report["modules"][mod_name]["errors"] = module_errors
    
    # Write report to file
    try:
        os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Generated detailed module status report: {report_path}")
        return report_path
    except Exception as e:
        logger.error(f"Failed to generate module status report: {e}", exc_info=True)
        return None


def build_audit_block(start_time, modules, error_list, module_exec_times=None, previous_history=None):
    """
    Creates or updates an 'audit_info' dictionary that tracks:
    - Execution time in seconds/minutes
    - Error details
    - Timestamp
    - Modules downloaded/attempted
    - Execution mode and executable name
    - Dictionary of individual module execution times for the current run
    - A full 'History' array containing all runs
    """
    end_time = time.time()
    total_exec_time = end_time - start_time  # Overall time for the whole process being audited
    exec_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_error_count = len([err for err in error_list if err.get("ErrorFlag")])

    # Use provided module times or an empty dict
    current_module_times = module_exec_times if module_exec_times is not None else {}

    # Get executable name and mode
    executable_name = get_executable_name()
    script_mode = 'compiled' if getattr(sys, 'frozen', False) else 'script'

    # Build a record for this new run
    new_record = {
        "Timestamp": exec_datetime,
        "ModulesAttempted": modules,  # Renamed for clarity
        "TotalExecutionTimeSeconds": round(total_exec_time, 4),
        "TotalExecutionTimeMinutes": round(total_exec_time / 60, 4),
        "ModuleExecutionTimes": {mod: round(t, 4) for mod, t in current_module_times.items() if t >= 0},  # Add module times, format, ignore -1
        "SkippedOrTimeoutModules": [mod for mod, t in current_module_times.items() if t < 0],  # List modules with -1 time
        "ErrorCount": total_error_count,
        "ErrorDetails": error_list,
        "ExecutionMode": script_mode,
        "ExecutableName": executable_name
    }

    # Ensure previous_history is a list
    if previous_history is None:
        previous_history = []

    # Add new record to history
    previous_history.append(new_record)
    logger.debug(f"Appended new run record to audit history. History length: {len(previous_history)}")

    # The most recent run is always the last item of history
    most_recent = previous_history[-1]

    # Build the final 'audit_info' structure from the most recent record
    # and include the full history
    audit_info = {
        "Timestamp":            most_recent["Timestamp"],
        "ModulesAttempted":     most_recent["ModulesAttempted"],
        "TotalExecutionTimeSeconds": most_recent["TotalExecutionTimeSeconds"],
        "TotalExecutionTimeMinutes": most_recent["TotalExecutionTimeMinutes"],
        "ModuleExecutionTimes": most_recent.get("ModuleExecutionTimes", {}),  # Ensure key exists
        "ErrorCount":           most_recent["ErrorCount"],
        "ErrorDetails":         most_recent["ErrorDetails"],
        "History":              previous_history  # Include the full history
    }

    # Calculate cumulative time based on the potentially updated history
    cumulative_seconds = sum(item.get("TotalExecutionTimeSeconds", 0.0) for item in previous_history)
    audit_info["CumulativeTimeSeconds"] = round(cumulative_seconds, 4)

    logger.info(f"Audit block built for run at {exec_datetime}. Total time: {total_exec_time:.2f}s.")
    # Return the dict and the total execution time for this specific run (used for CSV logging)
    return audit_info, total_exec_time
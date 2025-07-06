"""
Enhanced main.py that properly integrates standalone modules into the master JSON.
This version ensures each module has an entry even if it returns no data,
avoids audit duplication, and correctly processes all module outputs.
It also manages Midway authentication consistently across all modules.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime, timedelta

from PyQt5 import QtWidgets

# Import OneFlow components for non-isolated modules
from utils.authenticate import Authentication
from OneFlow.oneflow import OneFlow_MainFunction
from OneGui import OneFlowGUI
from OneFlow.oneflow_config import STANDALONE_MODULES, MODULE_ORDER
from OneFlow.oneflow_utils import parse_datetime, reorder_modules
from OneFlow.oneflow_output import merge_and_write_json
from OneFlow.oneflow_audit import build_audit_block

# Enhanced logging configuration: log to both console and file.
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler("main.log")]
)
logger = logging.getLogger(__name__)


def check_and_refresh_authentication(auth, max_hours=1):
    """
    Checks if the Midway authentication is older than max_hours and refreshes if needed.
    Returns the authentication object with valid Midway session.
    
    Args:
        auth (Authentication): The authentication object
        max_hours (int): Maximum age of the Midway session in hours before refreshing
        
    Returns:
        Authentication: The authentication object with a valid session
    """
    try:
        # Only refresh if cookie is older than max_hours
        auth.refresh_cookie_if_needed(max_hours=max_hours)
        auth._load_cookie()
        logger.info(f"Authentication checked - refreshed if older than {max_hours} hours.")
        return auth
    except Exception as e:
        logger.error(f"Error checking/refreshing authentication: {e}", exc_info=True)
        raise RuntimeError(f"Authentication failed during refresh check: {e}") from e


def force_mwinit_reauth_in_ui(auth):
    """
    Forces the 'mwinit' re-authentication in normal UI mode, regardless of the last successful cookie.
    This makes sure we always get a fresh session, similar to headless mode.
    """
    try:
        # Force 'mwinit' for a fresh authentication
        auth.refresh_cookie_if_needed(max_hours=1)  # Always refresh cookie
        auth._load_cookie()
        logger.info("[UI] Forced re-authentication (cookie refreshed).")
    except Exception as e:
        logger.error("[UI] Error in re-authentication: %s", e, exc_info=True)
        raise RuntimeError("UI mode authentication failed! Please check your credentials.") from e


def get_base_dir():
    """
    Returns the directory where we should look for external files.
    - If running under PyInstaller --onefile (frozen=True), we return the directory containing the executable.
    - Otherwise, return the directory where this script resides.
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


# This is a partial update to main.py - update the find_params_file function
def find_params_file():
    """
    Try to find 'OnePyFlowParams.json' or 'OnePyFlowParams' (no extension) in the directory determined by get_base_dir().
    Returns the full path if found, otherwise returns None.
    """
    base_dir = get_base_dir()
    possible_filenames = ["OnePyFlowParams.json", "OnePyFlowParams"]

    for fname in possible_filenames:
        test_path = os.path.join(base_dir, fname)
        if os.path.exists(test_path):
            logger.info(f"Parameters file found: {test_path}")
            return test_path

    # Search current working directory as fallback if it's different from base_dir
    current_dir = os.getcwd()
    if current_dir != base_dir:
        logger.info(f"Checking current working directory as fallback: {current_dir}")
        for fname in possible_filenames:
            test_path = os.path.join(current_dir, fname)
            if os.path.exists(test_path):
                logger.info(f"Parameters file found in current directory: {test_path}")
                return test_path

    logger.info(f"No parameters file found in base directory: {base_dir} or current directory: {current_dir}")
    return None


def run_standalone_modules(modules, params, auth):
    """
    Run standalone modules and collect their data.
    Now enhanced to track execution times and timestamps for each module.
    
    Args:
        modules (list): List of module names to run
        params (dict): Configuration parameters
        auth (Authentication): Authentication object with valid session
        
    Returns:
        tuple: (combined_data, module_exec_times, module_timestamps)
            - combined_data: Dictionary containing the output of each module
            - module_exec_times: Dictionary mapping module names to execution times
            - module_timestamps: Dictionary mapping module names to ISO timestamps
    """
    combined_data = {}
    module_exec_times = {}  # Store execution times for modules
    module_timestamps = {}  # Store timestamps for modules
    
    # Get authentication sessions for modules that need them
    session = auth.session
    midway_session, cookie_jar = auth.get_midway_session()
    
    for module in modules:
        logger.info(f"Executing standalone module: {module}")
        
        # Start timing this module's execution
        module_start_time = time.time()
        module_timestamp = datetime.now().isoformat()
        
        # Initialize exec time with 0 - will be updated after module completes
        module_exec_times[module] = 0
        module_timestamps[module] = module_timestamp
        
        if module == "Echo":
            try:
                from isolated_modules.echo_module import EchoFunction
                # Call without parameters - it doesn't accept any
                echo_data = EchoFunction()
                # Even if it returns None, create an entry for the module
                combined_data["Echo"] = echo_data or {
                    "timestamp_iso": datetime.now().isoformat(),
                    "echo_message": "No data available",
                    "error": "Module execution failed or returned no data"
                }
                # Add timestamp metadata to module output
                if isinstance(combined_data["Echo"], dict):
                    combined_data["Echo"]["LastRunTimestamp"] = module_timestamp
                logger.info("Echo module executed successfully")
            except Exception as e:
                logger.error(f"Error executing Echo module: {e}", exc_info=True)
                combined_data["Echo"] = {
                    "timestamp_iso": datetime.now().isoformat(),
                    "echo_message": "No data available",
                    "error": str(e),
                    "LastRunTimestamp": module_timestamp
                }
                
        elif module == "PHC":
            try:
                from isolated_modules.phc_module import PHCpuller
                # Call without parameters - it doesn't accept any
                phc_data = PHCpuller()
                # Always include module in output even if empty
                combined_data["PHC"] = phc_data or {
                    "headcount_date": datetime.now().strftime("%Y-%m-%d"),
                    "fc": params.get("Site", "UNKNOWN"),
                    "shift": params.get("shift", "UNKNOWN"),
                    "update_time": datetime.now().isoformat(),
                    "error": "Module execution failed or returned no data",
                    "predictedHc": []
                }
                # Add execution time and timestamp in a separate metadata object
                # Use the current value from module_exec_times - will be updated later
                combined_data["PHC_metadata"] = {
                    "LastRunTimestamp": module_timestamp,
                    "ExecutionTimeSeconds": 0,  # Will be updated after module completes
                    "ExecutionDate": module_timestamp.split("T")[0] if "T" in module_timestamp else module_timestamp
                }
                logger.info("PHC module executed successfully")
            except Exception as e:
                logger.error(f"Error executing PHC module: {e}", exc_info=True)
                combined_data["PHC"] = {
                    "headcount_date": datetime.now().strftime("%Y-%m-%d"),
                    "fc": params.get("Site", "UNKNOWN"),
                    "shift": params.get("shift", "UNKNOWN"),
                    "update_time": datetime.now().isoformat(),
                    "error": str(e),
                    "predictedHc": [],
                    "LastRunTimestamp": module_timestamp
                }
                
        elif module == "HCTool":
            try:
                from isolated_modules.hctool_module import HCtoolPuller
                # Call without parameters - it doesn't accept any
                hctool_data = HCtoolPuller()
                # Always include module in output even if empty
                combined_data["HCTool"] = hctool_data or {
                    "headcount_date": datetime.now().strftime("%Y-%m-%d"),
                    "fc": params.get("Site", "UNKNOWN"),
                    "shift": params.get("shift", "UNKNOWN"),
                    "update_time": datetime.now().isoformat(),
                    "error": "Module execution failed or returned no data",
                    "actualHc": [],
                    "actualChart": []
                }
                # Add execution time and timestamp in a separate metadata object
                combined_data["HCTool_metadata"] = {
                    "LastRunTimestamp": module_timestamp,
                    "ExecutionTimeSeconds": 0,  # Will be updated after module completes
                    "ExecutionDate": module_timestamp.split("T")[0] if "T" in module_timestamp else module_timestamp
                }
                logger.info("HCTool module executed successfully")
            except Exception as e:
                logger.error(f"Error executing HCTool module: {e}", exc_info=True)
                combined_data["HCTool"] = {
                    "headcount_date": datetime.now().strftime("%Y-%m-%d"),
                    "fc": params.get("Site", "UNKNOWN"),
                    "shift": params.get("shift", "UNKNOWN"),
                    "update_time": datetime.now().isoformat(),
                    "error": str(e),
                    "actualHc": [],
                    "actualChart": [],
                    "LastRunTimestamp": module_timestamp
                }
                
        elif module == "BackLog":
            try:
                from isolated_modules.backlog import BackLogPuller
                # Call without parameters - it doesn't accept any
                backlog_data = BackLogPuller()
                # Always include module in output even if empty
                combined_data["BackLog"] = backlog_data or {
                    "ICC-Yard": [],
                    "Palletized-Extra": [],
                    "Palletized": [],
                    "Inventory": [],
                    "Asset": [],
                    "Metadata": {
                        "fc": params.get("Site", "UNKNOWN"),
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "shift": params.get("shift", "UNKNOWN"),
                        "timestamp": datetime.now().isoformat(),
                        "error": "Module execution failed or returned no data"
                    }
                }
                # Add execution time and timestamp in a separate metadata object
                combined_data["BackLog_metadata"] = {
                    "LastRunTimestamp": module_timestamp,
                    "ExecutionTimeSeconds": 0,  # Will be updated after module completes
                    "ExecutionDate": module_timestamp.split("T")[0] if "T" in module_timestamp else module_timestamp
                }
                logger.info("BackLog module executed successfully")
            except Exception as e:
                logger.error(f"Error executing BackLog module: {e}", exc_info=True)
                combined_data["BackLog"] = {
                    "ICC-Yard": [],
                    "Palletized-Extra": [],
                    "Palletized": [],
                    "Inventory": [],
                    "Asset": [],
                    "Metadata": {
                        "fc": params.get("Site", "UNKNOWN"),
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "shift": params.get("shift", "UNKNOWN"),
                        "timestamp": datetime.now().isoformat(),
                        "error": str(e),
                        "LastRunTimestamp": module_timestamp
                    }
                }
                
        elif module == "CarrierMatrix":
            try:
                # Import the carrier matrix puller
                from data_retrieval.pull_carrier_matrix_data import pull_carrier_matrix
                from data_processing.process_carrier_matrix_data import process_carrier_matrix_data
                
                # This module does need parameters
                logger.info(f"Pulling carrier matrix data for FC={params.get('Site', 'UNKNOWN')}")
                csv_path = pull_carrier_matrix(
                    fc=params.get("Site", "UNKNOWN"),
                    midway_session=midway_session,
                    cookie_jar=cookie_jar
                )
                
                if csv_path:
                    # Process the data if pull was successful
                    carrier_matrix_data = process_carrier_matrix_data(csv_path)
                    logger.info(f"Successfully processed carrier matrix data: {len(carrier_matrix_data.get('matrix', []))} rows")
                else:
                    logger.error("Failed to pull carrier matrix data")
                    carrier_matrix_data = {
                        "matrix": [],
                        "metadata": {
                            "fc": params.get("Site", "UNKNOWN"),
                            "timestamp": datetime.now().isoformat(),
                            "error": "Failed to retrieve carrier matrix data",
                            "row_count": 0,
                            "destinations_count": 0
                        }
                    }
                
                # Add timestamp metadata to module output
                if isinstance(carrier_matrix_data, dict) and "metadata" in carrier_matrix_data:
                    # Avoid modifying the original data structure
                    # Instead create a separate metadata object
                    combined_data["CarrierMatrix_metadata"] = {
                        "LastRunTimestamp": module_timestamp,
                        "ExecutionTimeSeconds": 0,  # Will be updated after module completes
                        "ExecutionDate": module_timestamp.split("T")[0] if "T" in module_timestamp else module_timestamp
                    }
                
                # Add to combined data
                combined_data["CarrierMatrix"] = carrier_matrix_data
                logger.info("CarrierMatrix module executed successfully")
            except Exception as e:
                logger.error(f"Error executing CarrierMatrix module: {e}", exc_info=True)
                combined_data["CarrierMatrix"] = {
                    "matrix": [],
                    "metadata": {
                        "fc": params.get("Site", "UNKNOWN"),
                        "timestamp": datetime.now().isoformat(),
                        "error": str(e),
                        "row_count": 0,
                        "destinations_count": 0,
                        "LastRunTimestamp": module_timestamp
                    }
                }
                
        elif module == "KARIBA":
            try:
                from KARIBA import KARIBAPuller
                # Call with the Site parameter from config
                kariba_data = KARIBAPuller(Site=params.get("Site", ""))
                # Always include module in output even if empty
                combined_data["KARIBA"] = kariba_data or {
                    "total_units": 0,
                    "units": [],
                    "item_count": 0,
                    "extraction_time": datetime.now().isoformat(),
                    "kariba_site": params.get("Site", "UNKNOWN"),
                    "destination_fc": "UNKNOWN",
                    "error": "Module execution failed or returned no data"
                }
                # Add execution time and timestamp in a separate metadata object
                combined_data["KARIBA_metadata"] = {
                    "LastRunTimestamp": module_timestamp,
                    "ExecutionTimeSeconds": 0,  # Will be updated after module completes
                    "ExecutionDate": module_timestamp.split("T")[0] if "T" in module_timestamp else module_timestamp
                }
                logger.info("KARIBA module executed successfully")
            except Exception as e:
                logger.error(f"Error executing KARIBA module: {e}", exc_info=True)
                combined_data["KARIBA"] = {
                    "total_units": 0,
                    "units": [],
                    "item_count": 0,
                    "extraction_time": datetime.now().isoformat(),
                    "kariba_site": params.get("Site", "UNKNOWN"),
                    "destination_fc": "UNKNOWN",
                    "error": str(e),
                    "LastRunTimestamp": module_timestamp
                }
        
        elif module == "SCACs":
            try:
                from data_retrieval.pull_scacs_mapping_data import pull_scacs_mapping_data
                from data_processing.process_scacs_mapping_data import process_scacs_mapping_data
                
                # This module needs FC parameter
                logger.info(f"Pulling SCACs mapping data for FC={params.get('Site', 'UNKNOWN')}")
                raw_data = pull_scacs_mapping_data(
                    fc=params.get("Site", "UNKNOWN"),
                    start_date=None,
                    end_date=None,
                    session=None,
                    cookie_jar=None
                )
                
                if raw_data:
                    # Process the data if pull was successful
                    scacs_data = process_scacs_mapping_data(raw_data)
                    logger.info(f"Successfully processed SCACs mapping data: {len(scacs_data.get('scacs_mapping', []))} rows")
                else:
                    logger.error("Failed to pull SCACs mapping data")
                    scacs_data = {
                        "scacs_mapping": [],
                        "metadata": {
                            "fc": params.get("Site", "UNKNOWN"),
                            "timestamp": datetime.now().isoformat(),
                            "error": "Failed to retrieve SCACs mapping data",
                            "row_count": 0,
                            "equipment_types": []
                        }
                    }
                
                # Add timestamp metadata 
                # Use current execution time - will be updated after module completes
                if isinstance(scacs_data, dict) and "metadata" in scacs_data:
                    # Create a separate metadata object
                    combined_data["SCACs_metadata"] = {
                        "LastRunTimestamp": module_timestamp,
                        "ExecutionTimeSeconds": 0,  # Will be updated after module completes
                        "ExecutionDate": module_timestamp.split("T")[0] if "T" in module_timestamp else module_timestamp
                    }
                
                # Add to combined data
                combined_data["SCACs"] = scacs_data
                logger.info("SCACs module executed successfully")
            except Exception as e:
                logger.error(f"Error executing SCACs module: {e}", exc_info=True)
                combined_data["SCACs"] = {
                    "scacs_mapping": [],
                    "metadata": {
                        "fc": params.get("Site", "UNKNOWN"),
                        "timestamp": datetime.now().isoformat(),
                        "error": str(e),
                        "row_count": 0,
                        "equipment_types": [],
                        "LastRunTimestamp": module_timestamp
                    }
                }

        elif module == "PPR_Q":
            try:
                from PPR_Q.PPR_Q_FF import PPR_Q_function
                # Call with datetime granularity - get from params dictionary
                ppr_q_data = PPR_Q_function(
                    Site=params.get("Site", "UNKNOWN"),
                    start_datetime=params.get("SOSdatetime", ""),
                    end_datetime=params.get("EOSdatetime", "")
                )
                # Always include module in output even if empty
                combined_data["PPR_Q"] = ppr_q_data or {
                    "total_volume": 0,
                    "total_hours": 0,
                    "rate": 0,
                    "timestamp": datetime.now().isoformat(),
                    "error": "Module execution failed or returned no data"
                }
                # Add execution time and timestamp in a separate metadata object
                combined_data["PPR_Q_metadata"] = {
                    "LastRunTimestamp": module_timestamp,
                    "ExecutionTimeSeconds": 0,  # Will be updated after module completes
                    "ExecutionDate": module_timestamp.split("T")[0] if "T" in module_timestamp else module_timestamp
                }
                logger.info("PPR_Q module executed successfully")
            except Exception as e:
                logger.error(f"Error executing PPR_Q module: {e}", exc_info=True)
                combined_data["PPR_Q"] = {
                    "total_volume": 0,
                    "total_hours": 0,
                    "rate": 0,
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                    "LastRunTimestamp": module_timestamp
                }
        
        elif module == "VIP":
            try:
                # Import the VIP puller
                from data_retrieval.pull_vip_data import pull_vip_data
                from data_processing.process_vip_data import process_vip_data
                
                # This module needs parameters
                logger.info(f"Pulling VIP data for FC={params.get('Site', 'UNKNOWN')}")
                file_path = pull_vip_data(
                    fc=params.get("Site", "UNKNOWN"),
                    midway_session=midway_session,
                    cookie_jar=cookie_jar
                )
                
                if file_path:
                    # Process the data if pull was successful
                    vip_data = process_vip_data(file_path)
                    logger.info(f"Successfully processed VIP data")
                else:
                    logger.error("Failed to pull VIP data")
                    vip_data = {
                        "vip_data": {},
                        "metadata": {
                            "timestamp": datetime.now().isoformat(),
                            "error": "Failed to retrieve VIP data",
                            "site_count": 0,
                            "sites": [],
                            "row_count": 0
                        }
                    }
                
                # Add timestamp metadata to module output
                if isinstance(vip_data, dict) and "metadata" in vip_data:
                    # Create a separate metadata object
                    combined_data["VIP_metadata"] = {
                        "LastRunTimestamp": module_timestamp,
                        "ExecutionTimeSeconds": 0,  # Will be updated after module completes
                        "ExecutionDate": module_timestamp.split("T")[0] if "T" in module_timestamp else module_timestamp
                    }
                
                # Add to combined data
                combined_data["VIP"] = vip_data
                logger.info("VIP module executed successfully")
            except Exception as e:
                logger.error(f"Error executing VIP module: {e}", exc_info=True)
                combined_data["VIP"] = {
                    "vip_data": {},
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "error": str(e),
                        "site_count": 0,
                        "sites": [],
                        "row_count": 0,
                        "LastRunTimestamp": module_timestamp
                    }
                }
        
        else:
            logger.warning(f"Unknown isolated module: {module}")
        
        # Calculate execution time and store it with timestamp
        module_exec_time = time.time() - module_start_time
        module_exec_times[module] = round(module_exec_time, 4)
        
        # Update execution time in module metadata
        if module + "_metadata" in combined_data:
            combined_data[module + "_metadata"]["ExecutionTimeSeconds"] = module_exec_times[module]
        
        # Add execution time to module output if it's a dict
        if module in combined_data:
            if isinstance(combined_data[module], dict):
                combined_data[module]["ExecutionTimeSeconds"] = module_exec_times[module]
            elif isinstance(combined_data[module], dict) and "Metadata" in combined_data[module]:
                combined_data[module]["Metadata"]["ExecutionTimeSeconds"] = module_exec_times[module]
        
        logger.info(f"Module {module} completed in {module_exec_time:.2f}s")
    
    return combined_data, module_exec_times, module_timestamps


def run_oneflow_with_json_return(Site, SOSdatetime, EOSdatetime, plan_type, shift, modules, external_auth=None):
    """
    A wrapper function that runs OneFlow_MainFunction and returns the raw JSON data instead of filepath.
    Enhanced to preserve module timestamps and execution times.
    
    Returns:
        tuple: (outputJSON, module_timestamps, module_exec_times)
            - outputJSON: The complete OneFlow output JSON, or None if an error occurs
            - module_timestamps: Dictionary mapping module names to ISO timestamps
            - module_exec_times: Dictionary mapping module names to execution times
    """
    from OneFlow.oneflow import OneFlow_MainFunction
    from OneFlow.oneflow_config import FC_TO_COUNTRY
    from OneFlow.oneflow_utils import get_parameters, parse_datetime
    from OneFlow.oneflow_data_sources import build_data_sources
    from OneFlow.oneflow_concurrency import run_all_tasks
    from OneFlow.oneflow_audit import build_audit_block
    from threading import Lock
    import pandas as pd
    import time
    
    logger.info(f"Running OneFlow modules: {modules}")
    start_time = time.time()
    error_list = []
    module_timestamps = {}  # Store timestamps for modules
    module_exec_times = {}  # Store execution times for modules
    
    # Authentication
    auth = external_auth
    if not auth:
        from utils.authenticate import Authentication
        auth = Authentication()
        try:
            # Check and refresh authentication if older than 2 hours
            auth = check_and_refresh_authentication(auth, max_hours=1)
        except Exception as auth_error:
            msg = f"Authentication failed: {auth_error}"
            logger.error(msg, exc_info=True)
            error_list.append({
                "Function": "Authentication",
                "ErrorFlag": True,
                "ErrorName": f"Authentication_Error: {auth_error}"
            })
            return None, {}, {}
    
    session = auth.session
    midway_session, cookie_jar = auth.get_midway_session()
    user_login = auth.get_os_username()
    
    # Parameters & Date Parsing
    params = get_parameters(Site, FC_TO_COUNTRY)
    fc = params['FC']
    mp = params['MP']
    default_start_date = params['StartDate']
    default_end_date = pd.Timestamp.now().strftime("%Y-%m-%d")
    current_date = pd.Timestamp.now()
    
    if mp == 'Unknown':
        error_list.append({
            "Function": "get_parameters",
            "ErrorFlag": True,
            "ErrorName": f"Unknown MP for FC '{fc}'"
        })
    
    parsed_sos = parse_datetime(SOSdatetime)
    parsed_eos = parse_datetime(EOSdatetime)
    ppr_sos_str = parsed_sos.strftime("%Y-%m-%d %H:%M:%S")
    ppr_eos_str = parsed_eos.strftime("%Y-%m-%d %H:%M:%S")
    
    # Build DATA_SOURCES
    DATA_SOURCES = build_data_sources(
        modules, fc, mp,
        default_start_date, default_end_date,
        current_date, SOSdatetime, EOSdatetime,
        midway_session, cookie_jar, session,
        parsed_sos, ppr_sos_str, ppr_eos_str,
        Site, plan_type
    )
    
    # Run tasks with re-auth handling
    reauth_lock = Lock()
    partial_results, errors = run_all_tasks(DATA_SOURCES, 5, auth, reauth_lock)
    error_list.extend(errors)
    
    # Build output JSON from partial results
    outputJSON = {}
    
    # Process partial_results and extract timestamps and execution times
    for mod_name, result_data in partial_results.items():
        # The partial_results now contains tuples: (data, timestamp, exec_time)
        if isinstance(result_data, tuple) and len(result_data) >= 3:
            # Unpack the result tuple
            mod_data, mod_timestamp, mod_exec_time = result_data
            
            # Store timestamp and execution time
            module_timestamps[mod_name] = mod_timestamp
            module_exec_times[mod_name] = round(mod_exec_time, 4)
            
            # Special handling for certain modules
            if mod_name in ["DockMaster", "DockMaster2"] and isinstance(mod_data, dict):
                for subkey, val in mod_data.items():
                    if isinstance(val, pd.DataFrame):
                        outputJSON[subkey] = val.to_dict(orient='records')
                    else:
                        outputJSON[subkey] = val
                    
                    # Add metadata as a separate entry for each subkey
                    outputJSON[subkey + "_metadata"] = {
                        "LastRunTimestamp": mod_timestamp,
                        "ExecutionTimeSeconds": mod_exec_time,
                        "ParentModule": mod_name,
                        "ExecutionDate": mod_timestamp.split("T")[0] if "T" in mod_timestamp else mod_timestamp
                    }
                        
            elif mod_name in ["Galaxy", "Galaxy2"] and isinstance(mod_data, tuple):
                df_obj, second_obj = mod_data
                outputJSON[mod_name] = (
                    df_obj.to_dict(orient='records') if isinstance(df_obj, pd.DataFrame) else []
                )
                
                # Create a metadata object at the module level instead of per array item
                outputJSON[mod_name + "_metadata"] = {
                    "LastRunTimestamp": mod_timestamp,
                    "ExecutionTimeSeconds": mod_exec_time,
                    "ExecutionDate": mod_timestamp.split("T")[0] if "T" in mod_timestamp else mod_timestamp
                }
                
                if second_obj:
                    suffix = "_percentages" if mod_name == "Galaxy" else "_values"
                    outputJSON[mod_name + suffix] = second_obj
                    
                    # Add metadata for the second object as well
                    outputJSON[mod_name + suffix + "_metadata"] = {
                        "LastRunTimestamp": mod_timestamp,
                        "ExecutionTimeSeconds": mod_exec_time,
                        "ExecutionDate": mod_timestamp.split("T")[0] if "T" in mod_timestamp else mod_timestamp
                    }
                    
            else:
                # Generic approach
                if isinstance(mod_data, pd.DataFrame):
                    outputJSON[mod_name] = mod_data.to_dict(orient='records')
                    
                    # Add metadata as a separate entry rather than to each record
                    outputJSON[mod_name + "_metadata"] = {
                        "LastRunTimestamp": mod_timestamp,
                        "ExecutionTimeSeconds": mod_exec_time,
                        "RecordCount": len(outputJSON[mod_name]),
                        "ExecutionDate": mod_timestamp.split("T")[0] if "T" in mod_timestamp else mod_timestamp
                    }
                else:
                    outputJSON[mod_name] = mod_data
                    
                    # Add timestamp to the module data if it's a dict
                    if isinstance(outputJSON[mod_name], dict):
                        # Don't add directly to dict to avoid cluttering the module's actual data
                        # Instead create a dedicated metadata object
                        outputJSON[mod_name + "_metadata"] = {
                            "LastRunTimestamp": mod_timestamp,
                            "ExecutionTimeSeconds": mod_exec_time,
                            "ExecutionDate": mod_timestamp.split("T")[0] if "T" in mod_timestamp else mod_timestamp
                        }
        else:
            # Fallback for unexpected format
            if isinstance(result_data, pd.DataFrame):
                outputJSON[mod_name] = result_data.to_dict(orient='records')
            else:
                outputJSON[mod_name] = result_data
            
            # Use current time as timestamp
            current_timestamp = datetime.now().isoformat()
            module_timestamps[mod_name] = current_timestamp
            
            # Use -1 as a marker for unknown execution time
            module_exec_times[mod_name] = -1
    
    # Add Audit block
    previous_history = None  # Start fresh
    audit_info, exec_time = build_audit_block(
        start_time,
        modules,
        error_list,
        module_exec_times,  # Pass execution times for modules
        previous_history
    )
    
    # PROMINENTLY ADD MODULE EXECUTION TIMES TO THE AUDIT
    audit_info["ModuleExecutionTimes"] = module_exec_times
    
    # Add module timestamps to audit block
    audit_info["ModuleTimestamps"] = module_timestamps
    
    # Create module histories for the audit
    module_histories = {}
    for mod_name in modules:
        if mod_name in module_timestamps:
            module_histories[mod_name] = [{
                "Timestamp": module_timestamps[mod_name],
                "ExecutionTimeSeconds": module_exec_times.get(mod_name, -1)
            }]
    
    # Add module histories to audit
    audit_info["ModuleHistories"] = module_histories
    
    # Add a dedicated "ModulePerformance" section for better visibility
    audit_info["ModulePerformance"] = {
        mod_name: {
            "LastExecutionTime": module_timestamps.get(mod_name, "Unknown"),
            "ExecutionTimeSeconds": module_exec_times.get(mod_name, -1),
            "Status": "Success" if module_exec_times.get(mod_name, -1) >= 0 else "Failed or Timeout"
        } for mod_name in modules
    }
    
    # Add the audit block to the output
    outputJSON["Audit"] = audit_info
    
    return outputJSON, module_timestamps, module_exec_times


def main():
    """
    Entry point with improved integration of standalone and regular modules.
    Enhanced with module-level timestamp tracking and execution time recording.
    """
    logger.info("Starting OneFlow application with integrated modules.")
    json_file_path = find_params_file()

    if json_file_path:
        # HEADLESS MODE
        print("[INFO] Running in headless mode with integrated modules.")
        try:
            # Parse the JSON parameters
            with open(json_file_path, "r", encoding="utf-8") as jf:
                params = json.load(jf)

            # Extract parameters
            requested_modules = params.get("Modules", [])
            site = params.get("Site", "")
            sos_dt = params.get("SOSdatetime", "")
            eos_dt = params.get("EOSdatetime", "")
            plan_type = params.get("plan_type", "")
            shift = params.get("shift", "")

            # Validate required parameters
            if not site:
                raise ValueError("Missing 'Site' in parameters file.")
            
            # Track execution time for the entire process
            start_time = time.time()
            
            # Split modules
            isolated_modules = [mod for mod in requested_modules if mod in STANDALONE_MODULES]
            regular_modules = [mod for mod in requested_modules if mod not in STANDALONE_MODULES]
            
            # Initialize master data structure
            combined_data = {}
            all_modules = []  # For audit tracking
            error_list = []   # For audit tracking
            all_module_timestamps = {}  # For timestamp tracking
            all_module_exec_times = {}  # For execution time tracking
            
            # Create a shared authentication object and check if it needs refreshing
            auth = Authentication()
            try:
                # Check and refresh authentication if older than 2 hours
                auth = check_and_refresh_authentication(auth, max_hours=1)
                logger.info("[HEADLESS] Successfully checked/refreshed authentication for headless mode.")
            except Exception as auth_error:
                logger.error(f"[HEADLESS] Authentication failed: {auth_error}", exc_info=True)
                error_list.append({
                    "Function": "Authentication",
                    "ErrorFlag": True,
                    "ErrorName": f"Authentication_Error: {auth_error}"
                })
                # Continue with empty placeholders for all modules
                current_timestamp = datetime.now().isoformat()
                for module in requested_modules:
                    combined_data[module] = {
                        "error": f"Authentication failed: {str(auth_error)}",
                        "LastRunTimestamp": current_timestamp,
                        "ExecutionTimeSeconds": -1
                    }
                    all_module_timestamps[module] = current_timestamp
                    all_module_exec_times[module] = -1
                    
                all_modules.extend(requested_modules)
            else:
                # Step 1: Run standalone modules if any
                if isolated_modules:
                    logger.info(f"Running {len(isolated_modules)} standalone modules: {isolated_modules}")
                    standalone_data, standalone_exec_times, standalone_timestamps = run_standalone_modules(
                        isolated_modules, params, auth
                    )
                    
                    # Update the combined data and tracking
                    combined_data.update(standalone_data)
                    all_modules.extend(isolated_modules)
                    all_module_timestamps.update(standalone_timestamps)
                    all_module_exec_times.update(standalone_exec_times)
                    
                    logger.info(f"Collected data from {len(standalone_data)} standalone modules")
                
                # Step 2: Run regular modules through OneFlow if any
                if regular_modules:
                    logger.info(f"Running {len(regular_modules)} regular modules: {regular_modules}")
                    MAX_ATTEMPTS = 3
                    for attempt in range(1, MAX_ATTEMPTS + 1):
                        try:
                            logger.info(f"[HEADLESS] Attempt #{attempt}/{MAX_ATTEMPTS}: Running OneFlow modules")
                            
                            # Check if authentication needs refreshing before each attempt
                            auth = check_and_refresh_authentication(auth, max_hours=1)
                            
                            # Run OneFlow with our wrapper function to get data directly
                            oneflow_data, oneflow_timestamps, oneflow_exec_times = run_oneflow_with_json_return(
                                Site=site,
                                SOSdatetime=sos_dt,
                                EOSdatetime=eos_dt,
                                plan_type=plan_type,
                                shift=shift,
                                modules=regular_modules,
                                external_auth=auth
                            )
                            
                            if oneflow_data:
                                # Extract Audit section (we'll create a unified one)
                                if "Audit" in oneflow_data:
                                    audit_data = oneflow_data.pop("Audit")
                                    
                                    # Get error details from audit if available
                                    if "ErrorDetails" in audit_data:
                                        error_list.extend(audit_data["ErrorDetails"])
                                    
                                    # Extract module execution times from audit if available
                                    if "ModuleExecutionTimes" in audit_data:
                                        for mod, time_value in audit_data["ModuleExecutionTimes"].items():
                                            all_module_exec_times[mod] = time_value
                                    
                                    # Also check for the legacy format where they might be stored
                                    if "ModulePerformance" in audit_data:
                                        for mod, perf_data in audit_data["ModulePerformance"].items():
                                            if "ExecutionTimeSeconds" in perf_data:
                                                all_module_exec_times[mod] = perf_data["ExecutionTimeSeconds"]
                                
                                # Add OneFlow data to combined data
                                combined_data.update(oneflow_data)
                                all_modules.extend(regular_modules)
                                
                                # Update timestamp and execution time tracking
                                all_module_timestamps.update(oneflow_timestamps)
                                all_module_exec_times.update(oneflow_exec_times)
                                
                                logger.info(f"Successfully retrieved data from OneFlow")
                                break
                            else:
                                logger.error(f"OneFlow returned no data")
                                error_list.append({
                                    "Function": "OneFlow_MainFunction",
                                    "ErrorFlag": True,
                                    "ErrorName": "No data returned"
                                })
                                
                                # Add empty placeholders with timestamps for regular modules
                                current_timestamp = datetime.now().isoformat()
                                for module in regular_modules:
                                    combined_data[module] = {
                                        "error": "Module execution failed or returned no data",
                                        "LastRunTimestamp": current_timestamp,
                                        "ExecutionTimeSeconds": -1
                                    }
                                    all_module_timestamps[module] = current_timestamp
                                    all_module_exec_times[module] = -1
                                
                        except Exception as e:
                            logger.error(f"[HEADLESS] Attempt #{attempt} failed: {e}", exc_info=True)
                            error_list.append({
                                "Function": "OneFlow_MainFunction",
                                "ErrorFlag": True,
                                "ErrorName": str(e)
                            })
                            
                            if attempt < MAX_ATTEMPTS:
                                logger.info(f"[HEADLESS] Retrying... (attempt {attempt+1}/{MAX_ATTEMPTS})")
                            else:
                                logger.error("[HEADLESS] All attempts exhausted.")
                                # Add empty placeholders for all regular modules
                                current_timestamp = datetime.now().isoformat()
                                for module in regular_modules:
                                    combined_data[module] = {
                                        "error": f"All attempts failed: {str(e)}",
                                        "LastRunTimestamp": current_timestamp,
                                        "ExecutionTimeSeconds": -1
                                    }
                                    all_module_timestamps[module] = current_timestamp
                                    all_module_exec_times[module] = -1
            
            # Step 3: Create a unified Audit section for the combined data
            exec_time = time.time() - start_time
            
            # Build module histories for the audit
            module_histories = {}
            for module in all_modules:
                if module in all_module_timestamps:
                    module_histories[module] = [{
                        "Timestamp": all_module_timestamps[module],
                        "ExecutionTimeSeconds": all_module_exec_times.get(module, -1)
                    }]
            
            # Create audit info with module timings
            audit_info, _ = build_audit_block(
                start_time,
                all_modules,
                error_list,
                all_module_exec_times,  # Pass module execution times
                None  # No previous history
            )
            
            # Add MODULE EXECUTION TIMES IN A PROMINANT SECTION OF THE AUDIT
            audit_info["ModuleExecutionTimes"] = all_module_exec_times
            
            # Add module timestamps and histories to audit
            audit_info["ModuleTimestamps"] = all_module_timestamps
            audit_info["ModuleHistories"] = module_histories
            
            # Add a dedicated "ModulePerformance" section for better visibility
            audit_info["ModulePerformance"] = {
                module: {
                    "LastExecutionTime": all_module_timestamps.get(module, "Unknown"),
                    "ExecutionTimeSeconds": all_module_exec_times.get(module, -1),
                    "Status": "Success" if all_module_exec_times.get(module, -1) >= 0 else "Failed or Timeout"
                } for module in all_modules
            }
            
            # Add unified audit to combined data
            combined_data["Audit"] = audit_info
            
            # Step 4: Calculate the parsed start time for the filename
            parsed_sos = parse_datetime(sos_dt)
            
            # Step 5: Save the combined data using the standard output function
            try:
                # Reorder modules according to MODULE_ORDER
                ordered_data = reorder_modules(combined_data, MODULE_ORDER)
                
                # Save using standard function
                final_path = merge_and_write_json(ordered_data, site, shift, plan_type, parsed_sos)
                logger.info(f"Integrated master JSON saved to: {final_path}")
                print(f"[INFO] Integrated master JSON saved to: {final_path}")
                
            except Exception as e:
                logger.error(f"Error saving integrated master JSON: {e}", exc_info=True)
                print(f"[ERROR] Failed to save integrated master JSON: {e}")
            
            # Step 6: Delete parameter file to prevent reexecution
            try:
                os.remove(json_file_path)
                logger.info(f"Deleted parameters file: {json_file_path}")
            except Exception as e:
                logger.warning(f"Could not delete parameters file: {e}")
                
            logger.info("Headless execution completed successfully.")
            sys.exit(0)
                
        except Exception as e:
            logger.error(f"Error in headless mode: {e}", exc_info=True)
            sys.exit(1)

    else:
        # UI MODE
        print("[INFO] No JSON found => launching PyQt GUI.")
        try:
            # Create authentication object for UI mode
            auth = Authentication()
            
            # Check if cookie is valid and refresh only if needed (older than 2 hours)
            try:
                # For UI mode, we can just check if it's older than 2 hours
                auth = check_and_refresh_authentication(auth, max_hours=1)
                logger.info("[UI] Authentication checked/refreshed if needed.")
            except Exception as e:
                # If there are any issues, fall back to force refresh
                logger.warning(f"[UI] Error checking authentication, forcing refresh: {e}")
                force_mwinit_reauth_in_ui(auth)
            
            app = QtWidgets.QApplication(sys.argv)
            window = OneFlowGUI()  # The GUI handles its own normal cookie checks
            window.show()
            logger.info("Launching UI mode.")
            sys.exit(app.exec_())
        except Exception as e:
            logger.error(f"[UI] Authentication failed before launching GUI. Exiting: {e}", exc_info=True)
            sys.exit(1)


if __name__ == '__main__':
    main()
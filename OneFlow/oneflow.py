import time
import logging
import sys
import pandas as pd

from OneFlow.oneflow_config import FC_TO_COUNTRY
from OneFlow.oneflow_utils import get_parameters, parse_datetime
from OneFlow.oneflow_output import merge_and_write_json
from OneFlow.oneflow_data_sources import build_data_sources
from OneFlow.oneflow_concurrency import run_all_tasks

logger = logging.getLogger(__name__)

def OneFlow_MainFunction(Site: str, SOSdatetime: str, EOSdatetime: str,
                         plan_type: str, shift: str,
                         modules=None, max_workers=5, external_auth=None,
                         return_json=False):
    """
    Orchestrates data collection with concurrency and robust re-auth on SSPI/cookie error.

    The final JSON includes top-level data and also an 'Audit' section, which:
      - Tracks the *latest* run info in top-level fields (Timestamp, ExecutionTimeSeconds, etc.)
      - Optionally accumulates all runs in 'Audit["History"]' if you want repeated calls.
    """
    logger.info(f"Starting OneFlow_MainFunction for {Site}, plan_type={plan_type}, shift={shift}, modules={modules}.")

    if modules is None:
        modules = []

    start_time = time.time()
    error_list = []
    partial_results = {}
    final_json_filepath = None

    # --- A) Authentication ---
    if external_auth:
        auth = external_auth
        logger.info("[AUTH] Using external_auth => skipping refresh_cookie_if_needed.")
    else:
        logger.info("[AUTH] Creating new Authentication => refresh if older than 4h.")
        from utils.authenticate import Authentication  # Ensure this is available
        auth = Authentication()
        try:
            auth.refresh_cookie_if_needed(max_hours=4)
            auth._load_cookie()
        except Exception as auth_error:
            msg = f"Authentication failed: {auth_error}"
            logger.error(msg, exc_info=True)
            error_list.append({
                "Function": "Authentication",
                "ErrorFlag": True,
                "ErrorName": f"Authentication_Error: {auth_error}",
                "ErrorType": "Authentication"
            })
            return None

    session = auth.session
    midway_session, cookie_jar = auth.get_midway_session()
    user_login = auth.get_os_username()

    print(f"[INFO] Site={Site}, PlanType={plan_type}, Shift={shift}, Modules={modules}")
    logger.info(f"User login: {user_login}")

    # --- B) Parameters & Date Parsing ---
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
            "ErrorName": f"Unknown MP for FC '{fc}'",
            "ErrorType": "Configuration"
        })

    parsed_sos = parse_datetime(SOSdatetime)
    parsed_eos = parse_datetime(EOSdatetime)
    ppr_sos_str = parsed_sos.strftime("%Y-%m-%d %H:%M:%S")
    ppr_eos_str = parsed_eos.strftime("%Y-%m-%d %H:%M:%S")

    # --- C) Build DATA_SOURCES list ---
    DATA_SOURCES = build_data_sources(
        modules, fc, mp,
        default_start_date, default_end_date,
        current_date, SOSdatetime, EOSdatetime,
        midway_session, cookie_jar, session,
        parsed_sos, ppr_sos_str, ppr_eos_str,
        Site, plan_type
    )

    # --- D) Concurrency: Run tasks with re-auth handling ---
    from threading import Lock
    reauth_lock = Lock()
    
    # Start time for the task execution phase
    tasks_start_time = time.time()
    partial_results, errors = run_all_tasks(DATA_SOURCES, max_workers, auth, reauth_lock)
    tasks_execution_time = time.time() - tasks_start_time
    
    # Log the overall task execution time
    logger.info(f"All modules executed in {tasks_execution_time:.2f}s")

    # Combine concurrency errors
    error_list.extend(errors)

    # --- E) Build output JSON from partial results ---
    outputJSON = {}
    
    # Extract module execution times from partial_results
    module_exec_times = {}
    for mod_name, result_data in partial_results.items():
        if isinstance(result_data, tuple) and len(result_data) >= 3:
            # result_data is (data, timestamp, execution_time)
            module_exec_times[mod_name] = result_data[2]
            # Now handle the actual data
            processed_data = result_data[0]
        else:
            module_exec_times[mod_name] = -1  # Indicate unknown time
            processed_data = result_data
            
        # Special handling for certain modules
        if mod_name in ["DockMaster", "DockMaster2"] and isinstance(processed_data, dict):
            for subkey, val in processed_data.items():
                if isinstance(val, pd.DataFrame):
                    outputJSON[subkey] = val.to_dict(orient='records')
                else:
                    outputJSON[subkey] = val

        elif mod_name in ["Galaxy", "Galaxy2"] and isinstance(processed_data, tuple):
            df_obj, second_obj = processed_data
            outputJSON[mod_name] = (
                df_obj.to_dict(orient='records') if isinstance(df_obj, pd.DataFrame) else []
            )
            if second_obj:
                suffix = "_percentages" if mod_name == "Galaxy" else "_values"
                outputJSON[mod_name + suffix] = second_obj

        else:
            # Generic approach
            if isinstance(processed_data, pd.DataFrame):
                outputJSON[mod_name] = processed_data.to_dict(orient='records')
            else:
                outputJSON[mod_name] = processed_data

    # --- F) Audit block ---
    from OneFlow.oneflow_audit import build_audit_block, record_execution_time, generate_module_status_report

    # If you want to preserve older runs in 'History' across multiple calls or merges,
    # fetch it from a prior object, e.g.:
    # previous_history = outputJSON.get("Audit", {}).get("History", [])
    # For now, pass None to start fresh each run.
    previous_history = None

    audit_info, exec_time = build_audit_block(
        start_time,
        modules,
        error_list,
        module_exec_times,
        previous_history
    )
    outputJSON["Audit"] = audit_info

    # --- G) Write Execution Time CSV with enhanced details ---
    # Extract module execution statuses from audit info
    module_statuses = {}
    # Create pass/fail statuses based on execution times and errors
    for mod_name in modules:
        # Check if module is in error list
        mod_errors = [err for err in error_list if err.get("Function") == mod_name]
        if mod_errors:
            module_statuses[mod_name] = "Failed"
        else:
            exec_time = module_exec_times.get(mod_name, -1)
            if exec_time < 0:
                module_statuses[mod_name] = "Unknown"
            else:
                module_statuses[mod_name] = "Success"

    # Call enhanced function with module-specific data
    try:
        record_execution_time(
            Site, 
            plan_type, 
            shift, 
            exec_time, 
            user_login,
            module_exec_times=module_exec_times,
            module_statuses=module_statuses,
            error_list=error_list
        )
        logger.info(f"Recorded detailed execution metrics for {len(module_exec_times)} modules")
    except Exception as csv_error:
        logger.error(f"Failed to record execution metrics: {csv_error}", exc_info=True)
    
    # Generate a detailed module status report
    try:
        report_path = generate_module_status_report(
            Site,
            module_exec_times,
            module_statuses,
            error_list
        )
        logger.info(f"Generated module status report: {report_path}")
    except Exception as report_error:
        logger.error(f"Failed to generate module status report: {report_error}", exc_info=True)

    # --- H) Merge & Write Final JSON ---
    if not return_json:
        try:
            # Skip ANT folder for PHC, HCTool, and BackLog modules
            modules_to_skip_ant = ["PHC", "HCTool", "BackLog"]
            final_json_filepath = merge_and_write_json(
                outputJSON, Site, shift, plan_type, parsed_sos,
                skip_ant_for_modules=modules_to_skip_ant
            )
            logger.info(f"Wrote final JSON to: {final_json_filepath}")
        except Exception as e:
            print(f"Failed to save JSON: {e}")
            logger.error(f"Failed to save JSON: {e}", exc_info=True)
            final_json_filepath = None
            
        return final_json_filepath
    else:
        return outputJSON


# --- Command-line usage ---
if __name__ == "__main__":
    if len(sys.argv) >= 6:
        Site = sys.argv[1]
        SOSdatetime = sys.argv[2]
        EOSdatetime = sys.argv[3]
        plan_type = sys.argv[4]
        shift = sys.argv[5]
    else:
        Site = input("Enter site code: ").strip()
        SOSdatetime = input("Enter SOS datetime: ").strip()
        EOSdatetime = input("Enter EOS datetime: ").strip()
        plan_type = input("Enter plan type: ").strip()
        shift = input("Enter shift: ").strip()

    result = OneFlow_MainFunction(
        Site, SOSdatetime, EOSdatetime, plan_type, shift,
        modules=["YMS", "FMC", "PPR"]
    )
    print("Final JSON written to:", result)
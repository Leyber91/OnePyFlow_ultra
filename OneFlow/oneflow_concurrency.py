# oneflow_concurrency.py
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time  # Ensure time is imported

logger = logging.getLogger(__name__)

def run_module_task(source, auth, reauth_lock):
    """
    Runs a module task with up to 2 attempts. Records execution time.
    Returns a tuple:
      (module_name, processed_data, error_flag, error_message, timestamp|None, execution_time_seconds)
    Timestamp is ISO format string on success, None on failure.
    Execution_time is float seconds for the task duration.
    """
    func_name = source["name"]
    start_task_time = time.time()  # Start timing the entire task attempt

    def attempt_retrieve_process():
        # This inner function timing for detailed tracking
        inner_start = time.time()
        logger.debug(f"{func_name}: Attempting retrieval...")
        raw_data = source["retrieve_func"]()
        retrieval_time = time.time() - inner_start
        logger.debug(f"{func_name}: Retrieval took {retrieval_time:.2f}s")

        inner_start = time.time()  # Reset timer for processing
        logger.debug(f"{func_name}: Attempting processing...")
        processed = source["process_func"](raw_data)
        processing_time = time.time() - inner_start
        logger.debug(f"{func_name}: Processing took {processing_time:.2f}s")

        # SUCCESS: Capture timestamp here
        success_timestamp = datetime.now().isoformat()
        logger.debug(f"{func_name}: Processing successful at {success_timestamp}.")
        return processed, success_timestamp, retrieval_time, processing_time

    try:
        result, timestamp, retrieval_time, processing_time = attempt_retrieve_process()
        end_task_time = time.time()
        exec_time = end_task_time - start_task_time  # Calculate total task time
        logger.info(f"{func_name}: Task successful in {exec_time:.2f}s (Retrieval: {retrieval_time:.2f}s, Processing: {processing_time:.2f}s)")
        # Return success: data, no error, empty message, timestamp, exec_time
        return func_name, result, False, "", timestamp, exec_time
    except Exception as e1:
        err_str = str(e1)
        
        # Categorize the error
        error_type = "General"
        if any(keyword in err_str for keyword in ["InitializeSecurityContext", "SSPI", "invalid token", "negotiate"]):
            error_type = "Authentication"
        elif "credential" in err_str.lower():
            error_type = "Authentication"
        elif "401" in err_str:
            error_type = "Authentication"
        elif "timeout" in err_str.lower():
            error_type = "Timeout"
        elif "connection" in err_str.lower():
            error_type = "Connection"
        
        # --- Re-auth logic (enhanced for more error types) ---
        if error_type == "Authentication":
            logger.warning(f"{func_name}: Authentication error encountered: {err_str}. Retrying with re-auth...")
            acquired_lock = reauth_lock.acquire(blocking=True, timeout=60)
            if not acquired_lock:
                logger.error(f"{func_name}: Could not acquire re-auth lock, skipping retry.")
                # Still record time taken until failure
                exec_time = time.time() - start_task_time
                return func_name, None, True, f"Re-auth lock timeout. Original error: {err_str}", None, exec_time

            try:
                logger.info(f"{func_name}: Acquired re-auth lock. Refreshing cookie.")
                auth.refresh_cookie_if_needed(max_hours=0)
                auth._load_cookie()
                logger.info(f"{func_name}: Cookie potentially refreshed.")
            except Exception as reauth_err:
                logger.error(f"{func_name} re-auth process failed: {reauth_err}", exc_info=True)
                exec_time = time.time() - start_task_time  # Time until reauth failure
                return func_name, None, True, f"Re-auth failed: {reauth_err}. Original error: {err_str}", None, exec_time
            finally:
                reauth_lock.release()
                logger.info(f"{func_name}: Released re-auth lock.")

            # --- Retry the operation AFTER releasing the lock ---
            logger.info(f"{func_name}: Retrying operation after re-auth attempt...")
            try:
                result, timestamp, retrieval_time, processing_time = attempt_retrieve_process()
                end_task_time = time.time()
                exec_time = end_task_time - start_task_time  # Total time including wait and retry
                logger.info(f"{func_name}: Task successful on retry in {exec_time:.2f}s.")
                return func_name, result, False, "", timestamp, exec_time
            except Exception as e2:
                final_msg = f"Retry after re-auth also failed for {func_name}: {e2}"
                logger.error(final_msg, exc_info=True)
                exec_time = time.time() - start_task_time  # Total time until final failure
                return func_name, None, True, final_msg, None, exec_time
        else:
            # Handle non-auth errors
            logger.error(f"{func_name} encountered a {error_type} error: {e1}", exc_info=True)
            exec_time = time.time() - start_task_time  # Time until failure
            return func_name, None, True, f"{error_type} error: {err_str}", None, exec_time


def run_all_tasks(DATA_SOURCES, max_workers, auth, reauth_lock):
    """
    Runs all conditioned tasks concurrently and collects execution times.
    Returns:
        dict: partial_results {module_name: (processed_data, iso_timestamp_str, exec_time_sec)}
        list: error_list [{..., "ExecutionTimeSeconds": exec_time_sec}]
    """
    partial_results = {}  # Store tuples: (data, timestamp, exec_time)
    error_list = []
    futures = {}
    scheduled_modules = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for source in DATA_SOURCES:
            if source["condition"]():
                mod_name = source["name"]
                scheduled_modules.append(mod_name)
                logger.info(f"Scheduling concurrent module: {mod_name}")
                future = executor.submit(run_module_task, source, auth, reauth_lock)
                futures[future] = mod_name
            else:
                logger.info(f"Skipping {source['name']} based on condition.")

        logger.info(f"Scheduled {len(scheduled_modules)} modules for concurrent execution: {scheduled_modules}")
        
        for future in as_completed(futures):
            mod_name = futures[future]
            try:
                # Unpack the result tuple including the timestamp and exec_time
                _, mod_data, mod_err_flag, mod_err_msg, mod_timestamp, mod_exec_time = future.result()

                if not mod_err_flag:
                    # Store successful result as a tuple (data, timestamp, exec_time)
                    partial_results[mod_name] = (mod_data, mod_timestamp, mod_exec_time)
                    logger.info(f"Successfully completed module: {mod_name} at {mod_timestamp} (took {mod_exec_time:.2f}s)")
                else:
                    # Capture more detailed error information
                    error_details = {
                        "Function": mod_name,
                        "ErrorFlag": True,
                        "ErrorName": mod_err_msg,
                        "ErrorTimestamp": datetime.now().isoformat(),
                        "ExecutionTimeSeconds": mod_exec_time  # Add time taken until failure
                    }
                    
                    # Add more specific status information if available in the error message
                    if "timeout" in mod_err_msg.lower():
                        error_details["ErrorType"] = "Timeout"
                    elif "auth" in mod_err_msg.lower() or "cookie" in mod_err_msg.lower():
                        error_details["ErrorType"] = "Authentication"
                    else:
                        error_details["ErrorType"] = "Processing"
                        
                    error_list.append(error_details)
                    logger.error(f"Module failed: {mod_name} - {mod_err_msg} (after {mod_exec_time:.2f}s)")
                    
                    # Still add the module to partial_results with None data to ensure tracking
                    partial_results[mod_name] = (None, datetime.now().isoformat(), mod_exec_time)
            except Exception as e:
                # Catch potential errors during future.result() itself
                logger.error(f"Critical error processing result for module {mod_name}: {e}", exc_info=True)
                error_list.append({
                    "Function": mod_name,
                    "ErrorFlag": True,
                    "ErrorName": f"Future processing error: {e}",
                    "ExecutionTimeSeconds": -1,  # Indicate unknown execution time
                    "ErrorType": "Critical"
                })
                
                # Add to partial_results to ensure it's tracked even with errors
                partial_results[mod_name] = (None, datetime.now().isoformat(), -1)

    # Log summary of module execution
    success_count = sum(1 for mod_name, result in partial_results.items() 
                        if result[0] is not None)
    failed_count = len(partial_results) - success_count
    logger.info(f"Module execution complete: {success_count} successful, {failed_count} failed")
    
    return partial_results, error_list
# oneflow_audit.py
import os
import csv
import time
from datetime import datetime
import logging
from OneFlow.oneflow_config import CSV_OUTPUT_DIR, CSV_FILENAME

logger = logging.getLogger(__name__)

def record_execution_time(Site, plan_type, shift, exec_time, user_login):
    exec_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    csv_path = os.path.join(CSV_OUTPUT_DIR, CSV_FILENAME)
    os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)
    try:
        write_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
        with open(csv_path, mode='a', newline='') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow([
                    'Datetime', 'Site', 'PlanType', 'Shift',
                    'TotalExecutionTime (seconds)',
                    'TotalExecutionTime (minutes)', 'UserLogin'
                ])
            writer.writerow([
                exec_datetime, Site, plan_type, shift,
                exec_time, exec_time / 60, user_login
            ])
        logger.info(f"Execution time recorded: {exec_time:.2f}s at {exec_datetime}")
    except Exception as e:
        logger.error(f"Failed to record execution time: {e}", exc_info=True)

def build_audit_block(start_time, modules, error_list):
    end_time = time.time()
    exec_time = end_time - start_time
    exec_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_error_count = len([err for err in error_list if err["ErrorFlag"]])
    audit_info = {
        "ExecutionTimeSeconds": exec_time,
        "ExecutionTimeMinutes": exec_time / 60,
        "ErrorCount": total_error_count,
        "Timestamp": exec_datetime,
        "ErrorDetails": error_list,
        "ModulesDownloaded": modules
    }
    return audit_info, exec_time

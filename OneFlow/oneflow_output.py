import os
import json
import logging

from OneFlow.oneflow_config import JSON_OUTPUT_DIR, MODULE_ORDER
from OneFlow.oneflow_utils import reorder_modules, merge_json_dicts

logger = logging.getLogger(__name__)
 
def merge_and_write_json(outputJSON, Site, shift, plan_type, start_datetime, skip_ant_for_modules=None):
    """
    Merges the newly generated 'outputJSON' with an existing JSON file (if present).
    Avoids duplicating the most recent run in 'Audit["History"]'.
    Includes JSON integrity check to handle corrupted files gracefully.
    Checks both local and network paths for existing files.
    
    Args:
        outputJSON (dict): The output JSON to merge and write
        Site (str): Site code
        shift (str): Shift code
        plan_type (str): Plan type
        start_datetime (datetime): Start datetime
        skip_ant_for_modules (list, optional): List of module names to skip saving to ANT folder
    
    Returns:
        str: Path to the saved JSON file
    """
    import os
    import json
    import logging
    from OneFlow.oneflow_config import JSON_OUTPUT_DIR, MODULE_ORDER
    from OneFlow.oneflow_utils import reorder_modules, merge_json_dicts
    
    logger = logging.getLogger(__name__)
    
    # Default list of modules to skip ANT folder for if not provided
    if skip_ant_for_modules is None:
        skip_ant_for_modules = ["PHC", "HCTool", "BackLog"]
    
    # Check if this JSON contains any of the modules we want to skip saving to ANT
    contains_skip_modules = False
    for module in skip_ant_for_modules:
        if module in outputJSON:
            contains_skip_modules = True
            logger.info(f"Detected module {module} that will be skipped for ANT folder save")
            break

    plan_date_str = start_datetime.strftime("%Y.%m.%d")
    filename = f"{Site}-{plan_date_str}-{shift}-{plan_type}.json"
    final_path = os.path.join(JSON_OUTPUT_DIR, filename)
    final_path_ant_dir = os.path.join(r'\\ant\dept-eu\BCN1\ECFT\IXD\01.PLANS', Site, plan_date_str)
    final_path_ant = os.path.join(final_path_ant_dir, filename)

    # 1) Ensure output directories exist
    # Always create local directory
    if not os.path.exists(JSON_OUTPUT_DIR):
        try:
            os.makedirs(JSON_OUTPUT_DIR, exist_ok=True)
            logger.info(f"Created directory: {JSON_OUTPUT_DIR}")
        except Exception as e:
            logger.error(f"Failed to create directory '{JSON_OUTPUT_DIR}': {e}")
    
    # Only create ANT directory if we're not skipping it
    if not contains_skip_modules and not os.path.exists(final_path_ant_dir):
        try:
            os.makedirs(final_path_ant_dir, exist_ok=True)
            logger.info(f"Created directory: {final_path_ant_dir}")
        except Exception as e:
            logger.error(f"Failed to create directory '{final_path_ant_dir}': {e}")

    # 2) Check if files already exist, are non-empty, and are valid JSON => Merge
    existing_file_valid = False
    existing_data = None

    # First try local file
    if os.path.exists(final_path) and os.path.getsize(final_path) > 0:
        try:
            with open(final_path, "r", encoding="utf-8") as existing_file:
                existing_data = json.load(existing_file)
            existing_file_valid = True
            logger.info(f"Successfully loaded existing local JSON file: {final_path}")
        except json.JSONDecodeError:
            logger.warning(f"Existing local JSON file is corrupted: {final_path}.")
            try:
                # Backup the corrupted file 
                backup_path = final_path + ".corrupted"
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(final_path, backup_path)
                logger.info(f"Backed up corrupted local JSON file to: {backup_path}")
            except Exception as e:
                logger.error(f"Failed to backup corrupted local JSON file: {e}")
                try:
                    os.remove(final_path)
                    logger.info(f"Deleted corrupted local JSON file: {final_path}")
                except Exception as del_e:
                    logger.error(f"Failed to delete corrupted local JSON file: {del_e}")

    # If local file wasn't valid, try network file (only if we're not skipping ANT folder)
    if not existing_file_valid and not contains_skip_modules and os.path.exists(final_path_ant) and os.path.getsize(final_path_ant) > 0:
        try:
            with open(final_path_ant, "r", encoding="utf-8") as existing_file:
                existing_data = json.load(existing_file)
            existing_file_valid = True
            logger.info(f"Successfully loaded existing network JSON file: {final_path_ant}")
        except json.JSONDecodeError:
            logger.warning(f"Existing network JSON file is corrupted: {final_path_ant}. Will create a new one.")
            try:
                # Backup the corrupted file
                backup_path = final_path_ant + ".corrupted"
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(final_path_ant, backup_path)
                logger.info(f"Backed up corrupted network JSON file to: {backup_path}")
            except Exception as e:
                logger.error(f"Failed to backup corrupted network JSON file: {e}")
                try:
                    os.remove(final_path_ant)
                    logger.info(f"Deleted corrupted network JSON file: {final_path_ant}")
                except Exception as del_e:
                    logger.error(f"Failed to delete corrupted network JSON file: {del_e}")

    if existing_file_valid and existing_data:
        # -- A) Merge non-Audit modules/data into existing_data --
        new_modules_only = {k: v for k, v in outputJSON.items() if k != "Audit"}
        merged_data = merge_json_dicts(existing_data, new_modules_only)

        # -- B) Merge the new Audit with the old one, avoiding duplication --
        if "Audit" not in merged_data:
            merged_data["Audit"] = {}
        if "History" not in merged_data["Audit"]:
            merged_data["Audit"]["History"] = []
        if "CumulativeTimeSeconds" not in merged_data["Audit"]:
            merged_data["Audit"]["CumulativeTimeSeconds"] = 0.0

        old_history = merged_data["Audit"]["History"]
        old_cumulative = merged_data["Audit"]["CumulativeTimeSeconds"]

        new_audit = outputJSON.get("Audit", {})
        new_history = new_audit.get("History", [])

        # Combine histories
        combined_history = old_history + new_history

        # Remove duplicates by building a set of identifiers
        def record_key(r):
            return (
                r.get("Timestamp"), 
                r.get("ExecutionTimeSeconds"), 
                r.get("ErrorCount")
            )

        seen = set()
        unique_history = []
        for rec in combined_history:
            key = record_key(rec)
            if key not in seen:
                seen.add(key)
                unique_history.append(rec)

        merged_data["Audit"]["History"] = unique_history

        # -- C) Update top-level Audit fields from the "latest run" 
        if new_history:
            latest_run = new_history[-1]
        else:
            latest_run = merged_data["Audit"]["History"][-1] if merged_data["Audit"]["History"] else {}

        # Copy fields from the latest run into top-level
        for field in [
            "Timestamp", "ModulesDownloaded", 
            "ExecutionTimeSeconds", "ExecutionTimeMinutes",
            "ErrorCount", "ErrorDetails"
        ]:
            if field in latest_run:
                merged_data["Audit"][field] = latest_run[field]

        # Recompute CumulativeTimeSeconds from final, unique history
        merged_data["Audit"]["CumulativeTimeSeconds"] = sum(
            run.get("ExecutionTimeSeconds", 0.0) for run in unique_history
        )

        # -- D) Reorder modules according to your global MODULE_ORDER
        merged_data = reorder_modules(merged_data, MODULE_ORDER)

        # -- E) Write final JSON to both paths (or just local path if skipping ANT)
        try:
            # Always write to local path
            with open(final_path, "w", encoding="utf-8") as f:
                json.dump(merged_data, f, indent=4, default=str)
            logger.info(f"[INFO] Merged modules & updated Audit: {final_path}")
                
            # Only write to ANT path if not skipping
            if not contains_skip_modules:
                with open(final_path_ant, "w", encoding="utf-8") as f:
                    json.dump(merged_data, f, indent=4, default=str)
                logger.info(f"[INFO] Merged modules & updated Audit: {final_path_ant}")
            else:
                logger.info(f"[INFO] Skipped writing to ANT folder for optimization (contains skip modules).")
                
        except Exception as write_err:
            logger.error(f"Error writing merged JSON: {write_err}")
            # If merge writing fails, fall back to creating new file
            existing_file_valid = False

    if not existing_file_valid:
        # 3) If no valid files exist => create a brand-new JSON
        outputJSON.setdefault("Audit", {})
        outputJSON["Audit"].setdefault("History", [])
        outputJSON["Audit"].setdefault("CumulativeTimeSeconds", 0.0)

        # The new Audit block might already contain a run in "History"
        # but if not, we add it for consistency
        current_audit = outputJSON["Audit"]
        current_history = current_audit["History"]
 
        # If no runs in "History", add the top-level as a run 
        if not current_history:
            run_record = {
                "Timestamp": current_audit.get("Timestamp", ""),
                "ModulesDownloaded": current_audit.get("ModulesDownloaded", []),
                "ExecutionTimeSeconds": current_audit.get("ExecutionTimeSeconds", 0.0),
                "ExecutionTimeMinutes": current_audit.get("ExecutionTimeMinutes", 0.0),
                "ErrorCount": current_audit.get("ErrorCount", 0),
                "ErrorDetails": current_audit.get("ErrorDetails", []),
            }
            current_history.append(run_record)
            current_audit["CumulativeTimeSeconds"] += run_record["ExecutionTimeSeconds"]

        # Reorder modules for a consistent layout
        outputJSON = reorder_modules(outputJSON, MODULE_ORDER)

        # Write the brand-new JSON with error handling to both paths (or just local if skipping ANT)
        try:
            # Always write to local path
            with open(final_path, "w", encoding="utf-8") as f:
                json.dump(outputJSON, f, indent=4, default=str)
            logger.info(f"[INFO] Created new JSON file: {final_path}")
                
            # Only write to ANT path if not skipping
            if not contains_skip_modules:
                with open(final_path_ant, "w", encoding="utf-8") as f:
                    json.dump(outputJSON, f, indent=4, default=str)
                logger.info(f"[INFO] Created new JSON file: {final_path_ant}")
            else:
                logger.info(f"[INFO] Skipped writing to ANT folder for optimization (contains skip modules).")
                
        except Exception as e:
            logger.error(f"Failed to write new JSON file: {e}")

    return final_path
# -------------------------------
# Transform Module Functions
# -------------------------------

import logging
import pandas as pd

logger = logging.getLogger(__name__)

def recursive_find_lane(obj):
    """
    Recursively search for any key named 'lane' (case-insensitive)
    and return a list of string values.
    """
    lanes = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() == "lane" and isinstance(value, str):
                lanes.append(value)
            else:
                lanes.extend(recursive_find_lane(value))
    elif isinstance(obj, list):
        for item in obj:
            lanes.extend(recursive_find_lane(item))
    return lanes

def recursive_find_shipper_accounts(obj):
    """
    Recursively search for any key named 'shipperAccounts' (case-insensitive)
    and return a list of string values.
    """
    accounts = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() == "shipperaccounts":
                if isinstance(value, list):
                    accounts.extend([str(item) for item in value if isinstance(item, str)])
                elif isinstance(value, str):
                    accounts.append(value)
            else:
                accounts.extend(recursive_find_shipper_accounts(value))
    elif isinstance(obj, list):
        for item in obj:
            accounts.extend(recursive_find_shipper_accounts(item))
    return accounts

def recursive_find_status(obj):
    """
    Recursively search for any key named 'status' (case-insensitive)
    and return a list of its values.
    """
    statuses = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() == "status":
                statuses.append(value)
            statuses.extend(recursive_find_status(value))
    elif isinstance(obj, list):
        for item in obj:
            statuses.extend(recursive_find_status(item))
    return statuses

def transform_yard_data(raw_data):
    """
    Transforms raw YMS data into a list of records.
    Includes the 'movesbyitself' flag so it can later be used for cross-checking.
    """
    if not raw_data:
        logger.warning("transform_yard_data received empty or None raw_data.")
        return []
    all_transformed = []
    summaries = raw_data.get("locationsSummaries", [])
    for summary in summaries:
        for location in summary.get("locations", []):
            # Extract lane information recursively.
            lane_list = recursive_find_lane(location)
            normalized_lanes = [lane.replace("->", "_") for lane in lane_list if isinstance(lane, str)]
            complete_lane = ", ".join(normalized_lanes) if normalized_lanes else "NaN"
            
            for asset in location.get("yardAssets", []):
                load_obj = asset.get("load") or {}

                # --- VRID Extraction ---
                vrid_value = None
                isa_value = None
                for ident in load_obj.get("identifiers", []):
                    if ident.get("type") == "VR_ID":
                        vrid_value = ident.get("identifier")
                        break
                    elif ident.get("type") == "ISA":
                        isa_value = ident.get("identifier")
                if vrid_value is None:
                    vrid_value = isa_value
                # --- End VRID Extraction ---

                # --- Status Extraction ---
                # Simply take the last found status value (or "NaN" if none found).
                status_list = recursive_find_status(asset)
                final_status = status_list[-1] if status_list else "NaN"
                # --- End Status Extraction ---
                
                # Get lane value from the load object and normalize it.
                lane_value = load_obj.get("lane")
                normalized_lane = lane_value.replace("->", "_") if lane_value and isinstance(lane_value, str) else "NaN"
                
                # Determine the load value using shipperAccounts from load if available,
                # or fallback to a recursive search.
                if load_obj and "shipperAccounts" in load_obj and isinstance(load_obj["shipperAccounts"], list) and len(load_obj["shipperAccounts"]) > 0:
                    load_value = load_obj["shipperAccounts"][0]
                else:
                    shipper_accounts_list = recursive_find_shipper_accounts(location)
                    load_value = ", ".join(shipper_accounts_list) if shipper_accounts_list else "NaN"
                
                # Process unavailableReason - convert HEALTHY to NaN since healthy equipment has no unavailable reason
                unavailable_reason = asset.get("unavailableReason")
                if unavailable_reason == "HEALTHY":
                    unavailable_reason = "NaN"
                
                record = {
                    "name": location.get("code"),
                    "locationLabel": location.get("name"),
                    "isempty": final_status,    # This value remains unaltered.
                    "equipment_type": asset.get("type"),
                    "ownercode": (asset.get("owner") or {}).get("code"),
                    "movesbyitself": asset.get("movesbyitself", False),
                    "isunderdocksystemcontrol": asset.get("isunderdocksystemcontrol", "NaN"),
                    "vrid": vrid_value,
                    "unavailable": asset.get("unavailable"),  # Remains as originally provided.
                    "unavailableReason": unavailable_reason,  # Now uses processed value
                    "lane": normalized_lane,  # This is the unfiltered lane value.
                    "complete_lane": complete_lane,
                    "load": load_value
                }
                all_transformed.append(record)
    return all_transformed

def _enhanced_fill_vrid(filtered_df, fmc_df, site_code):
    """
    Fills missing VRIDs by matching YMS records with FMC data.
    """
    logger = logging.getLogger(__name__)
    filled_count = 0
    missing_mask = filtered_df['vrid'].isna() | (filtered_df['vrid'].astype(str).str.strip() == "") | (filtered_df['vrid'].astype(str) == "NaN")
    missing_indices = filtered_df[missing_mask].index

    for idx in missing_indices:
        yms_name = filtered_df.at[idx, 'name']
        owner = filtered_df.at[idx, 'SCAC'] if 'SCAC' in filtered_df.columns else ""
        
        lane = filtered_df.at[idx, 'lane'] if 'lane' in filtered_df.columns else None
        building_code = None
        destination = None
        if lane and isinstance(lane, str) and "->" in lane:
            parts = lane.split("->")
            building_code = parts[0].strip() if parts[0] else yms_name
            destination = parts[1].strip() if len(parts) > 1 else None
        else:
            building_code = yms_name

        candidates = fmc_df[fmc_df['Facility Sequence'].astype(str).str.startswith(building_code, na=False)]
        if destination:
            candidates = candidates[candidates['Facility Sequence'].astype(str).str.contains("_" + destination, na=False)]
        
        if owner:
            candidates = candidates[
                candidates['Shipper Accounts'].astype(str).str.contains(owner, case=False, na=False) |
                candidates['Carrier'].astype(str).str.contains(owner, case=False, na=False)
            ]
        
        if len(candidates) == 1:
            new_vrid = candidates.iloc[0].get("VR ID", "NaN")
            if new_vrid and new_vrid != "NaN":
                filtered_df.at[idx, 'vrid'] = new_vrid
                filled_count += 1
        else:
            logger.debug("[%s] Ambiguous matching for YMS record (index %s): building_code=%s, destination=%s, owner=%s, candidates=%d",
                         site_code, idx, building_code, destination, owner, len(candidates))
    
    logger.info("[%s] Enhanced matching: Filled %d missing VRIDs using FMC data", site_code, filled_count)
    return filtered_df, filled_count

def _post_process_and_crosscheck(df, fmc_df, site_code):
    """
    Applies cross-checking rules on the transformed DataFrame and enhances VRID values.
    IMPORTANT: We are not modifying the 'isempty' or 'unavailable' fields,
    so the final output will simply reflect what was provided originally.
    """
    try:
        ordered_cols = [
            'name', 'isempty', 'movesbyitself', 'equipment_type', 'ownercode', 'vrid',
            'unavailable', 'unavailableReason', 'lane', 'complete_lane'
        ]
        if 'isunderdocksystemcontrol' in df.columns:
            ordered_cols.append('isunderdocksystemcontrol')
        if 'load' in df.columns:
            ordered_cols.append('load')
        filtered_df = df[ordered_cols].copy(deep=True)
    except KeyError:
        filtered_df = df.copy(deep=True)
    
    # Note: We deliberately do not modify the 'isempty' or 'unavailable' fields.

    if not fmc_df.empty and 'VR ID' in fmc_df.columns:
        logger.info(f"[{site_code}] Cross-checking VRIDs with FMC data...")
        fmc_vr_ids = set(fmc_df['VR ID'].dropna())
        yms_vr_ids = set(filtered_df['vrid'].dropna())
        shared_vrids = fmc_vr_ids.intersection(yms_vr_ids)
        for vrid in shared_vrids:
            row_fmc = fmc_df[fmc_df['VR ID'] == vrid]
            if not row_fmc.empty:
                load_val = row_fmc.iloc[0].get('Shipper Accounts', '')
                lane_val = row_fmc.iloc[0].get('Facility Sequence', '').replace('->', '_')
                idx = filtered_df[filtered_df['vrid'] == vrid].index
                if not idx.empty:
                    filtered_df.loc[idx, 'isdrop'] = load_val
                    filtered_df.loc[idx, 'isunderdocksystemcontrol'] = lane_val
        filtered_df, _ = _enhanced_fill_vrid(filtered_df, fmc_df, site_code)
    return filtered_df

def _final_json(filtered_df, unfiltered_json, site_code):
    """
    Assembles the final JSON from the processed DataFrame.
    While most fields come from the cross-checked (filtered) DataFrame,
    the final "YMS_Lane" is taken directly from the unfiltered data's "lane" field.
    """
    try:
        final_filtered = {
            "YMS_unfiltered": unfiltered_json,
            "YMS_status": filtered_df['status'].fillna('NaN').tolist(),
            "YMS_name": filtered_df['name'].fillna('NaN').tolist(),
            "YMS_type": filtered_df['type'].fillna('NaN').tolist(),
            "YMS_SCAC": filtered_df['SCAC'].fillna('NaN').tolist(),
            "YMS_Unavailable": filtered_df['Unavailable'].fillna('NaN').tolist(),
            "YMS_UnavailableReason": filtered_df['unavailableReason'].fillna('NaN').tolist(),
            # YMS_Lane is taken directly from the unfiltered data's "lane" field.
            "YMS_Lane": [record.get("lane", "NaN") for record in unfiltered_json],
            "YMS_Load": filtered_df['Load'].fillna('NaN').tolist(),
            "YMS_VRID": filtered_df['VRID'].fillna('NaN').tolist()
        }
        return final_filtered
    except Exception as exc:
        logger.error(f"[{site_code}] JSON assembly error: {exc}", exc_info=True)
        return {"YMS_unfiltered": unfiltered_json, "YMS_filtered": []}

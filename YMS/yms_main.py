import re
import time
import logging
import pandas as pd
import requests
from requests_negotiate_sspi import HttpNegotiateAuth

# Import functions from our transform module.
from YMS.yms_network import switch_yard, get_yard_state
from YMS.yms_validation import validate_yard_state
from YMS.yms_fmc import load_fmc_data
from YMS.yms_config import EXTERNAL_LINKS
from YMS.yms_transform import transform_yard_data, _post_process_and_crosscheck, _final_json

logger = logging.getLogger(__name__)

def process_yms_data(site_code: str, max_cycle_retries: int = 7) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
    }
    attempt = 0
    final_raw_json = None
    while attempt < max_cycle_retries:
        logger.info("Cycle attempt %s/%s for site %s", attempt + 1, max_cycle_retries, site_code)
        session = requests.Session()
        session.auth = HttpNegotiateAuth()
        yms_url = "https://trans-logistics-eu.amazon.com/yms/shipclerk/#/yard"
        try:
            response = session.get(yms_url, headers=headers, allow_redirects=True, timeout=30, verify=False)
        except Exception as e:
            logger.error("Exception during initial YMS GET: %s", str(e))
            attempt += 1
            time.sleep(15)
            continue

        logger.info("Initial YMS page returned status code %s", response.status_code)
        if response.status_code != 200:
            logger.error("Initial YMS GET failed with status %s", response.status_code)
            attempt += 1
            time.sleep(15)
            continue

        token_match = re.search(r'window\.ymsSecurityToken\s*=\s*"([^"]+)"', response.text)
        if token_match:
            security_token = token_match.group(1)
            logger.info("Extracted security token: Successful")
        else:
            logger.error("Security token not found in initial response")
            attempt += 1
            time.sleep(15)
            continue

        switch_yard(site_code, session, headers)
        time.sleep(15)

        raw_json = get_yard_state(session, security_token)
        if raw_json:
            logger.info("Yard state retrieved successfully")
        else:
            logger.error("Failed to retrieve yard state")

        if raw_json and validate_yard_state(raw_json, site_code):
            final_raw_json = raw_json
            logger.info("Yard state validated for expected site %s", site_code)
            break
        else:
            logger.error("Yard state did not validate for expected value '%s'", site_code)
            attempt += 1
            time.sleep(15)

    if not final_raw_json:
        logger.error("Failed after %s full-cycle attempts for site %s", max_cycle_retries, site_code)
        return {"error": f"Failed after {max_cycle_retries} attempts for site {site_code}"}

    records = transform_yard_data(final_raw_json)
    if not records:
        logger.error("Transformation yielded no records for site %s", site_code)
        return {"error": "No records after transformation"}
    df = pd.DataFrame(records)
    # Capture unfiltered JSON exactly as produced by transform_yard_data.
    unfiltered_json = df.fillna("NaN").to_dict(orient="records")
    
    total_yms_entries = len(unfiltered_json)
    yms_nonempty_vrid = sum(1 for rec in unfiltered_json if rec.get("vrid") not in [None, "", "NaN"])
    yms_empty_vrid = total_yms_entries - yms_nonempty_vrid

    fmc_df = load_fmc_data(site_code)
    if not fmc_df.empty and "VR ID" in fmc_df.columns:
        total_fmc_entries = len(fmc_df)
        fmc_nonempty_vrid = sum(1 for x in fmc_df["VR ID"] if x not in [None, "", "NaN"])
    else:
        total_fmc_entries = 0
        fmc_nonempty_vrid = 0

    # Apply cross-checking and VRID enhancements.
    filtered_df = _post_process_and_crosscheck(df, fmc_df, site_code)

    # Rename columns to their final names.
    try:
        filtered_df.rename(
            columns={
                'isempty': 'status',
                'equipment_type': 'type',
                'ownercode': 'SCAC',
                'unavailable': 'Unavailable',
                'isunderdocksystemcontrol': 'Lane',
                'load': 'Load',
                'vrid': 'VRID',
                'unavailableReason': 'unavailableReason'
            },
            inplace=True
        )
    except Exception as exc:
        logger.error("Error renaming columns for site %s: %s", site_code, str(exc))
        return {"YMS_unfiltered": unfiltered_json, "error": str(exc)}

    # IMPORTANT: We do not alter the lane field here.
    # The final JSON's YMS_Lane will be taken directly from the unfiltered data's "lane" field.
    final_json = _final_json(filtered_df, unfiltered_json, site_code)
    
    # Assess VRID filling counts.
    filtered_vrid_list = final_json.get("YMS_VRID", [])
    yms_filtered_nonempty_vrid = sum(1 for vr in filtered_vrid_list if vr not in [None, "", "NaN"])
    yms_vrid_filled = yms_filtered_nonempty_vrid - yms_nonempty_vrid if yms_filtered_nonempty_vrid > yms_nonempty_vrid else 0

    final_json["YMS_total_entries"] = total_yms_entries
    final_json["YMS_empty_VRID_count"] = yms_empty_vrid
    final_json["YMS_nonempty_VRID_count"] = yms_nonempty_vrid
    final_json["FMC_total_entries"] = total_fmc_entries
    final_json["FMC_nonempty_VRID_count"] = fmc_nonempty_vrid
    final_json["YMS_VRID_count_unfiltered"] = yms_nonempty_vrid
    final_json["YMS_VRID_count_filtered"] = yms_filtered_nonempty_vrid
    final_json["YMS_VRID_filled_from_FMC"] = yms_vrid_filled

    return final_json


# NEW: Helper function to merge two final JSON dictionaries while preserving the key order.
def merge_final_json(main_json: dict, ext_json: dict) -> dict:
    """
    Merge two processed JSON objects field by field while preserving the key order.
    The following ordered keys are expected and maintained:
    
      1. YMS_unfiltered
      2. YMS_status
      3. YMS_name
      4. YMS_type
      5. YMS_SCAC
      6. YMS_Unavailable
      7. YMS_UnavailableReason
      8. YMS_Lane
      9. YMS_Load
      10. YMS_VRID
      11. YMS_total_entries
      12. YMS_empty_VRID_count
      13. YMS_nonempty_VRID_count
      14. FMC_total_entries
      15. FMC_nonempty_VRID_count
      16. YMS_VRID_count_unfiltered
      17. YMS_VRID_count_filtered
      18. YMS_VRID_filled_from_FMC

    For list-type fields, the lists are concatenated (main first, then external).
    For numeric fields, the values are summed.
    """
    ordered_keys = [
        "YMS_unfiltered",
        "YMS_status",
        "YMS_name",
        "YMS_type",
        "YMS_SCAC",
        "YMS_Unavailable",
        "YMS_UnavailableReason",
        "YMS_Lane",
        "YMS_Load",
        "YMS_VRID",
        "YMS_total_entries",
        "YMS_empty_VRID_count",
        "YMS_nonempty_VRID_count",
        "FMC_total_entries",
        "FMC_nonempty_VRID_count",
        "YMS_VRID_count_unfiltered",
        "YMS_VRID_count_filtered",
        "YMS_VRID_filled_from_FMC"
    ]
    merged = {}
    for key in ordered_keys:
        main_val = main_json.get(key)
        ext_val = ext_json.get(key)
        if isinstance(main_val, list) and isinstance(ext_val, list):
            merged[key] = main_val + ext_val
        elif isinstance(main_val, (int, float)) and isinstance(ext_val, (int, float)):
            merged[key] = main_val + ext_val
        else:
            merged[key] = main_val if main_val is not None else ext_val
    return merged


def YMSfunction(site: str) -> dict:
    """
    Aggregator function to pull YMS data.
    If the site has an external yard (per configuration), it also pulls external yard data
    and merges its fields into the main data while preserving key order.
    Returns a combined JSON with a single "Main" key.
    """
    logger.info("Starting YMSfunction for site = %s", site)
    main_result = process_yms_data(site)
    if site in EXTERNAL_LINKS:
        ext_site = EXTERNAL_LINKS[site]
        logger.info("%s also has external yard => %s", site, ext_site)
        ext_result = process_yms_data(ext_site)
        # Merge the external JSON into the main JSON while preserving key order.
        main_result = merge_final_json(main_result, ext_result)
    else:
        logger.info("No external yard for %s; skipping external pull...", site)
    return {"Main": main_result}


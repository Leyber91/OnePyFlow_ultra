# File: pull_dock_master.py

import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

def pull_dock_master(fc, start_date, end_date, midway_session, cookie_jar):
    """
    Retrieves data from DockMaster for the given FC and date range.

    - Removed ±1 day shift. We rely on the caller to pass the correct start_date and end_date.
    - Added debug logging to inspect request parameters and raw JSON result (up to some limit).
    """

    # 1) Convert inputs to string "YYYY-MM-DD" if they are datetime/date objects
    def ensure_ymd_string(d):
        if isinstance(d, datetime):
            return d.strftime("%Y-%m-%d")
        elif isinstance(d, str):
            return d
        else:
            # Fallback if something unexpected is passed in
            return str(d)

    start_date_str = ensure_ymd_string(start_date)
    end_date_str   = ensure_ymd_string(end_date)

    logger.debug(
        f"[DEBUG] DockMaster raw range for FC={fc}: "
        f"start_date={start_date_str}, end_date={end_date_str}"
    )

    # 2) Build request parameters
    url = (
        "https://fc-inbound-dock-execution-service-eu-eug1-dub.dub.proxy.amazon.com/"
        "appointment/bySearchParams"
    )
    params = {
        "warehouseId": fc,
        "searchResultLevel": "FULL",
        "clientId": "dockmaster",
        "localStartDate": f"{start_date_str}T00:00:00",
        "localEndDate": f"{end_date_str}T23:59:59",
        "isStartInRange": "True"
    }

    logger.debug(f"[DEBUG] DockMaster URL: {url}")
    logger.debug(f"[DEBUG] DockMaster params: {params}")

    # 3) Make the GET request
    try:
        response = requests.get(url, params=params, cookies=cookie_jar, verify=False)
        response.raise_for_status()
        data = response.json()
        

        # Log some basic info about the response
        logger.info(f"Data retrieved from DockMaster for FC={fc} | Status Code: {response.status_code}")
        # For debugging: log the first 500 characters of the raw text (optional)
        logger.debug(f"[DEBUG] Raw DockMaster Response (truncated): {response.text[:500]} ...")

        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving data from DockMaster: {e}")
        return None

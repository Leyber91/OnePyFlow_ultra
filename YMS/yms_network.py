# yms_network.py

import time
import logging
import requests
import urllib3

from YMS.yms_config import FC_URL_MAP, EXTERNAL_YARD_MAP

logger = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def switch_yard(yard_code: str, session: requests.Session, headers: dict) -> dict:
    if yard_code in FC_URL_MAP:
        base_url = FC_URL_MAP[yard_code]
        timestamp = int(time.time() * 1000)
        url = f"{base_url}&_={timestamp}"
    elif yard_code in EXTERNAL_YARD_MAP:
        account_id = EXTERNAL_YARD_MAP[yard_code]["account_id"]
        timestamp = int(time.time() * 1000)
        url = f"https://trans-logistics-eu.amazon.com/transcore/putData?operation=setActiveAccount&accountId={account_id}&_={timestamp}"
    else:
        logger.error("Yard code '%s' not found in URL maps", yard_code)
        return {}
    try:
        response = session.get(url, headers=headers, allow_redirects=True, timeout=30, verify=False)
        return {
            "yard_code": yard_code,
            "switch_url": url,
            "status_code": response.status_code,
            "response_headers": dict(response.headers),
            "session_cookies": session.cookies.get_dict()
        }
    except Exception as e:
        logger.error("Exception during switch_yard: %s", str(e))
        return {}

def get_yard_state(session: requests.Session, security_token: str) -> dict:
    logger.info("Retrieving yard state")
    url = "https://jwmjkz3dsd.execute-api.eu-west-1.amazonaws.com/call/getYardStateWithPendingMoves"
    post_payload = {"requester": {"system": "YMSWebApp"}}
    post_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "api": "getYardStateWithPendingMoves",
        "method": "POST",
        "token": security_token,
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://trans-logistics-eu.amazon.com",
        "Connection": "keep-alive",
        "Referer": "https://trans-logistics-eu.amazon.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "TE": "trailers"
    }
    try:
        response = session.post(url, headers=post_headers, json=post_payload, timeout=30, verify=False)
        logger.info("Yard state request returned status code %s", response.status_code)
        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                logger.error("Error parsing yard state JSON: %s", str(e))
                return {}
        else:
            logger.error("Non-200 response while retrieving yard state")
            return {}
    except Exception as e:
        logger.error("Exception during get_yard_state: %s", str(e))
        return {}

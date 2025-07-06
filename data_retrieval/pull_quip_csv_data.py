#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: pull_quip_csv_data.py
Description: Retrieves Quip CSV data in memory using browser cookies (if available)
             and returns the CSV content as a list of lists.
"""

import logging
import csv
from io import StringIO
import requests

try:
    import browsercookie
    BROWSERCOOKIE_AVAILABLE = True
except ImportError:
    BROWSERCOOKIE_AVAILABLE = False

logger = logging.getLogger(__name__)

def pull_quip_csv_data():
    """
    Retrieves Quip CSV data by:
      1. Using browsercookie (if available) to obtain authentication cookies.
      2. Downloading the CSV file from the specified endpoint.
      3. Parsing the CSV text into a list of lists.
    
    Returns:
        list of lists: The CSV data, or None if retrieval fails.
    """
    jar = None
    if BROWSERCOOKIE_AVAILABLE:
        try:
            jar = browsercookie.firefox()
            logger.info("[QuipCSV] Using Firefox browser cookies.")
        except Exception:
            try:
                jar = browsercookie.chrome()
                logger.info("[QuipCSV] Using Chrome browser cookies.")
            except Exception as e:
                logger.warning(f"[QuipCSV] Could not load cookies from browser: {e}")
                jar = None
    else:
        logger.warning("[QuipCSV] browsercookie not installed; no auto cookies. This may cause authentication issues.")

    # Define the CSV endpoint and parameters.
    quip_csv_base = "https://quip-amazon.com/-/csv/QJa9BATQ2bX"
    quip_csv_params = {
        "download": "1",
        "s": "fnyEA5a2zWoh",
        "table_id": "QJa9CAfBJ3p"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://quip-amazon.com/fnyEA5a2zWoh/FCs-enabled",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        # This function uses its own requests session - not the shared one
        # This is intentional as it needs browser cookies
        resp = requests.get(
            quip_csv_base,
            params=quip_csv_params,
            headers=headers,
            cookies=jar,  # Use browser cookies, not Midway
            verify=False,
            timeout=60
        )
    except Exception as e:
        logger.error(f"[QuipCSV] Error during GET request: {e}")
        return None

    logger.info(f"[QuipCSV] GET status_code={resp.status_code}, final URL={resp.url}")

    if resp.status_code != 200 or b"account/login" in resp.content:
        logger.warning("[QuipCSV] Possibly not authenticated or received a login page.")
        return None

    # Parse CSV text.
    try:
        csv_text = resp.text
        f = StringIO(csv_text)
        reader = csv.reader(f)
        rows = list(reader)
        if not rows:
            logger.warning("[QuipCSV] CSV is empty or parsing failed.")
            return None

        logger.info(f"[QuipCSV] Parsed {len(rows)} rows from Quip CSV.")
        return rows
    except Exception as parse_err:
        logger.error(f"[QuipCSV] Error parsing CSV data: {parse_err}")
        return None
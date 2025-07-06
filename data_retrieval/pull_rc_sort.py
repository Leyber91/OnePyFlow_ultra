#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module: pull_rc_sort.py
Description: Retrieves ALPS RC Sort data by fetching and parsing HTML from the ALPS endpoint.
             The URL is built using the provided site code and start date.
"""

import logging
import re
import requests
from requests.exceptions import SSLError, RequestException
from urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup

# Suppress warnings for unverified HTTPS requests (if applicable)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def extract_rc_sort_values(tag):
    """
    Given a BeautifulSoup tag (typically a <tr> or its sibling), find all <td> elements
    whose 'id' attribute starts with '60_63_2_' and return a dictionary mapping cell IDs to text.
    """
    measure_cells = tag.find_all("td", attrs={"id": re.compile(r"^60_63_2_")})
    results = {}
    for cell in measure_cells:
        cell_id = cell.get("id")
        cell_val = cell.get_text(strip=True)
        results[cell_id] = cell_val
    return results

def fetch_alps_rc_sort_data(session, Site, start_str):
    """
    Fetches and parses ALPS RC Sort data.

    Parameters:
      - session: An authenticated requests.Session instance.
      - Site (str): The site code (e.g., 'CDG7') used in the ALPS URL.
      - start_str (str): A date string in "YYYY-MM-DD" format to be used in the URL.

    Returns:
      - dict: A dictionary of RC Sort values, or None if retrieval or parsing fails.
    """
    # Build the URL dynamically using the given start date.
    url = (
        f"https://alps-eu.amazon.com/timeseries_sets/latest_BASE.html?"
        f"fcs={Site}&metrics=FLOW_PATH_PERCENTAGE&start_date={start_str}"
    )
    logging.info(f"Fetching ALPS RC Sort data from: {url}")

    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # Find all rows (<tr>) containing the text "RC Sort - Total"
        rc_sort_rows = [row for row in soup.find_all("tr") if "RC Sort - Total" in row.get_text()]
        if not rc_sort_rows:
            logging.warning("Could not find any row containing 'RC Sort - Total' in the HTML.")
            return None

        final_results = {}
        for row in rc_sort_rows:
            # Try to extract RC Sort values from the current row.
            row_results = extract_rc_sort_values(row)
            if row_results:
                final_results.update(row_results)
            else:
                # Check the next sibling row (for multi-row scenarios)
                next_tr = row.find_next_sibling("tr")
                if next_tr:
                    row_results = extract_rc_sort_values(next_tr)
                    if row_results:
                        final_results.update(row_results)

        if not final_results:
            logging.warning("Found 'RC Sort - Total' but no <td> with IDs starting with '60_63_2_'.")
            return None

        logging.info("Extracted ALPS RC Sort data successfully.")

        return final_results

    except SSLError:
        logging.error(
            "SSL certificate verification failed. "
            "If you have a corporate CA bundle, point session.verify to it. "
            "Otherwise, set verify=False (DEV ONLY).",
            exc_info=True
        )
        return None
    except RequestException as req_err:
        logging.error(f"Failed to retrieve ALPS RC Sort data: {req_err}", exc_info=True)
        return None

def pull_rc_sort_data(session, Site="CDG7", start_date=None, rc_sort_url=None):
    """
    Fetches ALPS RC Sort data using the provided session and start date.

    Args:
        session (requests.Session): Authenticated session.
        Site (str): Site code (default is "CDG7").
        start_date (datetime or str, optional): A date value used in the URL.
            If provided as a datetime object, it will be converted to "YYYY-MM-DD".
            If not provided, a default date "2024-12-16" is used.
        rc_sort_url (str, optional): The RC Sort URL to fetch. If not provided,
            a default URL is built using the start date.

    Returns:
        dict: Raw ALPS RC Sort data, or None if retrieval fails.
    """
    logging.info("Starting pull_alps_rc_sort_data.")

    # Determine the start date string.
    if start_date is None:
        start_date_str = "2024-12-16"
    else:
        if isinstance(start_date, str):
            start_date_str = start_date  # Assume properly formatted "YYYY-MM-DD"
        else:
            try:
                start_date_str = start_date.strftime("%Y-%m-%d")
            except Exception as e:
                logging.error(f"Error formatting start_date: {e}")
                return None

    # If an explicit URL is not provided, build one.
    if not rc_sort_url:
        rc_sort_url = (
            f"https://alps-eu.amazon.com/timeseries_sets/latest_BASE.html?"
            f"fcs={Site}&metrics=FLOW_PATH_PERCENTAGE&start_date={start_date_str}"
        )
    data = fetch_alps_rc_sort_data(session, Site, start_date_str)
    if data is None:
        logging.error("No RC Sort data retrieved from ALPS endpoint.")
    else:
        logging.info("RC Sort data retrieved successfully.")

    return data


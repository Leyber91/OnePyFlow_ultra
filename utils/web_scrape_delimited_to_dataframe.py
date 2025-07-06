# utils/web_scrape_delimited_to_dataframe.py

import logging
import pandas as pd
from io import StringIO
from http.cookiejar import MozillaCookieJar

logger = logging.getLogger(__name__)

from utils.authenticate import Authentication

def web_scrape_delimited_to_dataframe(session, url, cookie_jar, delimiter=','):
    """
    Fetches data from a URL using the Midway cookies and returns a DataFrame.

    Parameters:
    - session (requests.Session): The current session object.
    - url (str): The URL to fetch data from.
    - cookie_jar (MozillaCookieJar): The cookie jar containing session cookies.
    - delimiter (str): The delimiter used in the data.

    Returns:
    - pd.DataFrame or None: The resulting DataFrame or None if failed.
    """
    try:
        response = session.get(url, cookies=cookie_jar, verify=False)
        if response.status_code == 401:
            logger.warning("Authentication failed. Reinitializing Midway...")
            Authentication().initialize_midway()
            midway_session, cookie_jar = Authentication().get_midway_session()
            session.cookies.update(cookie_jar)
            response = session.get(url, cookies=cookie_jar, verify=False)

        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), delimiter=delimiter, header=None)
        logger.info(f"Data retrieved from {url}: {df.shape}")
        return df

    except Exception as e:
        logger.error(f"Failed to retrieve data from {url}: {e}")
        return None

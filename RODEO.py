import logging

# Create or retrieve a logger
logger = logging.getLogger(__name__)

def RODEOfunction(Site):
    logger.info("RODEO: Importing libraries...")
    from datetime import datetime, timedelta
    import requests
    from http.cookiejar import MozillaCookieJar
    import getpass
    import pandas as pd
    import warnings
    import io
    from bs4 import BeautifulSoup
    from openpyxl import load_workbook

    warnings.filterwarnings('ignore')

    # 1) Load cookies from Midway
    cookie_file_path = f'C:/Users/{getpass.getuser()}/.midway/cookie'
    cookie_jar = MozillaCookieJar(cookie_file_path)
    cookie_jar.load()

    logger.info("RODEO: Requesting latest data...")
    # 2) The target URL
    url = f"https://rodeo-dub.amazon.com/{Site}/CSV/ExSD?Excel=true"

    try:
        # 3) Send GET request
        response = requests.get(url, cookies=cookie_jar, verify=False)
        status_code = response.status_code
        logger.info(f"RODEO: HTTP status code: {status_code}")

        if status_code != 200:
            logger.warning(f"RODEO: Error in HTTP request: {status_code}")
            return None

        # 4) Check if the response is HTML (login page) rather than CSV
        first_chunk = response.text[:500].lower()
        if "<html" in first_chunk or "<!doctype" in first_chunk:
            logger.error("[ERROR] RODEO returned HTML (likely a login page), not CSV.")
            logger.debug("[DEBUG] Partial content:\n" + response.text[:500])
            return None

        # 5) Attempt to parse the CSV
        logger.info("RODEO: Request successful. Attempting to parse CSV...")
        df = pd.read_csv(io.StringIO(response.text))

        # 6) Check for expected '<table>' column
        if '<table>' not in df.columns:
            logger.error("[ERROR] No '<table>' column in the CSV. Possibly unexpected format.")
            return None

        # 7) Parse the HTML in the '<table>' column
        html_content = ''.join(df['<table>'].astype(str))
        soup = BeautifulSoup(html_content, 'html.parser')

        headers = [header.get_text() for header in soup.find_all('th')]
        rows = []
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if cells:
                rows.append([cell.get_text() for cell in cells])

        if not headers:
            logger.warning("[WARNING] No <th> elements found. The table might be empty or unstructured.")

        # 8) Create a new DataFrame from parsed HTML
        cleaned_data = pd.DataFrame(rows, columns=headers if headers else None)

    except requests.RequestException as RODEO_data_request_error:
        logger.error(f"RODEO: Error RODOE_data_request_error: {RODEO_data_request_error}")
        return None
    except Exception as general_error:
        logger.error(f"[ERROR] Some other error while parsing RODEO data: {general_error}")
        return None

    # 9) Validate the resulting DataFrame
    if cleaned_data.empty or cleaned_data.shape[1] < 3:
        logger.error("[ERROR] The extracted 'cleaned_data' is empty or missing columns. Cannot proceed.")
        return None

    RodeoPull_WorkPool = cleaned_data.iloc[:, 0]
    RodeoPull_Quantity = cleaned_data.iloc[:, 2]

    Crossdock = 0.0
    Palletized = 0.0
    Loaded = 0.0

    try:
        Crossdock = cleaned_data[cleaned_data.iloc[:, 0] == "Crossdock"].iloc[:, 2].astype(float).sum()
        Palletized = cleaned_data[cleaned_data.iloc[:, 0] == "Palletized"].iloc[:, 2].astype(float).sum()
        Loaded = cleaned_data[cleaned_data.iloc[:, 0] == "Loaded"].iloc[:, 2].astype(float).sum()
    except Exception as parse_error:
        logger.error(f"[ERROR] Could not parse numeric columns for Crossdock/Palletized/Loaded: {parse_error}")

    logger.info(f"RODEO: Total 'Crossdock' sum: {Crossdock}")
    logger.info(f"RODEO: Total 'Palletized' sum: {Palletized}")
    logger.info(f"RODEO: Total 'Loaded' sum: {Loaded}")

    RodeoPuller_json = {
        "RodeoPull_WorkPool": RodeoPull_WorkPool.tolist(),
        "RodeoPull_Quantity": RodeoPull_Quantity.tolist(),
        "Crossdock": Crossdock,
        "Palletized": Palletized,
        "Loaded": Loaded
    }

    logger.info('RODEO: Finished!')
    return RodeoPuller_json

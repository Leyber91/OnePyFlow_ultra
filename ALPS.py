import logging

# Get or create a logger
logger = logging.getLogger(__name__)

def ALPSfunction(Site, start_date_str=None, end_date_str=None):
    """
    Downloads ALPS data (IB, Hours, Densities) for the given Site.
    If start_date_str/end_date_str are provided, uses them for both IB and Hours portions;
    otherwise falls back to (today-1, today+6).
    """

    logger.info('ALPS: Importing libraries...')
    from datetime import datetime, timedelta
    import requests
    from http.cookiejar import MozillaCookieJar
    import getpass
    import pandas as pd
    import warnings
    import io

    warnings.filterwarnings('ignore')

    # Definir la ruta del archivo de cookies de Midway
    cookie_file_path = f'C:/Users/{getpass.getuser()}/.midway/cookie'
    
    # Inicializar el archivo de cookies
    cookie_jar = MozillaCookieJar(cookie_file_path)
    cookie_jar.load()

    # Extraer la sesión de Midway del archivo de cookies
    midway_session = ''
    with open(cookie_file_path, 'r') as file:
        for line in file:
            if 'session' in line:
                midway_session = 'session=' + line.split('session')[-1].strip()

    # Initialize the JSON dictionary to return
    ALPS_JSON = {}

    # Determine date range - use provided dates if available, otherwise use default range
    if start_date_str and end_date_str:
        # Use user-provided date range
        logger.info(f'ALPS: Using provided date range: {start_date_str} to {end_date_str}')
        startDate_str = start_date_str
        endDate_str = end_date_str
    else:
        # Fall back to default range (yesterday to yesterday+6 days)
        startDate = datetime.now() - timedelta(days=1)
        endDate = startDate + timedelta(days=6)
        startDate_str = startDate.strftime("%Y-%m-%d")
        endDate_str = endDate.strftime("%Y-%m-%d")
        logger.info(f'ALPS: Using default date range: {startDate_str} to {endDate_str}')

    # ------------------------- ALPS IB -------------------------
    logger.info(f'ALPS: Requesting IB data for period {startDate_str} to {endDate_str}...')

    url = (
        "https://midway.eu-west-1.prod.tsv.alps.lamps.amazon.dev/"
        f"labor-plan?sites={Site}&concept=PROCESSING_CAPABILITY&aspect=FORECAST&"
        f"startDate={startDate_str}&endDate={endDate_str}"
    )

    try:
        response = requests.get(url, cookies=cookie_jar, verify=False)
        if response.status_code == 200:
            logger.info('ALPS: IB Request successful')
            df = pd.read_csv(io.StringIO(response.text), delimiter='\t')

            ALPS_IB_LaborPool1 = df.iloc[:, 6]  # Column 7
            ALPS_IB_LaborPool2 = df.iloc[:, 7]  # Column 8
            ALPS_IB_Date       = df.iloc[:, 14] # Column 15
            ALPS_IB_Value      = df.iloc[:, 15] # Column 16

            ALPS_IB = {
                "ALPS_IB_Labor Pool 1": ALPS_IB_LaborPool1.fillna('NaN').tolist(),
                "ALPS_IB_Labor Pool 2": ALPS_IB_LaborPool2.fillna('NaN').tolist(),
                "ALPS_IB_Date": ALPS_IB_Date.fillna('NaN').tolist(),
                "ALPS_IB_Value": ALPS_IB_Value.fillna('NaN').tolist(),
            }

            ALPS_JSON.update({"ALPS_IB": ALPS_IB})
        else:
            logger.warning(f'ALPS: IB request returned status code {response.status_code}')

    except requests.RequestException as ALPS_request_error1:
        logger.error(f"ALPS: The ALPS_request_error1 is: {ALPS_request_error1}")

    # ------------------------- ALPS HOURS -------------------------
    logger.info(f'ALPS: Requesting Hours data for period {startDate_str} to {endDate_str}...')

    url = (
        "https://midway.eu-west-1.prod.tsv.alps.lamps.amazon.dev/"
        f"labor-plan?sites={Site}&concept=SHOW_HOURS&aspect=FORECAST&"
        f"startDate={startDate_str}&endDate={endDate_str}"
    )

    try:
        response = requests.get(url, cookies=cookie_jar, verify=False)
        if response.status_code == 200:
            logger.info('ALPS: Hours Request successful')
            df = pd.read_csv(io.StringIO(response.text), delimiter='\t')

            ALPS_HOURS_LaborPool1 = df.iloc[:, 6]
            ALPS_HOURS_LaborPool2 = df.iloc[:, 7]
            ALPS_HOURS_Date       = df.iloc[:, 14]
            ALPS_HOURS_Value      = df.iloc[:, 15]

            ALPS_HOURS = {
                "ALPS_HOURS_Labor Pool 1": ALPS_HOURS_LaborPool1.fillna('NaN').tolist(),
                "ALPS_HOURS_Labor Pool 2": ALPS_HOURS_LaborPool2.fillna('NaN').tolist(),
                "ALPS_HOURS_Date": ALPS_HOURS_Date.fillna('NaN').tolist(),
                "ALPS_HOURS_Value": ALPS_HOURS_Value.fillna('NaN').tolist(),
            }

            ALPS_JSON.update({"ALPS_HOURS": ALPS_HOURS})
        else:
            logger.warning(f'ALPS: Hours request returned status code {response.status_code}')

    except requests.RequestException as ALPS_request_error2:
        logger.error(f"ALPS: The ALPS_request_error2 is: {ALPS_request_error2}")

    # ------------------------- ALPS DENSITIES -------------------------
    logger.info('ALPS: Requesting Densities data...')
    startDate = datetime.now() - timedelta(days=7)
    startDate_str_dens = startDate.strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    start_of_week = datetime.now() - timedelta(
        days=datetime.now().weekday() + 1 if datetime.now().weekday() != 6 else 0
    )
    start_of_week_str = start_of_week.strftime("%Y-%m-%d")
    logger.debug(f"The day is {today}. The start of the week is {start_of_week_str}")

    url = (
        "https://midway.eu-west-1.prod.tsv.alps.lamps.amazon.dev/"
        f"labor-plan?sites={Site}&concept=UNITS_PER_BUNDLE&aspect=FORECAST&"
        f"startDate={startDate_str_dens}"
    )
    print(url)

    try:
        response = requests.get(url, cookies=cookie_jar, verify=False)
        if response.status_code == 200:
            logger.info('ALPS: Densities Request successful')
            df = pd.read_csv(io.StringIO(response.text), delimiter='\t')

            # FIXED: Get LP Receive UPC (not sum)
            # First try with week filter
            lp_week_data = df[
                (df.iloc[:, 14] == start_of_week_str) & 
                (df.iloc[:, 6] == "PPR_DETAIL_INBOUND_RECEIVE_LP_RECEIVE")
            ].iloc[:, 15]
            
            if len(lp_week_data) > 0:
                # Found data for specific week - use mean instead of sum
                ALPS_Densitites_LPReceive = float(lp_week_data.mean())
                logger.info(f'ALPS: LP Receive UPC for week {start_of_week_str}: {ALPS_Densitites_LPReceive}')
            else:
                # No data for that week, get ANY LP Receive data
                lp_any_data = df[df.iloc[:, 6] == "PPR_DETAIL_INBOUND_RECEIVE_LP_RECEIVE"].iloc[:, 15]
                
                if len(lp_any_data) > 0:
                    # Use mean of all available data
                    ALPS_Densitites_LPReceive = float(lp_any_data.mean())
                    logger.info(f'ALPS: No LP data for week {start_of_week_str}, using overall mean: {ALPS_Densitites_LPReceive}')
                else:
                    ALPS_Densitites_LPReceive = 0.0
                    logger.warning('ALPS: No LP Receive data found at all')

            # FIXED: Get Pallet Receive UPP (not sum)
            # First try with week filter
            pallet_week_data = df[
                (df.iloc[:, 14] == start_of_week_str) & 
                (df.iloc[:, 6] == "PPR_DETAIL_INBOUND_RECEIVE_PALLET_RECEIVE")
            ].iloc[:, 15]
            
            if len(pallet_week_data) > 0:
                # Found data for specific week - use mean instead of sum
                ALPS_Densitites_PalletReceive = float(pallet_week_data.mean())
                logger.info(f'ALPS: Pallet Receive UPP for week {start_of_week_str}: {ALPS_Densitites_PalletReceive}')
            else:
                # No data for that week, get ANY Pallet Receive data
                pallet_any_data = df[df.iloc[:, 6] == "PPR_DETAIL_INBOUND_RECEIVE_PALLET_RECEIVE"].iloc[:, 15]
                
                if len(pallet_any_data) > 0:
                    # Use mean of all available data
                    ALPS_Densitites_PalletReceive = float(pallet_any_data.mean())
                    logger.info(f'ALPS: No Pallet data for week {start_of_week_str}, using overall mean: {ALPS_Densitites_PalletReceive}')
                else:
                    ALPS_Densitites_PalletReceive = 0.0
                    logger.warning('ALPS: No Pallet Receive data found at all')

            ALPS_DENSITIES = {
                "ALPS_Densitites_LPReceive": ALPS_Densitites_LPReceive,
                "ALPS_Densitites_PalletReceive": ALPS_Densitites_PalletReceive
            }

            ALPS_JSON.update({"ALPS_DENSITIES": ALPS_DENSITIES})
        else:
            logger.warning(f'ALPS: Densities request returned status code {response.status_code}')

    except requests.RequestException as ALPS_request_error3:
        logger.error(f"ALPS: The ALPS_request_error3 is: {ALPS_request_error3}")

    logger.info('ALPS: Finished!')
    return ALPS_JSON
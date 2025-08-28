import logging
import pandas as pd
from datetime import datetime
from utils.authenticate import Authentication  

# Import data retrieval functions
from data_retrieval.pull_dock_master import pull_dock_master
from data_retrieval.pull_dock_master_2 import pull_dock_master_2
from data_retrieval.pull_galaxy import pull_galaxy
from data_retrieval.pull_galaxy2 import pull_galaxy2
from data_retrieval.pull_icqa import pull_icqa
from data_retrieval.pull_dockflow_data import pull_dockflow_data
from data_retrieval.pull_f2p_data import pull_f2p_data
from data_retrieval.pull_necronomicon_data import pull_necronomicon_data
from data_retrieval.pull_ssp_data import pull_ssp_data
from data_retrieval.pull_rc_sort import pull_rc_sort_data
from data_retrieval.pull_quip_csv_data import pull_quip_csv_data
from data_retrieval.pull_carrier_matrix_data import pull_carrier_matrix
from data_retrieval.pull_sspot_data import pull_sspot_data
from data_retrieval.pull_scacs_mapping_data import pull_scacs_mapping_data
from data_retrieval.pull_spark_snapshot_data import pull_spark_snapshot_data
from data_retrieval.pull_vip_data import pull_vip_data
from data_retrieval.pull_ibbt_data import pull_ibbt_data  # Add IBBT import

# Configure logging
logger = logging.getLogger(__name__)

def retrieve_data(func_name, fc, start_date, end_date, midway_session, cookie_jar, session=None, mp=None):
    """
    Retrieves data based on the function name, ensuring proper session handling.
    
    Parameters:
        func_name (str): Name of the function to execute.
        fc (str): Fulfillment Center code (or Site code for ALPS_RC_Sort).
        start_date: Start date for data retrieval (or parsed_sos for ALPS_RC_Sort).
        end_date: End date for data retrieval (not used for ALPS_RC_Sort).
        midway_session: Midway session information (not used for ALPS_RC_Sort).
        cookie_jar: Cookie jar with authentication cookies (not used for ALPS_RC_Sort).
        session (requests.Session, optional): Existing session to use.
        mp (str, optional): Marketplace code.
        
    Returns:
        Data retrieved from the respective function.
    """
    try:
        # Create session if not provided.
        if session is None:
            session = Authentication().setup_session()
            logger.info("New session created for data retrieval")
        
        # Update session cookies with cookie jar if provided.
        if cookie_jar:
            # Fixed: Properly handle MozillaCookieJar objects
            try:
                if hasattr(cookie_jar, 'update'):
                    session.cookies.update(cookie_jar)
                else:
                    # For MozillaCookieJar objects, we need to add cookies one by one
                    for cookie in cookie_jar:
                        session.cookies.set_cookie(cookie)
                logger.debug("Cookies successfully added to session")
            except Exception as cookie_err:
                logger.warning(f"Error adding cookies to session: {cookie_err}")

        # Map functions to their handlers with appropriate parameters.
        # Note: For ALPS_RC_Sort, we assume:
        #   - fc is used as the Site code.
        #   - start_date is a datetime object (parsed_sos).
        func_mapping = {
            'DockMaster': lambda: pull_dock_master(fc, start_date, end_date, midway_session, cookie_jar),
            'DockMaster2': lambda: pull_dock_master_2(fc, midway_session, cookie_jar),
            'Galaxy': lambda: pull_galaxy(session, fc, start_date),
            'Galaxy2': lambda: pull_galaxy2(session, fc, start_date),
            'ICQA': lambda: pull_icqa(fc, 
                                    start_date if isinstance(start_date, datetime) else datetime.now(), 
                                    midway_session, cookie_jar),
            'DockFlow': lambda: pull_dockflow_data(fc, midway_session, cookie_jar),
            'F2P': lambda: pull_f2p_data(session, fc, mp, cookie_jar),
            'kNekro': lambda: pull_necronomicon_data(fc, start_date, session, cookie_jar),
            'SSP': lambda: pull_ssp_data(fc, start_date, end_date, session, cookie_jar),
            'SSPOT': lambda: pull_sspot_data(fc, start_date, end_date, session, cookie_jar),
            'ALPS_RC_Sort': lambda: pull_rc_sort_data(session, fc, start_date),
            'QuipCSV': lambda: pull_quip_csv_data(),  # QuipCSV handles its own authentication via browser cookies
            'CarrierMatrix': lambda: pull_carrier_matrix(fc, midway_session, cookie_jar),
            'SCACs': lambda: pull_scacs_mapping_data(fc, start_date, end_date, session, cookie_jar),
            'SPARK': lambda: pull_spark_snapshot_data(fc, start_date, end_date, session, cookie_jar),
            'VIP': lambda: pull_vip_data(fc, midway_session, cookie_jar),
            'IBBT': lambda: pull_ibbt_data(fc, midway_session, cookie_jar)  # Add IBBT function mapping
        }

        # Check if function exists in mapping.
        if func_name not in func_mapping:
            logger.error(f"No data retrieval function defined for {func_name}")
            raise ValueError(f"No data retrieval function defined for {func_name}")

        # Execute the function and return its result.
        logger.info(f"Executing data retrieval for: {func_name}")
        result = func_mapping[func_name]()
        
        if result is None:
            logger.warning(f"No data retrieved for {func_name}")
        else:
            logger.info(f"Successfully retrieved data for {func_name}")
        
        return result

    except Exception as e:
        logger.error(f"Error in retrieve_data for {func_name}: {e}")
        logger.debug("Exception details:", exc_info=True)
        return None
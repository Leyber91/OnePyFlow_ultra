# oneflow_data_sources.py
import logging
from datetime import timedelta
from data_retrieval.data_retrieval import retrieve_data
from data_processing.data_processing import process_data, process_ssp_data
from PPR.PPR_FF import PPRfunction
from PPR_Q import PPRQProcessor
from ALPS import ALPSfunction

def PPR_Q_function(Site, SOSdatetime, EOSdatetime):
    """
    Wrapper function for PPRQProcessor to maintain compatibility with existing code.
    """
    from datetime import datetime
    from OneFlow.oneflow_utils import parse_datetime
    
    # Parse datetime strings to datetime objects
    sos_dt = parse_datetime(SOSdatetime) if SOSdatetime else None
    eos_dt = parse_datetime(EOSdatetime) if EOSdatetime else None
    
    if not sos_dt or not eos_dt:
        logger.error("PPR_Q: Invalid SOS/EOS datetime provided")
        return {}
    
    # Create PPRQProcessor and run it
    ppr_q = PPRQProcessor(site=Site, sos_datetime=sos_dt, eos_datetime=eos_dt)
    return ppr_q.run()
from RODEO import RODEOfunction
# ULTRA-ENHANCED YMS: 100% traditional quality, 8x faster!
# from YMS_API.yms_ultra_main import YMSfunction
from YMS.yms_main import YMSfunction
from FMC import FMCfunction
from OneFlow.oneflow_utils import parse_datetime
from ALPSRoster import ALPSRosterFunction


logger = logging.getLogger(__name__)


def retrieve_with_default(mod_name, fc, SOSdatetime, EOSdatetime,
                          default_start_date, default_end_date,
                          midway_session, cookie_jar, session):
    """
    Generic retrieval function that:
      - If 'mod_name' is in ["DockMaster", ...] and valid SOS/EOS, override date range to (SOS-1, EOS+1).
      - Otherwise, use a "Sunday-based" or default range.
    """
    if mod_name in ["DockMaster", "DockMaster2", "DockFlow"] and (SOSdatetime and EOSdatetime):
        sdt_parsed = parse_datetime(SOSdatetime)
        edt_parsed = parse_datetime(EOSdatetime)
        start_ = (sdt_parsed - timedelta(days=1)).strftime("%Y-%m-%d")
        end_ = (edt_parsed + timedelta(days=1)).strftime("%Y-%m-%d")
        logger.info(f"[DEBUG] Overriding {mod_name} range: {start_} to {end_}")
        return retrieve_data(mod_name, fc, start_, end_, midway_session, cookie_jar)
    else:
        logger.info(f"[DEBUG] Using default Sunday-based range for {mod_name}.")
        return retrieve_data(
            mod_name, fc,
            default_start_date, default_end_date,
            midway_session, cookie_jar,
            session=session
        )


def no_processing(data):
    """No-op function if the retrieved data doesn't require further 'process_data' calls."""
    return data


def retrieve_ALPS(Site, SOSdatetime, EOSdatetime):
    """
    Retrieves ALPS data.
    If SOSdatetime and EOSdatetime are provided, it adjusts the range to
    (SOSdatetime - 1 day) to (EOSdatetime + 1 day) before calling ALPSfunction.
    Otherwise, ALPSfunction's default date logic is used.
    """
    sdt_parsed = parse_datetime(SOSdatetime) if SOSdatetime else None
    edt_parsed = parse_datetime(EOSdatetime) if EOSdatetime else None

    adjusted_start_str = None
    adjusted_end_str = None

    if sdt_parsed and edt_parsed:
        # Adjust the date range: -1 day for start, +1 day for end
        adjusted_start_dt = sdt_parsed - timedelta(days=3)
        adjusted_end_dt = edt_parsed + timedelta(days=3)

        adjusted_start_str = adjusted_start_dt.strftime("%Y-%m-%d")
        adjusted_end_str = adjusted_end_dt.strftime("%Y-%m-%d")

        logger.info(f"ALPS: Adjusting requested date range ({SOSdatetime} to {EOSdatetime}) to cover "
                    f"{adjusted_start_str} to {adjusted_end_str} for FlexSim compatibility.")
        # Pass the *adjusted* date strings to ALPSfunction
        return ALPSfunction(Site, adjusted_start_str, adjusted_end_str)
    else:
        # If specific dates weren't provided or couldn't be parsed,
        # call ALPSfunction without date arguments to trigger its default logic.
        logger.info("ALPS: No valid SOS/EOS provided. Using ALPSfunction default date range.")
        return ALPSfunction(Site, None, None)


def build_data_sources(modules, fc, mp, default_start_date, default_end_date, current_date,
                       SOSdatetime, EOSdatetime, midway_session, cookie_jar, session,
                       parsed_sos, ppr_sos_str, ppr_eos_str, Site, plan_type):
    """
    Builds the list (or dict) of data sources that OneFlow concurrency will iterate over.
    Each entry includes:
      1) A condition to check if we should run this module.
      2) A retrieval function that does the raw data fetch.
      3) A processing function for post-processing.
    """
    DATA_SOURCES = [
        {
            "name": "DockMaster",
            "condition": lambda: "DockMaster" in modules,
            "retrieve_func": lambda: retrieve_with_default(
                "DockMaster", fc, SOSdatetime, EOSdatetime,
                default_start_date, default_end_date,
                midway_session, cookie_jar, session
            ),
            "process_func": lambda raw: process_data("DockMaster", raw),
        },
        {
            "name": "DockMaster2",
            "condition": lambda: "DockMaster2" in modules,
            "retrieve_func": lambda: retrieve_with_default(
                "DockMaster2", fc, SOSdatetime, EOSdatetime,
                default_start_date, default_end_date,
                midway_session, cookie_jar, session
            ),
            "process_func": lambda raw: process_data("DockMaster2", raw),
        },
        {
            "name": "DockFlow",
            "condition": lambda: "DockFlow" in modules,
            "retrieve_func": lambda: retrieve_with_default(
                "DockFlow", fc, SOSdatetime, EOSdatetime,
                default_start_date, default_end_date,
                midway_session, cookie_jar, session
            ),
            "process_func": lambda raw: process_data("DockFlow", raw),
        },
        {
            "name": "Galaxy",
            "condition": lambda: "Galaxy" in modules,
            "retrieve_func": lambda: retrieve_data(
                "Galaxy", fc,
                default_start_date, default_end_date,
                midway_session, cookie_jar, session=session
            ),
            "process_func": lambda raw: process_data("Galaxy", raw),
        },
        {
            "name": "Galaxy2",
            "condition": lambda: "Galaxy2" in modules,
            "retrieve_func": lambda: retrieve_data(
                "Galaxy2", fc,
                default_start_date, default_end_date,
                midway_session, cookie_jar, session=session
            ),
            "process_func": lambda raw: process_data("Galaxy2", raw),
        },
        {
            "name": "ICQA",
            "condition": lambda: "ICQA" in modules,
            "retrieve_func": lambda: retrieve_data(
                "ICQA", fc,
                current_date, default_end_date,
                midway_session, cookie_jar
            ),
            "process_func": lambda raw: process_data("ICQA", raw),
        },
        {
            "name": "F2P",
            "condition": lambda: "F2P" in modules,
            "retrieve_func": lambda: retrieve_data(
                "F2P", fc,
                default_start_date, default_end_date,
                midway_session, cookie_jar, session=session,
                mp=mp
            ),
            "process_func": lambda raw: process_data("F2P", raw),
        },
        {
            "name": "kNekro",
            "condition": lambda: "kNekro" in modules or "necronomicon" in modules,
            "retrieve_func": lambda: retrieve_data(
                "kNekro", fc,
                current_date, default_end_date,
                midway_session, cookie_jar, session=session
            ),
            "process_func": lambda raw: process_data("kNekro", raw),
        },
        {
            "name": "QuipCSV",
            "condition": lambda: "QuipCSV" in modules,
            "retrieve_func": lambda: retrieve_data(
                "QuipCSV", fc,
                default_start_date, default_end_date,
                midway_session, cookie_jar, session=session
            ),
            "process_func": lambda raw: process_data("QuipCSV", raw)
        },
        {
            "name": "PPR",
            "condition": lambda: "PPR" in modules and plan_type == 'Prior-Day',
            "retrieve_func": lambda: PPRfunction(Site, ppr_sos_str, ppr_eos_str),
            "process_func": no_processing,
        },
        {
            "name": "PPR_Q",
            "condition": lambda: "PPR_Q" in modules,
            "retrieve_func": lambda: PPR_Q_function(Site, SOSdatetime, EOSdatetime),
            "process_func": no_processing,
        },
        {
            "name": "ALPS",
            "condition": lambda: "ALPS" in modules,
            "retrieve_func": lambda: retrieve_ALPS(Site, SOSdatetime, EOSdatetime),
            "process_func": no_processing,
        },
        {
            "name": "ALPS_RC_Sort",
            "condition": lambda: "ALPS_RC_Sort" in modules or "alps_hours" in modules,
            "retrieve_func": lambda: retrieve_data(
                "ALPS_RC_Sort", Site,
                parsed_sos, None, None, None, session
            ),
            "process_func": lambda raw: process_data("ALPS_RC_Sort", raw)
        },
        {
            "name": "ALPSRoster",
            "condition": lambda: "ALPSRoster" in modules,
            "retrieve_func": lambda: ALPSRosterFunction(
                Site,
                midway_session,
                cookie_jar,
                session
            ),
            "process_func": no_processing,
        },
        {
        "name": "SSP",
        "condition": lambda: "SSP" in modules,
        "retrieve_func": lambda: retrieve_data(
            "SSP", 
            fc, 
            default_start_date,   # SSP doesn't need SOS/EOS override; using defaults is sufficient.
            default_end_date, 
            midway_session, 
            cookie_jar, 
            session=session
            ),
            "process_func": lambda raw: process_data("SSP", raw),
        },

        { # <--- ADD NEW SSPOT ENTRY ---
        "name": "SSPOT", # New module for Shift Schedule
        "condition": lambda: "SSPOT" in modules,
        "retrieve_func": lambda: retrieve_data(
            "SSPOT",
            fc, # Pass FC for filtering
            None, # Start date ignored by pull_sspot_data
            None, # End date ignored by pull_sspot_data
            None, # Midway session ignored
            None, # Cookie jar ignored
            session=None # Session ignored
            ),
            "process_func": lambda raw: process_data("SSPOT", raw),
        }, # <--- END NEW SSPOT ENTRY ---

        { # <--- ADD NEW SCACs ENTRY ---
        "name": "SCACs", # New module for SCACs Mapping
        "condition": lambda: "SCACs" in modules,
        "retrieve_func": lambda: retrieve_data(
            "SCACs",
            fc, # Pass FC for filtering
            None, # Start date ignored by pull_scacs_mapping_data
            None, # End date ignored by pull_scacs_mapping_data
            None, # Midway session ignored
            None, # Cookie jar ignored
            session=None # Session ignored
            ),
            "process_func": lambda raw: process_data("SCACs", raw),
        }, # <--- END NEW SCACs ENTRY ---

        {
            "name": "RODEO",
            "condition": lambda: "RODEO" in modules,
            "retrieve_func": lambda: RODEOfunction(Site),
            "process_func": no_processing,
        },
        {
            "name": "YMS",
            "condition": lambda: "YMS" in modules,
            "retrieve_func": lambda: YMSfunction(Site),
            "process_func": no_processing,
        },
        {
            "name": "FMC",
            "condition": lambda: "FMC" in modules,
            "retrieve_func": lambda: FMCfunction(Site),
            "process_func": no_processing,
        },
        {
            "name": "QuipCSV",
            "condition": lambda: "QuipCSV" in modules,
            "retrieve_func": lambda: retrieve_data(
                "QuipCSV", fc,
                default_start_date, default_end_date,
                midway_session, cookie_jar, session=session
            ),
            "process_func": lambda raw: process_data("QuipCSV", raw)
        },
         { # <--- ADD NEW VIP ENTRY ---
        "name": "VIP", # New module for VIP data
        "condition": lambda: "VIP" in modules,
        "retrieve_func": lambda: retrieve_data(
            "VIP",
            fc, # Pass FC for filtering
            None, # Start date ignored
            None, # End date ignored
            midway_session,
            cookie_jar
            ),
            "process_func": lambda raw: process_data("VIP", raw),
        },
        {
        "name": "IBBT", 
        "condition": lambda: "IBBT" in modules,
        "retrieve_func": lambda: retrieve_data(
            "IBBT",
            fc, # Pass FC for the specific IBBT file
            None, # Start date not needed
            None, # End date not needed
            midway_session,
            cookie_jar
            ),
            "process_func": lambda raw: process_data("IBBT", raw),
        }, 
    ]
    return DATA_SOURCES
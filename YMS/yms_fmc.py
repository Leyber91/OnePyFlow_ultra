# yms_fmc.py

import logging
import pandas as pd

logger = logging.getLogger(__name__)

def load_fmc_data(site: str) -> pd.DataFrame:
    try:
        from FMC import FMCfunction  # Adjust module name/path as needed
        fmc_json = FMCfunction(site)
        if isinstance(fmc_json, pd.DataFrame):
            if fmc_json.empty:
                return pd.DataFrame()
            return fmc_json
        return pd.DataFrame(fmc_json)
    except Exception as exc:
        logger.error(f"FMCfunction error for '{site}': {exc}", exc_info=True)
        return pd.DataFrame()

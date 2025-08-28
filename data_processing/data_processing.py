import logging
import pandas as pd

from data_processing.process_dock_master_data import process_dock_master_data
from data_processing.process_dock_master2_data import process_dock_master2_data
from data_processing.process_galaxy_data import process_galaxy_data
from data_processing.process_galaxy2_data import process_galaxy2_data
from data_processing.process_icqa_data import process_icqa_data
from data_processing.process_dockflow_data import process_dockflow_data
from data_processing.process_f2p_data import process_f2p_data
from data_processing.process_necronomicon_data import process_necronomicon_data
from data_processing.process_ssp_data import process_ssp_data
from data_processing.process_quip_csv_data import process_quip_csv_data
from data_processing.process_rc_sort_data import process_rc_sort_data
from data_processing.process_carrier_matrix_data import process_carrier_matrix_data 
from data_processing.process_sspot_data import process_sspot_data
from data_processing.process_scacs_mapping_data import process_scacs_mapping_data
from data_processing.process_spark_snapshot_data import process_spark_snapshot_data
from data_processing.process_vip_data import process_vip_data
from data_processing.process_ibbt_data import process_ibbt_data  # Add IBBT import

logger = logging.getLogger(__name__)

def process_data(func_name, raw_data, start_datetime=None, end_datetime=None):
    """
    Processes data based on the function name. 
    Optionally filters if start_datetime/end_datetime are provided (for DockMaster & DockMaster2).
    """
    if func_name == 'DockMaster':
        return process_dock_master_data(raw_data, start_datetime, end_datetime)
    elif func_name == 'DockMaster2':
        return process_dock_master2_data(raw_data, start_datetime, end_datetime)
    elif func_name == 'Galaxy':
        return process_galaxy_data(raw_data)
    elif func_name == 'Galaxy2':
        return process_galaxy2_data(raw_data)
    elif func_name == 'ICQA':
        return process_icqa_data(raw_data)
    elif func_name == 'DockFlow':
        return process_dockflow_data(raw_data)
    elif func_name == 'F2P':
        df_f2p = raw_data
        return process_f2p_data(df_f2p)
    elif func_name == 'kNekro':
        df = raw_data['df']
        fc_name = raw_data['fc_name']
        return process_necronomicon_data(df, fc_name)
    elif func_name == 'SSP':
        return process_ssp_data(raw_data)
    elif func_name == 'SSPOT':
        return process_sspot_data(raw_data)
    elif func_name == 'SCACs':
        return process_scacs_mapping_data(raw_data)
    elif func_name == 'SPARK':
        return process_spark_snapshot_data(raw_data)
    elif func_name == 'ALPS_RC_Sort':
        return process_rc_sort_data(raw_data)
    elif func_name == 'QuipCSV':
        return process_quip_csv_data(raw_data)
    elif func_name == 'CarrierMatrix':
        return process_carrier_matrix_data(raw_data)
    elif func_name == 'VIP':
        return process_vip_data(raw_data)
    elif func_name == 'IBBT':  # Add IBBT condition
        return process_ibbt_data(raw_data)
    else:
        logger.error(f"No data processing function defined for {func_name}")
        raise ValueError(f"No data processing function defined for {func_name}")
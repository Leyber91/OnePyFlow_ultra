# utils/replace_nan_with_string.py

import logging
import numpy as np

logger = logging.getLogger(__name__)

def replace_nan_with_string(data_list):
    """
    Replace NaN values in a list of dictionaries with the string 'NaN'.

    Parameters:
    - data_list (list): List of dictionaries containing the data.

    Returns:
    - list: Updated list with NaN values replaced.
    """
    for item in data_list:
        for key, value in item.items():
            if isinstance(value, float) and np.isnan(value):
                item[key] = 'NaN'
    return data_list

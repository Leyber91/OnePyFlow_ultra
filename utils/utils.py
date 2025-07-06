# utils.py

import logging
import urllib3

# Configure logging for utils module
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Log to stderr
    ]
)

# Disable SSL warnings (Not recommended for production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import functions from the utils folder
from utils.check_for_tokens import check_for_tokens
from utils.parse_json_response import parse_json_response
from utils.send_http_request import send_http_request
from utils.get_value_or_default import get_value_or_default
from utils.calculate_percentages import calculate_percentages
from utils.iso_week_number import iso_week_number
from utils.get_fiscal_week import get_fiscal_week
from utils.get_csrf_token import get_csrf_token
from utils.prepare_data_payload import prepare_data_payload
from utils.web_scrape_delimited_to_dataframe import web_scrape_delimited_to_dataframe
from utils.download_and_extract_data import download_and_extract_data
from utils.add_calculations_to_galaxy import add_calculations_to_galaxy
from utils.add_calculations_to_galaxy2 import add_calculations_to_galaxy2
from utils.make_request import make_request
from utils.replace_nan_with_string import replace_nan_with_string
from utils.extract_calculations import extract_calculations
from utils.send_graphql_request import send_graphql_request
from utils.authenticate_with_dockflow import authenticate_with_dockflow
from utils.get_graphql_endpoint import get_graphql_endpoint
from utils.process_load_fullness import process_load_fullness
from utils.process_trailer_container_count import process_trailer_container_count


__all__ = [
    'check_for_tokens',
    'parse_json_response',
    'send_http_request',
    'get_value_or_default',
    'calculate_percentages',
    'iso_week_number',
    'get_csrf_token',
    'prepare_data_payload',
    'web_scrape_delimited_to_dataframe',
    'download_and_extract_data',
    'add_calculations_to_galaxy',
    'add_calculations_to_galaxy2',
    'make_request',
    'replace_nan_with_string',
    'extract_calculations',
    'get_fiscal_week',
    'send_graphql_request',
    'authenticate_with_dockflow',
    'get_graphql_endpoint',
    'process_load_fullness',
    'process_trailer_container_count'
]

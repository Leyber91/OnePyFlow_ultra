
import re
import logging
from utils.utils import send_http_request, parse_json_response

# Configure logging
logger = logging.getLogger(__name__)


def pull_galaxy(session, fc, start_date):
    """
    Pulls data for the 'Galaxy' function.
    """
    try:
        # Construct URL
        report_date_str = start_date.strftime("%Y-%m-%d")
        url = f"https://galaxybi-eu.aka.corp.amazon.com/api/metadata/pageUrl?pageName=FlowPathPercentages&site={fc}&reportDate={report_date_str}"
        logger.debug(f"Constructed URL for Galaxy: {url}")

        # Send GET request
        response = send_http_request(session, url)

        # Parse JSON response
        json_data = parse_json_response(response.text)

        # Handle potential redirects
        partes = response.text.split('"')
        if len(partes) < 4:
            logger.error("Unexpected response format when retrieving redirect URL for Galaxy.")
            raise ValueError("Unexpected response format for Galaxy redirect.")

        redirect_url = partes[3].strip()
        ## logger.info(f"Redirect URL for Galaxy: {redirect_url}")

        if not re.match(r'^https?://', redirect_url):
            logger.error(f"Invalid redirect URL: {redirect_url}")
            raise ValueError("Invalid redirect URL for Galaxy.")

        # Send GET request to redirect URL
        final_response = send_http_request(session, redirect_url)
        json_data = parse_json_response(final_response.text)

        logger.info("Galaxy data retrieved successfully.")
        return json_data
    except Exception as e:
        logger.error(f"Error pulling Galaxy data: {e}")
        return None
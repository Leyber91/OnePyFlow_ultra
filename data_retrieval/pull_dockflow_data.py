import logging

from utils.utils import (
    authenticate_with_dockflow,
    get_graphql_endpoint,
    send_graphql_request,
)



# Configure logging
logger = logging.getLogger(__name__)


def pull_dockflow_data(fc, midway_session, cookie_jar):
    """
    Retrieves DockFlow data for the given FC.
    """
    site_name = fc
    try:
        # Authenticate with DockFlow
        id_token, refresh_token = authenticate_with_dockflow(midway_session, cookie_jar)
        
        # Get GraphQL endpoint
        graphql_endpoint = get_graphql_endpoint(midway_session)
        
        # Send GraphQL request
        data = send_graphql_request(graphql_endpoint, id_token, site_name)
        
        if data:
            logger.info("DockFlow data retrieved successfully.")
            return data
        else:
            logger.error("No data retrieved from DockFlow.")
            return None
    except Exception as e:
        logger.error(f"Error retrieving DockFlow data: {e}")
        return None
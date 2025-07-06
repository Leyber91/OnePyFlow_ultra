import requests
import logging


# Configure logging
logger = logging.getLogger(__name__)


def pull_dock_master_2(fc, midway_session, cookie_jar):
    """
    Retrieves data from DockMaster for appointments with status 'ARRIVED'.
    """
    url = "https://fc-inbound-dock-execution-service-eu-eug1-dub.dub.proxy.amazon.com/appointment/bySearchParams"
    params = {
        "warehouseId": fc,
        "clientId": "dockmaster",
        "searchResultLevel": "FULL",
        "searchCriteriaName": "STATUS",
        "searchCriteriaValue": "ARRIVED"
    }

    try:
        response = requests.get(url, params=params, cookies=cookie_jar, verify=False)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Data retrieved from DockMaster2 for FC: {fc}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving data from DockMaster2: {e}")
        return None
import logging
import requests
import urllib.parse
from utils.check_for_tokens import check_for_tokens

logger = logging.getLogger(__name__)

def authenticate_with_dockflow(cookie_string, cookie_jar):
    """
    Attempts to authenticate with DockFlow using Midway cookies
    """
    logger.info("Initiating DockFlow authentication...")
    redirect_uri = "https://prod-eu.dockflow.robotics.a2z.com"
    client_id = "6pbe17dfbrvhnjdi5m26h6qijp"

    session = requests.Session()
    session.cookies = cookie_jar
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    })

    try:
        cognito_auth_url = (
            f"https://cog-dockflow-eu-west-1-prod-eu.auth.eu-west-1.amazoncognito.com/"
            f"authorize?redirect_uri={urllib.parse.quote(redirect_uri)}"
            f"&response_type=code&client_id={client_id}&state=2Fmanifest.json"
        )

        response = session.get(cognito_auth_url, verify=False, allow_redirects=True)
        logger.info(f"Auth response status: {response.status_code}")

        # Check for tokens in the final response
        tokens = check_for_tokens(session, response)
        if tokens:
            return tokens

        logger.error("Failed to obtain authentication tokens")
        raise Exception("Authentication failed - no tokens received")

    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise
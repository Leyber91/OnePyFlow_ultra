# utils/authenticate.py
import subprocess
import logging
import getpass
from http.cookiejar import MozillaCookieJar
import urllib3
import os
import re
import requests
from requests.adapters import HTTPAdapter, Retry
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Authentication:
    def __init__(self):
        """
        1) Creates a requests.Session.
        2) Immediately calls self.setup_session(), which tries to load existing cookies.
        """
        self.session = requests.Session()
        self.cookie_jar = None
        self.session_cookie = None
        self.amazon_eac_cookie = None
        self.setup_session()
    
    def is_cookie_valid(self):
        """
        Checks if the cookie file contains the required "amazon_enterprise_access" cookie
        AND validates it with a real API call to prevent false positives.
        
        Returns:
            bool: True if the cookie is valid, False otherwise
        """
        try:
            cookie_file_path = self._get_midway_cookie_path()
            
            # First check if the file exists
            if not os.path.exists(cookie_file_path):
                logger.warning(f"[CookieValidation] Cookie file doesn't exist at {cookie_file_path}")
                return False
                
            # Then check if it contains the required cookie
            has_cookie = False
            with open(cookie_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'amazon_enterprise_access' in line:
                        has_cookie = True
                        break
            
            if not has_cookie:
                logger.warning(f"[CookieValidation] Cookie file exists but 'amazon_enterprise_access' not found")
                return False
                
            # CRITICAL FIX: Actually test the cookie with a real API call
            logger.info(f"[CookieValidation] Found amazon_enterprise_access cookie, testing with API call...")
            
            # Load the cookie and test it
            from http.cookiejar import MozillaCookieJar
            import requests
            
            cookie_jar = MozillaCookieJar()
            cookie_jar.load(cookie_file_path, ignore_discard=True, ignore_expires=True)
            
            # Test with a simple API endpoint that requires authentication
            test_url = "https://fclm-portal.amazon.com/fcresearch-na/public/api/sites"  # Site list endpoint
            
            response = requests.get(
                test_url, 
                cookies=cookie_jar, 
                timeout=10,
                verify=False  # Match the main application's SSL settings
            )
            
            if response.status_code == 200:
                logger.info(f"[CookieValidation] [SUCCESS] Cookie validation successful - API test passed")
                return True
            elif response.status_code == 401:
                logger.warning(f"[CookieValidation] ❌ Cookie is expired/invalid - API returned 401")
                return False
            else:
                logger.warning(f"[CookieValidation] [WARNING] Cookie test inconclusive - API returned {response.status_code}")
                # For other status codes, assume cookie might be OK but endpoint has issues
                return True
                
        except Exception as e:
            logger.warning(f"[CookieValidation] Error validating cookie: {e}")
            # If we can't test the cookie due to network issues, assume it might be valid
            # to avoid unnecessary authentication prompts during network outages
            return True

    def refresh_cookie_if_needed(self, max_hours=8):
        """
        Checks the .midway/cookie file. If it doesn't exist, is invalid, or if its
        creation/modification time is older than `max_hours`, run 'mwinit -s -o'.

        Raises an exception if 'mwinit' fails, so the caller knows we have no valid cookie.
        """
        cookie_file_path = self._get_midway_cookie_path()
        run_mwinit = False

        if not os.path.exists(cookie_file_path):
            logger.info(f"No cookie found at {cookie_file_path} => will run mwinit.")
            run_mwinit = True
        elif not self.is_cookie_valid():  # FIXED: Added parentheses and NOT operator
            logger.info(f"Cookie found at {cookie_file_path} BUT seems not correct => will run mwinit.")
            run_mwinit = True
        else:
            try:
                ctime = os.path.getctime(cookie_file_path)
                file_age_hours = (datetime.now() - datetime.fromtimestamp(ctime)).total_seconds() / 3600.0
                remaining_hours = max_hours - file_age_hours
                logger.info(
                    f"[CookieAgeCheck] Cookie file is {file_age_hours:.2f}h old. "
                    f"Threshold={max_hours}h => {remaining_hours:.2f}h remain."
                )
                if file_age_hours < 0:
                    logger.warning(
                        "[CookieAgeCheck] Negative file age? System clock changed? Not refreshing by default."
                    )
                elif file_age_hours > max_hours:
                    logger.info(
                        f"[CookieAgeCheck] Cookie older than {max_hours}h => will run mwinit."
                    )
                    run_mwinit = True
            except OSError as e:
                logger.error(f"[CookieAgeCheck] Could not read file ctime: {e}")
                # Force a refresh anyway
                run_mwinit = True

        if run_mwinit:
            # NEW: Added second try feature with retries=2 instead of 1
            self.force_mwinit_reauth(retries=2)

    def force_mwinit_reauth(self, retries=3):
        """
        Perform 'mwinit -s -o' up to `retries` times.
        With enhanced error messaging for retry attempts and YubiKey checks.
        """
        import time
        for attempt in range(1, retries + 1):
            try:
                # NEW: Enhanced messaging for different attempts
                if attempt == 1:
                    logger.info(
                        f"[mwinit] Initial authentication attempt. "
                        "Please enter your Midway PIN if prompted, then hold your security key for 3-5 seconds."
                    )
                elif attempt == 2:
                    # NEW: Second try messaging
                    logger.info(
                        f"[mwinit] Second attempt. Please carefully re-enter your Midway PIN. "
                        "Ensure your security key is properly inserted and hold it for 3-5 seconds when prompted."
                    )
                else:
                    # For any additional retries
                    logger.info(
                        f"[mwinit] Attempt #{attempt} of {retries}. "
                        "Please try again with your Midway PIN and security key."
                    )
                
                subprocess.run('mwinit -s -o', shell=True, check=True)
                logger.info("[mwinit] Midway cookie refreshed successfully.")
                return
            except subprocess.CalledProcessError as e:
                logger.error(f"[mwinit] Attempt #{attempt} failed: {e}")
                if attempt < retries:
                    time.sleep(3)
                    if attempt == 1:
                        # NEW: Guidance for second attempt
                        logger.warning("[mwinit] First attempt failed. Will try again. Please ensure:")
                        logger.warning("         1. You are entering the correct PIN")
                        logger.warning("         2. Your security key is properly inserted")
                        logger.warning("         3. The security key light is blinking when prompted")
                else:
                    # NEW: YubiKey check message on final failure
                    error_msg = (
                        "All mwinit attempts failed! "
                        "Please verify your PIN/security key. "
                        "If issues persist, please contact PCS to check if your YubiKey "
                        "is working properly, as it may be a source of authentication failures."
                    )
                    logger.error(f"[mwinit] {error_msg}")
                    raise RuntimeError(error_msg) from e

    def _get_midway_cookie_path(self):
        """
        Get the path to the Midway cookie file.
        Try multiple locations, with the following priority:
        1. Environment variable MIDWAY_COOKIE_PATH if set
        2. Default paths on both C: and D: drives
        
        Returns:
            str: Path to the Midway cookie file
        """
        # Check for environment variable first
        if 'MIDWAY_COOKIE_PATH' in os.environ:
            return os.environ['MIDWAY_COOKIE_PATH']
        
        # Get username
        username = getpass.getuser()
        
        # Try multiple locations in order of preference
        potential_paths = [
            f'C:/Users/{username}/.midway/cookie',
            f'D:/Users/{username}/.midway/cookie',
            # Add any other potential locations here
        ]
        
        # Check each path and return the first one that exists
        for path in potential_paths:
            if os.path.exists(path):
                logger.info(f"Found Midway cookie at: {path}")
                return path
        
        # If no cookie file was found, return the C: drive default path
        # so that mwinit will create it there
        logger.info(f"No existing Midway cookie found, using default path: {potential_paths[0]}")
        return potential_paths[0]

    def setup_session(self):
        """
        Configures the requests.Session and tries to load existing cookies.
        """
        try:
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)

            self.session.headers.clear()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            })

            self._load_cookie()  # Attempt to load an existing cookie
            logger.info("Session setup completed successfully.")
        except Exception as e:
            logger.error(f"Failed to set up session: {e}")
            raise

        return self.session

    def _load_cookie(self):
        """
        Loads the .midway/cookie file into self.cookie_jar,
        sets them in the session, turns off SSL verify, etc.
        """
        cookie_file_path = self._get_midway_cookie_path()
        self.cookie_jar = MozillaCookieJar()

        if not os.path.exists(cookie_file_path):
            logger.warning(f"Cookie file doesn't exist at {cookie_file_path} => no Midway login yet.")
            return

        try:
            self.cookie_jar.load(cookie_file_path, ignore_discard=True, ignore_expires=True)
            logger.info(f"Loaded cookies from {cookie_file_path}")
        except Exception as e:
            logger.error(f"Error loading cookie file: {e}")
            return

        # Extract 'session' and 'amazon_enterprise_access'
        with open(cookie_file_path, 'r') as file:
            content = file.read()
            session_match = re.search(r'session\s+(.+)', content)
            amazon_eac_match = re.search(r'amazon_enterprise_access\s+(.+)', content)

            if session_match:
                self.session_cookie = session_match.group(1).strip()
            if amazon_eac_match:
                self.amazon_eac_cookie = amazon_eac_match.group(1).strip()

        if self.session_cookie:
            self.session.cookies.set('session', self.session_cookie, domain='.amazon.com', path='/')
        if self.amazon_eac_cookie:
            self.session.cookies.set('amazon_enterprise_access', self.amazon_eac_cookie, domain='.amazon.com', path='/')

        self.session.verify = False  # Often needed for intranet calls

    def get_midway_session(self):
        """
        Return a (midway_session, cookie_jar) tuple.
        The 'midway_session' might just be an empty string if not used.
        """
        return '', self.cookie_jar

    def get_os_username(self):
        return getpass.getuser()
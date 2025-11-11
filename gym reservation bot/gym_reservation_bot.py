#!/usr/bin/env python3
"""
Gym Reservation Bot
Automatically reserves a gym timeslot at 11:00 AM daily using Selenium.
Designed to run on GCP Linux VM in headless mode.
"""

import os
import sys
import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Optional GCP Secret Manager imports
try:
    from google.cloud import secretmanager
    from google.auth.exceptions import GoogleAuthError
    GCP_SECRETS_AVAILABLE = True
except ImportError:
    GCP_SECRETS_AVAILABLE = False

# Configure logging
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gym_reservation.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class GymReservationBot:
    """Automated gym reservation bot using Selenium."""
    
    def __init__(self, use_gcp_secrets=False):
        """
        Initialize the bot.
        
        Args:
            use_gcp_secrets: If True, use GCP Secret Manager. Otherwise, use environment variables.
        """
        self.use_gcp_secrets = use_gcp_secrets
        self.driver = None
        self.username = None
        self.password = None
        self.reservation_url = None
        
    def get_credentials(self):
        """Retrieve credentials from environment variables or GCP Secret Manager."""
        try:
            if self.use_gcp_secrets:
                if not GCP_SECRETS_AVAILABLE:
                    raise ImportError(
                        "GCP Secret Manager is not available. "
                        "Install it with: pip install google-cloud-secret-manager"
                    )
                logger.info("Retrieving credentials from GCP Secret Manager...")
                client = secretmanager.SecretManagerServiceClient()
                project_id = os.getenv('GCP_PROJECT_ID')
                
                if not project_id:
                    raise ValueError("GCP_PROJECT_ID environment variable is required when using GCP Secret Manager")
                
                # Retrieve secrets
                username_secret = f"projects/{project_id}/secrets/gym-username/versions/latest"
                password_secret = f"projects/{project_id}/secrets/gym-password/versions/latest"
                url_secret = f"projects/{project_id}/secrets/gym-reservation-url/versions/latest"
                
                self.username = client.access_secret_version(request={"name": username_secret}).payload.data.decode('UTF-8')
                self.password = client.access_secret_version(request={"name": password_secret}).payload.data.decode('UTF-8')
                self.reservation_url = client.access_secret_version(request={"name": url_secret}).payload.data.decode('UTF-8')
                
                logger.info("Successfully retrieved credentials from GCP Secret Manager")
            else:
                logger.info("Retrieving credentials from environment variables...")
                self.username = os.getenv('GYM_USERNAME')
                self.password = os.getenv('GYM_PASSWORD')
                self.reservation_url = os.getenv('GYM_RESERVATION_URL')
                
                if not all([self.username, self.password, self.reservation_url]):
                    missing = [k for k, v in {
                        'GYM_USERNAME': self.username,
                        'GYM_PASSWORD': self.password,
                        'GYM_RESERVATION_URL': self.reservation_url
                    }.items() if not v]
                    raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
                
                logger.info("Successfully retrieved credentials from environment variables")
                
        except GoogleAuthError as e:
            logger.error(f"GCP authentication error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving credentials: {e}")
            raise
    
    def setup_driver(self):
        """Setup Chrome WebDriver with headless options."""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User agent to avoid detection
            chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Try to find chromedriver in common locations
            chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
            
            if os.path.exists(chromedriver_path):
                service = Service(chromedriver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Let Selenium manage the driver
                self.driver = webdriver.Chrome(options=chrome_options)
            
            logger.info("Chrome WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {e}")
            raise
    
    def login(self):
        """
        Log in to the gym reservation system.
        
        NOTE: You need to customize the selectors based on your gym's website structure.
        Common patterns:
        - Username field: input[name='username'], input[id='username'], input[type='email']
        - Password field: input[name='password'], input[id='password'], input[type='password']
        - Login button: button[type='submit'], input[type='submit'], button.login-btn
        """
        try:
            logger.info(f"Navigating to reservation URL: {self.reservation_url}")
            self.driver.get(self.reservation_url)
            
            wait = WebDriverWait(self.driver, 20)
            
            # Wait for login page to load
            # CUSTOMIZE THESE SELECTORS FOR YOUR GYM'S WEBSITE
            username_selector = os.getenv('GYM_USERNAME_SELECTOR', "input[name='username']")
            password_selector = os.getenv('GYM_PASSWORD_SELECTOR', "input[name='password']")
            login_button_selector = os.getenv('GYM_LOGIN_BUTTON_SELECTOR', "button[type='submit']")
            
            logger.info("Waiting for login form to load...")
            username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, username_selector)))
            password_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, password_selector)))
            
            logger.info("Filling in login credentials...")
            username_field.clear()
            username_field.send_keys(self.username)
            
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Wait for login button and click
            login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, login_button_selector)))
            login_button.click()
            
            # Wait for navigation after login (adjust timeout and condition as needed)
            # CUSTOMIZE: Wait for an element that appears after successful login
            post_login_selector = os.getenv('GYM_POST_LOGIN_SELECTOR', None)
            if post_login_selector:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, post_login_selector)))
            
            logger.info("Login successful")
            time.sleep(2)  # Brief pause to ensure page loads
            
        except TimeoutException as e:
            logger.error(f"Timeout during login: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise
    
    def check_existing_reservation(self):
        """
        Check if a reservation already exists for today.
        
        NOTE: Customize this method based on how your gym's website displays existing reservations.
        """
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # CUSTOMIZE: Selector for checking existing reservations
            existing_reservation_selector = os.getenv('GYM_EXISTING_RESERVATION_SELECTOR', None)
            
            if existing_reservation_selector:
                try:
                    existing_reservation = self.driver.find_element(By.CSS_SELECTOR, existing_reservation_selector)
                    if existing_reservation and existing_reservation.is_displayed():
                        logger.info("Existing reservation detected. Exiting cleanly.")
                        return True
                except NoSuchElementException:
                    logger.info("No existing reservation found. Proceeding with new reservation.")
                    return False
            else:
                # If no selector is provided, assume no existing reservation
                logger.info("No existing reservation check configured. Proceeding with reservation.")
                return False
                
        except Exception as e:
            logger.warning(f"Error checking for existing reservation: {e}. Proceeding anyway.")
            return False
    
    def make_reservation(self):
        """
        Navigate to the reservation page and make a reservation for 11:00 AM.
        
        NOTE: You need to customize this method based on your gym's website structure.
        Common patterns:
        - Date selection: calendar widget, date picker, or direct date link
        - Time slot selection: buttons, links, or dropdowns for time slots
        - Submit button: button[type='submit'], button.reserve-btn, etc.
        """
        try:
            wait = WebDriverWait(self.driver, 20)
            
            # CUSTOMIZE: Navigate to reservation/booking page
            # This might be clicking a "Book" or "Reserve" link/button
            reservation_page_selector = os.getenv('GYM_RESERVATION_PAGE_SELECTOR', None)
            if reservation_page_selector:
                logger.info("Navigating to reservation page...")
                reservation_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, reservation_page_selector)))
                reservation_link.click()
                time.sleep(2)
            
            # CUSTOMIZE: Select today's date
            # This might involve clicking on a calendar date or selecting from a date picker
            date_selector = os.getenv('GYM_DATE_SELECTOR', None)
            if date_selector:
                logger.info("Selecting date...")
                date_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, date_selector)))
                date_element.click()
                time.sleep(1)
            
            # CUSTOMIZE: Select 11:00 AM time slot
            # This is critical - you need to find the selector for the 11:00 AM slot
            time_slot_selector = os.getenv('GYM_TIME_SLOT_SELECTOR', None)
            if time_slot_selector:
                logger.info("Selecting 11:00 AM time slot...")
                time_slot = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, time_slot_selector)))
                time_slot.click()
                time.sleep(1)
            else:
                # Fallback: try to find any element containing "11:00" or "11:00 AM"
                logger.info("Attempting to find 11:00 AM time slot...")
                try:
                    # Try XPath to find element containing "11:00"
                    time_slot = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//*[contains(text(), '11:00') or contains(text(), '11:00 AM')]")
                    ))
                    time_slot.click()
                    time.sleep(1)
                except TimeoutException:
                    logger.error("Could not find 11:00 AM time slot. Please configure GYM_TIME_SLOT_SELECTOR.")
                    raise
            
            # CUSTOMIZE: Submit the reservation
            submit_selector = os.getenv('GYM_SUBMIT_SELECTOR', "button[type='submit']")
            logger.info("Submitting reservation...")
            submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, submit_selector)))
            submit_button.click()
            
            # Wait for confirmation
            time.sleep(3)
            
        except TimeoutException as e:
            logger.error(f"Timeout during reservation process: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during reservation: {e}")
            raise
    
    def confirm_reservation(self):
        """
        Confirm that the reservation was successful.
        
        NOTE: Customize this method to check for success messages on your gym's website.
        """
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # CUSTOMIZE: Selector for success confirmation message
            success_selector = os.getenv('GYM_SUCCESS_SELECTOR', None)
            
            if success_selector:
                try:
                    success_message = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, success_selector)))
                    if success_message and success_message.is_displayed():
                        logger.info(f"Reservation confirmed! Message: {success_message.text}")
                        return True
                except TimeoutException:
                    logger.warning("Success message not found, but reservation may have been submitted.")
                    return False
            else:
                # Check page source for common success keywords
                page_source = self.driver.page_source.lower()
                success_keywords = ['success', 'confirmed', 'reserved', 'booked']
                if any(keyword in page_source for keyword in success_keywords):
                    logger.info("Reservation appears to be successful (found success keywords in page).")
                    return True
                else:
                    logger.warning("Could not confirm reservation success. Please configure GYM_SUCCESS_SELECTOR.")
                    return False
                    
        except Exception as e:
            logger.warning(f"Error confirming reservation: {e}")
            return False
    
    def run(self):
        """Execute the complete reservation process."""
        try:
            logger.info("=" * 60)
            logger.info(f"Starting gym reservation bot at {datetime.now()}")
            logger.info("=" * 60)
            
            # Get credentials
            self.get_credentials()
            
            # Setup driver
            self.setup_driver()
            
            try:
                # Login
                self.login()
                
                # Check for existing reservation
                if self.check_existing_reservation():
                    logger.info("Reservation already exists. Exiting.")
                    return True
                
                # Make reservation
                self.make_reservation()
                
                # Confirm reservation
                success = self.confirm_reservation()
                
                if success:
                    logger.info("=" * 60)
                    logger.info("RESERVATION SUCCESSFUL!")
                    logger.info("=" * 60)
                    return True
                else:
                    logger.warning("Reservation may have been submitted, but confirmation was unclear.")
                    return False
                    
            finally:
                # Always close the driver
                if self.driver:
                    self.driver.quit()
                    logger.info("WebDriver closed")
                    
        except Exception as e:
            logger.error(f"Fatal error in reservation bot: {e}", exc_info=True)
            if self.driver:
                self.driver.quit()
            return False


def main():
    """Main entry point."""
    # Check if GCP Secret Manager should be used
    use_gcp_secrets = os.getenv('USE_GCP_SECRETS', 'false').lower() == 'true'
    
    bot = GymReservationBot(use_gcp_secrets=use_gcp_secrets)
    success = bot.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


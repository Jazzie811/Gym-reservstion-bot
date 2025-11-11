#!/usr/bin/env python3
"""
Test script to verify the bot setup without making an actual reservation.
Useful for testing selectors and configuration.
"""

import os
import sys
from gym_reservation_bot import GymReservationBot

def test_setup():
    """Test the bot setup without making a reservation."""
    print("=" * 60)
    print("Gym Reservation Bot - Test Mode")
    print("=" * 60)
    print()
    
    # Check environment variables
    print("Checking environment variables...")
    use_gcp_secrets = os.getenv('USE_GCP_SECRETS', 'false').lower() == 'true'
    
    if use_gcp_secrets:
        print("✓ Using GCP Secret Manager")
        project_id = os.getenv('GCP_PROJECT_ID')
        if not project_id:
            print("✗ ERROR: GCP_PROJECT_ID not set")
            return False
        print(f"✓ GCP Project ID: {project_id}")
    else:
        print("✓ Using environment variables")
        required_vars = ['GYM_USERNAME', 'GYM_PASSWORD', 'GYM_RESERVATION_URL']
        missing = [v for v in required_vars if not os.getenv(v)]
        if missing:
            print(f"✗ ERROR: Missing environment variables: {', '.join(missing)}")
            return False
        print("✓ All required environment variables are set")
    
    # Check ChromeDriver
    print("\nChecking ChromeDriver...")
    chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
    if os.path.exists(chromedriver_path):
        print(f"✓ ChromeDriver found at: {chromedriver_path}")
    else:
        print(f"⚠ ChromeDriver not found at: {chromedriver_path}")
        print("  Will attempt to use system ChromeDriver")
    
    # Check Python packages
    print("\nChecking Python packages...")
    try:
        import selenium
        print(f"✓ Selenium version: {selenium.__version__}")
    except ImportError:
        print("✗ ERROR: Selenium not installed. Run: pip3 install -r requirements.txt")
        return False
    
    if use_gcp_secrets:
        try:
            from google.cloud import secretmanager
            print("✓ google-cloud-secret-manager installed")
        except ImportError:
            print("✗ ERROR: google-cloud-secret-manager not installed. Run: pip3 install -r requirements.txt")
            return False
    
    # Test credential retrieval (without actually using them)
    print("\nTesting credential retrieval...")
    try:
        bot = GymReservationBot(use_gcp_secrets=use_gcp_secrets)
        bot.get_credentials()
        print("✓ Credentials retrieved successfully")
        print(f"  Username: {bot.username[:3]}*** (hidden)")
        print(f"  URL: {bot.reservation_url}")
    except Exception as e:
        print(f"✗ ERROR retrieving credentials: {e}")
        return False
    
    # Test WebDriver setup (optional - can be skipped)
    print("\nTesting WebDriver setup...")
    test_driver = input("Do you want to test WebDriver initialization? (y/n): ").strip().lower()
    if test_driver == 'y':
        try:
            bot.setup_driver()
            print("✓ WebDriver initialized successfully")
            bot.driver.quit()
        except Exception as e:
            print(f"✗ ERROR initializing WebDriver: {e}")
            return False
    else:
        print("  Skipping WebDriver test")
    
    print("\n" + "=" * 60)
    print("All tests passed! Bot is ready to use.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_setup()
    sys.exit(0 if success else 1)


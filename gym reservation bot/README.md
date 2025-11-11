# Gym Reservation Bot

A fully automated Python bot that reserves a gym timeslot at 11:00 AM daily using Selenium WebDriver. Designed to run on Google Cloud Platform (GCP) Linux VMs in headless mode.

## Features

- ✅ Automated gym reservation at 11:00 AM daily
- ✅ Secure credential management (GCP Secret Manager or environment variables)
- ✅ Headless Chrome browser for cloud execution
- ✅ WebDriverWait for reliable element detection (no fixed sleeps)
- ✅ Existing reservation detection and clean exit
- ✅ Comprehensive logging to file and console
- ✅ Cron job scheduling support
- ✅ Error handling and retry logic

## Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account (for VM hosting)
- Chrome browser and ChromeDriver
- Access to the gym reservation website

## Project Structure

```
gym-reservation-bot/
├── gym_reservation_bot.py    # Main bot script
├── requirements.txt           # Python dependencies
├── gcp_secrets_setup.py      # Helper script for GCP Secret Manager setup
├── env.example               # Example environment variables
├── README.md                # This file
└── gym_reservation.log       # Log file (created automatically)
```

## Setup Instructions

### Step 1: Set Up GCP Virtual Machine

1. **Create a VM Instance:**
   ```bash
   # Using gcloud CLI
   gcloud compute instances create gym-bot-vm \
     --zone=us-central1-a \
     --machine-type=e2-micro \
     --image-family=ubuntu-2204-lts \
     --image-project=ubuntu-os-cloud \
     --boot-disk-size=10GB
   ```

2. **SSH into the VM:**
   ```bash
   gcloud compute ssh gym-bot-vm --zone=us-central1-a
   ```

3. **Update system packages:**
   ```bash
   sudo apt-get update
   sudo apt-get upgrade -y
   ```

### Step 2: Install Chrome and ChromeDriver

1. **Install Chrome:**
   ```bash
   # Install dependencies
   sudo apt-get install -y \
     wget \
     gnupg \
     unzip \
     curl \
     ca-certificates \
     fonts-liberation \
     libasound2 \
     libatk-bridge2.0-0 \
     libatk1.0-0 \
     libc6 \
     libcairo2 \
     libcups2 \
     libdbus-1-3 \
     libexpat1 \
     libfontconfig1 \
     libgbm1 \
     libgcc1 \
     libglib2.0-0 \
     libgtk-3-0 \
     libnspr4 \
     libnss3 \
     libpango-1.0-0 \
     libpangocairo-1.0-0 \
     libstdc++6 \
     libx11-6 \
     libx11-xcb1 \
     libxcb1 \
     libxcomposite1 \
     libxcursor1 \
     libxdamage1 \
     libxext6 \
     libxfixes3 \
     libxi6 \
     libxrandr2 \
     libxrender1 \
     libxss1 \
     libxtst6 \
     lsb-release \
     xdg-utils

   # Add Google Chrome repository
   wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
   echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list

   # Install Google Chrome
   sudo apt-get update
   sudo apt-get install -y google-chrome-stable
   ```

2. **Install ChromeDriver:**
   ```bash
   # Get Chrome version
   CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)

   # Download matching ChromeDriver
   CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
   wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"

   # Extract and install
   unzip /tmp/chromedriver.zip -d /tmp
   sudo mv /tmp/chromedriver /usr/local/bin/chromedriver
   sudo chmod +x /usr/local/bin/chromedriver

   # Verify installation
   chromedriver --version
   ```

   **Alternative: Use ChromeDriver Manager (automatic version matching):**
   ```bash
   # Install chromedriver-autoinstaller
   pip3 install chromedriver-autoinstaller
   ```

### Step 3: Install Python and Dependencies

1. **Install Python 3 and pip:**
   ```bash
   sudo apt-get install -y python3 python3-pip
   ```

2. **Clone or upload the bot files to the VM:**
   ```bash
   # Create project directory
   mkdir -p ~/gym-reservation-bot
   cd ~/gym-reservation-bot

   # Upload files using SCP (from your local machine)
   # scp gym_reservation_bot.py requirements.txt gcp_secrets_setup.py user@gym-bot-vm:~/gym-reservation-bot/
   ```

3. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

### Step 4: Configure Credentials

You have two options for storing credentials securely:

#### Option A: Environment Variables (Recommended for simplicity)

1. **Create a script to set environment variables:**
   ```bash
   nano ~/gym-reservation-bot/set_env.sh
   ```

2. **Add the following content:**
   ```bash
   #!/bin/bash
   export GYM_USERNAME="your_username_here"
   export GYM_PASSWORD="your_password_here"
   export GYM_RESERVATION_URL="https://your-gym-reservation-url.com"
   
   # Optional: Customize selectors for your gym's website
   # export GYM_USERNAME_SELECTOR="input[name='username']"
   # export GYM_PASSWORD_SELECTOR="input[name='password']"
   # export GYM_LOGIN_BUTTON_SELECTOR="button[type='submit']"
   # export GYM_TIME_SLOT_SELECTOR="button[data-time='11:00']"
   # ... (see env.example for all options)
   ```

3. **Make it executable:**
   ```bash
   chmod +x ~/gym-reservation-bot/set_env.sh
   ```

4. **Source it before running the bot:**
   ```bash
   source ~/gym-reservation-bot/set_env.sh
   ```

#### Option B: GCP Secret Manager (Recommended for production)

1. **Enable Secret Manager API:**
   ```bash
   gcloud services enable secretmanager.googleapis.com
   ```

2. **Set up authentication:**
   ```bash
   gcloud auth application-default login
   ```

3. **Grant Secret Manager access to the VM:**
   ```bash
   # Get the VM's service account
   VM_SERVICE_ACCOUNT=$(gcloud compute instances describe gym-bot-vm \
     --zone=us-central1-a \
     --format="value(serviceAccounts[0].email)")

   # Grant Secret Manager Secret Accessor role
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:${VM_SERVICE_ACCOUNT}" \
     --role="roles/secretmanager.secretAccessor"
   ```

4. **Run the setup script to store secrets:**
   ```bash
   cd ~/gym-reservation-bot
   export GCP_PROJECT_ID="your-gcp-project-id"
   python3 gcp_secrets_setup.py
   ```

5. **Set environment variable to use GCP secrets:**
   ```bash
   export USE_GCP_SECRETS=true
   export GCP_PROJECT_ID="your-gcp-project-id"
   ```

### Step 5: Customize Website Selectors

The bot needs to know how to interact with your gym's website. You need to customize the CSS selectors:

1. **Inspect your gym's website** using browser developer tools (F12)
2. **Identify the following elements:**
   - Username input field
   - Password input field
   - Login button
   - Date selector (for today's date)
   - 11:00 AM time slot button/link
   - Submit/Confirm reservation button
   - Success confirmation message
   - Existing reservation indicator (optional)

3. **Set environment variables with your selectors:**
   ```bash
   export GYM_USERNAME_SELECTOR="input#username"
   export GYM_PASSWORD_SELECTOR="input#password"
   export GYM_LOGIN_BUTTON_SELECTOR="button.login-btn"
   export GYM_TIME_SLOT_SELECTOR="button[data-time='11:00 AM']"
   # ... etc.
   ```

   Or add them to your `set_env.sh` script.

### Step 6: Test the Bot Manually

Before setting up the cron job, test the bot manually:

```bash
cd ~/gym-reservation-bot
source set_env.sh  # If using environment variables
python3 gym_reservation_bot.py
```

Check the log file for any errors:
```bash
tail -f gym_reservation.log
```

### Step 7: Set Up Cron Job for Daily Execution

1. **Open crontab:**
   ```bash
   crontab -e
   ```

2. **Add the following line to run at 11:00 AM daily:**
   ```cron
   # Gym reservation bot - runs daily at 11:00 AM
   0 11 * * * cd /home/YOUR_USERNAME/gym-reservation-bot && source set_env.sh && /usr/bin/python3 gym_reservation_bot.py >> /home/YOUR_USERNAME/gym-reservation-bot/cron.log 2>&1
   ```

   **For GCP Secret Manager:**
   ```cron
   # Gym reservation bot - runs daily at 11:00 AM (using GCP secrets)
   0 11 * * * cd /home/YOUR_USERNAME/gym-reservation-bot && export USE_GCP_SECRETS=true && export GCP_PROJECT_ID="your-project-id" && /usr/bin/python3 gym_reservation_bot.py >> /home/YOUR_USERNAME/gym-reservation-bot/cron.log 2>&1
   ```

   **Note:** Replace `YOUR_USERNAME` with your actual username on the VM.

3. **Verify cron job is set:**
   ```bash
   crontab -l
   ```

4. **Test cron job (optional - run at current time + 1 minute):**
   ```bash
   # Get current time
   date
   # Add a test cron job for 1 minute from now
   # Then remove it after testing
   ```

## Configuration Options

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GYM_USERNAME` | Yes* | Gym website username |
| `GYM_PASSWORD` | Yes* | Gym website password |
| `GYM_RESERVATION_URL` | Yes* | URL of the gym reservation page |
| `USE_GCP_SECRETS` | No | Set to `true` to use GCP Secret Manager |
| `GCP_PROJECT_ID` | Yes (if using secrets) | Your GCP project ID |
| `CHROMEDRIVER_PATH` | No | Path to ChromeDriver (default: `/usr/local/bin/chromedriver`) |
| `GYM_USERNAME_SELECTOR` | No | CSS selector for username field |
| `GYM_PASSWORD_SELECTOR` | No | CSS selector for password field |
| `GYM_LOGIN_BUTTON_SELECTOR` | No | CSS selector for login button |
| `GYM_POST_LOGIN_SELECTOR` | No | CSS selector for element that appears after login |
| `GYM_RESERVATION_PAGE_SELECTOR` | No | CSS selector to navigate to reservation page |
| `GYM_DATE_SELECTOR` | No | CSS selector for date selection |
| `GYM_TIME_SLOT_SELECTOR` | No | CSS selector for 11:00 AM time slot |
| `GYM_SUBMIT_SELECTOR` | No | CSS selector for submit button |
| `GYM_SUCCESS_SELECTOR` | No | CSS selector for success message |
| `GYM_EXISTING_RESERVATION_SELECTOR` | No | CSS selector to detect existing reservations |

*Required unless using GCP Secret Manager

## Logging

The bot logs all activities to:
- **File:** `gym_reservation.log` (in the script directory)
- **Console:** Standard output (when run manually)

Log entries include:
- Timestamps
- Login attempts
- Reservation status
- Errors and warnings
- Success confirmations

## Troubleshooting

### ChromeDriver Version Mismatch

If you get a ChromeDriver version error:
```bash
# Check Chrome version
google-chrome --version

# Download matching ChromeDriver
# See Step 2 in setup instructions
```

### Element Not Found Errors

1. **Inspect the website** to find correct CSS selectors
2. **Set environment variables** with the correct selectors
3. **Test selectors** using browser console:
   ```javascript
   document.querySelector('your-selector-here')
   ```

### Authentication Errors (GCP Secret Manager)

1. **Verify authentication:**
   ```bash
   gcloud auth application-default login
   ```

2. **Check IAM permissions:**
   ```bash
   gcloud projects get-iam-policy YOUR_PROJECT_ID
   ```

### Cron Job Not Running

1. **Check cron service:**
   ```bash
   sudo systemctl status cron
   ```

2. **Check cron logs:**
   ```bash
   grep CRON /var/log/syslog
   ```

3. **Verify cron job syntax:**
   ```bash
   crontab -l
   ```

4. **Check cron output:**
   ```bash
   cat ~/gym-reservation-bot/cron.log
   ```

### Headless Mode Issues

If the bot works in non-headless mode but fails in headless:
- Add more Chrome options in `setup_driver()` method
- Increase WebDriverWait timeouts
- Check if the website blocks headless browsers

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use GCP Secret Manager** for production deployments
3. **Restrict file permissions:**
   ```bash
   chmod 600 set_env.sh  # Only owner can read/write
   ```
4. **Use VM service accounts** with minimal required permissions
5. **Enable VM firewall rules** to restrict access
6. **Regularly update** Chrome and ChromeDriver

## Maintenance

### Updating ChromeDriver

ChromeDriver should match your Chrome version. To update:
```bash
# Follow Step 2 in setup instructions
```

### Monitoring

Check logs regularly:
```bash
tail -n 50 gym_reservation.log
```

### Testing Changes

Always test changes manually before updating the cron job:
```bash
python3 gym_reservation_bot.py
```

## Support

For issues or questions:
1. Check the log file: `gym_reservation.log`
2. Review the troubleshooting section
3. Verify all selectors are correct for your gym's website

## License

This project is provided as-is for educational and personal use.


# Quick Start Guide

This guide will help you get the gym reservation bot running quickly on a GCP Linux VM.

## Prerequisites Checklist

- [ ] GCP account with a project created
- [ ] VM instance created (Ubuntu 22.04 LTS recommended)
- [ ] SSH access to the VM
- [ ] Gym reservation website URL
- [ ] Gym login credentials

## 5-Minute Setup

### 1. Connect to Your VM

```bash
gcloud compute ssh YOUR_VM_NAME --zone=YOUR_ZONE
```

### 2. Install Dependencies

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python and pip
sudo apt-get install -y python3 python3-pip

# Install Chrome and ChromeDriver (automated)
wget https://raw.githubusercontent.com/YOUR_REPO/setup_chromedriver.sh
chmod +x setup_chromedriver.sh
./setup_chromedriver.sh
```

### 3. Upload Bot Files

From your local machine:

```bash
# Create directory on VM
gcloud compute ssh YOUR_VM_NAME --zone=YOUR_ZONE --command="mkdir -p ~/gym-reservation-bot"

# Upload files
gcloud compute scp gym_reservation_bot.py requirements.txt YOUR_VM_NAME:~/gym-reservation-bot/ --zone=YOUR_ZONE
```

Or clone from repository:

```bash
cd ~
git clone YOUR_REPO_URL gym-reservation-bot
cd gym-reservation-bot
```

### 4. Install Python Packages

```bash
cd ~/gym-reservation-bot
pip3 install -r requirements.txt
```

### 5. Configure Credentials

**Option A: Environment Variables (Quick)**

```bash
nano ~/gym-reservation-bot/set_env.sh
```

Add:
```bash
#!/bin/bash
export GYM_USERNAME="your_username"
export GYM_PASSWORD="your_password"
export GYM_RESERVATION_URL="https://your-gym-url.com"
```

```bash
chmod +x ~/gym-reservation-bot/set_env.sh
source ~/gym-reservation-bot/set_env.sh
```

**Option B: GCP Secret Manager (Secure)**

```bash
# Enable API
gcloud services enable secretmanager.googleapis.com

# Authenticate
gcloud auth application-default login

# Run setup script
cd ~/gym-reservation-bot
export GCP_PROJECT_ID="your-project-id"
python3 gcp_secrets_setup.py

# Set environment
export USE_GCP_SECRETS=true
export GCP_PROJECT_ID="your-project-id"
```

### 6. Customize Selectors

You need to find the CSS selectors for your gym's website. Open the website in a browser, press F12, and inspect elements.

Set environment variables:
```bash
export GYM_USERNAME_SELECTOR="input#username"
export GYM_PASSWORD_SELECTOR="input#password"
export GYM_LOGIN_BUTTON_SELECTOR="button.login"
export GYM_TIME_SLOT_SELECTOR="button[data-time='11:00']"
# ... add more as needed
```

### 7. Test the Bot

```bash
cd ~/gym-reservation-bot
source set_env.sh  # If using env vars
python3 gym_reservation_bot.py
```

Check logs:
```bash
tail -f gym_reservation.log
```

### 8. Schedule with Cron

```bash
crontab -e
```

Add:
```cron
0 11 * * * cd /home/YOUR_USERNAME/gym-reservation-bot && source set_env.sh && /usr/bin/python3 gym_reservation_bot.py >> /home/YOUR_USERNAME/gym-reservation-bot/cron.log 2>&1
```

Verify:
```bash
crontab -l
```

## Finding CSS Selectors

1. Open your gym's website in Chrome
2. Press F12 to open Developer Tools
3. Click the element selector tool (top-left)
4. Click on the element you want to target
5. In the Elements panel, right-click the highlighted element
6. Select "Copy" → "Copy selector"
7. Use that selector in your environment variables

## Common Issues

**ChromeDriver version mismatch:**
```bash
./setup_chromedriver.sh  # Re-run setup script
```

**Element not found:**
- Check selectors using browser console: `document.querySelector('your-selector')`
- Verify selectors are correct for your website

**Cron not running:**
```bash
# Check cron service
sudo systemctl status cron

# Check logs
tail -f ~/gym-reservation-bot/cron.log
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize selectors for your specific gym website
- Set up monitoring and alerts
- Test thoroughly before relying on automation

## Support

Check `gym_reservation.log` for detailed error messages and debugging information.


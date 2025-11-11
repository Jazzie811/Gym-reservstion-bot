#!/bin/bash
# Setup script for Chrome and ChromeDriver on Linux
# Run this script on your GCP VM to install Chrome and ChromeDriver

set -e  # Exit on error

echo "=========================================="
echo "Chrome and ChromeDriver Setup Script"
echo "=========================================="

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
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

# Install Google Chrome
echo "Installing Google Chrome..."
if ! command -v google-chrome &> /dev/null; then
  wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
  echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
  sudo apt-get update
  sudo apt-get install -y google-chrome-stable
else
  echo "Google Chrome is already installed."
fi

# Get Chrome version
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
echo "Detected Chrome version: $CHROME_VERSION"

# Install ChromeDriver
echo "Installing ChromeDriver..."
if ! command -v chromedriver &> /dev/null; then
  # Try to get ChromeDriver version from Chrome for Testing
  CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}" 2>/dev/null || \
    curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
  
  if [ -z "$CHROMEDRIVER_VERSION" ]; then
    echo "Warning: Could not determine ChromeDriver version. Using latest stable..."
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
  fi
  
  echo "Downloading ChromeDriver version: $CHROMEDRIVER_VERSION"
  
  # Try Chrome for Testing first (newer method)
  if wget -q --spider "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" 2>/dev/null; then
    wget -O /tmp/chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"
    unzip -q /tmp/chromedriver.zip -d /tmp
    sudo mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
  else
    # Fallback to old ChromeDriver storage
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
    unzip -q /tmp/chromedriver.zip -d /tmp
    sudo mv /tmp/chromedriver /usr/local/bin/chromedriver
  fi
  
  sudo chmod +x /usr/local/bin/chromedriver
  rm -f /tmp/chromedriver.zip
  rm -rf /tmp/chromedriver*
else
  echo "ChromeDriver is already installed."
fi

# Verify installations
echo ""
echo "=========================================="
echo "Verification:"
echo "=========================================="
echo "Chrome version:"
google-chrome --version

echo ""
echo "ChromeDriver version:"
chromedriver --version

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="


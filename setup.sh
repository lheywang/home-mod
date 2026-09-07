#!/bin/bash
echo "Configuring home-bot"

# Ensuring python3
python3 -m venv .venv
source .venv/bin/activate

# Create the user if not already exists
if getent passwd homemod > /dev/null 2>&1; then
    echo "Skipping user creation"
else
    echo "Creating user ..."
    useradd -m homemod &&
    passwd homemod
fi

# Configuring the user permissions
chown -R homemod:homemod /opt/home-mod

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy the service file
echo "Installing the service"
cp systemd/home-mod.service /etc/systemd/system/home-mod.service

# Enable the system
echo "Starting the service"
systemctl daemon-reload
systemctl enable home-mod
systemctl start home-mod

# Configuring git
git config --global --add safe.directory /opt/home-mod

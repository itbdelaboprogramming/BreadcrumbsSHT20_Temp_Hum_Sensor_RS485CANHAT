#!/usr/bin/env bash
read -p "Do you want to configure the .env file? (y/n): " configure_choice

if [[ "$configure_choice" == "y" || "$configure_choice" == "Y" ]]; then
    # Prompt the user for each configuration variable
    read -p "Enter FTP Hostname: " FTP_HOSTNAME
    read -p "Enter FTP Username: " FTP_USERNAME
    read -p "Enter FTP Password: " FTP_PASSWORD

    read -p "Enter DB User: " DB_USER
    read -p "Enter DB Password: " DB_PASSWORD
    read -p "Enter DB Host: " DB_HOST
    read -p "Enter DB Port: " DB_PORT
    read -p "Enter DB Database: " DB_DATABASE

    read -p "Enter Baud Rate: " BAUD_RATE

    read -p "Enter Device Name: " DEVICE_NAME

    # Create the .env file with the provided values
    cat <<EOL > .env
FTP_HOSTNAME=${FTP_HOSTNAME}
FTP_USERNAME=${FTP_USERNAME}
FTP_PASSWORD=${FTP_PASSWORD}
FTP_DIRECTORY=${FTP_DIRECTORY}

DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_DATABASE=${DB_DATABASE}

SERIAL_PORT=${SERIAL_PORT}
BAUD_RATE=${BAUD_RATE}
RS485_RE_PIN=${RS485_RE_PIN}

DEVICE_NAME=${DEVICE_NAME}
DELTA_HOURS=${DELTA_HOURS}
SLEEP_INTERVAL=${SLEEP_INTERVAL}
EOL

    echo ".env file created successfully"
else
    echo "Configuration of .env file skipped"
    
fi
echo "running data acusition program"
python3 -m venv env
source env/bin/activate
python3 code_1.py

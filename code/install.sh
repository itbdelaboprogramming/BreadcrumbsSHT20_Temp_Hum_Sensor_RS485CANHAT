#!/usr/bin/env bash

echo "setting up hardware for RS485"
sudo raspi-config nonint do_serial_cons 1
echo "disable shell logging over serial"
sudo raspi-config nonint do_serial_hw 0
echo "enable serial hardware port"

if grep -Fxqw "enable_uart=1" /boot/firmware/config.txt
then
    echo -e "config.txt file configured"
else
    echo "enable_uart=1" | sudo tee -a /boot/firmware/config.txt
    echo -e "config.txt file configured"
fi

echo "setting up hardware for RS485 done"
echo "-----------------------------------"

echo "Installing python..."
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip

echo "Setting up virtual environment..."
python3 -m venv env
source env/bin/activate

echo "Installing required Python packages..."
pip install pyserial
pip install RPi.GPIO
pip install mariadb
pip install dotenv

deactivate

echo "Python environment setup complete."
echo "-----------------------------------"


echo "making .env file"
cat <<EOL > .env
FTP_HOSTNAME=192.168.46.3
FTP_USERNAME=anonymous
FTP_PASSWORD=zaiman.a.purnama@gmail.com
FTP_DIRECTORY=/XY-MD02/

DB_USER=zaim
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=test1

SERIAL_PORT=/dev/ttyS0
BAUD_RATE=9600
RS485_RE_PIN=4

DEVICE_NAME=TH1101
DELTA_HOURS=1
SLEEP_INTERVAL=3
EOL

echo ".env file created successfully"


echo "-----------------------------------"
echo "creating local database"
sudo apt install mariadb-server -y
mysql -uroot -padmin -e "CREATE DATABASE test1;"
mysql -uroot -padmin -e "CREATE USER 'zaim'@'localhost' IDENTIFIED BY 'admin';"
mysql -uroot -padmin -e "GRANT ALL PRIVILEGES ON test1.* TO 'zaim'@'localhost';"
mysql -uroot -padmin -e "FLUSH PRIVILEGES;"

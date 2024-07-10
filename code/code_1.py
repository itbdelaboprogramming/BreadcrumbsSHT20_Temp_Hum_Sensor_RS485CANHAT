import serial
import RPi.GPIO as GPIO
import time
import datetime
import os
import csv
import ftplib
import mariadb
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration variables
FTP_HOSTNAME = os.getenv("FTP_HOSTNAME")
FTP_USERNAME = os.getenv("FTP_USERNAME")
FTP_PASSWORD = os.getenv("FTP_PASSWORD")
FTP_DIRECTORY = os.getenv("FTP_DIRECTORY")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_DATABASE = os.getenv("DB_DATABASE")

SERIAL_PORT = os.getenv("SERIAL_PORT")
BAUD_RATE = int(os.getenv("BAUD_RATE"))
RS485_RE_PIN = int(os.getenv("RS485_RE_PIN"))

DEVICE_NAME = os.getenv("DEVICE_NAME")
DELTA_HOURS = int(os.getenv("DELTA_HOURS"))
SLEEP_INTERVAL = int(os.getenv("SLEEP_INTERVAL"))

# Connect to MariaDB Platform
def connect_to_db():
    try:
        conn = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_DATABASE
        )
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

conn = connect_to_db()
cur = conn.cursor()

# Setup GPIO for RE control on RS485 HAT
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RS485_RE_PIN, GPIO.OUT)

# Setup serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Command to get temperature and humidity
get_temphumid = '\x01\x04\x00\x01\x00\x02\x20\x0B'

# Function to read register
def read_register(command):
    GPIO.output(RS485_RE_PIN, GPIO.HIGH)
    ser.write(command.encode())
    time.sleep(0.1)
    GPIO.output(RS485_RE_PIN, GPIO.LOW)
    response = ser.readall()
    return response

# Setup FTP connection
def connect_to_ftp():
    ftp_server = ftplib.FTP(FTP_HOSTNAME, FTP_USERNAME, FTP_PASSWORD)
    ftp_server.encoding = "utf-8"
    ftp_server.cwd(FTP_DIRECTORY)
    return ftp_server

ftp_server = connect_to_ftp()

# CSV file setup
headers = ['timestamp', 'temp (oC)', 'humidity (%)']
master_filename = DEVICE_NAME + '.csv'
temp_filename = 'temp_file/temp_' + master_filename

# Check and create master file on the server
if master_filename not in ftp_server.nlst():
    print('Creating master file on the server')
    with open(master_filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(headers)
    with open(master_filename, 'rb') as file:
        ftp_server.storbinary('STOR ' + master_filename, file)
    os.remove(master_filename)
else:
    print(f'Master file for {DEVICE_NAME} already exists')

# Check and create temporary file if it doesn't exist
if not os.path.exists(temp_filename):
    with open(temp_filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')

# Data collection loop
delta = datetime.timedelta(hours=DELTA_HOURS)
start = datetime.datetime.now().replace(minute=0,second=0, microsecond=0)
stop = start + delta

while True:
    if datetime.datetime.now() > stop:
        with open(temp_filename, 'rb') as file:
            ftp_server.storbinary('APPE ' +

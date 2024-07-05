import serial
import RPi.GPIO as GPIO
import time
import datetime
import os
import csv
import ftplib
import mariadb
import sys

# Configuration variables
FTP_HOSTNAME = "192.168.46.3"
FTP_USERNAME = "anonymous"
FTP_PASSWORD = "zaiman.a.purnama@gmail.com"
FTP_DIRECTORY = '/XY-MD02/'

DB_USER = "zaim"
DB_PASSWORD = "admin"
DB_HOST = "localhost"
DB_PORT = 3306
DB_DATABASE = "test1"

SERIAL_PORT = "/dev/ttyS0"
BAUD_RATE = 9600
RS485_RE_PIN = 4

DEVICE_NAME = 'TH1101'
DELTA_HOURS = 1
SLEEP_INTERVAL = 3

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
            ftp_server.storbinary('APPE ' + master_filename, file)
        
        with open(temp_filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                cur.execute(
                    "INSERT INTO datastreams (created_at, sensor_id, value) VALUES (?, 'TT1001', ?)", (row[0], row[1])
                )
                cur.execute(
                    "INSERT INTO datastreams (created_at, sensor_id, value) VALUES (?, 'HT1001', ?)", (row[0], row[2])
                )
                conn.commit()

        os.remove(temp_filename)
        with open(temp_filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',')

        start = stop
        stop = start + delta

    temphumid = read_register(get_temphumid)
    temp = float(int.from_bytes(temphumid[3:5], byteorder='big')) / 10
    humid = float(int.from_bytes(temphumid[5:7], byteorder='big')) / 10
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ",", temp, ",", humid)

    new_row = [[now, temp, humid]]
    with open(temp_filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerows(new_row)
    
    time.sleep(SLEEP_INTERVAL)

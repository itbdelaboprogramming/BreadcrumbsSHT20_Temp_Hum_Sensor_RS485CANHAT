# SHT20_Temp_Hum_Sensor_RS485CANHAT
## Installation
### Setting up the Raspi
Open the Raspberry PI terminal, execute the following command to enter the Raspberry Pi configuration:
```
sudo raspi-config
```

You need to disable the login shell and enable the srial port hardware.
Choose Interfacing Options -> Serial -> No -> Yes:
![image](doc/img/L76X_GPS_Module_rpi_serial.png)
Open the /boot/config.txt file and find the following configuration statement to enable the serial port, if not, add it at the end of the file:
```
enable_uart=1
```

And then reboot the Raspberry Pi:

```
sudo reboot
```

## Running the program
There is already a virtual enviroment which contains all the package needed for the program to run. Before running the program, make sure to configre all the variable in the code (i.e. FTP and database connection).

To run the open the code directory in terminal and run:
```
bash main.sh
```

## TO DO
Make an external file so its easier to config without changing the python file
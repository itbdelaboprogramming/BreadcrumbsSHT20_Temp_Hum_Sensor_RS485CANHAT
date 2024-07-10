# SHT20_Temp_Hum_Sensor_RS485CANHAT
## Installation
### Setting up the Raspi
To setup the raspi to run the code just run the following code in the termnila
```
sudo bash install.sh
```
It will install all the dependency from python to mariadb

### Configuring the program
You can configure the program by editing the .env file or running the main.sh file and pressing Y to configure.

## Running the program
There is already a virtual enviroment which contains all the package needed for the program to run. Before running the program, make sure to configre all the variable in the code (i.e. FTP and database connection).

To run the open the code directory in terminal and run:
```
sudo bash main.sh
```

## TO DO
Make an external file so its easier to config without changing the python file
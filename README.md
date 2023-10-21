# SolarPowerBrampton
![Static Badge](https://img.shields.io/badge/Brampton2Zero-green?style=for-the-badge&link=https%3A%2F%2Fwww.brampton2zero.org.uk%2F) ![Static Badge](https://img.shields.io/badge/3.11-grey?style=for-the-badge&logo=Python&logoColor=%23ffdd54&label=version&labelColor=%233670A0&color=grey) ![Raspberry Pi](https://img.shields.io/badge/-RaspberryPi-C51A4A?style=for-the-badge&logo=Raspberry-Pi) ![InfluxDB](https://img.shields.io/badge/InfluxDB-22ADF6?style=for-the-badge&logo=InfluxDB&logoColor=white)
## Project Description 

[Brampton2Zero (B2Z)](https://www.brampton2zero.org.uk/) is a community interest company from the UNited Kingdom with the aim of decarbonizing Brampton. Of the many projects undertaken B2Z, the Solar Cooperative aims to reduce emissions by switching to clean energy. [You can find the feasibility study here](https://www.brampton2zero.org.uk/shared/images/content/bus_55661/pdf/Brampton2Zero_-_Feasibility_Study_v.1.21_redacted.pdf). 

In 2022, B2Z partnered with Lancaster University Physics department to create a scale model of a solar cooperative. This model was created by four students during their industrial year project. I started my work after the project was finished and my goal was to improve the visualisation of energy and electricity flow in the system. [You can find more about it in the project report](https://www.brampton2zero.org.uk/shared/images/content/bus_55661/pdf/Active_System_visualization_of_solar_model.pdf).

## Model description

The model is comprised out of three house units and a power plant. Each house unit has a 12v battery, a charge controller, a solar panel and a consumer circuit (two LEDs in series with a 1k resistor and all in parallel with a Rpi fan). For each house there are two switches, allowing the houses to "buy" energy from the power plant or "sell" it, or simply turn the consumer circuit on or of. The power plant is similar to a house but with a larger battery and solar panel.

To measure energy flow, an [INA219](https://learn.adafruit.com/adafruit-ina219-current-sensor-breakout) module is connected to a solar panel. These are then connected to a Raspberry Pi Model 3B+ through the [I<sup>2</sup>C]( https://en.wikipedia.org/wiki/I%C2%B2C#) connection. Additionally, as part of the project a module capable of using SIM card for internet connection was added to the system (see the project report), but it doesn't concern this code.

## Code Description

> This code was specifically made for a Raspberry Pi running Debian Bullseye. If you try to run this on a windows machine either use a VM or WSL (the later is what I am doing for development before I send it to my Raspberry Pi to test).

> **NOTE**: This will run on a Raspberry Pi Zero (as of 2023) but you cannot host the database locally as it is made for 64bit systems. The cloud solution works.

*This script reads all the data from the INA219 modules and sends it to a database.* That's the short description. Here is the long one:

The code connects to the database and then it starts taking measurements and sending them. At the end it waits all the extra time needed and repeats the last two steps. This is done in main.py. 

There is only one class that takes measurements, located in tools.py called <code>read_data</code>. Different measurements have different functions in that class. Each functions returns a value or a set of values if more than one measurement is taken. **NOTE**: Energy/Electricity values are taken 10 times in a ~1 second period and averaged. Other measurements are only taken once.

Logging this measurements into a database is done with [InfluxDB](https://www.influxdata.com/) API. There are two options:
1. local_solution.py - to log data in a locally hosted InfluxDB database
2. cloud_solution.py - to log data using InfluxDB Cloud.  

autostart.py is a file that is run at startup. It makes sure that everything works as it should and updates the code if needed

All errors are handled by the rpi_errors.py file. There are different levels of of errors because this code has to be operational even if someone who is not familiar with programming is using it. The following errors are used throughout the code:
  * Critical: only used when the code cannot function at all without solving this error, and it requires debugging.
  * Connection: when internet connection is broken (maybe someone forgot to change to start a hotspot/ the SIM module is disconnected)
  * Sending: it failed to log a point to the database. Blinks the LED twice to alert the user.
  * Measuring: trying to take a measurement failed. Blinks 3 times
  * Short: a quick LED blink for errors that aren't that important but should be acknowledged. 
  * Silent: for errors that don't matter, ie: measuring CPU use failed, this can be seen in the data and it should not be allowed to affect the rest of the process.
# Install and Setup

## Quick install 

## Documentation

# Contribution


-----
On your Rpi, navigate to the folder you want to use and download the code using the link:

    git clone https// 

Open the folder

    cd SolarPowerBrampton

Make a python environment # 

    sudo python -m venv ~/SolarPowerBrampton/env

Open the environment and work from it:

    source env/bin/activate

Install packages:

    sudo pip install -r requirements.txt

Get token

    export INFLUXDB_TOKEN= <your token here>
=======
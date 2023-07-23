# What this is 

A simple script that does a simple thing meant to run on a Raspberry Pi. 

First, it reads voltages with the INA219 module, formats it to the right values.
Seconds, it sends the formatted data to an InfluxDB cloud service. 

# What is this for

A very specific solar panel model

# Steps to install
> this is designed for Raspberry pi. It won't work for windows machines without using wsl.


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


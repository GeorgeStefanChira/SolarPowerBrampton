# SolarPowerBrampton
![Static Badge](https://img.shields.io/badge/Brampton2Zero-green?style=for-the-badge&link=https%3A%2F%2Fwww.brampton2zero.org.uk%2F) ![Static Badge](https://img.shields.io/badge/3.11-grey?style=for-the-badge&logo=Python&logoColor=%23ffdd54&label=version&labelColor=%233670A0&color=grey) ![Raspberry Pi](https://img.shields.io/badge/-RaspberryPi-C51A4A?style=for-the-badge&logo=Raspberry-Pi) ![InfluxDB](https://img.shields.io/badge/InfluxDB-22ADF6?style=for-the-badge&logo=InfluxDB&logoColor=white)


- [SolarPowerBrampton](#solarpowerbrampton)
  - [Project Description](#project-description)
    - [Model description](#model-description)
  - [Code Description](#code-description)
  - [Install and Setup](#install-and-setup)
    - [Quick install](#quick-install)
  - [Documentation](#documentation)
  - [Contribution](#contribution)
---

## Project Description 

[Brampton2Zero (B2Z)](https://www.brampton2zero.org.uk/) is a community interest company from the United Kingdom with the aim of decarbonizing Brampton. Of the many projects undertaken by B2Z, the Solar Cooperative aims to reduce emissions by switching to clean energy. [You can find the feasibility study here](https://www.brampton2zero.org.uk/shared/images/content/bus_55661/pdf/Brampton2Zero_-_Feasibility_Study_v.1.21_redacted.pdf). 

In 2022, B2Z partnered with Lancaster University's Physics department to create a scale model of a solar cooperative. This model was created by four students during their industrial year project. I started my work after the project was finished and my goal was to improve the visualisation of energy and electricity flow in the system. [You can find more about it in the project report](https://www.brampton2zero.org.uk/shared/images/content/bus_55661/pdf/Active_System_visualization_of_solar_model.pdf).

### Model description

The model is comprised of three house units and a power plant. Each housing unit has a 12v battery, a charge controller, a solar panel and a consumer circuit (two LEDs in series with a 1k resistor and all in parallel with a Rpi fan). For each house there are two switches, allowing the houses to "buy" energy from the power plant or "sell" it, or simply turn the consumer circuit on or off. The power plant is similar to a house but with a larger battery and solar panel.

To measure energy flow, an [INA219](https://learn.adafruit.com/adafruit-ina219-current-sensor-breakout) module is connected to a solar panel. These are then connected to a Raspberry Pi Model 3B+ through the [I<sup>2</sup>C]( https://en.wikipedia.org/wiki/I%C2%B2C#) connection. Additionally, as part of the project a module capable of using a SIM card for internet connection was added to the system (see the project report), but it doesn't concern this code.

---
## Code Description

> This code was specifically made for a Raspberry Pi running Debian Bullseye. If you try to run this on a Windows machine either use a VM or WSL (the latter is what I am doing for development before I send it to my Raspberry Pi to test).

> **NOTE**: This will run on a Raspberry Pi Zero (as of 2023) but you cannot host the database locally as it is made for 64-bit systems. The cloud solution works.

*This script reads all the data from the INA219 modules and sends it to a database.* That's the short description. Here is the long one:

This code allows you to interface with an InfluxDB database. This database can be hosted locally on your device or on the cloud. Whichever method you use, simply mark it into the configuration file. The data measured is given by voltage sensors (the INA219 modules) in the Solar Model and CPU, RAM and network usage in the Raspberry Pi. The code should give no errors unless they impede critical functionality. Additionally, all errors light up the on board LED.

There is only one class that takes measurements, located in [tools.py](/tools.py) called <code>read_data</code>. Different measurements have different functions in that class. Each function returns a value or a set of values if more than one measurement is taken. **NOTE**: Energy/Electricity values are taken 10 times in a ~1 second period and averaged. Other measurements are only taken once.

Logging these measurements into a database is done with [InfluxDB](https://www.influxdata.com/) API. There are two options:
1. [local_solution.py](/local_solution.py) - to log data in a locally hosted InfluxDB database
2. [cloud_solution.py](/cloud_solution.py) - to log data using InfluxDB Cloud.  

[autostart.py](/autostart.py) is a file that is run at startup. It makes sure that everything works as it should and updates the code if needed

All errors are handled by the [rpi_errors.py](/rpi_errors.py) file. There are different levels of errors because this code has to be operational even if someone who is not familiar with programming is using it. The following errors are used throughout the code:
  * Critical: only used when the code cannot function at all without solving this error, and it requires debugging.
  * Connection: when internet connection is broken (maybe someone forgot to change to start a hotspot/ the SIM module is disconnected)
  * Sending: it failed to log a point to the database. Blinks the LED twice to alert the user.
  * Measuring: trying to take a measurement failed. Blinks 3 times
  * Short: a quick LED blink for errors that aren't that important but should be acknowledged. 
  * Silent: for errors that don't matter, ie: measuring CPU use failed, this can be seen in the data and it should not be allowed to affect the rest of the process.

---
## Install and Setup
> #### Requirements:
>   * A Raspberry Pi is already set up. [Follow this guide](https://www.raspberrypi.com/documentation/computers/getting-started.html)
>   * [InfluxDB Cloud account](https://www.influxdata.com/products/influxdb-cloud/) if you use that solution.
>   * WSL or a Linux Machine / VM for development 
### Quick install 

**On Raspberry Pi:**
1. Clone the repo:
        
        git clone https://github.com/GeorgeStefanChira/SolarPowerBrampton
2. Edit [config.ini](/config.ini) file:

        cd SolarPowerBrampton 
        nano config.ini
3. Run autostart.py

        python3 autostart.py


**On PC (for development):**

1. Open WSL and navigate to your preferred folder:
   
        cd your/preferred/folder
        git clone https://github.com/GeorgeStefanChira/SolarPowerBrampton
        cd SolarPowerBrampton
2. Make a python environment and open it:

        sudo python -m venv ~/SolarPowerBrampton/env
        source env/bin/activate
3. Install dependencies manually (autostart.py won't work on WSL) 
   
        sudo pip install -r requirements.txt


## Documentation

There is no more documentation for this project, besides this README file and the report paper linked at the beginning. This is not exactly meant to be reused and the code is straightforward. But for more explanations here is a list of resources used to create this software:

| Code  | Use case| source link |
|---------|-----|------|
| InfluxDB cloud API| [cloud_solution.py](/cloud_solution.py) | https://docs.influxdata.com/influxdb/cloud/api-guide/client-libraries/python/ |  
| InfluxDB local API| [local_solution](/local_solution.py)|https://influxdb-python.readthedocs.io/en/latest/api-documentation.html|
| InfluxDB database| install on RPi if using local solution| https://docs.influxdata.com/influxdb/v2/install/?t=Raspberry+Pi|
| CPU data | [tools.py](/tools.py) / read_data()  |https://psutil.readthedocs.io/en/latest/#cpu|
| RAM data|[tools.py](/tools.py) / read_data()  | https://psutil.readthedocs.io/en/latest/#memory|
|Network data |[tools.py](/tools.py) / read_data()  |https://psutil.readthedocs.io/en/latest/#network |
| INA219 module|[tools.py](/tools.py) / read_data()  | https://learn.adafruit.com/adafruit-ina219-current-sensor-breakout|
| RPi.GPIO | [rpi_errors.py](/rpi_errors.py)/ blink() | |

## Contribution

The only contribution accepted is, literally, explaining what I got wrong. If you find this project, look at it and go "This guy is an idiot, here is a glaring issue", please tell me.

**So here is a list of issues I consider important:**

* <mark> **Security issues** </mark>:  This is the main one I am afraid of and I consider really important. Please provide a link to the problem or explain it if possible, any help here is more than welcome!
* **Performance issues**: I don't consider performance improvements important unless the code underperforms. By **underperforming** I mean that the main loop in the code doesn't execute usually within 3 seconds (this error would appear in errorfile.txt) or it occasionally takes more than 10 seconds. If this happens, then the code can't run. Please let me know about it.
* **Unexpected Bugs**: if there is a bug that is not accounted for, let me know. Additionally, any critical errors that are not caused by misuse or oversight are also important.

**I will not be updating the functionality of this code any more**
If you want to make something similar and you need a few changes, then feel free to fork this project! There is no need to add more stuff here but feel free to use this as a base model (if you think it's good enough). 

If you are currently working with, or for, Brampton2Zero to either modify the Solar Model this code was meant for, or a similar project that could benefit from this code, please contact me! Hopefully, I can help you!

---
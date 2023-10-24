""" 
A usefull class to take measuremnets with the model.
It's not as general as the upload classes, but can be addapted to different purposes.

classes:
    - read_data: lets you read ina219 voltages, cpu and ram usage, and lets you send fake data
    - read_fake_data: copy of the above class for debugging purposes.
    - read_config: reads the config files for the project
"""

from ina219 import INA219  # allows RPi to read voltages with the INA219 module
import psutil # cpu/ram/network monitoring
import socket # hostname
import numpy as np 
import time, os
from configparser import ConfigParser

import rpi_errors as rpie

class read_data:
    """
    ## Purpose and use:
    
        This class reads data from the solar model (or anything similar) and the raspberry pi.
        It's tailored to its purpose and it's unlikely to be usefull for other projects.
        Some of this is based on the original code previously used for the project.

    ### Methods:
        1. read_ina219
    
    """
    def __init__(self)->None:
        try:
            # Create INA objects only once (as I should have done from the start))
            self.ina_red = INA219(0.1, 3, address=0x40)
            self.ina_red.configure(self.ina_red.RANGE_16V, self.ina_red.GAIN_AUTO)
            
            self.ina_green = INA219(0.1, 3, address=0x41)
            self.ina_green.configure(self.ina_green.RANGE_16V, self.ina_green.GAIN_AUTO)
            
            self.ina_blue = INA219(0.1, 3, address=0x44)
            self.ina_blue.configure(self.ina_blue.RANGE_16V, self.ina_blue.GAIN_AUTO)
            
            self.ina_bus = INA219(0.1, 3, address=0x44)
            self.ina_bus.configure(self.ina_blue.RANGE_16V, self.ina_bus.GAIN_AUTO)
        except Exception as err:
            raise rpie.CriticalError(f"could not create INA Objects, error: {err}")
        
        
    def read_ina219(self, ina):
        """ 
        take an ina object and use it to read voltage data
        Args:    ina (object): pass an INA219() object 
        Returns: dict: {voltage: float, power: float, bus_voltage:float}
        Raises:  MeasurementError: if measuring the voltage fails
        """
        # measurement
        try:
            v = ina.voltage()
            v_shunt = ina.shunt_voltage()
        except Exception as err:
            rpie.MeasuringError("Error encountered when measuring voltage with the ina219")
            
        # average and pack
        result = {
            "voltage": round(v_shunt,4),
            "power": round(0.1*(v**2),3),
            "bus_voltage": round(v,3)
        }
        
        #send
        return result
    
    def measure(self):
        """Measures voltage from four parts

        Returns:
            dict: { house/blue/green/red/bus: read_ina(), bus_average: {voltage: float, power: float}}
        """
        # get the right shape
        data= {
            "blue_house": self.read_ina219(self.ina_blue),
            "red_house": self.read_ina219(self.ina_red),
            "green_house" :self.read_ina219(self.ina_green),
            "bus": self.read_ina219(self.ina_bus)
        }
        time.sleep(0.05) 
        
        ina_list=[self.ina_blue, self.ina_red,self.ina_green, self.ina_bus]
        data_keys=list(data.keys())
        
        for x in range(9):
            for i in range(4): # loop through all ina
                measure = self.read_ina219(ina=ina_list[i])
                for key in measure: # at every ina, loop through all measurements and add the value taken 
                    data[data_keys[i]][key]+=measure[key]    
            time.sleep(0.05) 

        # average out every value
        for key in data.keys(): 
            for value in data[key].values(): 
                value = value/10 # 10 because we measure once at start
                
        # get average bus voltage
        bus_voltage=0
        for key in ["blue_house","red_house","green_house"]: bus_voltage += data[key]["bus_voltage"]
        bus_voltage /= 3
        
        data["bus_average"]= {
            "voltage": float(round(bus_voltage,3)),
            "power":float(round(0.1*(bus_voltage**2),3))
        }
        
        return data
        
    def measure_cpu(self):
        """
        # Measure cpu and ram usage
        
        Usese psutil library
        #Todo: change name and pack data as dictionary
        
        Returns: (float, float) = cpu, ram
        Raises: SilentError
        """
        try:
            cpu_usage=psutil.cpu_percent()
            ram_usage=psutil.virtual_memory().used
        except Exception as err:
            rpie.SilentError("CPU or RAM could not be measured")
            cpu_usage= -1.0
            ram_usage= -1.0

        
        return cpu_usage, ram_usage
    
    def measure_network(self):
        """
        ### Measure network use
        
        ## NOTE: change this function if not using eth0 for network.
        there was an issue when passing the key as an argument.
        Usses psutil library
        #Todo: change name and pack data as dictionary
        
        Returns: (float, float) = net in, net out
        Raises: ShortError when it fails and changes the numbers
        """
        try:
            net_stat = psutil.net_io_counters(pernic=True)["eth0"]
            net_in = net_stat.bytes_recv
            net_out = net_stat.bytes_sent
        except Exception as err:
            rpie.ShortError(f"Network mesurment failed: {err}")
        return net_in,net_out

    def get_name(self):
        try:
            return socket.gethostname()
        except Exception as err:
            rpie.SilentError(f"Hostname could not be accessed in get_name() function, error: {err}")
            return "Name not found"

class read_fake_data:
    """
    ## Mimics read_data but only sends fake data
    
    To be used when developing and a Raspberry isn't availble.
    Aditionally, all values follow a sinusoidal pattern, usefull
    in diagnosing data accuracy. 
    
    """
    def __init__(self)->None:
        self.ina_blue =1
        self.ina_red =2
        self.ina_green =3
        self.ina_bus =0
        
    def measure(self):
        """
        # Fake
        Measures voltage from four parts

        Returns:
            dict: { house/blue/green/red/bus: read_ina(), bus_average: {voltage: float, power: float}}
        """

        # get the right shape
        data= {
            "blue_house": self.read_ina219(self.ina_blue),
            "red_house": self.read_ina219(self.ina_red),
            "green_house" :self.read_ina219(self.ina_green),
            "bus": self.read_ina219(self.ina_bus)
        }
        time.sleep(0.05) 
        
        ina_list=[self.ina_blue, self.ina_red,self.ina_green, self.ina_bus]
        data_keys=list(data.keys())
        
        for x in range(9):
            for i in range(4): # loop through all ina
                measure = self.read_ina219(ina=ina_list[i])
                for key in measure: # at every ina, loop through all measurements and add the value taken 
                    data[data_keys[i]][key]+=float(measure[key])    
            time.sleep(0.05) 

        # average out every value
        for key in data.keys(): 
            for value in data[key].values(): 
                value = value/10 # 10 because we measure once at start
                
        # get average bus voltage
        bus_voltage=0
        for key in ["blue_house","red_house","green_house"]: bus_voltage += data[key]["bus_voltage"]
        bus_voltage /= 3
        
        data["bus_average"]= {
            "voltage": float(round(bus_voltage,3)),
            "power":float(round(0.1*(bus_voltage**2),3))
        }
        
        return data
    
    def read_ina219(self, ina):
        """ # Fake
        take an ina object and use it to read voltage data
        Args:    ina (object): pass an INA219() object 
        Returns: dict: {voltage: float, power: float, bus_voltage:float}
        Raises:  MeasurementError: if measuring the voltage fails
        """
        result = {
            "voltage": float(ina*np.sin(time.time_ns())),
            "power": float(ina*np.sin(time.time_ns())),
            "bus_voltage": float(ina*np.sin(time.time_ns()))
        }
        return result
    
    def measure_cpu(self):
        """
        # Fake
        ### Measure cpu and ram usage
        
        Usese psutil library
        #Todo: change name and pack data as dictionary
        
        Returns: (float, float) = cpu, ram
        Raises: SilentError
        """
        try:
            cpu_usage= float(1*abs(np.sin(time.time_ns())))*100
            ram_usage= float(2*abs(np.cos(time.time_ns())))*500
        except Exception as err:
            rpie.SilentError("CPU or RAM could not be measured")
            cpu_usage= -1.0
            ram_usage= -1.0

        
        return cpu_usage, ram_usage
    
    def measure_network(self):
        """
        # Fake
        Measure network use
        
        Usese psutil library
        #Todo: change name and pack data as dictionary
        
        Returns: (float, float) = net in, net out
        Raises: ShortError when it fails and changes the numbers
        """
        try:
            net_in = float(2*abs(np.cos(time.time_ns())))*10
            net_out = float(2*abs(np.cos(time.time_ns())))*100
        except Exception as err:
            rpie.ShortError(f"Network mesurment failed: {err}")
        return net_in,net_out

    def get_name(self):
        """ # Fake version"""
        return "Fake_machine"        


# def blink_led(severity:int):
    """blinks the onboard led when enountering errors

    For severity 0: it turns on for 4 seconds, of for 4
    severity n>0: 
        it turns on for 4 seconds, waits 2 seconds and then blinks n times
        n gives the severity number. 
    
    1:
    2: Files are missing, will reinstall
    3: 
        
    Args:
        severity (int): the severity of the error
    """
    # for i in range(0,10):
    #     RPi.GPIO.output(16, RPi.GPIO.LOW)
    #     time.sleep(20)
    #     RPi.GPIO.output(16, RPi.GPIO.HIGH)
    #     time.sleep(40)
    #     RPi.GPIO.output(16, RPi.GPIO.LOW)
    #     time.sleep(20)
    #     for j in range(severity):
    #         RPi.GPIO.output(16, RPi.GPIO.LOW)
    #         time.sleep(10)
    #         RPi.GPIO.output(16, RPi.GPIO.HIGH)
            
class read_config:
    def __init__(self, filename) -> None:
        """
        ## Reads the config file
        
        This is tailored to the specific config.ini file in this project.
        
        Doesn't have any error correction
        """
        self.config =ConfigParser() 
        
        try:
            os.path.isfile(filename)
        except:
            raise rpie.CriticalError(f"{filename} is nt the correct path!")
        
        self.config.read(filenames=filename)
    def get_methods(self):
        cloud = self.config.getboolean(section="Method",option="Cloud") 
        fake = self.config.getboolean(section="Method",option="Fake")
        return cloud, fake
    def get_time(self):
        total_time= self.config.getint(section="Time", option="Seconds")/3
        endless = self.config.getboolean(section="Time", option="Endless")
        return total_time, endless
    def get_cloud(self):
        _dir={}
        for item in ["bucket","org","token","url"]:
            _dir[item]=self.config.get("Cloud", option=item)
        return _dir
    def get_local(self):
        _dir={}
        for item in ["ifuser","ifpass","ifdb","ifhost","ifport"]:
            _dir[item]=self.config.get("Local", option=item)
        return _dir
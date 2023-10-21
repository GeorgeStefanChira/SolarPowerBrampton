""" 
A usefull class to take measuremnets with the model.
It's not as general as the upload classes, but can be addapted to different purposes.

classes:
    - read_data: lets you read ina219 voltages, cpu and ram usage, and lets you send fake data
    - read_fake_data: copy of the above class for debugging purposes.
"""

from ina219 import INA219  # allows RPi to read voltages with the INA219 module
import psutil # cpu/ram/network monitoring
import socket # hostname
import numpy as np 
import time

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
        pass
        
    def read_ina219(self, ina):
        """ 
        take an ina object and use it to read voltage data
        Args:    ina (object): pass an INA219() object 
        Returns: dict: {voltage: float, power: float, bus_voltage:float}
        Raises:  MeasurementError: if measuring the voltage fails
        """
        power = []
        bus_voltage=[]
        shunt_voltage=[]
        
        # measure 10 times per second
        for x in range(10):
            try:
                v = ina.voltage()
                v_shunt = ina.shunt_voltage()
            except Exception as err:
                raise rpie.MeasuringError("Error encountered when measuring voltage with the ina219")
                
            power.append(round(0.1*(v**2),3))
            bus_voltage.append(round(v,3))
            shunt_voltage.append(round(v_shunt,4))
            time.sleep(0.1)
        
        # average and pack
        result = {
            "voltage": float(np.average(shunt_voltage)),
            "power": float(np.average(power)),
            "bus_voltage": float(np.average(bus_voltage))
        }
        
        #send
        return result
    
    def measure(self):
        """Measures voltage from four parts

        Returns:
            dict: { house/blue/green/red/bus: read_ina(), bus_average: {voltage: float, power: float}}
        """
        
        # This part is almost identical to the original, but with for loops and functions where apropriate.
        ina_red = INA219(0.1, 3, address=0x40)
        ina_red.configure(ina_red.RANGE_16V, ina_red.GAIN_AUTO)
        
        ina_green = INA219(0.1, 3, address=0x41)
        ina_green.configure(ina_green.RANGE_16V, ina_green.GAIN_AUTO)
        
        ina_blue = INA219(0.1, 3, address=0x44)
        ina_blue.configure(ina_blue.RANGE_16V, ina_blue.GAIN_AUTO)
        
        ina_bus = INA219(0.1, 3, address=0x44)
        ina_bus.configure(ina_blue.RANGE_16V, ina_bus.GAIN_AUTO)
        
        data= {
            "blue house": self.read_ina219(ina_blue),
            "red house": self.read_ina219(ina_red),
            "green house" :self.read_ina219(ina_green),
            "bus": self.read_ina219(ina_bus)
        }
        
        # get average bus voltage
        bus_voltage=0
        for key in data: bus_voltage += data[key]["bus_voltage"]
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
            raise rpie.SilentError("CPU or RAM could not be measured")
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
            raise rpie.ShortError(f"Network mesurment failed: {err}")
        return net_in,net_out

    def get_name(self):
        try:
            return socket.gethostname()
        except Exception as err:
            raise rpie.SilentError(f"Hostname could not be accessed in get_name() function, error: {err}")
            return "Name not found"

class read_fake_data:
    """
    ## Mimics read_data but only sends fake data
    
    To be used when developing and a Raspberry isn't availble.
    Aditionally, all values follow a sinusoidal pattern, usefull
    in diagnosing data accuracy. 
    
    """
    def __init__(self)->None:
        pass
        
    def measure(self):
        """
        # Fake
        Measures voltage from four parts

        Returns:
            dict: { house/blue/green/red/bus: read_ina(), bus_average: {voltage: float, power: float}}
        """
        data= {
            "blue house": self.read_fake_ina219(1),
            "red house": self.read_fake_ina219(2),
            "green house" :self.read_fake_ina219(3) 
        }
        
        bus_voltage=0
        for key in data:bus_voltage += data[key]["bus_voltage"]
        bus_voltage /= 3
        
        data["bus_average"]= {
            "voltage": float(round(bus_voltage,3)),
            "power":float(round(0.1*(bus_voltage**2),3))
        }
        
        return data
    
    def read_ina219(self, x):
        """ # Fake
        take an ina object and use it to read voltage data
        Args:    ina (object): pass an INA219() object 
        Returns: dict: {voltage: float, power: float, bus_voltage:float}
        Raises:  MeasurementError: if measuring the voltage fails
        """
        result = {
            "voltage": float(x*np.sin(time.time_ns())),
            "power": float(x*np.sin(time.time_ns())),
            "bus_voltage": float(x*np.sin(time.time_ns()))
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
            raise rpie.SilentError("CPU or RAM could not be measured")
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
            raise rpie.ShortError(f"Network mesurment failed: {err}")
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
            

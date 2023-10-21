""" 
A file that contains all the classes needed to write to a local InfluxDB database

Currently only one class in use.
"""

from influxdb import InfluxDBClient
import socket # hostname
import os, time
import rpi_errors as rpie 


class upload_data_local_influx:
    """ 
        ## Purpose and use:
            Simple class to upload data to InfluxDB database hosted on a raspberry pi.
            Make a new object for each bucket, organization or token
        ### Methods:
            - `local_performance`: send data about cpu/ram/disk usage
            - `net_usage`: sends net usage
            - `generic`: send a generic data point
    """
    def __init__(self, ifuser: str= None,
                    ifpass:str = None, 
                    ifdb: str =None, 
                    ifhost: str= None,
                    ifport: int = None):
        """ 
        ## Simple init function, establishes connection to InfluxDB
            Following this tutorial:  https://simonhearne.com/2020/pi-metrics-influx/
        ### Arguments:
            ifuser: str= user name
            ifpass: str= password
            ifdb: str= database name
            ifhost: str= host 
            ifport: int= port number
        Raises:
            rpie.CritcalError: when you don't fill the arguments or database connection isn't working.
        """
        
        if ifuser is None:  raise rpie.CritcalError("All fields should be completed")
        if ifpass is None:     raise rpie.CritcalError("All fields should be completed")
        if ifdb is None:     raise rpie.CritcalError("All fields should be completed")
        if ifhost is None:     raise rpie.CritcalError("All fields should be completed")
        if ifport is None:   raise rpie.CritcalError("All fields should be completed")
        
        try:    
            self.client = InfluxDBClient(ifhost,ifport,ifuser,ifpass,ifdb)
        except Exception as err: 
            raise rpie.CriticalError(f"creating the influxdb client failed, the following error was encountered:\n {err}, {type(err)}")

    
    def local_performance(self, machine_name:str=None, cpu_usage:float=None, ram_usage:float=None):
        """
        ## Sends performance data
        
        Currently only logs RAM and CPU usage, should soon also log memory usage
        This method isn't that important, it only raises silent exceptions to let 
        the rest of the code run.
        
        ## Arguments:
            - `cpu_usage`:float = percentage of cpu in use
            - `ram_uage`: float = total RAM use
        
        ## Raises:
            SilentError: if the point/measurment couldn't be added to the bucket.
            
            Additionally, if the ram/cpu values, they are set to -1 and if the 
            machine name isn't added it tries to read it or is set to "Machine
            Undetected". These values are then sent to 
        """
        if cpu_usage is None or ram_usage is None: 
            raise rpie.SilentError("either ram or cpu data was not supplied")
            pass
        
        if machine_name is None:
            try:
                machine_name=socket.gethostname()
            except Exception as e:
                machine_name="Machine Undetected" 
                pass
        
        point = [{
                "measurement": machine_name,
                "time": time.time(),
                "fields": {
                    "cpu": float(cpu_usage),
                    "ram": float(ram_usage),}
                }]       
        try:
            self.client.write_points(point)
        except Exception as err:
            raise rpie.SilentError(f"cpu data was not sent to influxdb, error: {err}")
            
    def net_usage(self,machine_name:str=None, net_in:float=None, net_out:float=None):
        """
        ## Sends performance data
        
        Sends net usage data. 
        
        ## Arguments:
            - `net_in`:float = amount of data recieved
            - `net_out`: float = amount of data sent
        
        ## Raises:
            ShortError: blinks the LED shortly to let the user know data usage is unavailble,
                        it then logs the measurment if it is availble. 
        """
        if net_in is None or net_out is None: 
            raise rpie.ShortError("Some net data was not supplied")
            pass
        
        if machine_name is None:
            try:
                machine_name=socket.gethostname()
            except Exception as e:
                machine_name="Machine Undetected" 
                pass
        point = [{
                "measurement": machine_name,
                "time": time.time(),
                "fields": {
                    "net_in": float(net_in),
                    "net_out": float(net_out),}
                }]       
        try:
            self.client.write_points(point)
        except Exception as err:
            raise rpie.ShortError(f"cpu data was not sent to influxdb, error: {err}")
    
    def generic(self, data, point_name:str ="m1", tag_type:str = "tag1"):
        """
        ## Somewhat Generic data logging method
        
        Good when you are comparing different measurments of the same thing.
        Needs specific format for data.
        Args:
            data (dict): of the following shape 
                    data = {"tag 1":{"field name 1": field value 1,
                                     "field name 2": field value 2}
                            }
            point_name (str): Name of the measurement logged in InfluxDB (ie, electric_data)
            tag_type (str): Name of the tag type used (ie, house)

        Raises:
            SendingError: when data cannot be logged. The LED on the Raspberry will blink.
        """
        if data is None:
            raise rpie.CritcalError("No data was assigned to the function")
        
        point = []  
        
        # there are better ways
        try:    
            for _tag in data:
                tag_dict=data[_tag]
                for value_name in tag_dict:
                    point.append(
                        {
                        "measurement": point_name,
                        "tags":{tag_type: _tag},
                        "time": time.time(),
                        "fields": {value_name: float(tag_dict[value_name])}
                        }
                    )
        except:
            raise rpie.CriticalError(f"making the points failed, likely due to improper formating:{data}")
        
        try:
            self.client.write_points(point)
        except Exception as err:
            raise rpie.SendingError(f"at time {time.time()} the process of writing to the api failed, bucket: {self.bucket}, org: {self.org}  \
                        \n the following error was encountered: {err}, {type(err)} \n \
                            the current values: {point_name}, {tag_type}:{_tag}, {value_name}:{tag_dict[value_name]}")


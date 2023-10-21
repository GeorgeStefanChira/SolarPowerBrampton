"""
A file that contains all the classes needed to write to an influxDB Cloud database.

Currently only one class in use. 
"""


import influxdb_client, os, time
from influxdb_client.client.write_api import SYNCHRONOUS
import socket # hostname
import rpi_errors as rpie 


class upload_data_influxdb_cloud:
    """ 
        ## Purpose and use:
            Allows for easy access to influxdb cloud datase.
            Makes a new connection to the influxDB cloud whenever you make a new object.
        ### Methods:
            - `local_performance`: send data about cpu/ram/disk usage
            - `net_usage`: sends net usage
            - `generic`: send a generic data point
        
    """
    def __init__(self, bucket: str= None, org:str = None, token: str =None, url: str= None):
        """ 
        ## Simple init function, establishes connection to InfluxDB cloud
        
        ### Arguments:
            bucket : str = the database name
            org : str = organization name
            token : str = the key influxdb uses to log you into the account
            url: str = database url, similar to https://eu-central-1-1.aws.cloud2.influxdata.com
              
            For more info, check:
            https://docs.influxdata.com/influxdb/cloud/api-guide/client-libraries/python/
        
        ### Raises:
            rpie.CriticalError: when you don't fill the arguments. Can hapen when not epxorting the token properly.
        """
        
        if bucket is None:  raise rpie.CriticalError(f"{bucket} is not a valid bucket")
        if org is None:     raise rpie.CriticalError(f"{org} is not a valid org")
        if url is None:     raise rpie.CriticalError(f"{url} is not a valid url")
        if token is None:   raise rpie.CriticalError("Token was not imported from the export, or it was omitted")
        
        try:
            self.client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
            # InfluxDBClient doesn't mention raising any specific errors.
        except Exception as err: 
            raise rpie.CriticalError(f"When creating InfluxDBClient object, the following error was encountered:\n {err}, {type(err)}")
        
        try:    
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        except Exception as err: 
            raise rpie.CriticalError(f"When creating write_api object, the following error was encountered:\n {err}, {type(err)}")
        
        self.bucket=bucket
        self.org=org
    
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
        
        data={
            "cpu_usage": ["CPU", cpu_usage],
            "ram_usage": ["RAM", ram_usage]
        } 
        
        try:
            for key in data:
                #Todo: Change to a better sintax and less repetitive naming in the database
                # idea for future implementation (requires changes to the grafana server which can't be done now):
                # point_cpu =  influxdb_client.Point("local_performance").tag("Machine", machine_name).field("CPU", cpu_usage)
                # point_ram =  influxdb_client.Point("local_performance").tag("Machine", machine_name).field("RAM", ram_usage)
                # alternatively, just use Generic, but where is the fun in that?
                
                # anyway, the reason to use this method is because errors are handled silently, and I won't change this until
                # i can also change the grafana server that relies on this infobeing dleivered the same way it used to be.
                
                point = influxdb_client.Point(key).tag("Machine", machine_name).field(data[key][0], data[key][1])
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
        except Exception as err:
            raise rpie.SilentError(f"cpu data was not sent to influxdb, error: {err}")
    
    def net_usage(self,machine_name:str=None, net_in:float=None, net_out:float=None):
        """
        ## Sends performance data
        
        Sends net data. 
        
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
        
        # create dictionary were the keys are the point names : [field name, field data]
        data={
            "upload": float(net_in),
            "download": float(net_out)
        }
        
        try:
            for key in data:
                # this is good, unlike local_performance...
                point = influxdb_client.Point("network").tag("Machine", machine_name).field(key, data[key])
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
        except Exception as err:
            raise rpie.ShortError(f"net usage info could not be sent, error: {err}")
    
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
            raise rpie.CriticalError("No data was assigned to the function")
        
        for _tag in data:
            tag_dict=data[_tag] # tag1
            for value_name in tag_dict:
                try:
                    point = influxdb_client.Point(point_name).tag(tag_type, _tag).field(value_name, float(tag_dict[value_name]))
                except Exception as err: 
                    raise rpie.SendingError(f"at time {time.time()} the process of creating a measurment failed, bucket: {self.bucket}, org: {self.org}  \
                        \n the following error was encountered: {err}, {type(err)} \n \
                            the current values: {point_name}, {tag_type}:{_tag}, {value_name}:{tag_dict[value_name]}")
                try:
                    self.write_api.write(bucket=self.bucket, org=self.org, record=point)
                except Exception as err: 
                    raise rpie.SendingError(f"at time {time.time()} the process of writing to the api failed, bucket: {self.bucket}, org: {self.org}  \
                        \n the following error was encountered: {err}, {type(err)} \n \
                            the current values: {point_name}, {tag_type}:{_tag}, {value_name}:{tag_dict[value_name]}")


from ina219 import INA219  # critical for this project
from influxdb import InfluxDBClient as localInfluxDBClient # overlaps with other influx function. should really just separate them
import influxdb_client, os, time
from influxdb_client.client.write_api import SYNCHRONOUS # enable if using cloud solution
import psutil # cpu/ram/network monitoring
import socket # hostname
import numpy as np # numpy, do I need to say more

class read_data:
    """A very tailored class, specific to the project
        Takes voltage measurements using the INA219 shunt sensor
    """
    def __init__(self):
        """This code is the reporpused from the original model
            Personally I will only use it for this specific purpose
        """
        
        self.SHUNT_OHMS = 0.1
        self.MAX_EXPECTED_AMPS = 3
        


    def read_ina219(self, ina):
        """ take an ina object and use it to read voltage data

        Args:
            ina (object) 

        Returns:
            dict: {voltage: float, power: float, bus_voltage:float}
        """
        power = []
        bus_voltage=[]
        shunt_voltage=[]
        
        # measure 10 times per second
        for x in range(10):
            try:
                power.append(round(0.1*(ina.voltage()**2),3))
                bus_voltage.append(round(ina.voltage(),3))
                shunt_voltage.append(round(ina.shunt_voltage(),4))
            except Exception as err:
                print("Error encountered when measuring voltage")
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
        ina_red = INA219(self.SHUNT_OHMS, self.MAX_EXPECTED_AMPS, address=0x40)
        ina_red.configure(ina_red.RANGE_16V, ina_red.GAIN_AUTO)
        
        ina_green = INA219(self.SHUNT_OHMS, self.MAX_EXPECTED_AMPS, address=0x41)
        ina_green.configure(ina_green.RANGE_16V, ina_green.GAIN_AUTO)
        
        ina_blue = INA219(self.SHUNT_OHMS, self.MAX_EXPECTED_AMPS, address=0x44)
        ina_blue.configure(ina_blue.RANGE_16V, ina_blue.GAIN_AUTO)
        
        ina_bus = INA219(self.SHUNT_OHMS, self.MAX_EXPECTED_AMPS, address=0x44)
        ina_bus.configure(ina_blue.RANGE_16V, ina_bus.GAIN_AUTO)
        
        data= {
            "blue house": self.read_ina219(ina_blue),
            "red house": self.read_ina219(ina_red),
            "green house" :self.read_ina219(ina_green),
            "bus": self.read_ina219(ina_bus)
        }
        
        bus_voltage=0
        for key in data:bus_voltage += data[key]["bus_voltage"]
        bus_voltage /= 3
        
        data["bus_average"]= {
            "voltage": float(round(bus_voltage,3)),
            "power":float(round(0.1*(bus_voltage**2),3))
        }
        
        return data
    
    def fake_measure(self):
        """exact same as measure, but the data is random

        Returns:
            
            dict: { house/blue/green/red/bus: read_fake_ina(), bus_average: {voltage: float, power: float}}
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
    
    def read_fake_ina219(self, x):
        """mimics read_ina but without using ina obects 
        (to test code when the parts are not connected)

        Args:
            x (int): place holder to ina

        Returns:
            dict: {voltage: float, power: float, bus_voltage:float}
        """
        result = {
            "voltage": float(x*np.sin(time.time_ns())),
            "power": float(x*np.sin(time.time_ns())),
            "bus_voltage": float(x*np.sin(time.time_ns()))
        }
        return result
    
    def measure_cpu(self):
        """measure cpu and ram use
        
        Returns:
            float, float
        """
        cpu_usage=psutil.cpu_percent(1)*100.0
        ram_usage=psutil.virtual_memory().percent*10.0

        
        # create dictionary were the keys are the point names : [field name, field data]

        return cpu_usage, ram_usage
    
    def measure_network(self):
        """measures network data sent at a certain moment

        Returns:
            float, float: current data use
        """
        net_stat = psutil.net_io_counters(pernic=True)["eth0"]
        net_in = net_stat.bytes_recv
        net_out = net_stat.bytes_sent

        return net_in,net_out
        
class upload_data_influxdb_cloud:
    """ 
        Simple class to upload data to InfluxDB cloud. Use only for cloud
        Make a new object for each bucket, organization or token
        Use the log functions to upload measurements/points
        
        Only raises errors on login. Once you set it up it should never stop
    """
    def __init__(self, bucket: str= None, org:str = None, token: str =None, url: str= None):
        """ Simple init function, establishes connection to InfluxDB cloud
        
        Arguments:
            bucket : str = the database name
            org : str = organization name
            token : str = the key influxdb uses to log you into the account
            url: str = database url, similar to https://eu-central-1-1.aws.cloud2.influxdata.com
              
            You should be familiar with all Arguments in this function, if not check:
            https://docs.influxdata.com/influxdb/cloud/api-guide/client-libraries/python/
        
        Raises:
            ValueError: when you don't fill the arguments. Can hapen when not epxorting the token properly.
        """
        
        if bucket is None:  raise ValueError("All fields should be completed")
        if org is None:     raise ValueError("All fields should be completed")
        if url is None:     raise ValueError("All fields should be completed")
        if token is None:   raise ValueError("Token was not imported from the export, or it was omitted")
        
        try:    
            self.client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
        except Exception as err: 
            raise ConnectionError(f"creating the influxdb client failed, the following error was encountered:\n {err}, {type(err)}")
        
        try:    
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        except Exception as err: 
            raise ConnectionError(f"crieting write_api object failed, the following error was encountered:\n {err}, {type(err)}")
        
        self.bucket=bucket
        self.org=org
    
    def cpu_data(self, cpu_usage, ram_usage):
        """Simple function to log some CPU/RAM data, will redo later as it can cause issues. He said.
        """
        machine_name=socket.gethostname()
        data={
            "cpu_usage": ["CPU", cpu_usage],
            "ram_usage": ["RAM", ram_usage]
        } # not ideal
        try:
            for key in data:
                point = influxdb_client.Point(key).tag("Machine", machine_name).field(data[key][0], data[key][1])
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
        except Exception as err:
            print(f"cpu data was not sent to influxdb, error: {err}")
            
    def net_usage(self, net_in, net_out):
        """send net data

        Args:
            net_in (float): _description_
            net_out (float): _description_
        """
        machine_name=socket.gethostname()
        # create dictionary were the keys are the point names : [field name, field data]
        data={
            "upload": float(net_in),
            "download": float(net_out)
        }
        try:
            for key in data:
                point = influxdb_client.Point("network").tag("Machine", machine_name).field(key, data[key])
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
        except Exception as err:
            print(f"net usage info could not be sent, error: {err}")
    def generic(self, data, point_name:str ="m1", tag_name:str = "tag1"):
        """
        A somewhat generic way to log data into influxDB cloud.
        Good when you are comparing different measurments of the same thing.
        Example: the power generated from multiple solar panels.

        Args:
            point_name (str): Name of the _measurment logged in InfluxDB 
            data (dict): of the following shape 
                    data = {"tag1":{"field1": field value1,
                                    "field2": field value2}
                            }
                    data = 
        """
        if data is None:
            raise ValueError("No data was assigned to the function")
        
        for _tag in data:
            tag_dict=data[_tag] # tag1
            for value_name in tag_dict:
                try:
                    point = influxdb_client.Point(point_name).tag(tag_name, _tag).field(value_name, float(tag_dict[value_name]))
                except Exception as err: 
                    print(f"at time {time.time()} the process of creating a measurment failed, bucket: {self.bucket}, org: {self.org}  \
                        \n the following error was encountered: {err}, {type(err)} \n \
                            the current values: {point_name}, {tag_name}:{_tag}, {value_name}:{tag_dict[value_name]}")
                try:
                    self.write_api.write(bucket=self.bucket, org=self.org, record=point)
                except Exception as err: 
                    print(f"at time {time.time()} the process of writing to the api failed, bucket: {self.bucket}, org: {self.org}  \
                        \n the following error was encountered: {err}, {type(err)} \n \
                            the current values: {point_name}, {tag_name}:{_tag}, {value_name}:{tag_dict[value_name]}")

class upload_data_local_influx:
    """ 
        Simple class to upload data to InfluxDB hosted on a raspberry pi.
        Make a new object for each bucket, organization or token
        Use the log functions to upload measurements/points
        
        Only raises errors on login. Once you set it up it should never stop
    """
    def __init__(self, ifuser: str= None,
                    ifpass:str = None, 
                    ifdb: str =None, 
                    ifhost: str= None,
                    ifport: int = None):
        """ Simple init function, establishes connection to InfluxDB
            Following this tutorial:  https://simonhearne.com/2020/pi-metrics-influx/
        Arguments:

        Raises:
            ValueError: when you don't fill the arguments. Can hapen when not epxorting the token properly.
        """
        
        if ifuser is None:  raise ValueError("All fields should be completed")
        if ifpass is None:     raise ValueError("All fields should be completed")
        if ifdb is None:     raise ValueError("All fields should be completed")
        if ifhost is None:     raise ValueError("All fields should be completed")
        if ifport is None:   raise ValueError("Make sure you get the port ")
        
        try:    
            self.client = localInfluxDBClient(ifhost,ifport,ifuser,ifpass,ifdb)
        except Exception as err: 
            raise ConnectionError(f"creating the influxdb client failed, the following error was encountered:\n {err}, {type(err)}")

    
    def cpu_data(self, cpu, ram):
        """Simple function to log some CPU/RAM data, will redo later as it can cause issues. He said.
        """
        machine_name=socket.gethostname()
        point = [{
                "measurement": machine_name,
                "time": time.time(),
                "fields": {
                    "cpu": float(cpu),
                    "ram": float(ram),}
                }]       
        try:
            self.client.write_points(point)
        except Exception as err:
            print(f"cpu data was not sent to influxdb, error: {err}")
            
    def net_usage(self, net_in, net_out):
        """
        this should be rewritten, works but its a bit trash
        """ 
        machine_name=socket.gethostname()
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
            print(f"cpu data was not sent to influxdb, error: {err}")
    
    def generic(self, data, point_name:str ="m1", tag_name:str = "tag1"):
        """
        A somewhat generic way to log data into influxDB cloud.
        Good when you are comparing different measurments of the same thing.
        Example: the power generated from multiple solar panels.

        Args:
            point_name (str): Name of the _measurment logged in InfluxDB 
            data (dict): of the following shape 
                    data = {"tag1":{"field1": field value1,
                                    "field2": field value2}
                            }
            
            
        """
        if data is None:
            raise ValueError("No data was assigned to the function")
        
        point = []  
        
        # there are better ways
        try:    
            for _tag in data:
                tag_dict=data[_tag]
                for value_name in tag_dict:
                    point.append(
                        {
                        "measurement": point_name,
                        "tags":{ tag_name: _tag},
                        "time": time.time(),
                        "fields": {value_name, float(tag_dict[value_name])}
                        }
                    )
        except:
            print("makeing the points failed")
        
        try:
            self.client.write_points(point)
        except Exception as err:
            print(f"sending data has failed, error {err}")
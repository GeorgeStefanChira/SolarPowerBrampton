import influxdb_client, os, time
import numpy as np
from influxdb_client.client.write_api import SYNCHRONOUS
import psutil 
import socket


class read_data:
    """A very tailored class, specific to the project
        Takes voltage measurements using the INA219 shunt sensor
    """
    def __init__(self):
        """This code is the reporpused from the original model
            Personally I will only use it for a specific purpose
        """
        
        # SHUNT_OHMS = 0.1
        # MAX_EXPECTED_AMPS = 3
        


    def read_ina219(ina):
        
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
    
    def measure(self, SHUNT_OHMS, MAX_EXPECTED_AMPS, address):
        ina_red = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address)
        ina_red.configure(ina_red.RANGE_16V, ina_red.GAIN_AUTO)
        
        ina_green = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address)
        ina_green.configure(ina_green.RANGE_16V, ina_green.GAIN_AUTO)
        
        ina_blue = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address)
        ina_blue.configure(ina_blue.RANGE_16V, ina_blue.GAIN_AUTO)
        
        data= {
            "blue house": self.read_ina219(ina_blue),
            "red house": self.read_ina219(ina_red),
            "green house" :self.read_ina219(ina_green) 
        }
        
        bus_voltage=0
        for key in data:bus_voltage += data[key]["bus_voltage"]
        bus_voltage /= 3
        
        data["bus_average"]= {
            "voltage": float(round(bus_voltage,3)),
            "power":float(round(0.1*(bus_voltage**2),3))
        }
        
        return data
    
    def fake_measure(self, x1,x2,x3):
        data= {
            "blue house": self.read_fake_ina219(x1),
            "red house": self.read_fake_ina219(x2),
            "green house" :self.read_fake_ina219(x3) 
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
        result = {
            "voltage": float(x*np.sin(time.time_ns())),
            "power": float(x*np.sin(time.time_ns())),
            "bus_voltage": float(x*np.sin(time.time_ns()))
        }
        return result
    
    def create_false_data(self):
        t_now = 2*np.pi* time.time_ns()*1e-9
        data = {
            "blue house": {"voltage":float(20.0*np.sin(t_now+0)),
                           "battery": float(50-10*np.sin(t_now+0)),
                           "power":float(2.0*np.cos(t_now+0)),
                           "savings":float(200*np.sin(t_now+30))
                           },
            "red house": {"voltage":float(50.0*np.sin(t_now+20)),
                           "battery": float(50-20*np.sin(t_now+20)),
                           "power":float(5.0*np.cos(t_now+20)),
                           "savings":float(200*np.sin(t_now+20))},
            "green house": {"voltage":float(40.0*np.sin(t_now+40)),
                           "battery": float(50-10*np.sin(t_now+40)),
                           "power":float(4.0*np.cos(t_now+40)),
                           "savings":float(200*np.sin(t_now+10))},
            "bus average":{ "voltage":float(50.0*np.sin(t_now+50)),
                           "power":float(8.0*np.cos(t_now+50))}
        }
        return data
    
    def measure_network(self):
        net_stat = psutil.net_io_counters(pernic=True)["eth0"]
        net_in = net_stat.bytes_recv
        net_out = net_stat.bytes_sent

        return net_in,net_out
        
class upload_data:
    """ Simple class to upload data to InfluxDB
        Make a new object for each bucket, organization or token
        Use the log functions to upload measurements/points
        Should not stop due to errors, just prints them.
    """
    def __init__(self, bucket: str= None, org:str = None, token: str =None, url: str= None):
        """ Simple init function, establishes connection to InfluxDB cloud
        
        Arguments:
            You should be familiar with all Arguments in this function, if not check:
            https://docs.influxdata.com/influxdb/cloud/api-guide/client-libraries/python/
        
        Raises:
            ValueError: when you don't fill the arguments. Can hapen when not epxorting the token properly
        """
        
        if bucket is None:  raise ValueError("All fields should be completed")
        if org is None:     raise ValueError("All fields should be completed")
        if url is None:     raise ValueError("All fields should be completed")
        if token is None:   raise ValueError("Token was not imported from the export, or it was omitted")
        
        # a bit of shadowing never hurt nobody (except for all those headaches when you get random errors)
        try:    
            self.client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        except Exception as err: 
            print(f"Connecting to InfluxDB cloud failed, the following error was encountered:\n {err}, {type(err)}")
        self.bucket=bucket
        self.org=org
        # Synchronus because that's what the tutorial says
    
    def log_cpu_data(self):
        """Simple function to log some CPU/RAM data, will redo later as it can cause issues.
        """
        cpu_usage=psutil.cpu_percent(1)*100.0
        ram_usage=psutil.virtual_memory().percent*10.0
        machine_name=socket.gethostname()
        
        # create dictionary were the keys are the point names : [field name, field data]
        data={
            "cpu_usage": ["CPU", cpu_usage],
            "ram_usage": ["RAM", ram_usage]
        }
        
        for key in data:
            point = influxdb_client.Point(key).tag("Machine", machine_name).field(data[key][0], data[key][1])
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
    
    # def net_usage(self, net_in_1, net_out_1, net_in_2, net_out_2):
    #     """
    #     part of the code is from here: https://stackoverflow.com/questions/62020140/psutil-network-monitoring-script
    #     modifoed to expot data
    #     """ 

    #     net_in = round((net_in_2 - net_in_1) / 1024 / 1024, 3)
    #     net_out = round((net_out_2 - net_out_1) / 1024 / 1024, 3)

    #     machine_name=socket.gethostname()
    #     # create dictionary were the keys are the point names : [field name, field data]
    #     data={
    #         "upload": ["MB", net_out],
    #         "download": ["MB", net_in]
    #     }
        
    #     for key in data:
    #         point = influxdb_client.Point(key).tag("Machine", machine_name).field(data[key][0], data[key][1])
    #         self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def net_usage(self):
        """
        part of the code is from here: https://stackoverflow.com/questions/62020140/psutil-network-monitoring-script
        modifoed to expot data
        """ 
        
        net_stat = psutil.net_io_counters(pernic=True)["eth0"]
        net_in = round(net_stat.bytes_recv / 1024 /1024, 3)
        net_out = round(net_stat.bytes_sent / 1024 /1024, 3)
        
        machine_name=socket.gethostname()
        # create dictionary were the keys are the point names : [field name, field data]
        data={
            "upload": net_in,
            "download": net_out
        }
        
        for key in data:
            point = influxdb_client.Point("network").tag("Machine", machine_name).field(key, data[key])
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
        
    
    def log_generic(self, data,point_name:str ="m1", tag_name:str = "tag1"):
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
        
        for _tag in data:
            tag_dict=data[_tag] # tag1
            for value_name in tag_dict:
                try:
                    point = influxdb_client.Point(point_name).tag(tag_name, _tag).field(value_name, float(tag_dict[value_name]))
                except Exception as err: 
                    raise(f"at time {time.time()} the process of creating a measurment failed, bucket: {self.bucket}, org: {self.org}  \
                        \n the following error was encountered: {err}, {type(err)} \n \
                            the current values: {point_name}, {tag_name}:{_tag}, {value_name}:{tag_dict[value_name]}")
                try:
                    self.write_api.write(bucket=self.bucket, org=self.org, record=point)
                except Exception as err: 
                    raise(f"at time {time.time()} the process of writing to the api failed, bucket: {self.bucket}, org: {self.org}  \
                        \n the following error was encountered: {err}, {type(err)} \n \
                            the current values: {point_name}, {tag_name}:{_tag}, {value_name}:{tag_dict[value_name]}")
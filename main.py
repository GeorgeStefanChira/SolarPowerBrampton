import time, os
import pathlib
path=pathlib.Path(__file__).parent.resolve()
print(path)
from on_start import check_code
check = check_code(path)

import tools
import rpi_errors as rpie
from local_solution import upload_data_local_influx
from cloud_solution import upload_data_influxdb_cloud

if __name__== "__main__":
    
    # get the config values
    config = tools.read_config(f"{path}/config.ini")
    
    use_cloud_solution, use_fake = config.get_methods()
    total_time, endless = config.get_time() 
    
    if use_cloud_solution:
        cloud_dir = config.get_cloud()
        send = upload_data_influxdb_cloud(bucket=cloud_dir["bucket"],
                                            org=cloud_dir["org"],
                                            token= cloud_dir["token"],
                                            url=cloud_dir["url"]) 
    else:    
        local_dir = config.get_local()
        send = upload_data_local_influx(ifuser=local_dir["ifuser"],
                                        ifpass=local_dir["ifpass"],
                                        ifdb=local_dir["ifdb"],
                                        ifhost=local_dir["ifhost"],
                                        ifport= local_dir["ifport"]) 

    if use_fake:
        model = tools.read_fake_data()
    else:
        model = tools.read_data()
    
    # hold the last network usage
    # the way the function works is by getting the total upload/download at the check
    # so you take one measurement at start and then one every step, take the difference, send that
    # and then save the last measurement. Now you have data from a whole loop, including sending the
    # network data.
    hash_netin1, hash_netout2 = model.measure_network()
    
    name = model.get_name()
    i=0
    while i< total_time:
        start_time=time.time_ns() 
        
        rpie.turn_led(True)
        time.sleep(0.1)
        rpie.turn_led(False)
        time.sleep(0.1)
        rpie.turn_led(True)
        time.sleep(0.2)
        rpie.turn_led(False)
        
        # net measuring part
        net_in, net_out = model.measure_network()
        send.net_usage(net_in=( (net_in-hash_netin1) /1024 /1024), net_out=((net_out-hash_netout2) / 1024 /1024))
        hash_netin1, hash_netout2 = net_in, net_out
        
        # send cpu and ram data 
        cpu,ram = model.measure_cpu()
        send.local_performance(machine_name=name,cpu_usage= cpu,ram_usage= ram)
        
        # voltage from the model
        data = model.measure()
        send.generic(data=data,point_name="Electricity Gen",tag_type="House")
        

        end_time=time.time_ns()
        
        time_elapsed = (end_time-start_time)*1e-9  # 1e-9 because nanoseconds
        
        # make sure a loop takes about 3 seconds.
        # if it' longer but still acceptable (10), then just send a short error
        # if it's shorter than 0, time travel (or trivial bug) -> short error
        # if the absolute value is larger than 10, then there is a big problem with the code
        
        
        if time_elapsed > 4 and time_elapsed <10:
            rpie.ShortError(f"Total loop time: {time_elapsed} is {time_elapsed-3} longer than expected")
        elif time_elapsed < 0 :
            rpie.ShortError(f"Time travel discovered! We have returned {time_elapsed} seconds in the past! Initial time at {start_time}, final: {end_time}")
        elif abs(time_elapsed) >10:
            raise rpie.CriticalError(f"This code is to buggy to work within it's time paramenters. Maintance required. Loop took {time_elapsed} seconds")
        else:
            duration=max(1,(3-time_elapsed))  
            time.sleep(duration)
        
        if endless: i+=1
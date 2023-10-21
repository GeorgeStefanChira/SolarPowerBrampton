import tools
import rpi_errors as rpie
from local_solution import upload_data_local_influx
from cloud_solution import upload_data_influxdb_cloud
import time, os

if __name__== "__main__":
    
    # get the config values
    
    cloud_database = True  
    use_fake = True
    
    if cloud_database:
        send = upload_data_influxdb_cloud(bucket="Solar Power",
                                            org="B2Z",
                                            token= os.environ.get("INFLUXDB_TOKEN"),
                                            url="https://eu-central-1-1.aws.cloud2.influxdata.com") 
    else:    
        send = upload_data_local_influx(ifuser="admin",
                                        ifpass="you_thought_this_was_it",
                                        ifdb="b2z",
                                        ifhost="",
                                        ifport= 8086) 

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
    
    for i in range(360):
        start_time=time.time_ns() 
        
        # net measuring part
        net_in, net_out = model.measure_network()
        send.net_usage(net_in=( (net_in-hash_netin1) /1024 /1024), net_out=((net_out-hash_netout2) / 1024 /1024))
        hash_netin1, hash_netout2 = net_in, net_out
        
        # send cpu and ram data 
        cpu,ram = model.measure_cpu()
        send.cpu_data(cpu,ram)
        
        # voltage from the model
        data = model.measure()
        send.generic(data=data,point_name="Electricity Gen",tag_name="House")
        

        end_time=time.time_ns()
        
        time_elapsed = (end_time-start_time)*1e-9  # 1e-9 because nanoseconds
        
        # make sure a loop takes about 3 seconds.
        # if it' longer but still acceptable (10), then just send a short error
        # if it's shorter than 0, time travel (or trivial bug) -> short error
        # if the absolute value is larger than 10, then there is a big problem with the code
        if time_elapsed > 3 and time_elapsed <10:
            raise rpie.ShortError(f"Total loop time: {time_elapsed} is {time_elapsed-3} longer than expected")
        elif time_elapsed < 0 :
            raise rpie.ShortError(f"Time travel discovered! We have returned {time_elapsed} seconds in the past! Initial time at {start_time}, final: {end_time}")
        elif abs(time_elapsed) >10:
            raise rpie.CriticalError(f"This code is to buggy to work within it's time paramenters. Maintance required. Loop took {time_elapsed} seconds")
        else:
            duration=max(1,(3-time_elapsed))  
            time.sleep(duration)
        
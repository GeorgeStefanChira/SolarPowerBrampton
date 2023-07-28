from tools import upload_data_influxdb_cloud, upload_data_local_influx, read_data
import time, os

if __name__== "__main__":
    # send = upload_data_influxdb_cloud(bucket="Solar-Power",
    #                                     org="B2Z",
    #                                     token= os.environ.get("INFLUXDB_TOKEN"),
    #                                     url="https://eu-central-1-1.aws.cloud2.influxdata.com") 
    
    send = upload_data_local_influx(ifuser="admin",
                                    ifpass="you_thought_this_was_it",
                                    ifdb="b2z",
                                    ifhost="",
                                    ifport= 8086) 
 
    
    
    model = read_data()
    
    
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
        data = model.measure_cpu()
        send.cpu_data(data)
        
        # voltage from the model
        data = model.fake_measure()
        send.generic(data=data,point_name="Electricity Gen",tag_name="House")
        

        end_time=time.time_ns()
        # make sure it's every 10 seconds -ish
        duration=max(1,(10+(start_time-end_time)*1e-9)) # 1e-9 because nanoseconds 
        time.sleep(duration)
        
from tools import upload_data, read_data
import time, os

if __name__== "__main__":
    upload_model_to_cloud = upload_data(bucket="Solar Power",
                                        org="B2Z",
                                        token= os.environ.get("INFLUXDB_TOKEN"),
                                        url="https://eu-central-1-1.aws.cloud2.influxdata.com") 
    
    get_data_model = read_data()
    
    hash_netin1, hash_netout2 = 0.0, 0.0

    for i in range(360):
        start_time=time.time_ns()
        
        
        # net measuring part
        net_in, net_out = get_data_model.measure_network()
        
        net_in  = (net_in-hash_netin1) /1024 /1024
        net_out = (net_out-hash_netout2) / 1024 /1024
        
        hash_netin1, hash_netout2 =get_data_model.measure_network()
        
        upload_model_to_cloud.net_usage(net_in=net_in, net_out=net_out)
        
        
        # send cpu and ram data 
        upload_model_to_cloud.log_cpu_data()
        data = get_data_model.measure()
        upload_model_to_cloud.log_generic(data=data,point_name="Electricity Gen",tag_name="House")
        
        
        
        end_time=time.time_ns()
        duration=max(1,(10+(start_time-end_time)*1e-9)) 
        print(duration, end_time, start_time)
        time.sleep(duration)
        
from tools import upload_data, read_data
import time, os

if __name__== "__main__":
    upload_model_to_cloud = upload_data(bucket="Solar Power",
                                        org="B2Z",
                                        token= os.environ.get("INFLUXDB_TOKEN"),
                                        url="https://eu-central-1-1.aws.cloud2.influxdata.com") 
    
    get_data_model = read_data()
    

    for i in range(360):
        start_time=time.time_ns()
        
        upload_model_to_cloud.net_usage()
        
        upload_model_to_cloud.log_cpu_data()
        data = get_data_model.fake_measure(10,23,45)
        upload_model_to_cloud.log_generic(data=data,point_name="Electricity Gen",tag_name="House")
        
        
        
        end_time=time.time_ns()
        duration=max(1,(10+(start_time-end_time)*1e-9)) 
        print(duration, end_time, start_time)
        time.sleep(duration)
        
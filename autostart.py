"""
A file that runs whenever the Raspberry Pi is powered.

This file checks for:

- os
- internet connectivity 
- any missing files/dependencies 
- any updates from the gitfile

It then:

- updates the software
- reads config files
- saves error log
- file management
- starts code 

If configured on cloud:
- check server connection to influxDB with token list
- check website

If configured locally:
-check database is open
-check grafana is ready
-open webpage 

"""

import os, time

required_files= ["main.py", "tools.py", "autostart.py", "requirements.txt"]

def check_files(dirpath:str, files:[str,...]):
    error_list=[]
    for file in files:
        if os.path.isfile((dirpath+file)):
            print(f"CRITCAL ERROR! file {file} could not be found!")
            error_list.append(file)
    if len(error_list) != 0:
        # reinstall from git
        pass
    
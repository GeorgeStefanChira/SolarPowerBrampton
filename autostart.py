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
import subprocess 
import rpi_errors as rpie
required_files= ["main.py", "tools.py", "autostart.py", "requirements.txt"]

def check_files(dirpath:str=None, files:[str,...]=None):
    if dirpath is None: dirpath= ""
    if files is None: 
        files= ["main.py","cloud_solution.py", "local_solution.py","rpi_errors.py",
                "tools.py", "requirements.txt", "config.ini"]
    if not os.path.isfile((dirpath+"errorfile.txt")):
        with open(file="errorfile.txt",mode="a") as errfile:
            date = time.localtime()
            errfile.write(f"|   Error log was created at {date.tm_year}/{date.tm_mon}/{date.tm_mday}/{date.tm_hour}:{date.tm_min}:{date.tm_sec}   |")
            errfile.write("\n####################################################")
    
    for file in files:
        if not os.path.isfile((dirpath+file)):
            rpie.ShortError(f"{file} is missing. Attempting install")
            # reinstall from git
            try:
                copy_file = subprocess.run(["wget", f"https://raw.github.com/GeorgeStefanChira/SolarPowerBrampton/{file}"], 
                                  stdout=subprocess.PIPE, 
                                  text=True,
                                   check=True)
            except Exception as err:
                raise rpie.CriticalError(f"Failed to copy file {file}. Critical part missing, error encountered: {err}")
            
def update_dependecies():
    """
    Will automatically call pip to check on requirements.txt
    
    https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program

    Raises:
        rpie.CriticalError: when something doesn't work
    """
    try:
        copy_file = subprocess.run(["python3", "pip", "install", "-r", "requirements.txt"], 
                            stdout=subprocess.PIPE, 
                            text=True,
                            check=True)
        print(copy_file.returncode, copy_file.stderr, copy_file.stdout)
    except Exception as err:
        raise rpie.CriticalError(f"When updating dependencies the following error was encountered:{err}")

update_dependecies()
print("did it work")
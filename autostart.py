"""
## Automatic setup and maintainance. 

This file contains a seroes of methods used to check for code integrity and setting up the Raspberry Pi.
It's meant to work even if you onlhy have python 3.11 installed. Everything else can be installed 
At this point I should probably package this up.

This file checks for:
- OS - Done 
- internet connectivity  - Done
- any missing files/dependencies -Done
- any updates from the gitfile  
- code starting at startup 

It then:

- replaces any missing files - Done
- updates files 
- installs requirements -Done
- file management (removes error logs if they are larger than 100 mb) -Done


If configured locally:
-check database exists
-check if its open

"""

# none of the imports can be external or require network
import os,sys, time
import subprocess 
import platform 

def log_error(mssg:str=None):
    if mssg is None:
        raise TypeError("Unspecified error ecountered")
    with open(file=f"errorfile.txt",mode="a+") as errorlog:
        date= time.localtime()
        errorlog.write(f"{date.tm_year}/{date.tm_mon}/{date.tm_mday}/{date.tm_hour}:{date.tm_min}:{date.tm_sec}| {mssg} \n")
    print(mssg)

def crit_error(mssg:str=None):
    if mssg is None:
        raise TypeError("Unspecified error ecountered")
    with open(file=f"errorfile.txt",mode="a+") as errorlog:
        date= time.localtime()
        errorlog.write(f"{date.tm_year}/{date.tm_mon}/{date.tm_mday}/{date.tm_hour}:{date.tm_min}:{date.tm_sec}| {mssg} \n")
    raise TypeError(mssg)

def create_errorfile(file):
    with open(file=file,mode="a") as errfile:
        date = time.localtime()
        errfile.write("\n#################################################### \n")
        errfile.write(f"#   Error log was created at {date.tm_year}/{date.tm_mon}/{date.tm_mday}/{date.tm_hour}:{date.tm_min}:{date.tm_sec}    #")
        errfile.write("\n#################################################### \n")
        
def check_files(dirpath:str=None, files:[str,...]=None):
    if dirpath is None: dirpath= ""
    if files is None: 
        files= ["main.py","cloud_solution.py", "local_solution.py","rpi_errors.py",
                "tools.py", "requirements.txt", "config.ini"]
    errorfile=f"{dirpath}errorfile.txt"
    
    # The errorfile has to be handled separate
    if os.path.isfile((errorfile)): 
        try: size = os.path.getsize(errorfile)
        except Exception as err:
            size = 0
            log_error(f"errorfile.txt exists but system could not find its size. Error: {err}")
        # make sure we don't overload the RPi with errors
        if size > 1e8: # 1e8 is 100 Mb
            if os.path.isfile(f"{dirpath}errorfile_old.txt"): os.remove(f"{dirpath}errorfile_old.txt") 
            os.rename(errorfile, f"{dirpath}errorfile_old.txt") # we keep the old one when it reaches 100 Mb 
            # the maximum size of errors is 200 Mb of data, plenty for debugging and not more than the RPi can handle
            os.remove(errorfile)
            create_errorfile
    create_errorfile(errorfile) # This will either create the error file or log the start

    # the other files are pulled from git
    #TODO: replace with git api
    for file in files:
        if not os.path.isfile((dirpath+file)):
            log_error(f"{file} is missing. Attempting install")
            # reinstall from git
            try:
                copy_file = subprocess.run(["wget", f"https://raw.github.com/GeorgeStefanChira/SolarPowerBrampton/{file}"], 
                                  stdout=subprocess.PIPE, 
                                  text=True,
                                   check=True)
            except Exception as err:
                crit_error(f"Failed to copy file {file}. Critical part missing, error encountered: {err}")
            
def check_dependecies():
    """
    Will automatically call pip to check on requirements.txt
    
    https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program

    Raises:
        crit-error: when something doesn't work
    """
    try:
        pip_install = subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    except Exception as err:
        crit_error(f"When updating dependencies the following error was encountered:{err}")

def check_OS():
    """ uses pltform.system to check for Raspberrr OS   """
    os=platform.system()
    if os == 'Raspbian GNU/Linux':
        return 
    crit_error(f"This code can olny work on Raspbian/ Raspberry OS. Your system runs {os}")

def check_network( host:str="google.com" ):
    """### Pings google and listens
    
    This method tries to detect network connection without requiering external libraries
    
    """
    response = subprocess.call(['ping', '-c', '1', host])

    # exit if network connection worked
    if response == 0: 
        # try github for the fun of it (make sure its not under maintance)
        gitresponse = os.system("ping -c 1 github.com")
        if gitresponse == 0: 
            print("Network fully functional")
            return 
        log_error("Github could not be reached at this time")
    log_error(f"Internet not availble or host {host} is down")

check_files()
check_dependecies()
check_network()
check_OS()
print("did it work")
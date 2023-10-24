"""
## Auto maintanance

This file contains a seroes of methods used to check for code integrity and setting up the Raspberry Pi.
It's meant to work even if you only have python 3.11 installed. Everything else can be installed 

"""

# none of the imports can be external or require network
import os,sys, time
import subprocess 
import platform 

class check_code:
    def __init__(self, path) -> None:
        """## Verify code before start
        
         This class checks for:
            - OS 
            - internet connectivity 
            - any missing files/dependencies
            - file management (removes error logs if they are larger than 100 mb)

        """
        self.path= path
        self.errorfile = f"{path}/errorfile.txt"

        self.check_OS()
        self.check_network()
        self.check_files()
        self.check_dependecies()
        
        # set the led up
        
        try:
            import RPi.GPIO as GPIO

            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(18,GPIO.OUT)
        
            for i in range(10):
                GPIO.output(18,GPIO.HIGH)
                time.sleep(1)
                GPIO.output(18,GPIO.LOW)
                time.sleep(0.5)
        except RuntimeError as err:
            print(f"The blinking is disabled on WSL: \n {err}")    
        # The following code is for onboard led:
        # I commented it out because it doesn't work for my board but you might want 
        # to try and waste your time too! If you get it running, well, let me know!
        
        # try:
        #     os.system('echo gpio | sudo tee /sys/class/leds/led0/trigger')
        # except:
        #     print("Led could not be set up, errors not visible!")
    
    def log_error(self, mssg:str=None):
        if mssg is None:
            raise TypeError("Unspecified error ecountered")
        with open(file=self.errorfile,mode="a+") as errorlog:
            date= time.localtime()
            errorlog.write(f"{date.tm_year}/{date.tm_mon}/{date.tm_mday}/{date.tm_hour}:{date.tm_min}:{date.tm_sec}| {mssg} \n")
        print(mssg)

    def crit_error(self, mssg:str=None):
        if mssg is None:
            raise TypeError("Unspecified error ecountered")
        with open(file=self.errorfile,mode="a+") as errorlog:
            date= time.localtime()
            errorlog.write(f"{date.tm_year}/{date.tm_mon}/{date.tm_mday}/{date.tm_hour}:{date.tm_min}:{date.tm_sec}| {mssg} \n")
        raise TypeError(mssg)

    def create_errorfile(self):
        with open(file=self.errorfile,mode="a") as errfile:
            date = time.localtime()
            errfile.write("\n#################################################### \n")
            errfile.write(f"#   Error log was created at {date.tm_year}/{date.tm_mon}/{date.tm_mday}/{date.tm_hour}:{date.tm_min}:{date.tm_sec}    #")
            errfile.write("\n#################################################### \n")
            
    def check_files(self, files:[str,...]=None):
        if files is None: 
            files= ["cloud_solution.py", "local_solution.py","rpi_errors.py",
                    "tools.py", "requirements.txt", "config.ini"]
        
        # The errorfile has to be handled separate
        if os.path.isfile((self.errorfile)): 
            try: size = os.path.getsize(self.errorfile)
            except Exception as err:
                size = 0
                self.log_error(f"errorfile.txt exists but system could not find its size. Error: {err}")
            # make sure we don't overload the RPi with errors
            if size > 1e8: # 1e8 is 100 Mb
                if os.path.isfile(f"errorfile_old.txt"): os.remove(f"errorfile_old.txt") 
                os.rename(self.errorfile, f"errorfile_old.txt") # we keep the old one when it reaches 100 Mb 
                # the maximum size of errors is 200 Mb of data, plenty for debugging and not more than the RPi can handle
                os.remove(self.errorfile)
                self.create_errorfile()
        self.create_errorfile() # This will either create the error file or log the start

        # the other files are pulled from git
        for file in files:
            if not os.path.isfile((f"{self.path}/{file}")):
                self.log_error(f"{file} is missing. Attempting install")
                # reinstall from git
                try:
                    copy_file = subprocess.run(["wget", f"https://raw.github.com/GeorgeStefanChira/SolarPowerBrampton/{file}"], 
                                    stdout=subprocess.PIPE, 
                                    text=True,
                                    check=True)
                except Exception as err:
                    self.crit_error(f"Failed to copy file {file}. Critical part missing, error encountered: {err}")
                
    def check_dependecies(self):
        """
        Will automatically call pip to check on requirements.txt
        
        https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program

        Raises:
            crit-error: when something doesn't work
        """
        try:
            pip_install = subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', f'{self.path}/requirements.txt'])
        except Exception as err:
            self.crit_error(f"When updating dependencies the following error was encountered:{err}")

    def check_OS(self):
        """ uses pltform.system to check for Raspberrr OS   """
        os=platform.system()
        if os == 'Linux':
            return 
        self.crit_error(f"This code can olny work on Raspbian/ Raspberry OS. Your system runs {os}")

    def check_network(self, host:str="google.com" ):
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
            self.log_error("Github could not be reached at this time")
        self.log_error(f"Internet not availble or host {host} is down")

""" 
## Raspberry Pi specific errors

This software is meant to work on a raspberry pi when there isn't a monitor or someone with
programing experience. Errors must then be handeled different.

TODO Add the blink function. 
This is a bit of an issue, as currently I want to use the on board LEDs from the raspberry pi
[the project this is meant for is no longer accessible to me so I can't add any LEDs].
I will try this latter as I get my own raspberry set up:
https://forums.raspberrypi.com/viewtopic.php?p=136266&sid=3132a8d0ff07cb506a027c50d7553a2b#p136266


### Error Types available

    1. CriticalError:
        Only called when the code wouldn't function and require maintance. 
        
    2. fixable error:
        - Internet connection Error / data sending error
        
    3. Reportable Error:
        Data collection error
        
    - Files missing / wrong os
    - Databasse not availble
    - Interface error
    - Data collection 
"""
# import RPi.GPIO as GPIO
import time

def Blink(number:int=None):
    if number is None: pass
    for i in range(0,number):
        print("blinking")
     
def Record(message:str="Generic Error"):
    
    with open(file=f"errorfile.txt",mode="a+") as errorlog:
        date= time.localtime()
        errorlog.write(f"{date.tm_year}/{date.tm_mon}/{date.tm_mday}/{date.tm_hour}:{date.tm_min}:{date.tm_sec}| {message} \n")
        
class CriticalError(Exception):
    def __init__(self, msg:str=None) -> None:
        """
        Stops the code during run and raises a normal dev error.
        Unlike normal error, it also turns the LED on or off and
        saves the error to the error log file.
        
        Usecase: when a bug would stop the rest of the code from 
        functioning and requires more in depth analysis to solve 
        """
        Blink(5)
        Record(msg)
        super().__init__(msg)
        
class SilentError(Exception):
    def __init__(self, msg:str=None) -> None:
        """
        Lets the code do it's thing and logs the data.
        
        Usecase: for trivial measurements errors that aren't 
        important and can be seen on the dashboard/website 
        """
        Record(msg)
        
class ShortError(Exception):
    def __init__(self, msg:str=None) -> None:
        """
        Stops the code for a short moment to blink the onboard
        led (a fraction of a second) and log the error code.
        
        Usecase: specific bugs that don't impede critcal code
        but can still limit functionality and should be sorted. 
        """
        Blink(1)
        Record(msg)
        
class SendingError(Exception):
    def __init__(self, msg:str=None) -> None:
        """
        Stops the code for a bit, blinks twice and saves the error
        
        Usecase: when the upload function fails to send a measurement
        """
        Blink(2)
        Record(msg)
        
class MeasuringError(Exception):
    def __init__(self, msg:str=None) -> None:
        """
        Stops the code for a bit, blinks 3 times and saves the 
        error
        
        Usecase: when the INA219 doesn't measure any volatage or
        doesn't work
        """
        Blink(3)
        Record(msg)
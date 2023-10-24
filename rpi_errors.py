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
try:
    import RPi.GPIO as GPIO
except RuntimeError as err:
    print(f"No GPIO pins available on WSL: \n {err} \n From now on the code will print 'blink' ")
import time, os

path = os.getcwd()

def turn_led(state:bool=True):
    """Turn led on pin 18 on

    Connect a 1k ressitor in series with an LED on pin 18, the other end to GND
    This will blink that LED
    Args:
        state (bool, optional): _description_. Defaults to True.
    """
    try:
        if state: GPIO.output(18,GPIO.HIGH)
        else: GPIO.output(18,GPIO.LOW)    
    except NameError as err:
        print("blink")     
def turn_board_led(state:bool=True):
    """Use the LED files from sys/class/leds to control the onboard led

    #! This only works on some boards
    This won't work on Zero.
    I recommend you add a physical LED and use that 
    
    
    Args:
        state (bool, optional): True = on, Flase= off. Defaults to True.
    """
    if state: os.system('echo 1 | sudo tee /sys/class/leds/led0/brightness > /dev/null 2>&1') # led on
    else: os.system('echo 0 | sudo tee /sys/class/leds/led0/brightness > /dev/null 2>&1') # led off

def Blink(number:int=None):
    if number is None: pass
    
    if number== 1:
        turn_led(False)
        time.sleep(0.1)
        turn_led(True)
        time.sleep(0.1)
        turn_led(False)
    else: 
        for i in range(number):
            turn_led(False)
            time.sleep(number)
            turn_led(True)
            time.sleep(number)
            turn_led(False)    
def Record(message:str="Generic Error"):
    with open(file=f"{path}/errorfile.txt",mode="a+") as errorlog:
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
        Blink(4)
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
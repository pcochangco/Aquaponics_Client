# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 16:23:16 2021

@author: pcochang
"""
import time
import RPi.GPIO as GPIO  
GPIO.setmode(GPIO.BOARD)      # Use physical pin numbering
GPIO.setwarnings(False)


class trigger(): 
    def pump_ON(self,prediction, pin_num, turn_on_time = 5):
        GPIO.setup(pin_num, GPIO.OUT, initial=GPIO.LOW)   # Set pin 8 to be an output pin and set initial value to low (off)
        if int(prediction):
            print("Turning the valve on.")
            GPIO.output(pin_num, 1) # Turn on or off base on prediction ( 1 -ON , 0 -OFF)
            time.sleep(turn_on_time)
        else: print("Valve remains off")
        GPIO.output(pin_num, GPIO.LOW)  # Turn off
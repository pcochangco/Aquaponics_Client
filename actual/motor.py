# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 16:22:38 2021

@author: pcochang
"""
import RPi.GPIO as GPIO  
import time
import timeit
from camera import capture
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
capture = capture()

class run():
    def cleanup(self, in1, in2, in3, in4):
        GPIO.output( in1, 0 )
        GPIO.output( in2, 0 )
        GPIO.output( in3, 0 )
        GPIO.output( in4, 0 )
            
            
    def motor_and_capture(self,directory):
        start_with_motor = timeit.default_timer()
        in1 = 11
        in2 = 12
        in3 = 13
        in4 = 15
        motor_pins = [in1,in2,in3,in4]
        motor_step_counter = 0
        
        GPIO.setup( in1, GPIO.OUT )
        GPIO.setup( in2, GPIO.OUT )
        GPIO.setup( in3, GPIO.OUT )
        GPIO.setup( in4, GPIO.OUT )
        
        # careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
        step_sleep = 0.001
        step_count = 6300 # 5.625*(1/64) per step, 4096 steps is 360°
        direction = False # True for clockwise, False for counter-clockwise
        # defining stepper motor sequence (found in documentation http://www.4tronix.co.uk/arduino/Stepper-Motors.php)
        step_sequence = [[1,0,0,1],
                         [1,0,0,0],
                         [1,1,0,0],
                         [0,1,0,0],
                         [0,1,1,0],
                         [0,0,1,0],
                         [0,0,1,1],
                         [0,0,0,1]]
         
        try:
            for d in [ (False,step_count), (False,step_count), (False, step_count), (True, step_count*3)]:
                direction = d[0]
                try: capture.takeImage(directory)
                except Exception as e: 
                    print(" Can't open Camera setup...\n", e)
                    time.sleep(2)
                for i in range(d[1]):
                    for x, pin in enumerate(motor_pins):
                        GPIO.output( pin, step_sequence[motor_step_counter][x] )
                    if direction==True:
                        motor_step_counter = (motor_step_counter - 1) % 8
                    elif direction==False:
                        motor_step_counter = (motor_step_counter + 1) % 8
                    time.sleep( step_sleep )
        except:
            self.cleanup(in1, in2, in3, in4)
                
        self.cleanup(in1, in2, in3, in4)
        stop_with_motor = timeit.default_timer()
        print("Overall time including motor run: {}sec".format(round(stop_with_motor - start_with_motor,2)))

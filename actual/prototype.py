# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 16:21:25 2021

@author: pcochang
"""

# Import Libraries
import sys
sys.path.insert(0,'Hydroponics/actual/')
from machine_learning import ML
from EC_PH import sense
from camera import capture
from image_processing import IP
from motor import run
from pump import trigger
import time

true_df, false_df = ML.read_datasets('Hydroponics/actual/MOCK_DATA.csv', 'Hydroponics/actual/MOCK_DATA-1.csv')
model = ML.train_model(true_df, false_df )

directory = "/home/pi/Pictures0/"
results_path = "/home/pi/results"
directory = capture.clean_dir(directory)
capture.clean_dir(results_path)

while True:
    pH_level, ec_level = sense.read_ph_ec()
    
    run.motor_and_capture(directory)
    area_of_lettuce = IP.Lettuce_Area(directory,results_path)
    
    sense.datalog(pH_level, ec_level, area_of_lettuce)
    
    prediction = ML.predict_user_input(model, pH_level, ec_level, area_of_lettuce)

    trigger.pump_ON(prediction, pin_num = 8, turn_on_time = 5)
    #pin num is where the relay for pump should be connected. turn on time is the time in seconds, the pump will turn on

    
    print("Timer ON, please wait 30 minutes for the next measurement.")
    time.sleep(1800)  #sleep for 30mins
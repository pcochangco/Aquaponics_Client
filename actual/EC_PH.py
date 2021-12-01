# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 16:26:21 2021

@author: pcochang
"""

##################### For EC and PH Sensor#######################
import time
import sys
import os
from datetime import datetime

sys.path.insert(0,'Hydroponics/actual/')
from DFRobot_ADS1115 import ADS1115

ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
##################### For EC and PH Sensor#######################
ads1115 = ADS1115()

class sense():
    def readEC(self,voltage, temperature = 25):
        _kvalue = 1.0
        _kvalueLow = 1.0
        _kvalueHigh = 1.02
        rawEC = 1000*voltage/820.0/200.0
        #print(">>>current rawEC is: %.3f" % rawEC)
        valueTemp = rawEC * _kvalue
        if(valueTemp > 2.5):
            _kvalue = _kvalueHigh
        elif(valueTemp < 2.0):
            _kvalue = _kvalueLow
        value = rawEC * _kvalue
        value = value / (1.0+0.0185*(temperature-25.0))
        return value
    
    def readPH(self,voltage):
        # pH 4.0
        _acidVoltage = 2032.44
        # pH 7.0
        _neutralVoltage = 1500.0
        slope = (7.0-4.0)/((_neutralVoltage-1500.0) / 3.0 - (_acidVoltage-1500.0)/3.0)
        intercept = 7.0 - slope*(_neutralVoltage-1500.0)/3.0
        _phValue = slope*(voltage-1500.0)/3.0+intercept
        return round(_phValue, 2)
    
    def read_ph_ec(self):
        try:
            global ads1115
            temperature = 25 # or make your own temperature read process
            #Set the IIC address
            ads1115.setAddr_ADS1115(0x48)
            #Sets the gain and input voltage range.
            ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)
            #Get the Digital Value of Analog of selected channel
            adc0 = ads1115.readVoltage(0)
            time.sleep(0.1)
            adc1 = ads1115.readVoltage(1)
            #Convert voltage to EC with temperature compensation
            EC = self.readEC(adc0['r'],temperature)
            PH = self.readPH(adc1['r'])
            print("Temperature:%.1f ^C EC:%.2f ms/cm PH:%.2f " %(temperature,EC,PH))
        except Exception as e:
            print("Error PH and EC sensor reading.",e)
            PH, EC = 0, 0
        return PH, EC
                  
    def datalog(self,PH, EC, Size, ip_time, train_time, predict_time, accuracy):
        try:
            dt_string = datetime.now().strftime("%d/%m/%Y")
            tm_string = datetime.now().strftime("%H:%M:%S")
            if os.path.isfile('output.csv'):
                with open('output.csv', 'a') as f:
                    f.write(str(dt_string) + "," + str(tm_string) + "," + str(PH) + "," + str(EC) + "," + str(Size) + "," + str(ip_time) + "," + str(train_time) + "," + str(predict_time) + "," + str(accuracy) + "\n")
            else: 
                with open('output.csv', 'a') as f:
                    f.write("Date" + "," + "Time" + "," + "PH Sensor" + "," + "EC Sensor" + "," + "Lettuce Area (in^2)" + "Image Processing time (s)" + "," + "Training time (s)" + "," + "Prediction time (s)" + "," + "Accuracy (%)" + "\n") 
                    f.write(str(dt_string) + "," + str(tm_string) + "," + str(PH) + "," + str(EC) + "," + str(Size) + "," + str(ip_time) + "," + str(train_time) + "," + str(predict_time) + "," + str(accuracy) + "\n")
        except Exception as e:
            print("Can't open output csv file.", e)
     

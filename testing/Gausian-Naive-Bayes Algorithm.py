# Import Libraries
##################### For Gaussian machine Learning#######################
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report
from datetime import datetime
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
import time    # Import the sleep function from the time module
##################### For Gaussian machine Learning#######################



##################### For EC and PH Sensor#######################
import time
import sys

sys.path.insert(0,'Aquaponics/DFRobot_ADS1115/RaspberryPi/Python/')
from DFRobot_ADS1115 import ADS1115

ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
##################### For EC and PH Sensor#######################


###########Functions###################

##################### For Gaussian machine Learning#######################
def GPIOSetup(prediction, pin_num, turn_on_time = 5):
    GPIO.setwarnings(False)    # Ignore warning for now
    GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
    GPIO.setup(pin_num, GPIO.OUT, initial=GPIO.LOW)   # Set pin 8 to be an output pin and set initial value to low (off)
    if int(prediction):
        print("Turning the valve on.")
        GPIO.output(pin_num, 1) # Turn on or off base on prediction ( 1 -ON , 0 -OFF)
        time.sleep(turn_on_time)
    else: print("Valve remains off")
    GPIO.output(pin_num, GPIO.LOW)  # Turn off

def read_datasets(true_csv, false_csv):
    true_df = pd.read_csv(true_csv)
    false_df = pd.read_csv(false_csv)
    return true_df, false_df

def add_target_variables(true_df, false_df):
    true_df['target'] = 1
    false_df['target'] = 0
    
def merge_datasets(true_df, false_df):
    merged_df = true_df.append(false_df, ignore_index=True)
    return merged_df

def separate_variables(merged_df):
    X = merged_df.drop(['target'], axis=1)
    y = merged_df['target']
    return X, y

def instantiate_model(X_train, y_train):
    training_start_time = datetime.now()
    model = GaussianNB()
    model.fit(X_train, y_train)
    training_stop_time = datetime.now()
    training_time = training_stop_time - training_start_time
    print(f'Training Time: {training_time}')
    return model    

def display_model_accuracy(model, X_test, y_test):
    accuracy = model.score(X_test, y_test)
    accuracy *= 100
    print(f'Model Accuracy: {accuracy}%' + '\n')

def display_classification_report(model, X_test):
    print('Classification Report:')
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    
def evaluate_model(model, X_test, y_test):
    display_model_accuracy(model, X_test, y_test)
    display_classification_report(model, X_test)
    
def read_user_inputs():
    area_of_lettuce = float(input("Enter Area of Lettuce: "))
    return area_of_lettuce
    
def predict_user_input(model, pH_level, ec_level, area_of_lettuce):
    prediction_start_time = datetime.now()
    prediction = model.predict([[pH_level, ec_level, area_of_lettuce]])[0]
    prediction_stop_time = datetime.now()
    prediction_time = prediction_stop_time - prediction_start_time
    print('\n' + f'Model Prediction: {prediction}')
    print(f'Prediction Time: {prediction_time}')
    return prediction
              
##################### For EC and PH Sensor#######################       
def readEC(voltage, temperature = 25):
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

def readPH(voltage):
    # pH 4.0
    _acidVoltage = 2032.44
    # pH 7.0
    _neutralVoltage = 1500.0
    slope = (7.0-4.0)/((_neutralVoltage-1500.0) / 3.0 - (_acidVoltage-1500.0)/3.0)
    intercept = 7.0 - slope*(_neutralVoltage-1500.0)/3.0
    _phValue = slope*(voltage-1500.0)/3.0+intercept
    return round(_phValue, 2)

def read_ph_ec():
    global ads1115
    temperature = 25 # or make your own temperature read process
    #Set the IIC address
    ads1115.setAddr_ADS1115(0x48)
    #Sets the gain and input voltage range.
    ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)
    #Get the Digital Value of Analog of selected channel
    time.sleep(0.1)
    adc0 = ads1115.readVoltage(0)
    time.sleep(0.1)
    adc1 = ads1115.readVoltage(1)
    #Convert voltage to EC with temperature compensation
    EC = readEC(adc0['r'],temperature)
    PH = readPH(adc1['r'])
    print("Temperature:%.1f ^C EC:%.2f ms/cm PH:%.2f " %(temperature,EC,PH))
    return PH, EC
              
def datalog(PH, EC, Size):
    import os
    from datetime import datetime
    dt_string = datetime.now().strftime("%d/%m/%Y")
    tm_string = datetime.now().strftime("%H:%M:%S")
    
    if os.path.isfile('output.csv'):
        with open('output.csv', 'a') as f:
            f.write(str(dt_string) + "," + str(tm_string) + "," + PH + "," + EC + "," + Size + "\n")
    else: 
        with open('output.csv', 'a') as f:
            f.write("Date" + "," + "Time" + "," + "PH Sensor" + "," + "EC Sensor" + "," + "Lettuce Area (in^2)" + "\n") 
            f.write(str(dt_string) + "," + str(tm_string) + "," + PH + "," + EC + "," + Size + "\n")              
              
ads1115 = ADS1115()
##################### For EC and PH Sensor#######################    

              
# Global Scope
true_df, false_df = read_datasets('MOCK_DATA.csv', 'MOCK_DATA-1.csv')
add_target_variables(true_df, false_df)
merged_df = merge_datasets(true_df, false_df)
X, y = separate_variables(merged_df)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
model = instantiate_model(X_train, y_train)
evaluate_model(model, X_test, y_test)
pH_level, ec_level = read_ph_ec()
area_of_lettuce = read_user_inputs()
prediction = predict_user_input(model, pH_level, ec_level, area_of_lettuce)
datalog(pH_level, ec_level, area_of_lettuce)
GPIOSetup(prediction, pin_num = 8)

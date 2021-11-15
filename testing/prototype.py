# Import Libraries
##################### For Gaussian machine Learning#######################
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report
from datetime import datetime
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
##################### For Gaussian machine Learning#######################



##################### For EC and PH Sensor#######################
import time
import sys
import os

sys.path.insert(0,'Aquaponics_Client/testing/DFRobot_ADS1115/RaspberryPi/Python/')
from DFRobot_ADS1115 import ADS1115

ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
##################### For EC and PH Sensor#######################

##################### For Image Processing #######################
import numpy as np
import cv2
import math
import shutil
import timeit
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
import picamera
##################### For Image Processing #######################




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



##################### For Image Processing #######################
def delete_img(folder):
    try:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except:
                folder = "/home/pi/Pictures0_" + str(time.time()) +"/"
                os.mkdir(folder)
                break
    except: os.mkdir(folder)
    return folder

def takeImage(directory):
    with picamera.PiCamera() as camera:
        time.sleep(2)
        camera.resolution = (1280, 720)
        camera.vflip = False
        camera.contrast = 10
        file_name = os.path.join(directory,"img_" + str(time.time()) + ".jpg")
        camera.capture(file_name)
        print("Picture taken.")
    
    
def ratio_to_actual(image_pixel_ratio):
    return image_pixel_ratio * 2.61

def get_lettuce_mask(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([30, 50, 50])
    upper = np.array([80, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    return mask

#get center of contoured image
def center(contours, image):
    image_y, image_x, _ = image.shape
    cnts = [x for x in contours if cv2.contourArea(x) > image_x*image_y*0.01]
    distance = []
    for c in cnts:
        M = cv2.moments(c)
        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            cv2.circle(image,(cx,cy),20,(255,255,0),10)
        distance.append(math.sqrt(((cx-image_x/2)**2)+((cy-image_y/2)**2)))
        #cv2.line(image, (cx,cy), (int(image_x/2),int(image_y/2)), [0, 255, 0], 2)
    #print(distance)
    min_value = min(distance)
    min_index = distance.index(min_value)   
    return cnts[min_index]

def get_all_contours(mask):
    ret,thresh = cv2.threshold(mask, 40, 255, 0)
    #im2,contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return contours

# find the biggest countour (c) by the area
def get_max_contour(contours):
    c = max(contours, key = cv2.contourArea)
    return c

def process_Image(directory):
    global start_image_processing, stop_image_processing
    overall_area = []
    for filename in os.listdir(directory):
        start_image_processing = timeit.default_timer()
        if filename.endswith(".jpg"):
            image = cv2.imread(os.path.join(directory, filename))
            mask = get_lettuce_mask(image)
            # print the masked image, all lettuce
            result = cv2.bitwise_and(image, image, mask=mask) 
            #cv2.imshow( image)
            #cv2.imshow( mask)
            #cv2.imshow( result)
    
            #locate the lettuce to measure
            contours = get_all_contours(mask)
            #target_contour = get_max_contour(contours)
            try:
                target_contour = center(contours, result)
            except: 
                target_contour = get_max_contour(contours)
            #n_white_pix = np.sum(np.array(mask) > 0)#white pixel area
    
            # draw contour and bounding box on target lettuce contour
            if len(contours) != 0:
                cv2.drawContours(result, target_contour, -1, 255, 2)
                x,y,w,h = cv2.boundingRect(target_contour)
                cv2.rectangle(result,(x,y),(x+w,y+h),(0,255,0),3)
     
            cv2.imwrite(os.path.join(results_path, filename), result)
            
            Area =  round(100*cv2.contourArea(target_contour)/(image.shape[0]*image.shape[1]),2)
            Area = ratio_to_actual(Area)
            print("Lettuce area is {} in^2".format(round(Area,2)))
            overall_area.append(Area)
            # show the images
            #cv2.imshow( result)
        stop_image_processing = timeit.default_timer()
    try: size = round(sum(overall_area)/len(overall_area),2)
    except: size = 0
    print("Lettuce average size is {} in^2".format(size))
    return size



def cleanup(in1, in2, in3, in4):
    GPIO.output( in1, 0 )
    GPIO.output( in2, 0 )
    GPIO.output( in3, 0 )
    GPIO.output( in4, 0 )
    

def Lettuce_Area():
    #Motor pins
    directory = "/home/pi/Pictures0/"
    results_path = "/home/pi/results"
    directory = delete_img(directory)
    delete_img(results_path)
         
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

    
    cleanup(in1, in2, in3, in4)
    try:
        for d in [ (False,step_count), (False,step_count), (False, step_count), (True, step_count*3)]:
            direction = d[0]
            try: takeImage(directory)
            except Exception as e: 
                print(" Can't open Camera setup...\n", e)
                time.sleep(3)
            for i in range(d[1]):
                for x, pin in enumerate(motor_pins):
                    GPIO.output( pin, step_sequence[motor_step_counter][x] )
                if direction==True:
                    motor_step_counter = (motor_step_counter - 1) % 8
                elif direction==False:
                    motor_step_counter = (motor_step_counter + 1) % 8
                time.sleep( step_sleep )
    except KeyboardInterrupt:
        cleanup(in1, in2, in3, in4)
     
    cleanup(in1, in2, in3, in4)
    print("")
    print("Computing the area...")
    try: 
        size = process_Image(directory)
        print("")
        print("Image processing time per image: {}sec ".format(round(stop_image_processing - start_image_processing,2)))
    except Exception as e: 
        print(" Error Image Processing...\n", e)
        size = 0
    stop_with_motor = timeit.default_timer()
    print("Overall time including motor run: {}sec".format(round(stop_with_motor - start_with_motor,2)))
    return size        
               
# Global Scope

true_df, false_df = read_datasets('Aquaponics_Client/testing/MOCK_DATA.csv', 'Aquaponics_Client/testing/MOCK_DATA-1.csv')
add_target_variables(true_df, false_df)
merged_df = merge_datasets(true_df, false_df)
X, y = separate_variables(merged_df)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
model = instantiate_model(X_train, y_train)
evaluate_model(model, X_test, y_test)

while True:
    pH_level, ec_level = read_ph_ec()
    start_with_motor = timeit.default_timer()
    area_of_lettuce = Lettuce_Area()
    prediction = predict_user_input(model, pH_level, ec_level, area_of_lettuce)
    datalog(pH_level, ec_level, area_of_lettuce)
    GPIOSetup(prediction, pin_num = 8)
    print("Timer ON, please wait 30 minutes for the next measurement.)
    time.sleep(60*30)

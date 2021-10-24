# Import Libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report
from datetime import datetime
from os import system
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
from time import sleep     # Import the sleep function from the time module


def GPIOSetup(prediction, pin_num):
    GPIO.setwarnings(False)    # Ignore warning for now
    GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
    GPIO.setup(pin_num, GPIO.OUT, initial=GPIO.LOW)   # Set pin 8 to be an output pin and set initial value to low (off)
    GPIO.output(pin_num, int(prediction)) # Turn on or off base on prediction ( 1 -ON , 0 -OFF)
    sleep(5)                  # Sleep for 5 second
    GPIO.output(pin_num, GPIO.LOW)  # Turn off
    sleep(1)

# Functions
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
    pH_level = float(input("Enter pH Level: "))
    ec_level = float(input("Enter EC Level: "))
    area_of_lettuce = float(input("Enter Area of Lettuce: "))
    return pH_level, ec_level, area_of_lettuce
    
def predict_user_input(model, pH_level, ec_level, area_of_lettuce):
    prediction_start_time = datetime.now()
    prediction = model.predict([[pH_level, ec_level, area_of_lettuce]])[0]
    prediction_stop_time = datetime.now()
    prediction_time = prediction_stop_time - prediction_start_time
    print('\n' + f'Model Prediction: {prediction}')
    print(f'Prediction Time: {prediction_time}')
    return prediction
    
# Global Scope
true_df, false_df = read_datasets('MOCK_DATA.csv', 'MOCK_DATA-1.csv')
add_target_variables(true_df, false_df)
merged_df = merge_datasets(true_df, false_df)
X, y = separate_variables(merged_df)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
model = instantiate_model(X_train, y_train)
evaluate_model(model, X_test, y_test)
pH_level, ec_level, area_of_lettuce = read_user_inputs()
prediction = predict_user_input(model, pH_level, ec_level, area_of_lettuce)
GPIOSetup(prediction, pin_num = 8)
system('pause')

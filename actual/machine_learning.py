# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 16:22:48 2021

@author: pcochang
"""

##################### For Gaussian machine Learning#######################
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report
from datetime import datetime
##################### For Gaussian machine Learning#######################

class ML():
    
    def train_model(self, true_df, false_df ):
        self.add_target_variables(true_df, false_df)
        merged_df = self.merge_datasets(true_df, false_df)
        X, y = self.separate_variables(merged_df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        model = self.instantiate_model(X_train, y_train)
        self.evaluate_model(model, X_test, y_test)
        
        return model
        
    
    
    def read_datasets(self,true_csv, false_csv):
        true_df = pd.read_csv(true_csv)
        false_df = pd.read_csv(false_csv)
        return true_df, false_df
    
    def add_target_variables(self,true_df, false_df):
        true_df['target'] = 1
        false_df['target'] = 0
        
    def merge_datasets(self,true_df, false_df):
        merged_df = true_df.append(false_df, ignore_index=True)
        return merged_df
    
    def separate_variables(self,merged_df):
        X = merged_df.drop(['target'], axis=1)
        y = merged_df['target']
        return X, y
    
    def instantiate_model(self,X_train, y_train):
        training_start_time = datetime.now()
        model = GaussianNB()
        model.fit(X_train, y_train)
        training_stop_time = datetime.now()
        training_time = training_stop_time - training_start_time
        print(f'Training Time: {training_time}')
        return model    
    
    def display_model_accuracy(self, model, X_test, y_test):
        accuracy = model.score(X_test, y_test)
        accuracy *= 100
        print(f'Model Accuracy: {accuracy}%' + '\n')
    
    def display_classification_report(self, model, X_test,y_test):
        print('Classification Report:')
        y_pred = model.predict(X_test)
        print(classification_report(y_test, y_pred))
        
    def evaluate_model(self, model, X_test, y_test):
        self.display_model_accuracy(model, X_test, y_test)
        self.display_classification_report(model, X_test ,y_test)
        
        
    def predict_user_input(self, model, pH_level, ec_level, area_of_lettuce):
        prediction_start_time = datetime.now()
        prediction = model.predict([[pH_level, ec_level, area_of_lettuce]])[0]
        prediction_stop_time = datetime.now()
        prediction_time = prediction_stop_time - prediction_start_time
        print('\n' + f'Model Prediction: {prediction}')
        print(f'Prediction Time: {prediction_time}')
        return prediction
                  
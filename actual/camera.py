# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 16:22:27 2021

@author: pcochang
"""
import picamera
import time
import os
import shutil

class capture():
    
    def clean_dir(self,folder):
        try:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except:
                    folder = folder[:-1] + "_1/"
                    os.mkdir(folder)
                    break
        except: os.mkdir(folder)
        return folder
    
    
    def takeImage(self,directory):
        with picamera.PiCamera() as camera:
            time.sleep(2)
            camera.resolution = (1280, 720)
            camera.vflip = False
            camera.contrast = 10
            file_name = os.path.join(directory,"img_" + str(time.time()) + ".jpg")
            camera.capture(file_name)
            print("Picture taken.")
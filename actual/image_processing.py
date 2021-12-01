# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 16:23:00 2021

@author: pcochang
"""


##################### For Image Processing #######################
import numpy as np
import cv2
import math
import os
import timeit



##################### For Image Processing #######################

class IP():
    
    def ratio_to_actual(self,image_pixel_ratio):
        return image_pixel_ratio * 2.61
    
    def get_lettuce_mask(self,frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array([30, 50, 50])
        upper = np.array([80, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        return mask
    
    #get center of contoured image
    def center(self,contours, image):
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
    
    def get_all_contours(self,mask):
        ret,thresh = cv2.threshold(mask, 40, 255, 0)
        #im2,contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return contours
    
    # find the biggest countour (c) by the area
    def get_max_contour(self,contours):
        c = max(contours, key = cv2.contourArea)
        return c
    
    def process_Image(self,directory, results_path):
        overall_area = []
        for filename in os.listdir(directory):
            if filename.endswith(".jpg"):
                image = cv2.imread(os.path.join(directory, filename))
                mask = self.get_lettuce_mask(image)
                # print the masked image, all lettuce
                result = cv2.bitwise_and(image, image, mask=mask) 
                #cv2.imshow( image)
                #cv2.imshow( mask)
                #cv2.imshow( result)
        
                #locate the lettuce to measure
                contours = self.get_all_contours(mask)
                #target_contour = get_max_contour(contours)
                try:
                    target_contour = self.center(contours, result)
                except: 
                    target_contour = self.get_max_contour(contours)
                #n_white_pix = np.sum(np.array(mask) > 0)#white pixel area
        
                # draw contour and bounding box on target lettuce contour
                if len(contours) != 0:
                    cv2.drawContours(result, target_contour, -1, 255, 2)
                    x,y,w,h = cv2.boundingRect(target_contour)
                    cv2.rectangle(result,(x,y),(x+w,y+h),(0,255,0),3)
         
                cv2.imwrite(os.path.join(results_path, filename), result)
                
                Area =  round(100*cv2.contourArea(target_contour)/(image.shape[0]*image.shape[1]),2)
                Area = self.ratio_to_actual(Area)
                print("Lettuce area is {} in^2".format(round(Area,2)))
                overall_area.append(Area)
                # show the images
                #cv2.imshow( result)
        try: size = round(sum(overall_area)/len(overall_area),2)
        except: size = 0
        print("Lettuce average size is {} in^2".format(size))
        return size, len(overall_area)
    
    

    def Lettuce_Area(self,directory,results_path):
        print("")
        print("Computing the area...")
        try: 
            start_image_processing = timeit.default_timer()
            size, qty = self.process_Image(directory, results_path)
            stop_image_processing = timeit.default_timer()
            print("")
            ip_time = round((stop_image_processing - start_image_processing),2)
            print("Image processing time per image: {}sec ".format(ip_time))
        except Exception as e: 
            print(" Error Image Processing...\n", e)
            size = 0
            ip_time = 0
        
        return size, ip_time       

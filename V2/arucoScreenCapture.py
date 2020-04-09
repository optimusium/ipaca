#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 09:40:08 2020

@author: jacky
"""

import numpy as np
import cv2
from cv2 import aruco
from PIL import Image
import time

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Initialize some variables
process_this_frame = True

while True:
    if not video_capture.isOpened():
        print('Unable to load camera.')
        time.sleep(5)
        pass
    
    key = cv2.waitKey(1) & 0xFF
    
    # Grab a single frame of video
    ret, frame = video_capture.read()
    if ret!=True: continue

    aruco_dict = aruco.Dictionary_get(aruco.DICT_APRILTAG_16h5)
    parameters =  aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
    corners_np = np.array(corners)
    corners_npint = corners_np.astype(int)
        
    if tuple(corners_npint) != ():
        try:
            marker1 = tuple(corners_npint[0][0][0])
            marker2 = tuple(corners_npint[1][0][0])
            rec = cv2.rectangle(frame,  marker1,  marker2, color=(0,255,0))
            cv2.imwrite("rec.png", rec)
                
            im = Image.open("rec.png")
            crop = marker1 + marker2
            ts = time.time()
            im_crop = im.crop(crop)
            print(im_crop.size)
            #im_crop.show()
            if im_crop.size != (0, 0):
                im_crop.save(str(int(ts)) + "crop.png", quality=95, format="PNG")
                print("Image saved at " + str(int(ts)))
                im.close()
                time.sleep(2)
        except:
            pass
                    
    # Hit 'q' on the keyboard to quit!
    if key == ord("q"):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
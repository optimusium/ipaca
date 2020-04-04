# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 18:23:23 2020

@author: Jacky
"""

#code forked and tweaked from https://github.com/ageitgey/face_recognition/blob/master/examples/facerec_from_webcam_faster.py
#to extend, just add more people into the known_people folder
#
#work_folder="C:\\Users\\User\\Documents\\UiPath\\IPA_CA_v0\\"
work_folder=".\\image\\"
import face_recognition
import cv2
import numpy as np
import os
import glob
import time
import re

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Increase the resolution of the video
def make_1080p():
    video_capture.set(3, 1920)
    video_capture.set(4, 1080)

make_1080p()

#make array of sample pictures with encodings
known_face_encodings = []
known_face_names = []
dirname = os.path.dirname(__file__)
path = os.path.join(dirname, 'known_people/')

#make an array of all the saved jpg files' paths
list_of_files = [f for f in glob.glob(path+'*.jpg')]
#find number of known faces
number_files = len(list_of_files)

names = list_of_files.copy()

for i in range(number_files):
    globals()['image_{}'.format(i)] = face_recognition.load_image_file(list_of_files[i])
    globals()['image_encoding_{}'.format(i)] = face_recognition.face_encodings(globals()['image_{}'.format(i)])[0]
    known_face_encodings.append(globals()['image_encoding_{}'.format(i)])

    # Create array of known names
    names[i] = names[i].replace("known_people\\", "").replace(".jpg", "")  
    known_face_names.append(names[i])

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
attendance = {}
outfile=open("image_login.csv","w+")
outfile.write("Name,Time\n")
for name in known_face_names:
    outfile.write("%s,99999\n" % (re.split("\\\\",name)[-1].replace("_NUS","")) )
outfile.close()
recognizedFace=[]
while True:
    if not video_capture.isOpened():
        if debug==1: print('Unable to load camera.')
        time.sleep(5)
        pass
    
    # Grab a single frame of video
    ret, frame = video_capture.read()
    print(ret)
    #frame=cv2.imread("known_people\\save_NUS.jpg")
    if ret!=True: continue

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = frame # cv2.resize(frame, (120,120), fx=0.25, fy=0.25)
    #small_frame=cv2.resize(frame, (120,120 ), interpolation = cv2.INTER_CUBIC)
    
    # Resize frame of video to 3 times the size for larger display
    frame = frame #cv2.resize(frame, (240,240), fx=3, fy=3) 
    cv2.imwrite(work_folder+"save_frame.jpg",frame)
    #frame =cv2.resize(frame, (180,180), interpolation = cv2.INTER_CUBIC) 

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame, number_of_times_to_upsample=2, model='hog') # For GPU, use model='cnn'
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations, num_jitters=2)
        print(face_encodings)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6) # Lower is more strict, default = 0.6
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                #print(name)

            face_names.append(name)
            
    process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/12 size
        print("999",name,attendance)
        
        top *= 12
        right *= 12
        bottom *= 12
        left *= 12

        # Draw a box around the face
        
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        if name!="" and name not in attendance:
            name2=re.split("\\\\",name)[-1].replace("_NUS","")

            datestamp=int( time.time() )
            attendance[name]=datestamp
            cv2.imwrite(work_folder+"%s_%s.jpg" % (datestamp,name2), frame)
            if name2 not in recognizedFace:
                recognizedFace.append(name2)
                cv2.imwrite(work_folder+"%s.jpg" % name2, frame)
                
                
            outfile2=open("image_login.csv","w+")
            
            
            outfile2.write("Name,Time\n")

            for name in known_face_names:
                if name in attendance:
                    outfile2.write("%s,%s\n" % (re.split("\\\\",name)[-1].replace("_NUS",""),attendance[name]) )
                else:
                    outfile2.write("%s,99999\n" % (re.split("\\\\",name)[-1].replace("_NUS","")) )
            outfile2.close()


        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 5.0, (0, 0, 0), 5)

    # Display the resulting image
    cv2.imshow('Video', frame)
    #refresh after 12 hrs
    for name in attendance:
        if attendance[name]<time.time()-43200:
            attendance.pop(name, None) 
    #time.sleep(1)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()

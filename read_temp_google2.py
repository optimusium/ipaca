import sys
import logging as alog

import os
from os.path import join, exists
import time

import cv2
import re
from google.cloud import vision

import face_recognition
import numpy as np
import glob

Google_AUTH_KEY = r'iss-ipa66-57b2c4a008f2.json'

TEMP_REG_PATTERN = re.compile(r'^[2345]\d\.?\d$')

def main(argv):
    # Setup service account authentication key
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Google_AUTH_KEY
    
    alog.basicConfig(level=alog.DEBUG)

    alog.info(f"opencv verion: {cv2.__version__}")

    client = vision.ImageAnnotatorClient()
    alog.info(f'Create client and connect to google cloud')
    ##############################################################################
    #face_recognition setup
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
    ###############################################################################
    #initialize alert file
    inf0=open("alert_initial.csv","r")
    inf0.readline()
    outf0=open("alert.csv","w+")
    outf0.write("Name,Alert,Temperature\n")
    for line in inf0.readlines():
        outf0.write(line)
    outf0.close()
    inf0.close()
    time.sleep(0.01)
    
    inf99=open("stop.csv","w+")
    inf99.close()
    
    os.popen("copy alert.csv alert_bk.csv")
    time.sleep(0.1)
    os.popen("del stop.csv")
    ##################################################################################    

    try:
        # Get a reference to webcam #0 (the default one)
        vidcap = cv2.VideoCapture(0)
        
        capture_temp = True
        start_time = time.time()
                
        while capture_temp:
            #blacklist handling
            blacklist=[]
            inf9=open("blacklist.csv","r")
            inf9.readline()
            for line in inf9.readlines():
                line=line.replace("\n","")
                if line=="": continue
                buf=re.split(",",line)
                if buf[0]!="":
                    blacklist.append(buf[0])
            #####################################################
            #capturing video        
            current_time = time.time()
            time_laped = int(current_time - start_time)
            
            start_time = current_time
            
            success, image = vidcap.read()
            if success!=True: continue
            frame=image
            # Convert BGR to RGB color for display
            #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            #if image is None:
            #    capture_temp = False
            #    break
                
            #cv2.imshow("frame", image)
            
            key = cv2.waitKey(25)
            

            #Face recognition
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = frame # cv2.resize(frame, (120,120), fx=0.25, fy=0.25)
            #small_frame=cv2.resize(frame, (120,120 ), interpolation = cv2.INTER_CUBIC)
            
            # Resize frame of video to 3 times the size for larger display
            frame = frame #cv2.resize(frame, (240,240), fx=3, fy=3) 

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
                    #cv2.imwrite("C:\\Users\\User\\Documents\\UiPath\\IPA_CA_v0\\%s_%s.jpg" % (datestamp,name2), frame)
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
            #############################################################################
            #check blacklist
            try:
                inf=open("image_login.csv","r")
            except:
                time.sleep(1)
                inf=open("image_login.csv","r")
                pass
            #generating alert file
            try:
                outf=open("alert.csv","w+")
            except:
                time.sleep(1)
                outf=open("alert.csv","w+")
                pass
            outf.write("Name,Alert,Temperature\n")
            bufl=""
            latest=99999.0
            inf.readline()
            for line in inf.readlines():
                line=line.replace("\n","")
                buf=re.split(",",line)
                if len(buf)<2: continue
                #print(eval(buf[1]),latest)
                if eval(buf[1])>latest:
                    latest=eval(buf[1])
                    bufl=buf[0]
            ter=""
            ter+=bufl+","
            if bufl in blacklist:
                temp = 99
                print("Please Stay Where You Are - Someone Will Come Over.")
                ter+="2,%s\n" % temp
                outf.write(ter)
            #######################################################################
            
            #capturing temperature
            if key & 0xFF == ord('q'):
                capture_temp = False
                alog.info("Stopped")
            elif key & 0xFF == ord('w'):
                cv2.imwrite("frames/frame_%d.jpg" % time_laped, image)
                alog.info("Save frames/frame_%d.jpg" % time_laped)
                
                temp_read = read_temp_from_image(image, client)
                if temp_read > 0:
                    alog.info(f"Found temperature: '{temp_read}'")
                    #cv2.imwrite("frames/frame_%d.jpg" % time_laped, image)
            else:
                temp_read = read_temp_from_image(image, client)
                if temp_read > 0:
                    #cv2.imwrite("frames/frame_%d.jpg" % time_laped, image)
                    alog.info(f"Found temperature: '{temp_read}'")
            
            if temp_read<=0: continue
            temp=temp_read
            ##########################################################################
            #temperature record
            if bufl in blacklist:
                temp = 99        
            elif temp>=38:
                ter+="1,%s\n" % temp
            else:
                ter+="99999,%s\n" % temp
            outf.write(ter)
            for line in inf.readlines():
                line=line.replace("\n","")
                buf=re.split(",",line)
                if buf[1] in blacklist:
                    ter+=buf[1]+"2,%s\n" % temp
                elif buf[1]!=bufl:
                    ter=buf[1]+",99999,%s\n" % temp
            outf.write(ter)
            outf.close()
            inf.close()
            time.sleep(0.01)
        
            inf99=open("stop.csv","w+")
            inf99.close()
            
            os.popen("copy alert.csv alert_bk.csv")
            time.sleep(0.1)
            os.popen("del stop.csv")
            ##########################################################################

                
    except Exception as exp:
        alog.exception("video read error")
    finally:
        try:
            vidcap.release()
        except:
            pass
        
        try:
            cv2.destroyAllWindows()
        except:
            pass
        
        alog.info('Completed')


def read_temp_from_image(cv_image, google_client):
    temp_list = []
    try:
        success, encoded_image = cv2.imencode('.jpg', cv_image)
        img_bytes = encoded_image.tobytes()
        
        image = vision.types.Image(content=img_bytes)
        response = google_client.text_detection(image=image)
        texts = response.text_annotations
        
        for text in texts:
            desc_text = text.description
            alog.debug(f'Found text: {desc_text}')
            temp = extract_temp_from_text(desc_text.strip())
            if temp >= 0:
                alog.debug(f'Found temperature: {temp}')
                temp_list.append(temp)
            
    except Exception as exp:
        alog.error("Cannot read text from image", exp)

    if len(temp_list) == 0:
        temp_found = 0
    elif len(temp_list) == 1:
        temp_found = temp_list[0]
    elif len(temp_list) == 2:
        alog.info(f'2 temperatures are found: {temp_list}')
        temp_found = temp_list[1]
    else:
        alog.info(f'More than 2 temperatures are found: {temp_list}')
        temp_found = temp_list[1]

    return temp_found

def extract_temp_from_text(text):
    if not TEMP_REG_PATTERN.match(text):
        return -1
    
    try:
        temp = float(text)
        # It may not read comma, so the number contains only 3 digits
        if temp > 100:
            temp = temp / 10
        
        if temp < 20 or temp > 60:
            alog.info(f'Invalid temperature < 20 or > 60: {temp}')
            return -1
    except Exception as exp:
        alog.exception("check temperature error")
    
    return temp

if __name__ == '__main__':
    try:
        main(argv = sys.argv[1:])
    except SystemExit:
        pass
   

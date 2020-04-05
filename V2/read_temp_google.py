import sys
import logging as alog

import os
from os.path import join, exists
import time

import cv2
import re
from google.cloud import vision

Google_AUTH_KEY = r'ipa-group-project-4a4e69d12770.json'

TEMP_REG_PATTERN = re.compile(r'^[2345]\d\.?\d$')

def main(argv):
    # Setup service account authentication key
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Google_AUTH_KEY
    
    alog.basicConfig(level=alog.DEBUG)

    alog.info(f"opencv verion: {cv2.__version__}")

    client = vision.ImageAnnotatorClient()
    alog.info(f'Create client and connect to google cloud')

    try:
        # Get a reference to webcam #0 (the default one)
        vidcap = cv2.VideoCapture(0)
        
        capture_temp = True
        start_time = time.time()
                
        while capture_temp:
            current_time = time.time()
            time_laped = int(current_time - start_time)
            
            start_time = current_time
            
            success, image = vidcap.read()
            
            # Convert BGR to RGB color for display
            #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            if image is None:
                capture_temp = False
                break
                
            cv2.imshow("frame", image)
            
            key = cv2.waitKey(25)
            
            if key & 0xFF == ord('q'):
                capture_temp = False
                alog.info("Stoped")
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
   

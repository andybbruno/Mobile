import requests
import time
import json
from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import os
import random
import png
import numpy as np
from PIL import Image
from io import BytesIO


# Duty cycle
duty = 5 

# Machine ID
ID = 11222

# Lists
prod = ["caffe", "cioccolato", "te", "cappucino", "laghine"]

trans = ["rfid", "cash", "app"]

# Amazon URL
ec2 = 'http://ec2-18-212-110-170.compute-1.amazonaws.com:3000'

# Microsoft API
subscription_key = os.environ['API_KEY']
vision_base_url = "https://francecentral.api.cognitive.microsoft.com/vision/v2.0/"
vision_analyze_url = vision_base_url + "analyze"


headers = {'Ocp-Apim-Subscription-Key': subscription_key,
           "Content-Type": "application/octet-stream"}

params = {'visualFeatures': 'Objects,Faces'}


debug = False
ssh = False


def getRectangle(personDict):
    if 'object' in personDict.keys():
        if(personDict['object'] == 'person'):
            rect = personDict['rectangle']
            left = rect['x']
            top = rect['y']
            bottom = left + rect['w']
            right = top + rect['h']
            return left, top, bottom, right
    else:
        rect = personDict['faceRectangle']
        left = rect['left']
        top = rect['top']
        bottom = left + rect['height']
        right = top + rect['width']
        return left, top, bottom, right


camera = PiCamera()
camera.resolution = (1280, 720)
time.sleep(2)

# elapsed_time = 0
try:
    while True:
         # Per evitare di fare più di 20 chiamate al min
        # if (elapsed_time < duty):
        #     time.sleep(duty - elapsed_time)

        # start_time = time.time()

        # rawCapture = PiRGBArray(camera)
        # camera.capture(rawCapture, format="bgr")
        # frame = rawCapture.array


        
        # Create an in-memory stream
        frame = np.empty((1280, 720, 3), dtype=np.uint8)
        camera.capture(frame, 'bgr')

        print("FRAME --> " , str(type(frame)))

        # print("FRAME --> " , str(type(frame.tobytes())))
        # ~ frame = cv2.flip(frame, -1)

        # img_str = cv2.imencode('.jpg', frame)[1].tostring()
        # print("BYTES --> " , str(type(img_str)))

        response = requests.post(vision_analyze_url,
                                 headers=headers,
                                 params=params,
                                 data=frame)

        print(response.content)

except Exception as e:
    print('Error:' , e)

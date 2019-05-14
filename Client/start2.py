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
from PIL import Image, ImageDraw
from io import BytesIO


# Duty cycle
duty = 3

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
            return ((left, top), (bottom, right))
    else:
        rect = personDict['faceRectangle']
        left = rect['left']
        top = rect['top']
        bottom = left + rect['height']
        right = top + rect['width']
        return ((left, top), (bottom, right))


camera = PiCamera()
camera.resolution = (1280, 720)
time.sleep(0.5)

elapsed_time = 0
try:
    while True:
        # Per evitare di fare più di 20 chiamate al min
        if (elapsed_time < duty):
            time.sleep(duty - elapsed_time)
        
        start_time = time.time()

        frame = np.empty((1280, 720, 3), dtype=np.uint8)
        camera.capture(frame, format='jpeg')


        response = requests.post(vision_analyze_url,
                                 headers=headers,
                                 params=params,
                                 data=frame.tostring())

        if response.status_code != 200:
            raise Exception("Error:", response)

        print(response.content)
        parsed = response.json()
        
        people = 0
        faces = len(parsed['faces'])
        
        img = Image.open(BytesIO(frame))
        draw = ImageDraw.Draw(img)
        
        for obj in parsed['objects']:
            print(obj)
            if (obj['object'] == 'person'):
                people += 1
                x, y, w, h = getRectangle(obj)
                draw.rectangle(getRectangle(obj), outline='red', linewidth=2)

        for face in parsed['faces']:
            print(face)
            x, y, w, h = getRectangle(face)
            draw.rectangle(getRectangle(obj), outline='green', linewidth=2)

        
        elapsed_time = time.time() - start_time

        print("<", people, " people, ", faces,
                "faces> ", elapsed_time, " seconds")

        url_ord = ec2 + '/' + str(ID) + '/order'

        # trn = trans[random.randint(1, len(trans) - 1)]
        # prd = prod[random.randint(1, len(prod) - 1)]

        # # TODO: add products levels
        # tmp = {"transaction_type": trn,
        #         "product": prd,
        #         "satisfaction": random.random(),
        #         "people_detected": people,
        #         "face_recognised": faces
        #         }

        # try:
        #     requests.post(url_ord, json=json.dumps(tmp))
        # except Exception as e:
        #     print('Error:' , e)


        # url_frame = ec2 + '/' + str(ID) + '/live'
        # path = str(ID) + ".jpg"


        # im = Image.fromarray(frame)
        # im.save(path)
        
        # with open(path, 'rb') as f:
        #     try:
        #         requests.post(url_frame, files={"frame": f})
        #     except Exception as e:
        #         print('Error:' , e)
        

except Exception as e:
    print('Error:', e)

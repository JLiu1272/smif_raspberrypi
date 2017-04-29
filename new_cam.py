from __future__ import print_function
import cv2
import json
import numpy as np
import socket
import sys
from picamera.array import PiRGBArray
from picamera import PiCamera
import pickle
import os
from time import sleep
import struct ### new code
from datetime import datetime
from subprocess import call
import pycurl
import requests
import struct ### new code
cap=cv2.VideoCapture(0)
cap.set(3,224)
cap.set(4,224)
clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsocket.connect(('ai.student.rit.edu',8083))
directionBuffer = []
bufferCounter = 0
pointsBuffer = []
max_conf_object = ""
last_time_of_interest = datetime.now()
oldFrame = [0,0]
newFrame = [0,0]

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (224, 224)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(224, 224))

def getAveragePoint(pointArr):

    sumX = 0
    sumY = 0
    for point in pointArr:
        sumX += point[0]
        sumY += point[1]

    X= sumX/len(pointArr)
    Y= sumY/len(pointArr)

    return [X,Y]

url_exp = "http://107.23.213.161/expiration_database.json"
url_add = "http://107.23.213.161/addItem.php"

"""
Type = Where is the food being placed
0 - Room Temperature
1 - Refrigerator
2 - Freezer at 0 F
"""



sleep(0.1)
for single in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = single.array
    data = pickle.dumps(frame) ### new code
    clientsocket.sendall(struct.pack("Q", len(data))+data) ### new code
    # sleep(.2)
    data = clientsocket.recv(4096*5)


    os.system('clear')


    # print (data)
    json_data = json.loads(data)
    print(json_data["None"])
    max_confidence_object = json_data['None'][0][0]
    max_confidence_value = float(json_data['None'][0][1])



    points = json.loads(data)['points']

    if max_confidence_value > .95:
        cv2.circle(frame,(points[0],points[1]),25,(0,0,255),-1)
        max_conf_object = max_confidence_object
        pointsBuffer.append(points[0])
        print(max_confidence_object)
        print(max_confidence_value)
        last_time_of_interest = datetime.now()

    elif len(pointsBuffer) > 0 and (datetime.now() -last_time_of_interest).total_seconds()>2 :
        if (pointsBuffer[0] - pointsBuffer[len(pointsBuffer)-1] ) >0:
            print('moving right')
            url = "http://107.23.213.161/expiration_database.json"
            r = requests.get(url)
            r.text
            postData({"name":max_confidence_object,'date_in':'2017-03-03','date_left':r.text})
            print("DONE")
        else:
            print("moving left")

        pointsBuffer = []
        max_conf_object = ""

    rawCapture.truncate(0)
    #cv2.circle(frame,(points[0],points[1]),25,(0,0,255),-1)
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('s'):
        exit()

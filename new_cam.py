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

#Imports for Computing Expiration Date 
from datetime import timedelta
import datetime
import re


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
def getRequest(url, food, type):
    r = requests.get(url)
    json = r.json()
    lower_food = food.lower()

    filtered = {}
    if lower_food not in json.keys():
        for key in json:
            regex = r"" + re.escape(food)
            need_match = re.search(regex, key)
            if need_match is not None:
                filtered[need_match.group(0)] = json[key]
                return filtered[need_match.group(0)][type]
    return json[lower_food][type]

"""
Compute Expiration Date
"""
def computeDateLeft(date, food, type):
    today = datetime.datetime.now()
    data = getRequest(url_exp, food, type)
    dateleft = ""

    if type == 2 and data == "" or data == "\u00a0":
        return "Unable to get value"
    elif data == "" or data == "\u00a0":
        return computeDateLeft(today, food, type+1)
    elif "month" in data or "months" in data:
        week = int(data[0])*365/12
        print("Month: " + str(week))
        dateleft = date + timedelta(week)
    elif "day" in data or "days" in data:
        dateleft = date + timedelta(days=int(data[0]))
    elif "year" in data or "years" in data:
        year = int(data[0])*365
        dateleft = date + timedelta(int(year))
    elif "week" in data or "weeks" in data:
        week = int(data[0])
        dateleft = date + timedelta(week)

    return dateleft

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
            today = datetime.datetime.now()
            date_left = computeDateLeft(today, max_confidence_object, 1)
            postData({"name":max_confidence_object,'date_in':today,'date_left':date_left})
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

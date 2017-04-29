import cv2
import numpy as np
import socket
import sys
import pickle
import os
import pycurl, json

from picamera.array import PiRGBArray
from picamera import PiCamera

import RPi.GPIO as GPIO
import time
import struct ## new code

from time import sleep


GPIO.setmode(GPIO.BCM)


def postData(buffer1):
    link = "http://129.21.65.108:81/fridge_app/addItem.php"
    c = pycurl.Curl()
    c.setopt(pycurl.URL, link)
    c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
    data = json.dumps(buffer1)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, data)
    c.setopt(pycurl.VERBOSE, 1)
    c.perform()
    #print curl_agent.getinfo(pycurl.RESPONSE_CODE)
    c.close()

def getDistance():
    TRIG = 23
    ECHO = 24

    #print 'Distance Measurement In Progress'

    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)

    GPIO.output(TRIG, False)
    #print 'Waiting For Sensor To Settle'
   # time.sleep(2)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = 0
    pulse_end = 0

    while GPIO.input(ECHO)==0:
        pulse_start = time.time()

    while GPIO.input(ECHO)==1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150

    distance = round(distance, 2)
    return distance


cap=cv2.VideoCapture(0)
cap.set(3,224)
cap.set(4,224)
clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsocket.connect(('ai.student.rit.edu',8083))

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (224, 224)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(224, 224))

# allow the camera to warmup
time.sleep(0.1)
buffer = []
print "Received"
senseStarted = False
for single in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    frame = single.array
    data = pickle.dumps(frame) ### new code
    distance = getDistance()
   # print distance
    if (distance < 30):
        senseStarted = True
        print "small"
        clientsocket.sendall(struct.pack("Q", len(data))+data) ### new code
        data = clientsocket.recv(4096)

        if(len(buffer)<5):
            buffer.append(data)
        else:
            buffer.pop(0)
        os.system('clear')
        print data



    else:
        if(senseStarted):
            print "will send data"
            print buffer[0]
            d_json = json.loads(buffer[0]);
            postData(d_json);

        senseStarted = False

    print getDistance()
#    dict = data.get('None')
    cv2.imshow('frame',frame)

    if cv2.waitKey(1) & 0xFF == ord('s'):
	exit()
    rawCapture.truncate(0)

print 'Distance:',distance,'cm'

GPIO.cleanup()


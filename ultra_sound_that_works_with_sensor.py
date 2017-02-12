import cv2
import numpy as np
import socket
import sys
import pickle
import os

from picamera.array import PiRGBArray
from picamera import PiCamera

import RPi.GPIO as GPIO
import time
import struct ## new code

from time import sleep


GPIO.setmode(GPIO.BCM)

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
clientsocket.connect(('delta.student.rit.edu',8083))

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (224, 224)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(224, 224))

# allow the camera to warmup
time.sleep(0.1)

print "Received"

for single in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    frame = single.array
    data = pickle.dumps(frame) ### new code
    distance = getDistance()
    #print distance
    if (distance < 30):
        print "small"
        clientsocket.sendall(struct.pack("Q", len(data))+data) ### new code
        data = clientsocket.recv(4096)
   # sleep(1)
        os.system('clear')
        print data

    print getDistance()
#    dict = data.get('None')
    cv2.imshow('frame',frame)

    if cv2.waitKey(1) & 0xFF == ord('s'):
	exit()
    rawCapture.truncate(0)

print 'Distance:',distance,'cm'

GPIO.cleanup()


import cv2
import numpy as np
import socket
import sys
import pickle
import os

from picamera.array import PiRGBArray
from picamera import PiCamera
import time
 
from time import sleep
import struct ### new code
cap=cv2.VideoCapture(0)
cap.set(3,224)
cap.set(4,224)
clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsocket.connect(('delta.student.rit.edu',8084))

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (224, 224)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(224, 224))
 
# allow the camera to warmup
time.sleep(0.1)

for single in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = single.array
    data = pickle.dumps(frame) ### new code
    clientsocket.sendall(struct.pack("Q", len(data))+data) ### new code
    sleep(1)
    data = clientsocket.recv(4096)
    os.system('clear')

    dict = data.get('None')
    print dict
    cv2.imshow('frame',frame)
	
    if cv2.waitKey(1) & 0xFF == ord('s'):
	exit()
    rawCapture.truncate(0) 

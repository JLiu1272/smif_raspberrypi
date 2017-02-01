from picamera import PiCamera
from time import sleep

import requests

camera = PiCamera()

camera.start_preview()
sleep(5)
camera.capture('/home/pi/Desktop/image.jpg')
camera.stop_preview()

url = 'http://delta.student.rit.edu:5000/upload'
files = {'file': open('/home/pi/Desktop/image.jpg', 'rb')}

r = requests.post(url, files=files)
r.text



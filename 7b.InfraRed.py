import RPi.GPIO as GPIO #import RPi.GPIO module
from time import sleep

GPIO.setmode(GPIO.BCM) #choose BCM mode
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.IN) # set GPIO 17 as input

while (True):
    if GPIO.input(17) == 0: #read a LOW i.e. motion is detected

            print('Object in range')
           
    else: #read a LOW i.e. no motion is detected
        if GPIO.input(17) == 1:
            print('No object in range')

    sleep(0.1)

#SPEECH RECOGNITION CODE

import speech_recognition as sr
import pyttsx3
import datetime
import dht11
import time
import RPi.GPIO as GPIO #import RPi.GPIO module, rename it as GPIO

GPIO.setmode(GPIO.BCM) #choose BCM mode, refer to pins as GPIO no.
GPIO.setwarnings(False)
GPIO.setup(24,GPIO.OUT) #set LED as output
GPIO.setup(26,GPIO.OUT) #set Servo as output
GPIO.setup(23,GPIO.OUT) #set DC Motor as output

PWM=GPIO.PWM(26,50) #set 50Hz PWM output at GPIO26/Servo
instance = dht11.DHT11(pin=21) #read data using pin 21


#Initialize Text to Speech
engine = pyttsx3.init()
#Initializer Speech
r = sr.Recognizer()
rate = engine.getProperty('rate')   # getting details of current speaking rate
engine.setProperty('rate', 165)     # setting up new voice rate

while(True):
    
    with sr.Microphone() as source:
        print("Start Talking")
        engine.say("Say something")
        engine.runAndWait()
        audio = r.listen(source)
    try:
        print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
        words = r.recognize_google(audio)
        if(words == "today"):
            today = datetime.datetime.now()
            print(today.strftime("%A, %d. %B %Y %I:%M%p"))
            engine.say(today.strftime("%A, %d. %B %Y %I:%M%p"))
            engine.runAndWait()
        if(words == "hi"):
            engine.say("Welcome back")
            engine.runAndWait()
        if(words == "light on"):
            print("Light On")
            GPIO.output(24,1) #output logic high/'1'
            engine.say("Turning on light")
            engine.runAndWait()
        if(words == "light off"):
            print("Light off")
            GPIO.output(24,0) #output logic low/'0'
            engine.say("Turning off light")
            engine.runAndWait()
        if(words == "open the door"):
            time.sleep(2)
            print("Opening Door")
            engine.say("Opening door")
            engine.runAndWait()
            PWM.start(3) #3% duty cycle
            print('duty cycle:', 3) #3 o'clock position
            time.sleep(3) #allow time for movement
        if(words == "close the door"):
            time.sleep(2)
            print("Closing Door")
            engine.say("Closing door")
            engine.runAndWait()
            PWM.start(12) #13% duty cycle
            print('duty cycle:', 12) #9 o'clock position
            time.sleep(3) #allow time for movement
        if(words == "turn on fan"):
            time.sleep(2)
            print("Turning on Fan")
            engine.say("Turning on Fan")
            engine.runAndWait()
            GPIO.output(23,1) #output logic high/'1'
        if(words == "turn off fan"):
            time.sleep(2)
            print("Turning off fan")
            engine.say("Turning off fan")
            engine.runAndWait()
            GPIO.output(23,0) #output logic low/'0'
        if(words == "how's the weather"):
            result = instance.read()
            while(True):
                if result.is_valid():
                    print("Temperature: %-3.1f C" % result.temperature)
                    engine.say("The Temperature is %-3.1f degrees celsius" % result.temperature)
                    engine.runAndWait()
                    print("Humidity: %-3.1f %%" % result.humidity)
                    engine.say("The Humidity is %-3.1f %%" % result.humidity)
                    engine.runAndWait()
                    break
                else:
                    print("Invalid result... retrying")
                    result = instance.read()
                    time.sleep(0.5)
        if(words == "I'm home"):
            engine.say("Welcome back")
            engine.runAndWait()
            GPIO.output(24,1) #Turn on LED
            PWM.start(12) #13% duty cycle
            print('duty cycle:', 12) #9 o'clock position
            time.sleep(3) #allow time for movement
            GPIO.output(23,1) #Turn on Fan
            
            
                    
            
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

#SPEECH RECOGNITION CODE
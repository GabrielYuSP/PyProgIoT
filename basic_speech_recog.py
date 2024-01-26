#SPEECH RECOGNITION CODE

import speech_recognition as sr
#TEXT TO SPEECH
import pyttsx3

engine = pyttsx3.init()
r = sr.Recognizer()

while(True):
    with sr.Microphone() as source:
        print("Start Talking")
        audio = r.listen(source)
        
    try:
        print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
        engine.say(r.recognize_google(audio))
        engine.runAndWait()
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

#SPEECH RECOGNITION CODE
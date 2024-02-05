import RPi.GPIO as GPIO
import I2C_LCD_driver #import the library
import sys
from mfrc522 import SimpleMFRC522
from time import sleep
from threading import Thread

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT) #set Buzzer as output
GPIO.setup(26,GPIO.OUT) #set GPIO 26 as output


#servo motor
PWM=GPIO.PWM(26,50) #set 50Hz PWM output at GPIO26

#set password
password = "123456"
input = ""
inputs = 0

#RFID
reader = SimpleMFRC522()
auth = []

#lcd test
LCD = I2C_LCD_driver.lcd() #instantiate an lcd object, call it LCD
sleep(0.5)
LCD.backlight(0) #turn backlight off
sleep(0.5)
LCD.backlight(1) #turn backlight on 
sleep(0.5)
LCD.lcd_clear() #clear lcd
sleep(0.5)
print("LCD TESTED")
#lcd test

def rfid(arg):
    GPIO.setwarnings(False)
    #reader = SimpleMFRC522()
    #auth = []
    global reader
    global auth
    print("Hold card near the reader to check if it is in the database")
    id = arg
    id = str(id)
    f = open("authlist.txt", "r+")
    if f.mode == "r+":
        auth=f.read()
    if id in auth:
        number = auth.split('\n')
        pos = number.index(id)
        print("Card with UID", id, "found in database entry #", pos, "; access granted")
        unlockDoor()
    else:
        print("Card with UID", id, "not found in database; access denied")


def unlockDoor():
    global inputs
    global input
    PWM.start(3) #3% duty cycle
    print('duty cycle:', 3) #3 o'clock position
    sleep(4) #allow time for movement
    PWM.start(12) #13% duty cycle
    print('duty cycle:', 12) #9 o'clock position
    sleep(4) #allow time for movement
    inputs = 0 #reset inputs to 0
    input = "" #reset input to nothing
    print("Reset input to 0")
    LCD.lcd_clear()


def main():
    #rfid threading
    rfid_thread = Thread(target=rfid)
    rfid_thread.start()
    
    MATRIX=[ [1,2,3],
            [4,5,6],
            [7,8,9],
            ['*',0,'#']] #layout of keys on keypad
    ROW=[6,20,19,13] #row pins
    COL=[12,5,16] #column pins

    #set column pins as outputs, and write default value of 1 to each
    for i in range(3):
        GPIO.setup(COL[i],GPIO.OUT)
        GPIO.output(COL[i],1)


    #set row pins as inputs, with pull up
    for j in range(4):
        GPIO.setup(ROW[j],GPIO.IN,pull_up_down=GPIO.PUD_UP)
        
    global input
    global inputs
    global reader
    global auth
    
    #scan keypad
    while (True):
        print("Key PIN")
        LCD.lcd_display_string("Enter PIN", 1) #write on line 1            
        for i in range(3): #loop thru’ all columns
            GPIO.output(COL[i],0) #pull one column pin low
            id = reader.read_id2()
            if(id != "none"):
                rfid(id)
            for j in range(4): #check which row pin becomes low
                id = reader.read_id2()
                if GPIO.input(ROW[j])==0: #if a key is pressed
                    key_pressed = MATRIX[j][i]
                    input = input + str(key_pressed) #add the keys into a PIN
                    inputs = inputs + 1 #increase number of inputs by 1
                    print (MATRIX[j][i]) #print the key pressed in terminal
                    print("Number of inputs: " + str(inputs))
                    LCD.lcd_display_string(input, 2) #write on line 1
                    print("Check Input")
                    if (inputs % 6 == 0): 
                        print("Input is 6")                 
                        if(input == password): #if the inputted pin is the same as password
                            LCD.lcd_clear() #clear the LCD
                            LCD.lcd_display_string("Access Granted", 1) #Access Granted
                            print("Access Granted")
                            unlockDoor() #call unlockDoor function
                            continue
                        elif(input != password):
                            LCD.lcd_clear() #clear the LCD
                            LCD.lcd_display_string("Access Denied", 1) #Access Denied
                            print("Access Denied")
                            input = ""
                            sleep(2)
                            LCD.lcd_clear()
                            if(inputs == 18): #after 3 wrong attempts 
                                print("3 Attempts Wrong!!")
                                for x in range(3):
                                    GPIO.output(18,1) #Buzzer output logic high/'1'
                                    sleep(0.5) #delay 1 second
                                    GPIO.output(18,0) #Buzzer output logic low/'0'
                                    sleep(0.5) #delay 1 second
                                LCD.lcd_clear()
                                inputs = 0
                            else:
                                continue
                    while GPIO.input(ROW[j])==0: #debounce
                        sleep(0.1)
            GPIO.output(COL[i],1) #write back default value of 1
            #check if pin is 6 numbers (remainder 0)
    
if __name__ == '__main__':
    main()
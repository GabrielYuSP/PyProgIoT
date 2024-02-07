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

#lcd test
LCD = I2C_LCD_driver.lcd() #instantiate an lcd object, call it LCD
sleep(0.5)
LCD.backlight(0) #turn backlight off
sleep(0.5)
LCD.backlight(1) #turn backlight on 
#lcd test

reader = SimpleMFRC522()
rfidUnlock = 1
cardAccess = 0

def rfid():
    global rfidUnlock
    global cardAccess
    GPIO.setwarnings(False)
    auth = []
    while (True):
        if (rfidUnlock == 1):
            print("Hold card near the reader to check if it is in the database")
            id = reader.read_id_no_block()
            id = str(id)
            f = open("authlist.txt", "r+")
            if f.mode == "r+":
                auth=f.read()
            if id in auth:
                number = auth.split('\n')
                pos = number.index(id)
                print("Card with UID", id, "found in database entry #", pos, "; access granted")
                cardAccess = 1
            else:
                print("Card with UID", id, "not found in database; access denied")
            sleep(2)
        else:
            continue

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
    
def rfid_del():
    global rfidUnlock
    rfidUnlock = 0
    LCD.lcd_clear()
    LCD.lcd_display_string("Tap RFID Card",1)
    print("Hold card near the reader to delete it from the database")
    id = reader.read_id()
    id = str(id)
    with open("authlist.txt", "r+") as fp:
        lines = fp.readlines()
        fp.seek(0)
        for line in lines:
            if id not in line.strip("\n"):
                fp.write(line)
        fp.truncate() 
        print("Card with UID " + id + " has been deleted")
        LCD.lcd_display_string("Card Deleted!",1)
        sleep(2)
        LCD.lcd_clear()
        sleep(2)
        rfidUnlock = 1

def rfid_add():
    global rfidUnlock
    rfidUnlock = 0
    LCD.lcd_clear()
    LCD.lcd_display_string("Tap RFID Card",1)
    print("Hold card near the reader to register it in the database")
    id = reader.read_id()
    id = str(id)
    f = open("authlist.txt", "a+")
    f = open("authlist.txt", "r+")
    if f.mode == "r+":
        auth=f.read()
    if id not in auth:
        f.write(id)
        f.write('\n')
        f.close()
        pos = auth.count('\n')
        print("New card with UID", id,  "detected; registered as entry #", pos)
        LCD.lcd_display_string("Card Registered!",1)
        sleep(2)
        LCD.lcd_clear()
    else:
        number = auth.split('\n')
        pos = number.index(id)
        print("Card with UID", id, "already registered as entry #", pos)
        LCD.lcd_display_string("Card Already",1)
        LCD.lcd_display_string("Registered!", 2)
        sleep(2)
        LCD.lcd_clear()
    sleep(2)
    rfidUnlock = 1

def main():    
    #rfid threading
    rfid_thread = Thread(target=rfid)
    rfid_thread.start()
    
    MATRIX=[[1,2,3],
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

    #set password
    password = "123456"
    input = ""
    inputs = 0
    LCD.lcd_clear()
    sleep(0.5)
    
    global cardAccess

    #scan keypad
    while (True):
        LCD.lcd_display_string("Enter PIN", 1) #write on line 1
        if(cardAccess == 1):
            LCD.lcd_clear() #clear the LCD
            LCD.lcd_display_string("Access Granted", 1) #Access Granted
            print("Access Granted")
            unlockDoor()
            LCD.lcd_clear()
            cardAccess = 0 #set back to 0
        for i in range(3): #loop thru’ all columns
            GPIO.output(COL[i],0) #pull one column pin low
            for j in range(4): #check which row pin becomes low
                if GPIO.input(ROW[j])==0: #if a key is pressed
                    key_pressed = MATRIX[j][i]
                    input = input + str(key_pressed) #add the keys into a PIN
                    inputs = inputs + 1 #increase number of inputs by 1
                    print (MATRIX[j][i]) #print the key pressed in terminal
                    print(inputs)
                    LCD.lcd_display_string(input, 2) #write on line 1
                    sleep(0.5)
                    print("Check Input")
                    if(key_pressed == "*"):
                        print("Add RFID Tag")
                        LCD.lcd_clear()
                        LCD.lcd_display_string("Add RFID Tag", 1)
                        sleep(2)
                        LCD.lcd_clear()
                        LCD.lcd_display_string("Tap RFID tag", 1)
                        rfid_add()
                        input = ""
                        inputs = 0
                    elif(key_pressed == "#"):
                        print("Remove RFID Tag")
                        LCD.lcd_clear()
                        LCD.lcd_display_string("Delete RFID Tag", 1)
                        sleep(2)
                        LCD.lcd_clear()
                        LCD.lcd_display_string("Tap RFID tag", 1)
                        rfid_del()
                        input = ""
                        inputs = 0
                    elif (inputs % 6 == 0): 
                        print("Input is 6")                 
                        if(input == password): #if the inputted pin is the same as password
                            LCD.lcd_clear() #clear the LCD
                            LCD.lcd_display_string("Access Granted", 1) #Access Granted
                            print("Access Granted")
                            unlockDoor()
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
                                input = ""
                            else:
                                continue
                    while GPIO.input(ROW[j])==0: #debounce
                        sleep(0.5)
            GPIO.output(COL[i],1) #write back default value of 1
            #check if pin is 6 numbers (remainder 0)
    
if __name__ == '__main__':
    main()
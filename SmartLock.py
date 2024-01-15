import RPi.GPIO as GPIO
import I2C_LCD_driver #import the library
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(12,GPIO.OUT) #set GPIO 18 as output

#lcd test
LCD = I2C_LCD_driver.lcd() #instantiate an lcd object, call it LCD
sleep(0.5)
LCD.backlight(0) #turn backlight off
sleep(0.5)
LCD.backlight(1) #turn backlight on 
#lcd test

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

#set password
password = "123456"
input = ""
inputs = 0

#scan keypad
while (True):
    for i in range(3): #loop thru’ all columns
        GPIO.output(COL[i],0) #pull one column pin low
        for j in range(4): #check which row pin becomes low
            if GPIO.input(ROW[j])==0: #if a key is pressed
                key_pressed = MATRIX[j][i]
                input = input + key_pressed #add the keys into a PIN
                inputs = inputs + 1 #increase number of inputs by 1
                print (MATRIX[j][i]) #print the key pressed in terminal
                LCD.lcd_display_string("Enter PIN", 1) #write on line 1
                LCD.lcd_display_string(input, 2) #write on line 1
                while GPIO.input(ROW[j])==0: #debounce
                    sleep(0.5)
        GPIO.output(COL[i],1) #write back default value of 1
        #check if pin is 6 numbers (remainder 0)
        if (inputs % 6 == 0):
            if(input == password): #if the inputted pin is the same as password
                LCD.lcd_clear() #clear the LCD
                LCD.lcd_display_string("Access Granted", 1) #Access Granted
                input = "" #reset input to nothing
            else:
                LCD.lcd_clear() #clear the LCD
                LCD.lcd_display_string("Access Denied", 1) #Access Denied
                if(inputs == 18): #after 3 wrong attempts 
                    print("3 Attempts Wrong!!")
                    GPIO.output(12,1) #Buzzer output logic high/'1'
                    sleep(1) #delay 1 second
                    GPIO.output(18,0) #Buzzer output logic low/'0'
                    sleep(1) #delay 1 second
                    
                    
                    
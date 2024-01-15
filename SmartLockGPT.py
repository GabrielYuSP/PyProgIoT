import RPi.GPIO as GPIO
from time import sleep
import I2C_LCD_driver

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

MATRIX = [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9],
          ['*', 0, '#']]  # layout of keys on keypad
ROW = [6, 20, 19, 13]  # row pins
COL = [12, 5, 16]  # column pins

PASSWORD = [1, 2, 3, 4]  # Set your desired password

BEEP_PIN = 18  # Buzzer GPIO pin

LCD = I2C_LCD_driver.lcd()


def setup_keypad():
    for i in range(3):
        GPIO.setup(COL[i], GPIO.OUT)
        GPIO.output(COL[i], 1)

    for j in range(4):
        GPIO.setup(ROW[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)


def scan_keypad():
    for i in range(3):
        GPIO.output(COL[i], 0)
        for j in range(4):
            if GPIO.input(ROW[j]) == 0:
                return MATRIX[j][i]
    return None


def display_pin_on_lcd(pin):
    LCD.lcd_clear()
    LCD.lcd_display_string("Enter PIN:", 1)
    LCD.lcd_display_string("*" * len(pin), 2)


def display_result_on_lcd(result):
    LCD.lcd_clear()
    LCD.lcd_display_string(result, 1)
    sleep(2)
    LCD.lcd_clear()
    display_pin_on_lcd("")


def main():
    GPIO.setup(BEEP_PIN, GPIO.OUT)

    setup_keypad()
    LCD.backlight(1)

    entered_pin = ""
    wrong_attempts = 0

    while True:
        key = scan_keypad()

        if key is not None:
            if key == '#':
                if list(map(int, entered_pin)) == PASSWORD:
                    display_result_on_lcd("Access Granted")
                else:
                    wrong_attempts += 1
                    if wrong_attempts >= 3:
                        GPIO.output(BEEP_PIN, 1)
                        sleep(5)
                        GPIO.output(BEEP_PIN, 0)
                        wrong_attempts = 0
                    else:
                        display_result_on_lcd("Access Denied")
                entered_pin = ""
            elif key == '*':
                entered_pin = ""
                display_pin_on_lcd(entered_pin)
            else:
                entered_pin += str(key)
                display_pin_on_lcd(entered_pin)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()

# A little test utility to help you make sure you wired up to the correct GPIO pins.
#
# LEDs will light up in synchronicity with the notification on the console which LED has been activated

import RPi.GPIO as GPIO
from gpiozero import LED
from time import sleep

GPIO.setmode(GPIO.BCM)

for led in range(0,27):
    print('GPIO %s activated' % (led))
    GPIO.setup(led, GPIO.OUT)
    GPIO.output(led, GPIO.HIGH)
    sleep(1)
    GPIO.output(led, GPIO.LOW)

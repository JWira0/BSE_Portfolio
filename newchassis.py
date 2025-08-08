from flask import Flask, Response, render_template_string
from picamera2 import Picamera2
import cv2
import numpy as np


import RPi.GPIO as GPIO
import time

# Motor A (Driver 1)
A_IA = 12   # GPIO17
A_IB = 11   # GPIO18

# Motor B (Driver 1)
B_IA = 15   # GPIO27
B_IB = 13   # GPIO22

# Motor C (Driver 2)
C_IA = 18   # GPIO23
C_IB = 16   # GPIO24

# Motor D (Driver 2)
D_IA = 23   # GPIO25
D_IB = 22   # GPIO11

# Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
for pin in [A_IA, A_IB, B_IA, B_IB, C_IA, C_IB, D_IA, D_IB]:
    GPIO.setup(pin, GPIO.OUT)

# PWM at 100 Hz
pwm_A_IA = GPIO.PWM(A_IA, 100)
pwm_A_IB = GPIO.PWM(A_IB, 100)
pwm_B_IA = GPIO.PWM(B_IA, 100)
pwm_B_IB = GPIO.PWM(B_IB, 100)
pwm_C_IA = GPIO.PWM(C_IA, 100)
pwm_C_IB = GPIO.PWM(C_IB, 100)
pwm_D_IA = GPIO.PWM(D_IA, 100)
pwm_D_IB = GPIO.PWM(D_IB, 100)

# Start all with 0% duty cycle (motors off)
for pwm in [pwm_A_IA, pwm_A_IB, pwm_B_IA, pwm_B_IB, pwm_C_IA, pwm_C_IB, pwm_D_IA, pwm_D_IB]:
    pwm.start(0)

def stop_all():
   for pwm in [pwm_A_IA, pwm_A_IB, pwm_B_IA, pwm_B_IB, pwm_C_IA, pwm_C_IB, pwm_D_IA, pwm_D_IB]:
       pwm.ChangeDutyCycle(0)
       
def forward_all(speed=70):
    #Turn ON forward direction pins (IA)
    for pwm in [pwm_A_IA, pwm_B_IA, pwm_C_IA, pwm_D_IA]:
        pwm.ChangeDutyCycle(speed)
    # Turn OFF backward direction pins (IB)
    for pwm in [pwm_A_IB, pwm_B_IB, pwm_C_IB, pwm_D_IB]:
        pwm.ChangeDutyCycle(0)

def backward(speed=70):
    for pwm in [pwm_A_IB, pwm_B_IB, pwm_C_IB, pwm_D_IB]:
        pwm.ChangeDutyCycle(speed)
    for pwm in [pwm_A_IA, pwm_B_IA, pwm_C_IA, pwm_D_IA]:
        pwm.ChangeDutyCycle(0)

def turn_left(speed=70):
    # Left side motors (A & C) go backward
    for pwm in [pwm_A_IB, pwm_C_IB]:
        pwm.ChangeDutyCycle(speed)
    for pwm in [pwm_A_IA, pwm_C_IA]:
        pwm.ChangeDutyCycle(0)

    # Right side motors (B & D) go forward
    for pwm in [pwm_B_IA, pwm_D_IA]:
        pwm.ChangeDutyCycle(speed)
    for pwm in [pwm_B_IB, pwm_D_IB]:
        pwm.ChangeDutyCycle(0)

def turn_right(speed=70):
    # Left side motors (A & C) go forward
    for pwm in [pwm_A_IA, pwm_C_IA]:
        pwm.ChangeDutyCycle(speed)
    for pwm in [pwm_A_IB, pwm_C_IB]:
        pwm.ChangeDutyCycle(0)

    # Right side motors (B & D) go backward
    for pwm in [pwm_B_IB, pwm_D_IB]:
        pwm.ChangeDutyCycle(speed)
    for pwm in [pwm_B_IA, pwm_D_IA]:
        pwm.ChangeDutyCycle(0)

def test_motor_A_forward():
    stop_all()
    pwm_A_IA.ChangeDutyCycle(70)
    pwm_A_IB.ChangeDutyCycle(0)
    time.sleep(2)
    stop_all()

def test_motor_A_backward():
    stop_all()
    pwm_A_IA.ChangeDutyCycle(0)
    pwm_A_IB.ChangeDutyCycle(70)
    time.sleep(2)
    stop_all()


if __name__ == "__main__":
    try:
        while True:
            forward_all(100)
            time.sleep(2)
            backward(100)
            time.sleep(2)
            turn_right(100)
            time.sleep(2)
            turn_left(100)
            time.sleep(2)
            stop_all()
            time.sleep(2)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        stop_all()
        GPIO.cleanup()


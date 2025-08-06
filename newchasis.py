import RPi.GPIO as GPIO
import time


A_IA = 12   # was GPIO18
A_IB = 16   # was GPIO23
B_IA = 33   # was GPIO24
B_IB = 18   # was GPIO13



# Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
for pin in [A_IA, A_IB, B_IA, B_IB]:
    GPIO.setup(pin, GPIO.OUT)

# PWM at 100 Hz
pwm_A_IA = GPIO.PWM(A_IA, 100)
pwm_A_IB = GPIO.PWM(A_IB, 100)
pwm_B_IA = GPIO.PWM(B_IA, 100)
pwm_B_IB = GPIO.PWM(B_IB, 100)
pwm_A_IA.start(0)
pwm_A_IB.start(0)
pwm_B_IA.start(0)
pwm_B_IB.start(0)

# Motor control functions
def motorA_forward(speed=100):
    pwm_A_IA.ChangeDutyCycle(speed)
    pwm_A_IB.ChangeDutyCycle(0)

def motorA_backward(speed=100):
    pwm_A_IA.ChangeDutyCycle(0)
    pwm_A_IB.ChangeDutyCycle(speed)

def motorB_forward(speed=100):
    pwm_B_IA.ChangeDutyCycle(speed)
    pwm_B_IB.ChangeDutyCycle(0)

def motorB_backward(speed=100):
    pwm_B_IA.ChangeDutyCycle(0)
    pwm_B_IB.ChangeDutyCycle(speed)

def stop_all():
    for pwm in [pwm_A_IA, pwm_A_IB, pwm_B_IA, pwm_B_IB]:
        pwm.ChangeDutyCycle(0)

# Test sequence
try:
    print("Both motors forward")
    motorA_forward(70)
    motorB_forward(70)
    time.sleep(2)

    print("Both motors backward")
    motorA_backward(70)
    motorB_backward(70)
    time.sleep(2)

    print("Spin in place")
    motorA_forward(70)
    motorB_backward(70)
    time.sleep(2)

    print("Stop")
    stop_all()

finally:
    stop_all()
    pwm_A_IA.stop()
    pwm_A_IB.stop()
    pwm_B_IA.stop()
    pwm_B_IB.stop()
    GPIO.cleanup()

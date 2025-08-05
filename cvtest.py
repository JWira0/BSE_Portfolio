from flask import Flask, Response, render_template_string
from picamera2 import Picamera2
import cv2
import numpy as np


import RPi.GPIO as GPIO
import time


# Motor A pins
A_IA = 18
A_IB = 23
# Motor B pins
B_IA = 24
B_IB = 13


# Setup
GPIO.setmode(GPIO.BCM)
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
def motorA_forward(speed=20):
   pwm_A_IA.ChangeDutyCycle(speed)
   pwm_A_IB.ChangeDutyCycle(0)


def motorA_backward(speed=20):
   pwm_A_IA.ChangeDutyCycle(0)
   pwm_A_IB.ChangeDutyCycle(speed)


def motorB_forward(speed=20):
   pwm_B_IA.ChangeDutyCycle(speed)
   pwm_B_IB.ChangeDutyCycle(0)


def motorB_backward(speed=20):
   pwm_B_IA.ChangeDutyCycle(0)
   pwm_B_IB.ChangeDutyCycle(speed)


def stop_all():
   for pwm in [pwm_A_IA, pwm_A_IB, pwm_B_IA, pwm_B_IB]:
       pwm.ChangeDutyCycle(0)












app = Flask(__name__)


# Initialize PiCam
picam2 = Picamera2()
picam2.configure(
   picam2.create_preview_configuration(
       main={"format": "BGR888", "size": (640, 480)}
   )
)
picam2.start()


frame = picam2.capture_array()
FRAME_WIDTH = frame.shape[1]
CENTER_X = FRAME_WIDTH // 2


def track_red_ball(frame):
   hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


   # Masks for detecting red color
   lower_red1 = np.array([0, 100, 100])
   upper_red1 = np.array([10, 255, 255])
   lower_red2 = np.array([160, 100, 100])
   upper_red2 = np.array([179, 255, 255])


   mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
   mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
   mask = cv2.bitwise_or(mask1, mask2)
   mask = cv2.erode(mask, None, iterations=2)
   mask = cv2.dilate(mask, None, iterations=2)


   contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


   if contours:
       largest = max(contours, key=cv2.contourArea)
       M = cv2.moments(largest)
       if M["m00"] > 0:
           cx = int(M["m10"] / M["m00"])
           cy = int(M["m01"] / M["m00"])
           offset = cx - CENTER_X


           if abs(offset) < 30:
               position = "Centered"
           elif offset < 0:
               position = "Left"
           else:
               position = "Right"


           cv2.drawContours(frame, [largest], -1, (0, 255, 0), 2)
           cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
           cv2.putText(
               frame,
               f"Offset: {offset} ({position})",
               (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX,
               0.7,
               (255, 255, 255),
               2,
           )


   return frame




def generate_frames():
   while True:
       frame = picam2.capture_array()
       frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
       frame = track_red_ball(frame)


       ret, buffer = cv2.imencode('.jpg', frame)
       jpg_frame = buffer.tobytes()


       yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n'
              b'Content-Length: ' + f"{len(jpg_frame)}".encode() + b'\r\n\r\n' +
              jpg_frame + b'\r\n')




@app.route('/')
def index():
   return render_template_string('''
       <html>
       <head><title>Red Ball Tracking Stream</title></head>
       <body>
           <h2>Live Tracking</h2>
           <img src="/video_feed">
       </body>
       </html>
   ''')




@app.route('/video_feed')
def video_feed():
   return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')




if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)
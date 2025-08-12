from flask import Flask, Response, render_template_string
from picamera2 import Picamera2
import cv2
import numpy as np

from flask import Flask, Response, render_template_string, redirect, url_for

import RPi.GPIO as GPIO
import time
import threading
frame_bgr = None

import atexit
atexit.register(GPIO.cleanup)


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

def backward_all(speed=70):
    for pwm in [pwm_A_IB, pwm_B_IB, pwm_C_IB, pwm_D_IB]:
        pwm.ChangeDutyCycle(speed)
    for pwm in [pwm_A_IA, pwm_B_IA, pwm_C_IA, pwm_D_IA]:
        pwm.ChangeDutyCycle(0)

def turn_left(speed=55):
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

def turn_right(speed=55):
    # Left side motors (A & C) go forward
    for pwm in [pwm_A_IA, pwm_C_IA]:
        pwm.ChangeDutyCycle(speed)
    for pwm in [pwm_A_IB, pwm_C_IB]:
        pwm.ChangeDutyCycle(0)

    # Right side motors (B & D) go backward
    for pwm in [pwm_B_IB, pwm_D_IB]:
        pwm.ChangeDutyCycle(50)
    for pwm in [pwm_B_IA, pwm_D_IA]:
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


#def track_red_ball(frame):
#   hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


#    # Masks for detecting red color
#    lower_red1 = np.array([0, 100, 100])
#    upper_red1 = np.array([10, 255, 255])
#    lower_red2 = np.array([160, 100, 100])
#    upper_red2 = np.array([179, 255, 255])


#    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
#    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
#    mask = cv2.bitwise_or(mask1, mask2)
#    mask = cv2.erode(mask, None, iterations=2)
#    mask = cv2.dilate(mask, None, iterations=2)


   #contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   


#    if contours:
#        largest = max(contours, key=cv2.contourArea)
#        M = cv2.moments(largest)
#        if M["m00"] > 0:
#            cx = int(M["m10"] / M["m00"])
#            cy = int(M["m01"] / M["m00"])
#            offset = cx - CENTER_X


#            if abs(offset) < 50:
#                position = "Centered"
#                #time.sleep(0.3)  # Small delay to avoid jitter
#                #forward_all()
#                print('go forward')
#            elif offset < 0:
#                position = "Left"
#                #time.sleep(0.3)  # Small delay to avoid jitter
#                print('turn left')
#               #turn_left(30)
#            elif offset > 50:
#                position = "Right"
#                #time.sleep(0.3)  # Small delay to avoid jitter
#                print('turn right')
#                #turn_right(30)
#            else:
#                 stop_all()


#            cv2.drawContours(frame, [largest], -1, (0, 255, 0), 2)
#            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
#            cv2.putText(
#                frame,
#                f"Offset: {offset} ({position})",
#                (10, 30),
#                cv2.FONT_HERSHEY_SIMPLEX,
#                0.7,
#                (255, 255, 255),
#                2,
#            )
#    else:
#       cv2.putText(
#     img=frame,
#     text="Where da red ball?",
#     org=(10, 60),
#     fontFace=cv2.FONT_HERSHEY_SIMPLEX,
#     fontScale=0.7,
#     color=(255, 255, 255),
#     thickness=2
#    )      
           


#return frame




def generate_frames():
    global frame_bgr
    while True:
        if frame_bgr is None:
            continue  # wait until a frame is captured
        # Convert to JPEG
        ret, buffer = cv2.imencode('.jpg', frame_bgr)
        jpg_frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n'
               b'Content-Length: ' + f"{len(jpg_frame)}".encode() + b'\r\n\r\n' +
               jpg_frame + b'\r\n')
        time.sleep(0.03)  # to control frame rate a bit

def capture_frames():
    global current_frame
    global frame_bgr

    while True:
        # Capture one frame from the camera here
        current_frame = picam2.capture_array() 
        frame_bgr = cv2.cvtColor(current_frame, cv2.COLOR_RGB2BGR)

        time.sleep(0.03)


@app.route('/')
def index():
   return render_template_string('''
       <html>
            <head>
            <title>Red Ball Tracking Stream</title>
            </head>
            <body>
            <h2>Live Tracking</h2>
            <img src="/video_feed" style="max-width: 100%; height: auto;"/>

            <div style="margin-top: 20px;">
                <button onclick="sendCommand('forward')">Forward</button>
                <button onclick="sendCommand('backward')">Backward</button>
                <button onclick="sendCommand('left')">Left</button>
                <button onclick="sendCommand('right')">Right</button>
                <button onclick="sendCommand('stop')">Stop</button>
            </div>

            <script>
                function sendCommand(command) {
                fetch('/' + command)
                    .then(response => response.text())
                    .then(data => {
                    console.log('Command sent:', data);
                    })
                    .catch(error => console.error('Error:', error));
                }
            </script>
            </body>
        </html>

   ''')
   


   
threading.Thread(target=capture_frames, daemon=True).start()

@app.route('/forward')
def forward():
    forward_all()
    return "OK"

@app.route('/backward')
def backward():
    backward_all()
    return "OK"

@app.route('/left')
def left():
    turn_left()
    return "OK"

@app.route('/right')
def right():
    turn_right()
    return "OK"

@app.route('/stop')
def stop():
    stop_all()
    return "OK"




@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')





if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        stop_all()
        GPIO.cleanup()


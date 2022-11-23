###############################################################################
### Simple demo on playing rock paper scissor
### Input : Live video of 2 hands playing rock paper scissor
### Output: 2D display of hand keypoint 
###         with gesture classification (rock=fist, paper=five, scissor=three/yeah)
###############################################################################

import cv2
import random
import time

from threading import Thread
from utils_display import DisplayHand
from utils_mediapipe import MediaPipeHand
from utils_joint_angle import GestureRecognition

start_game = 0
check_win = 0
result = "Nothing yet"
count_down = 4
start_count_down = False
rps_result = None
resultDisplay = None
nowGesture = None
winState = None
def rps():
    global count_down, start_count_down
    while count_down != 0:
        if count_down < 0:
            count_down = 0
        time.sleep(1)
        count_down -= 1
    

# Load mediapipe hand class
pipe = MediaPipeHand(static_image_mode=False, max_num_hands=1)

# Load display class
disp = DisplayHand(max_num_hands=2)

# Start video capture
cap = cv2.VideoCapture(0) # By default webcam is index 0

# Load gesture recognition class
gest = GestureRecognition(mode='eval')

while cap.isOpened():
    ret, img = cap.read()
    if not ret:
        break

    # Flip image for 3rd person view
    img = cv2.flip(img, 1)

    # To improve performance, optionally mark image as not writeable to pass by reference
    img.flags.writeable = False

    # Feedforward to extract keypoint
    param = pipe.forward(img)
    # Evaluate gesture for all hands

    for p in param:
        if p['class'] is not None:
            p['gesture'] = gest.eval(p['angle'])
            if p['gesture'] == "five":
                nowGesture = "paper"
            if p['gesture'] == "yeah":
                nowGesture = "scissor"
            if p['gesture'] == "fist":
                nowGesture = "rock"
            if p['gesture'] == 'ok': #five yeah fist
                if start_game == 0:
                    start_game = 1

    if start_game == 1:
        test = Thread(target=rps)
        test.start()
        check_win = 1
        start_count_down = True
        start_game = 2 
    if check_win == 1:
        
        if count_down != 0:
            cv2.putText(img, str(count_down), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        else:
            list1 = ["rock", "paper", "scissor"]
            rps_result = random.choice(list1)
        if rps_result in ["rock", "paper", "scissor"]:
            if rps_result == "rock":
                if nowGesture == "rock":
                    winState = "TIE"
                if nowGesture == "paper":
                    winState = "WIN"
                if nowGesture == "scissor":
                    winState = "LOSE"
            elif rps_result == "paper":
                if nowGesture == "rock":
                    winState = "LOSE"
                if nowGesture == "paper":
                    winState = "TIE"
                if nowGesture == "scissor":
                    winState = "WIN"
            else:
                if nowGesture == "rock":
                    winState = "WIN"
                if nowGesture == "paper":
                    winState = "LOSE"
                if nowGesture == "scissor":
                    winState = "TIE"
            resultDisplay = rps_result
            nowGesture = None
            rps_result = None
            count_down = 4
            start_count_down = False
            start_game = 0
            check_win = 0
    
    cv2.putText(img, (f"BOT:{resultDisplay}"), (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(img, (f"YOU {winState}"), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    print(f"LOGS: checkwin:{check_win} , start_game:{start_game}, count_down:{count_down}, start_count_down:{start_count_down}")
    img.flags.writeable = True

    # Display keypoint and result of rock paper scissor game
    cv2.imshow('Game: Rock Paper Scissor', disp.draw_game_rps(img.copy(), param))

    key = cv2.waitKey(1)
    if key==27:
        break

pipe.pipe.close()
cap.release()

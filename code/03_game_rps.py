###############################################################################
### Simple demo on playing rock paper scissor
### Input : Live video of 2 hands playing rock paper scissor
### Output: 2D display of hand keypoint 
###         with gesture classification (rock=fist, paper=five, scissor=three/yeah)
###############################################################################

import cv2
import random
import time
from playsound import playsound

from threading import Thread
from threading import active_count
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
rps_display = None
nowGesture = None
winState = None
x_offset=y_offset=0
soundeffectFlag = 1

def rps():
    global count_down, start_count_down
    while count_down != 0:
        if count_down < 0:
            count_down = 0
        time.sleep(1)
        count_down -= 1

def playMusic(music):
    playsound(music)

# Load mediapipe hand class
pipe = MediaPipeHand(static_image_mode=False, max_num_hands=1)

# Load display class
disp = DisplayHand(max_num_hands=2)

# Start video capture
cap = cv2.VideoCapture(0) # By default webcam is index 0

# Load gesture recognition class
gest = GestureRecognition(mode='eval')

rock_img = cv2.imread("./img/rock.png")
paper_img = cv2.imread("./img/paper.png")
scissor_img = cv2.imread("./img/scissor.png")

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
        rps_display = None
        start_game = 2 
    if check_win == 1:
        if count_down != 0:
            cv2.putText(img, str(count_down), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        else:
            list1 = ["rock", "paper", "scissor"]
            rps_result = random.choice(list1)
        if rps_result in ["rock", "paper", "scissor"]:

            if rps_result == "rock":
                rps_display = "rock"
                if nowGesture == "rock":
                    winState = "TIE"
                if nowGesture == "paper":
                    winState = "WIN"
                    if soundeffectFlag == 2:
                        soundeffect = Thread(target=playMusic, args={"./sound/win.mp3"})
                        soundeffect.start()
                        soundeffectFlag = 0 
                if nowGesture == "scissor":
                    winState = "LOSE"
                    if soundeffectFlag == 2:
                        soundeffect = Thread(target=playMusic, args={"./sound/lose.mp3"})
                        soundeffect.start()
                        soundeffectFlag = 0 

            elif rps_result == "paper":
                rps_display = "paper"
                if nowGesture == "rock":
                    winState = "LOSE"
                    if soundeffectFlag == 2:
                        soundeffect = Thread(target=playMusic, args={"./sound/lose.mp3"})
                        soundeffect.start()
                        soundeffectFlag = 0 
                if nowGesture == "paper":
                    winState = "TIE"
                if nowGesture == "scissor":
                    winState = "WIN"
                    if soundeffectFlag == 2:
                        soundeffect = Thread(target=playMusic, args={"./sound/win.mp3"})
                        soundeffect.start()
                        soundeffectFlag = 0 

            else:
                rps_display = "scissor"
                if nowGesture == "rock":
                    winState = "WIN"
                    if soundeffectFlag == 2:
                        soundeffect = Thread(target=playMusic, args={"./sound/win.mp3"})
                        soundeffect.start()
                        soundeffectFlag = 0 
                if nowGesture == "paper":
                    winState = "LOSE"
                    if soundeffectFlag == 2:
                        soundeffect = Thread(target=playMusic, args={"./sound/lose.mp3"})
                        soundeffect.start()
                        soundeffectFlag = 0 
                if nowGesture == "scissor":
                    winState = "TIE"
            resultDisplay = rps_result
            nowGesture = None
            rps_result = None
            count_down = 4
            start_count_down = False
            soundeffectFlag = 1
            start_game = 0
            check_win = 0

    
    # cv2.putText(img, (f"BOT:{resultDisplay}"), (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(img, (f"YOU {winState}"), (400, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    img.flags.writeable = True

    if count_down != 0 and check_win == 1:
        if soundeffectFlag == 1:
            soundeffect = Thread(target=playMusic, args={"./sound/random.mp3"})
            soundeffect.start()
            soundeffectFlag = 2 
        temp = random.randint(1, 3)
        if temp == 1: 
            img[y_offset:y_offset+rock_img.shape[0], x_offset:x_offset+rock_img.shape[1]] = rock_img
        if temp == 2:
            img[y_offset:y_offset+paper_img.shape[0], x_offset:x_offset+paper_img.shape[1]] = paper_img
        if temp == 3:
            img[y_offset:y_offset+scissor_img.shape[0], x_offset:x_offset+scissor_img.shape[1]] = scissor_img

    if rps_display == "rock":
        img[y_offset:y_offset+rock_img.shape[0], x_offset:x_offset+rock_img.shape[1]] = rock_img
    if rps_display == "paper":
        img[y_offset:y_offset+paper_img.shape[0], x_offset:x_offset+paper_img.shape[1]] = paper_img
    if rps_display == "scissor":
        img[y_offset:y_offset+scissor_img.shape[0], x_offset:x_offset+scissor_img.shape[1]] = scissor_img
    # Display keypoint and result of rock paper scissor game
    
    cv2.imshow('Game: Rock Paper Scissor', disp.draw_game_rps(img.copy(), param))

    print(f"LOGS: checkwin:{check_win} , start_game:{start_game}, count_down:{count_down}, start_count_down:{start_count_down}, soundEffectFlag:{soundeffectFlag}, thread_open:{active_count()}")

    key = cv2.waitKey(1)
    if key==27:
        break

pipe.pipe.close()
cap.release()

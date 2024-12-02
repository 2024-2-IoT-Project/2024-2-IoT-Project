import cv2
import mediapipe as mp
import numpy as np
import random
import time
from PIL import ImageFont, ImageDraw, Image, ImageTk
import tkinter as tk
from tkinter import Label
import os

# USB 카메라 초기화
os.environ["DISPLAY"] = ":0.0"

# MediaPipe Hands 모듈 초기화
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# 한글 텍스트를 이미지에 추가하는 함수
def put_text(image, text, position, font_size, color):
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)
    font_path = "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf"
    font = ImageFont.truetype(font_path, font_size)
    # font = ImageFont.truetype("malgun.ttf", font_size)
    draw.text(position, text, font=font, fill=color)
    return np.array(pil_image)

# 손 모양 분류 함수
def classify_hand_shape(hand_landmarks):
    landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
    
    def is_finger_open(tip_id, pip_id, wrist_id):
        tip_to_wrist = np.linalg.norm(np.array(landmarks[tip_id]) - np.array(landmarks[wrist_id]))
        pip_to_wrist = np.linalg.norm(np.array(landmarks[pip_id]) - np.array(landmarks[wrist_id]))
        return tip_to_wrist > pip_to_wrist

    thumb_open = is_finger_open(4, 3, 0)
    index_open = is_finger_open(8, 6, 0)
    middle_open = is_finger_open(12, 10, 0)
    ring_open = is_finger_open(16, 14, 0)
    pinky_open = is_finger_open(20, 18, 0)

    open_fingers = sum([thumb_open, index_open, middle_open, ring_open, pinky_open])

    if open_fingers == 2 or open_fingers == 3:
        return "가위"
    elif open_fingers == 0 or open_fingers == 1:
        return "바위"
    elif open_fingers == 5:
        return "보"
    else:
        return "준비"

# 승패 결정 함수
def determine_winner(player, computer):
    if player == computer:
        return "Draw"
    elif (player == "가위" and computer == "보") or \
         (player == "바위" and computer == "가위") or \
         (player == "보" and computer == "바위"):
        return "Win"
    else:
        return "Lose"

# Tkinter GUI 설정
root = tk.Tk()
root.title("가위바위보 게임")
lbl_video = Label(root)
lbl_video.pack()

# 게임 상태 변수
game_state = "준비"
countdown_start = 0
computer_choice = "준비"
result = ""
last_game_time = time.time()
COOLDOWN_TIME = 5

# MediaPipe Hands 객체 생성
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# 웹캠 초기화
cap = cv2.VideoCapture(0)

def update_frame():
    global game_state, countdown_start, computer_choice, result, last_game_time

    ret, frame = cap.read()
    if not ret:
        print("카메라를 읽을 수 없습니다.")
        return

    frame = cv2.flip(frame, 1)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    current_hand_shape = "준비"
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
            )
            current_hand_shape = classify_hand_shape(hand_landmarks)

    current_time = time.time()

    if game_state == "준비":
        if current_time - last_game_time >= COOLDOWN_TIME and current_hand_shape != "준비":
            game_state = "카운트다운"
            countdown_start = current_time
            computer_choice = random.choice(["가위", "바위", "보"])

    elif game_state == "카운트다운":
        time_elapsed = current_time - countdown_start
        countdown = 3 - int(time_elapsed)

        if countdown > 0:
            frame = put_text(frame, f'안 내면 진다, 가위 바위 보! {countdown}', (50, 50), 30, (255, 0, 0))
        else:
            game_state = "결과"
            result = determine_winner(current_hand_shape, computer_choice)
            last_game_time = current_time

    elif game_state == "결과":
        frame = put_text(frame, f"플레이어: {current_hand_shape}", (50, 50), 30, (255, 0, 0))
        frame = put_text(frame, f"컴퓨터: {computer_choice}", (50, 100), 30, (255, 0, 0))
        frame = put_text(frame, f"결과: {result}", (50, 150), 30, (255, 0, 0))

        if time.time() - last_game_time > 3:
            game_state = "준비"

    # Tkinter 이미지 업데이트
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img)
    lbl_video.imgtk = imgtk
    lbl_video.configure(image=imgtk)
    lbl_video.after(10, update_frame)

# Tkinter 메인 루프 실행
update_frame()
root.mainloop()

cap.release()
hands.close()
cv2.destroyAllWindows()

import cv2
import mediapipe as mp
import numpy as np
import random
import time
from PIL import ImageFont, ImageDraw, Image

# MediaPipe Hands 모듈 초기화
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# 게임 상태 변수
game_state = "준비"
countdown_start = 0
computer_choice = "준비"
result = ""
last_game_time = 0
COOLDOWN_TIME = 5

# 한글 텍스트를 이미지에 추가하는 함수
def put_text(image, text, position, font_size, color):
    # Pillow 이미지로 변환
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)
    
    # 폰트 설정 (맑은 고딕 또는 다른 한글 지원 폰트 경로로 변경하세요)
    font = ImageFont.truetype("malgun.ttf", font_size)
    
    # 텍스트 추가
    draw.text(position, text, font=font, fill=color)
    
    # NumPy 배열로 다시 변환
    return np.array(pil_image)

def classify_hand_shape(hand_landmarks):
    landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
    
    def is_finger_open(tip_id, pip_id, mcp_id, wrist_id):
        # 손목에서 손가락 끝까지의 거리 계산
        tip_to_wrist = np.linalg.norm(np.array(landmarks[tip_id]) - np.array(landmarks[wrist_id]))
        # 손목에서 손가락 중간 관절까지의 거리 계산
        pip_to_wrist = np.linalg.norm(np.array(landmarks[pip_id]) - np.array(landmarks[wrist_id]))
        return tip_to_wrist > pip_to_wrist  # 끝 관절이 중간 관절보다 멀리 있는지 확인

    # 각 손가락의 펴짐 여부를 계산
    thumb_open = is_finger_open(4, 3, 2, 0)    # 엄지
    index_open = is_finger_open(8, 6, 5, 0)    # 검지
    middle_open = is_finger_open(12, 10, 9, 0) # 중지
    ring_open = is_finger_open(16, 14, 13, 0)  # 약지
    pinky_open = is_finger_open(20, 18, 17, 0) # 새끼손가락

    # 펴진 손가락의 개수를 계산
    open_fingers = sum([thumb_open, index_open, middle_open, ring_open, pinky_open])
    print(open_fingers)
    print('엄지 ' + str(thumb_open))
    print('검지 ' + str(index_open))
    print('중지 ' + str(middle_open))
    print('약지 ' + str(ring_open))
    print('소지 ' + str(pinky_open))

    # 펴진 손가락의 개수에 따라 결과 반환
    if open_fingers == 2 or open_fingers == 3:
        return "가위"
    elif open_fingers == 0:
        return "바위"
    elif open_fingers == 5:
        return "보"
    else:
        return "준비"
    
def determine_winner(player, computer):
    if player == computer:
        return "Draw"
    elif (player == "가위" and computer == "보") or \
         (player == "바위" and computer == "가위") or \
         (player == "보" and computer == "바위"):
        return "Win"
    else:
        return "Lose"

def make_hands():
    hand = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5)

# def get_largest_hand(hands):


def rsp_game(cap):
    
    hand = make_hands()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("카메라에서 프레임을 가져올 수 없습니다.")
            break

        # BGR 이미지를 RGB로 변환
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hand.process(image)

        current_hand_shape = "준비"
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                current_hand_shape = classify_hand_shape(hand_landmarks)

        current_time = time.time()

        if game_state == "준비":
            if current_time - last_game_time >= COOLDOWN_TIME and \
            current_hand_shape != "준비":
                game_state = "카운트다운"
                countdown_start = current_time
                computer_choice = random.choice(["가위", "바위", "보"])
            
        elif game_state == "카운트다운":
            time_elapsed = current_time - countdown_start
            countdown = 3 - int(time_elapsed)

            if countdown > 0:
                image = put_text(image, '안 내면 진다, 가위 바위 보!' + str(countdown), (10, 50), 50, (255, 0, 0))
            elif countdown <= 0:
                game_state = "결과"
                result = determine_winner(current_hand_shape, computer_choice)
                last_game_time = current_time

        elif game_state == "결과":
            # 결과 표시
            image = put_text(image, f"플레이어: {current_hand_shape}, 컴퓨터: {computer_choice}", (10, 10), 20, (0, 0, 0))
            image = put_text(image, f"결과: {result}!!", (10, 40), 20, (0, 0, 0))
            
            # 결과 화면 유지
            cv2.imshow('Rock Scissors Paper', image)
            cv2.waitKey(1)  # 한 프레임을 출력하기 위해 짧게 대기
            time.sleep(3)  # 3초 대기

            if result == "draw":
                game_state = "준비"
            else:
                return result
        
        if game_state == "준비":
            image = put_text(image, "가위바위보 준비!", (10, 30), 30, (255, 0, 0))

        cv2.imshow('Rock Scissors Paper', image)

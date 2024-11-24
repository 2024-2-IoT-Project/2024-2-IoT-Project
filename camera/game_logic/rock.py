import cv2
import mediapipe as mp
import numpy as np

# MediaPipe Hands 모듈 초기화
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# 랜드마크를 기반으로 가위바위보 판단
def classify_hand_shape(hand_landmarks):
    # 랜드마크 배열
    landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]

    # 손가락 끝과 시작의 y좌표를 비교하여 각 손가락의 상태를 확인
    thumb_open = landmarks[4][0] > landmarks[3][0]  # 엄지
    index_open = landmarks[8][1] < landmarks[6][1]  # 검지
    middle_open = landmarks[12][1] < landmarks[10][1]  # 중지
    ring_open = landmarks[16][1] < landmarks[14][1]  # 약지
    pinky_open = landmarks[20][1] < landmarks[18][1]  # 새끼

    # 가위: 검지와 중지만 펴짐
    if index_open and middle_open and not ring_open and not pinky_open:
        return "가위"
    # 바위: 모든 손가락이 접힘
    elif not index_open and not middle_open and not ring_open and not pinky_open:
        return "바위"
    # 보: 모든 손가락이 펴짐
    elif index_open and middle_open and ring_open and pinky_open:
        return "보"
    else:
        return "알 수 없음"

# 웹캠 입력 캡처
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

# Hands 솔루션 사용
with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,  # 한 손만 처리
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("카메라를 읽을 수 없습니다.")
            break

        # 프레임 색상 변환 (OpenCV는 BGR, MediaPipe는 RGB 사용)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # MediaPipe Hands에 이미지 입력
        results = hands.process(image)

        # 다시 BGR로 변환 (시각화를 위해)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # 손 랜드마크 시각화 및 가위바위보 결과 표시
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 랜드마크를 그리기
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # 손 모양 판별
                hand_shape = classify_hand_shape(hand_landmarks)
                cv2.putText(image, f"Hand Shape: {hand_shape}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # 화면에 출력
        cv2.imshow('MediaPipe Hands - 가위바위보', image)

        # ESC 키로 종료
        if cv2.waitKey(5) & 0xFF == 27:
            break

# 자원 해제
cap.release()
cv2.destroyAllWindows()

# import cv2
# import mediapipe as mp
# import numpy as np
# import time
# import random

# def make_face_mesh():
#     # MediaPipe FaceMesh 초기화
#     mp_face_mesh = mp.solutions.face_mesh

#     # FaceMesh 객체 생성
#     face_mesh = mp_face_mesh.FaceMesh(
#         max_num_faces=5,  # 최대 얼굴 수
#         refine_landmarks=True,
#         min_detection_confidence=0.5,
#         min_tracking_confidence=0.5
#     )
#     return face_mesh

# def cham_game(cap):

#     face_mesh = make_face_mesh()

#     now = time.time()
#     direction = None
#     result = None

#     while cap.isOpened() and time.time() - now < 5:
#         ret, frame = cap.read()
#         if not ret:
#             print("카메라에서 프레임을 가져올 수 없습니다.")
#             break

#         # BGR 이미지를 RGB로 변환
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         # FaceMesh 처리
#         results = face_mesh.process(rgb_frame)

#         if results.multi_face_landmarks:
#             largest_face_index = -1
#             largest_face_size = -1

#             for i, face_landmarks in enumerate(results.multi_face_landmarks):
#                 # 랜드마크 가져오기
#                 landmarks = face_landmarks.landmark

#                 # 얼굴 크기 계산: 양쪽 눈의 가로 거리
#                 left_eye = np.array([landmarks[33].x, landmarks[33].y])
#                 right_eye = np.array([landmarks[263].x, landmarks[263].y])
#                 face_width = np.linalg.norm(left_eye - right_eye)  # 두 눈 사이 거리 계산

#                 # 가장 큰 얼굴 선택
#                 if face_width > largest_face_size:
#                     largest_face_size = face_width
#                     largest_face_index = i

#             # 가장 큰 얼굴의 방향 계산
#             if largest_face_index != -1:
#                 face_landmarks = results.multi_face_landmarks[largest_face_index]
#                 landmarks = face_landmarks.landmark

#                 # 주요 랜드마크 좌표 추출 (코 끝, 양쪽 눈, 이마 중심)
#                 nose_tip = np.array([landmarks[1].x, landmarks[1].y, landmarks[1].z])
#                 left_eye = np.array([landmarks[33].x, landmarks[33].y, landmarks[33].z])
#                 right_eye = np.array([landmarks[263].x, landmarks[263].y, landmarks[263].z])
#                 forehead = np.array([landmarks[10].x, landmarks[10].y, landmarks[10].z])  # 이마 중심

#                 # 얼굴 중심(코 끝과 이마 중심의 중간점)
#                 face_center = (nose_tip + forehead) / 2

#                 # 좌우 회전 (Yaw): 얼굴 중심의 x 좌표와 왼쪽/오른쪽 눈의 중심 비교
#                 eye_center = (left_eye + right_eye) / 2
#                 yaw = (face_center[0] - eye_center[0]) * 100  # 스케일링 팩터로 변화값 확대

#                 # 방향 결정
#                 direction = "Center"
#                 if yaw > 2.5:
#                     direction = "Left"
#                 elif yaw < -2.5:
#                     direction = "Right"

#                 computer_choice = random.choice(["Left", "Right"])
#                 if direction != computer_choice:
#                     result = True
#                 else:
#                     result = False

#     return result
import cv2
import mediapipe as mp
import numpy as np
import time
import random
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk

def make_face_mesh():
    # MediaPipe FaceMesh 초기화
    mp_face_mesh = mp.solutions.face_mesh

    # FaceMesh 객체 생성
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=5,  # 최대 얼굴 수
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    return face_mesh

def cham_game(cap):
    face_mesh = make_face_mesh()

    # Tkinter 초기화
    root = tk.Tk()
    root.title("ChamChamCham Game")

    # Tkinter 라벨 생성 (LCD에 영상 출력)
    lbl_video = Label(root)
    lbl_video.pack()

    now = time.time()
    direction = None
    result = None

    def update_frame():
        nonlocal direction, result  # 외부 변수를 수정하기 위해 nonlocal 선언

        if not cap.isOpened():
            print("카메라를 열 수 없습니다.")
            cap.release()
            root.destroy()
            return

        ret, frame = cap.read()
        if not ret:
            print("카메라에서 프레임을 가져올 수 없습니다.")
            cap.release()
            root.destroy()
            return

        # BGR 이미지를 RGB로 변환
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # FaceMesh 처리
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            largest_face_index = -1
            largest_face_size = -1

            for i, face_landmarks in enumerate(results.multi_face_landmarks):
                # 랜드마크 가져오기
                landmarks = face_landmarks.landmark

                # 얼굴 크기 계산: 양쪽 눈의 가로 거리
                left_eye = np.array([landmarks[33].x, landmarks[33].y])
                right_eye = np.array([landmarks[263].x, landmarks[263].y])
                face_width = np.linalg.norm(left_eye - right_eye)  # 두 눈 사이 거리 계산

                # 가장 큰 얼굴 선택
                if face_width > largest_face_size:
                    largest_face_size = face_width
                    largest_face_index = i

            # 가장 큰 얼굴의 방향 계산
            if largest_face_index != -1:
                face_landmarks = results.multi_face_landmarks[largest_face_index]
                landmarks = face_landmarks.landmark

                # 주요 랜드마크 좌표 추출 (코 끝, 양쪽 눈, 이마 중심)
                nose_tip = np.array([landmarks[1].x, landmarks[1].y, landmarks[1].z])
                left_eye = np.array([landmarks[33].x, landmarks[33].y, landmarks[33].z])
                right_eye = np.array([landmarks[263].x, landmarks[263].y, landmarks[263].z])
                forehead = np.array([landmarks[10].x, landmarks[10].y, landmarks[10].z])  # 이마 중심

                # 얼굴 중심(코 끝과 이마 중심의 중간점)
                face_center = (nose_tip + forehead) / 2

                # 좌우 회전 (Yaw): 얼굴 중심의 x 좌표와 왼쪽/오른쪽 눈의 중심 비교
                eye_center = (left_eye + right_eye) / 2
                yaw = (face_center[0] - eye_center[0]) * 100  # 스케일링 팩터로 변화값 확대

                # 방향 결정
                direction = "Center"
                if yaw > 2.5:
                    direction = "Left"
                elif yaw < -2.5:
                    direction = "Right"

                computer_choice = random.choice(["Left", "Right"])
                if direction != computer_choice:
                    result = True
                else:
                    result = False

        # Tkinter에 실시간 영상 출력
        img = Image.fromarray(rgb_frame)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)

        # 게임 종료 조건
        if time.time() - now >= 5:
            cap.release()
            root.destroy()
            return

        lbl_video.after(30, update_frame)

    # 프레임 업데이트 시작
    update_frame()

    # Tkinter 메인 루프 실행
    root.mainloop()

    return result

import cv2
import mediapipe as mp
import numpy as np

# MediaPipe FaceMesh 초기화
mp_face_mesh = mp.solutions.face_mesh
        
# 카메라 초기화
# 0: 노트북 내장 카메라
# 1: usb 연결한 카메라
# 라즈베리파이의 경우 수정 필요
cap = cv2.VideoCapture(1)

# FaceMesh 객체 생성
with mp_face_mesh.FaceMesh(
    max_num_faces=5,  # 최대 얼굴 수
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("카메라에서 프레임을 가져올 수 없습니다.")
            break

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

                # 위아래 회전 (Pitch): 코 끝과 이마 중심의 y 좌표 비교
                pitch = (face_center[1] - forehead[1]) * 100  # 스케일링 팩터로 변화값 확대

                # 방향 결정
                direction = "Center"
                if yaw > 5:
                    direction = "Right"
                elif yaw < -5:
                    direction = "Left"

                if pitch > 5:
                    direction += " Down"
                elif pitch < -5:
                    direction += " Up"

                # 얼굴 방향 시각화
                text = f"Yaw: {yaw:.2f}, Pitch: {pitch:.2f} ({direction})"
                cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                # 랜드마크 시각화
                for face_landmark in face_landmarks.landmark:
                    x = int(face_landmark.x * frame.shape[1])
                    y = int(face_landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        # 결과 출력
        cv2.imshow('Largest Face Direction', frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# 자원 해제
cap.release()
cv2.destroyAllWindows()

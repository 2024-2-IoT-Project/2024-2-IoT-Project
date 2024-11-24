import cv2
from pyzbar.pyzbar import decode
import numpy as np

# 사용자를 구분할 예시 데이터
user_data = {
    "player1": "1",
    "player2": "2",
    "player3": "3"
}

def recognize_qr_code(cap):

    while True:
        # 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다. 종료합니다.")
            break
        
        # QR 코드 디코딩
        qr_codes = decode(frame)
        for qr_code in qr_codes:
            # QR 코드 데이터 읽기
            qr_data = qr_code.data.decode('utf-8').strip()

            # 사용자 구분
            user_name = user_data.get(qr_data.split(':')[0], "알 수 없는 사용자")
            print(f"사용자: {user_name}")

            # 사용자 정보 반환
            return user_name

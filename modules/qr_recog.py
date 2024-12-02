# import cv2
# from pyzbar.pyzbar import decode
# import numpy as np

# # 사용자를 구분할 예시 데이터
# user_data = {
#     "player1": "1",
#     "player2": "2",
#     "player3": "3",
#     "player4": "4"
# }

# def recognize_qr_code(cap):

#     while True:
#         # 프레임 읽기
#         ret, frame = cap.read()
#         if not ret:
#             print("프레임을 읽을 수 없습니다. 종료합니다.")
#             break
        
#         # QR 코드 디코딩
#         qr_codes = decode(frame)
#         for qr_code in qr_codes:
#             # QR 코드 데이터 읽기
#             qr_data = qr_code.data.decode('utf-8').strip()

#             # 사용자 구분
#             user_name = user_data.get(qr_data.split(':')[0], "알 수 없는 사용자")
#             print(f"사용자: {user_name}")

#             # 사용자 정보 반환
#             return user_name

import cv2
from pyzbar.pyzbar import decode
import numpy as np
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk

# 사용자를 구분할 예시 데이터
user_data = {
    "player1": "1",
    "player2": "2",
    "player3": "3",
    "player4": "4"
}

def recognize_qr_code(cap):
    # Tkinter 초기화
    root = tk.Tk()
    root.title("QR 코드 인식기")

    # Tkinter 라벨 생성
    lbl_video = Label(root)
    lbl_video.pack()

    lbl_result = Label(root, text="QR 코드 결과: 없음", font=("Arial", 16))
    lbl_result.pack()

    def update_frame():
        ret, frame = cap.read()
        if not ret:
            print("카메라를 읽을 수 없습니다.")
            cap.release()
            root.destroy()
            return

        # QR 코드 디코딩
        qr_codes = decode(frame)
        for qr_code in qr_codes:
            qr_data = qr_code.data.decode('utf-8').strip()
            user_name = user_data.get(qr_data.split(':')[0], "알 수 없는 사용자")
            print(f"사용자: {user_name}")

            # "알 수 있는 사용자"일 경우 프로그램 종료
            if user_name != "알 수 없는 사용자":
                return user_name

        # Tkinter에 실시간으로 웹캠 영상 업데이트
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)

        lbl_video.after(30, update_frame)

    # 업데이트 함수 실행
    update_frame()

    # Tkinter 메인 루프 실행
    root.mainloop()

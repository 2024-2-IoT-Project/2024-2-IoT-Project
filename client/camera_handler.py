import cv2
from qr_decoder import decode_qr

def start_camera():
    # 카메라 초기화
    cap = cv2.VideoCapture(0)  # 0번 카메라 사용 (내장 카메라)

    if not cap.isOpened():
        print("[ERROR] 카메라를 열 수 없습니다!")
        exit()

    print("[INFO] 카메라 시작...")

    try:
        while True:
            # 카메라에서 프레임 읽기
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] 프레임을 읽을 수 없습니다!")
                break

            # QR 코드 감지
            user_id = decode_qr(frame)
            if user_id:
                print(f"[INFO] QR 코드 인식 성공: {user_id}")
                yield user_id  # 인식된 QR 코드를 반환

            # 실시간 카메라 화면 출력
            cv2.imshow("Live Camera Feed", frame)

            # 'q' 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # 카메라 리소스 해제 및 창 닫기
        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] 카메라 종료")


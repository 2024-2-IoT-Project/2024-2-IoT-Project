import cv2
from pyzbar.pyzbar import decode
import numpy as np

# 사용자를 구분할 예시 데이터
user_data = {
    "player1": "P1",
    "player2": "P2",
    "player3": "P3"
}

# 결과를 저장할 파일 경로
output_file = "qr_code_results.txt"

def save_result_to_file(user_name):
    """QR 코드 데이터를 파일에 저장"""
    try:
        with open(output_file, "w") as file:
            file.write(f"{user_name}\n")
        print(f"결과를 {output_file}에 저장했습니다.")
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {e}")

def recognize_qr_code():
    # 카메라 초기화 (카메라 번호는 기본값 0)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    print("QR 코드 스캐너가 시작되었습니다. 'q'를 눌러 종료하세요.")
    
    pause_recognition = False  # QR 코드 인식 멈춤 상태 플래그
    recognized_qrs = set()  # 중복 저장 방지를 위한 집합

    while True:
        # QR 코드 인식이 멈춘 상태라면 엔터 키 입력 대기
        if pause_recognition:
            print("엔터 키를 누르면 다시 QR 코드 인식을 시작합니다.")
            input()  # 엔터 입력 대기
            pause_recognition = False
            print("QR 코드 인식을 재개합니다.")

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
            print(f"QR 코드 인식됨: {qr_data}")

            # 사용자 구분
            user_name = user_data.get(qr_data.split(':')[0], "알 수 없는 사용자")
            print(f"사용자: {user_name}")

            save_result_to_file(user_name)

            # QR 코드 위치에 사각형 그리기
            points = qr_code.polygon
            if len(points) == 4:
                pts = [(point.x, point.y) for point in points]
                cv2.polylines(frame, [np.array(pts)], isClosed=True, color=(0, 255, 0), thickness=3)

            # 사용자 이름 화면에 표시
            rect = qr_code.rect
            cv2.putText(frame, user_name, (rect.left, rect.top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # QR 코드가 인식되었으므로, 인식을 멈추고 엔터 키 입력 대기
            pause_recognition = True
            break

        # 결과 화면 출력
        cv2.imshow("QR Code Scanner", frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("QR 코드 스캐너를 종료합니다.")
            break

    # 카메라와 창 닫기
    cap.release()
    cv2.destroyAllWindows()

# QR 코드 인식 함수 실행
recognize_qr_code()

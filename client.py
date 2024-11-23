import socket
import threading
from camera_handler import start_camera

SERVER_HOST = '59.187.203.169'  # 라즈베리파이 공인 IP (공유기 IP)
SERVER_PORT = 1234              # 서버 포트 번호

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_qr_data():
    """QR 코드를 읽고 서버로 전송"""
    last_user_id = None  # 마지막으로 인식한 QR 코드 저장

    try:
        for user_id in start_camera():
            if user_id == last_user_id:
                print(f"[INFO] 이미 처리된 QR 코드: {user_id}")
                continue  # 동일한 QR 코드는 무시

            # QR 코드 인식 시 서버로 CREATE 명령어 생성
            command = f"{user_id}"
            print(f"[INFO] 생성된 명령어: {command}")

            # 명령어 서버로 전송
            client.send(command.encode())

            # 서버 응답 확인
            response = client.recv(1024).decode()
            print(f"[INFO] 서버 응답: {response}")

            # 마지막 처리된 QR 코드 업데이트
            last_user_id = user_id

    except Exception as e:
        print(f"[ERROR] QR 전송 중 에러 발생: {e}")

    """QR 코드를 읽고 서버로 전송"""
    try:
        for user_id in start_camera():
            # QR 코드 인식 시 서버로 CREATE 명령어 생성
            command = f"{user_id}"
            print(f"[INFO] 생성된 명령어: {command}")

            # 명령어 서버로 전송
            client.send(command.encode())

            # 서버 응답 확인
            response = client.recv(1024).decode()
            print(f"[INFO] 서버 응답: {response}")
    except Exception as e:
        print(f"[ERROR] QR 전송 중 에러 발생: {e}")


def handle_user_input():
    """사용자 입력 처리"""
    try:
        while True:
            command = input("[DEBUG] 명령어 입력 (종료: exit): ").strip()
            if command.lower() == "exit":
                print("[INFO] 클라이언트 종료 요청")
                client.send("DISCONNECT".encode())
                break

            # 명령어 서버로 전송
            client.send(command.encode())

            # 서버 응답 확인
            response = client.recv(1024).decode()
            print(f"[INFO] 서버 응답: {response}")
    except Exception as e:
        print(f"[ERROR] 사용자 입력 처리 중 에러 발생: {e}")


### main ###
try:
    print(f"[DEBUG] 서버에 연결 시도: {SERVER_HOST}:{SERVER_PORT}")
    client.connect((SERVER_HOST, SERVER_PORT))
    print("[INFO] 서버 연결 성공")

    # 멀티스레딩: QR 데이터 전송과 사용자 입력 병렬 처리
    # qr_thread = threading.Thread(target=send_qr_data, daemon=True)
    # qr_thread.start()

    send_qr_data()  # QR 데이터 전송 (메인 스레드에서 실행)
    # handle_user_input()  # 사용자 입력 처리 (메인 스레드에서 실행)

except Exception as e:
    print(f"[ERROR] 클라이언트 에러 발생: {e}")
finally:
    client.close()
    print("[INFO] 클라이언트 연결 종료")

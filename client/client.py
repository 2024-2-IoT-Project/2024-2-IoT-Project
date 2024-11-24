import socket
from camera_handler import start_camera

SERVER_HOST = '59.187.203.169'  # 라즈베리파이 공인 IP (공유기 IP)
SERVER_PORT = 1234              # 서버 포트 번호

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def receive_user_count():
    """서버로부터 생성할 유저 수를 수신"""
    try:
        user_count_message = client.recv(1024).decode().strip()
        print(f"[SERVER] {user_count_message}")
        if user_count_message.startswith("SETUP:"):
            _, user_count = user_count_message.split(":")
            return int(user_count.strip())
        else:
            raise ValueError("[ERROR] 서버로부터 유저 수를 받을 수 없습니다.")
    except Exception as e:
        print(f"[ERROR] 유저 수 수신 중 에러 발생: {e}")
        return 0


def send_qr_data(expected_user_count):
    """QR 코드를 읽고 서버로 전송"""
    last_user_id = None  # 마지막으로 인식한 QR 코드 저장
    registered_users = 0

    try:
        for user_id in start_camera():
            if user_id == last_user_id:
                print(f"[INFO] 이미 처리된 QR 코드: {user_id}")
                continue  # 동일한 QR 코드는 무시

            # QR 코드 인식 시 서버로 전송
            print(f"[INFO] QR 코드 전송: {user_id}")
            client.send(user_id.encode())

            # 서버 응답 확인
            response = client.recv(1024).decode().strip()
            print(f"[SERVER] {response}")

            # 성공적으로 등록된 경우 등록된 유저 수 증가
            if "created" in response:
                registered_users += 1
                last_user_id = user_id

            # 모든 유저가 등록되었으면 종료
            if registered_users >= expected_user_count:
                print("[INFO] 모든 유저가 등록되었습니다.")
                break

    except Exception as e:
        print(f"[ERROR] QR 전송 중 에러 발생: {e}")


def handle_server_messages():
    """서버로부터 오는 메시지를 수신하여 출력"""
    try:
        while True:
            message = client.recv(1024).decode().strip()  # 서버로부터 메시지 수신
            if not message:
                break  # 서버가 연결을 닫으면 루프 종료
            print(f"[SERVER] {message}")  # 수신한 메시지 출력
    except Exception as e:
        print(f"[ERROR] 서버 메시지 수신 중 에러 발생: {e}")


### main ###
try:
    print(f"[DEBUG] 서버에 연결 시도: {SERVER_HOST}:{SERVER_PORT}")
    client.connect((SERVER_HOST, SERVER_PORT))
    print("[INFO] 서버 연결 성공")

    # 서버로부터 생성할 유저 수를 받음
    expected_user_count = receive_user_count()
    if expected_user_count <= 0:
        print("[ERROR] 유저 수가 유효하지 않습니다. 클라이언트를 종료합니다.")
        client.close()
        exit()

    # 카메라를 열어 QR 코드로 유저 등록
    send_qr_data(expected_user_count)

    # 서버 메시지 수신
    handle_server_messages()

except Exception as e:
    print(f"[ERROR] 클라이언트 에러 발생: {e}")
finally:
    client.close()
    print("[INFO] 클라이언트 연결 종료")

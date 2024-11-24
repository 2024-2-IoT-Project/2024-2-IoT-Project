import socket
from camera_handler import start_camera

SERVER_HOST = '59.187.203.169'  # 라즈베리파이 공인 IP (공유기 IP)
SERVER_PORT = 1234              # 서버 포트 번호

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def process_qr_data(expected_user_count):
    """
    카메라를 열어서 QR 등록과 게임 진행을 처리.
    QR 등록 중에는 유저 생성 요청을 서버로 전송,
    게임 시작 후에는 HP 회복 요청을 전송.
    """
    try:
        print("[INFO] 카메라를 시작합니다.")
        registered_users = 0
        registered_user_ids = set()  # 등록된 유저 ID 저장
        game_started = False

        for user_id in start_camera():
            if not game_started:
                # QR 등록 단계
                if user_id in registered_user_ids:
                    print(f"[INFO] 이미 등록된 QR 코드: {user_id}")
                    continue  # 동일한 QR 코드는 무시

                print(f"[INFO] QR 코드 전송 (등록): {user_id}")
                client.send(user_id.encode())

                # 서버 응답 확인
                response = client.recv(1024).decode().strip()
                print(f"[SERVER] {response}")

                if "created" in response:
                    registered_users += 1
                    registered_user_ids.add(user_id)

                # 모든 유저가 등록되었으면 게임 시작 대기
                if registered_users >= expected_user_count:
                    print("[INFO] 모든 유저가 등록되었습니다. 게임을 시작합니다.")
                    game_started = True
            else:
                # 게임 진행 단계: HP 회복
                print(f"[INFO] QR 코드 전송 (HP 회복): {user_id}")
                client.send(f"PLAYER_HEAL:{user_id}".encode())

                # 서버 응답 확인
                response = client.recv(1024).decode().strip()
                print(f"[SERVER] {response}")

    except Exception as e:
        print(f"[ERROR] QR 처리 중 에러 발생: {e}")


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

    # QR 데이터를 처리하여 유저 등록 및 게임 진행
    process_qr_data(expected_user_count)

except Exception as e:
    print(f"[ERROR] 클라이언트 에러 발생: {e}")
finally:
    client.close()
    print("[INFO] 클라이언트 연결 종료")

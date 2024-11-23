import socket
from user import User  # user.py에서 User 클래스를 가져옴

# 서버 설정
HOST = '0.0.0.0'  # 모든 네트워크 인터페이스에서 요청 수신
PORT = 1234        # 포트 번호

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 포트 재사용 설정
server.bind((HOST, PORT))
server.listen(1)
print(f"[INFO] 서버가 {HOST}:{PORT} 에서 실행 중...")

client_socket, client_address = server.accept()
print(f"[INFO] 클라이언트 연결됨: {client_address}")

# 사용자 관리 (userID를 키로 저장)
users = {}
processed_users = set()  # 이미 작업이 처리된 유저ID 저장

try:
    # 초기 유저 수 설정
    max_users = int(input("[SETUP] 생성할 유저 수를 입력하세요: "))
    print(f"[INFO] 설정된 유저 수: {max_users}")

    # 유저 생성 단계
    while len(users) < max_users:
        # 클라이언트로부터 데이터 수신
        data = client_socket.recv(1024).decode().strip()
        if not data:
            break

        print(f"[INFO] 클라이언트 메시지: {data}")
        
        user_id = data  # 클라이언트가 보내는 데이터는 항상 user_id

        # 유저 생성 처리
        if user_id in users:
            print(f"[INFO] {user_id} 이미 생성됨.")
            client_socket.send(f"ERROR: {user_id} already exists".encode())
        else:
            users[user_id] = User(user_id)
            users[user_id].hp = 0  # 초기 HP를 0으로 설정
            print(f"[INFO] {user_id} 사용자 생성 완료: {users[user_id]}")
            client_socket.send(f"User {user_id} created".encode())
            print(f"[INFO] 현재 생성된 유저 수: {len(users)}/{max_users}")

    # 모든 유저가 생성된 후 게임 시작
    print("[INFO] 모든 유저가 생성되었습니다!")
    print("[GAME] Game Start!")
    client_socket.send("Game Start".encode())

    # 게임 진행 단계: 명령어 처리 루프
    while True:
        # 클라이언트로부터 데이터 수신
        data = client_socket.recv(1024).decode().strip()
        if not data:
            break

        print(f"[INFO] 클라이언트 메시지: {data}")
        
        user_id = data  # 클라이언트가 보내는 데이터는 항상 user_id

        # 유저 존재 여부 확인
        if user_id in users:
            if user_id in processed_users:
                # 이미 작업이 처리된 경우
                print(f"[INFO] {user_id} 작업 이미 처리됨.")
                client_socket.send(f"ERROR: {user_id} already processed".encode())
            else:
                # 작업 처리: HP를 1로 설정
                users[user_id].hp = 1
                processed_users.add(user_id)  # 처리된 유저ID 저장
                print(f"[INFO] {user_id}의 HP가 1로 설정됨.")
                client_socket.send(f"{user_id} HP set to 1".encode())
        else:
            # 유저가 없는 경우 오류 반환
            print(f"[ERROR] {user_id}는 존재하지 않음.")
            client_socket.send(f"ERROR: {user_id} does not exist".encode())

finally:
    client_socket.close()
    server.close()
    print("[INFO] 서버 종료")

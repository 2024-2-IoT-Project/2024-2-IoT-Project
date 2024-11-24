import socket
import random
import time
import threading
from typing import List, Dict
from user import User  # user.py에서 User 클래스를 가져옴

# 서버 설정
HOST = '0.0.0.0'  # 모든 네트워크 인터페이스에서 요청 수신
PORT = 1234        # 포트 번호
MAX_CLIENTS = 1    # 최대 클라이언트 수 (미션 개수, 테스트 시 1)
BUFFER_SIZE = 1024  # 소켓 수신 버퍼 크기
CHECK_INTERVAL = 1  # 클라이언트 접속 확인 간격


class GameServer:
    def __init__(self, host=HOST, port=PORT):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(MAX_CLIENTS)

        self.clients: List[socket.socket] = []  # 접속한 클라이언트 소켓
        self.users: Dict[str, User] = {}  # 사용자 관리 (userID: User 객체)
        self.expected_user_count = 0  # 입력받은 유저 수
        self.is_game_running = threading.Event()  # 게임 상태를 관리하는 Event

    def accept_clients(self):
        """클라이언트 접속 대기"""
        print("[INFO] 클라이언트 접속 대기 중...")
        while len(self.clients) < MAX_CLIENTS:
            client_socket, addr = self.server_socket.accept()
            print(f"[INFO] 새로운 클라이언트 접속: {addr}")
            self.clients.append(client_socket)

        print(f"[INFO] {MAX_CLIENTS}개의 클라이언트가 접속했습니다.")
        print("[INFO] 이제 유저 등록 단계로 진행합니다...")

    def register_users(self):
        """유저 수 입력 및 QR 코드로 유저 등록"""
        # 유저 수 입력
        while True:
            try:
                self.expected_user_count = int(input("[SETUP] 생성할 유저 수를 입력하세요: "))
                if self.expected_user_count > 0:
                    break
                else:
                    print("[ERROR] 유저 수는 1 이상이어야 합니다.")
            except ValueError:
                print("[ERROR] 숫자를 입력하세요.")

        print(f"[INFO] 설정된 유저 수: {self.expected_user_count}")
        print("[INFO] QR 코드로 유저를 등록해주세요.")

        # 유저 수를 모든 클라이언트에 전송
        for client in self.clients:
            try:
                client.send(f"SETUP: {self.expected_user_count}".encode())
                print(f"[INFO] 클라이언트에 유저 수 전송: SETUP: {self.expected_user_count}")
            except socket.error:
                print(f"[ERROR] 클라이언트에게 유저 수 전송 실패")

        # QR 코드로 유저 등록
        while len(self.users) < self.expected_user_count:
            for client in self.clients:
                try:
                    data = client.recv(BUFFER_SIZE).decode().strip()
                    if data.startswith("user") and data[4:].isdigit():
                        if data not in self.users:
                            self.users[data] = User(data)
                            print(f"[INFO] {data} 사용자 등록 완료.")
                            client.send(f"User {data} created".encode())
                        else:
                            client.send(f"ERROR: {data} already exists".encode())
                    else:
                        client.send("ERROR: Invalid user format".encode())
                except socket.error:
                    print(f"[ERROR] 클라이언트와 통신 중 오류 발생")

        print("[INFO] 모든 유저가 등록되었습니다.")

    def start_game(self):
        """게임 시작"""
        print("[INFO] 게임 시작!")
        self.is_game_running.set()  # 게임 상태를 활성화
        threading.Thread(target=self.send_mission_messages, daemon=True).start()

    def send_mission_messages(self):
        """랜덤으로 START_MISSION 메시지 전송"""
        while self.is_game_running.is_set():
            if self.clients:
                random_client = random.choice(self.clients)
                try:
                    random_client.send("START_MISSION".encode())
                    print("[INFO] START_MISSION 메시지 전송")
                except socket.error:
                    with self.lock:
                        self.clients.remove(random_client)
            
            # 랜덤 간격 대기
            wait_time = random.uniform(5, 10)
            for _ in range(int(wait_time * 10)):  # 0.1초씩 체크하며 대기
                if not self.is_game_running.is_set():
                    return
                time.sleep(0.1)


    def end_game(self):
        """게임 종료"""
        print("[INFO] 게임 종료!")
        self.is_game_running.clear()  # 게임 상태를 비활성화

        for client in self.clients:
            try:
                client.send("GAME_OVER".encode())
                client.close()
            except:
                pass

        self.server_socket.close()

    def start(self):
        """서버 시작"""
        print("[INFO] 서버를 시작합니다.")
        self.accept_clients()
        self.register_users()
        self.start_game()

        # 게임 종료를 위한 타이머
        threading.Timer(20.0, self.end_game).start()


if __name__ == "__main__":
    server = GameServer()
    server.start()

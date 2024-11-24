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
        self.lock = threading.Lock()  # 스레드 동기화를 위한 Lock

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
        print("[INFO] QR 코드로 유저를 등록하거나 테스트 용도로 자동 생성 중입니다...")

        # 테스트용으로 자동으로 사용자 객체 생성
        for i in range(1, self.expected_user_count + 1):
            user_id = str(i)  # User ID를 숫자로 사용
            if user_id not in self.users:
                self.users[user_id] = User(user_id)  # User 객체 생성
                print(f"[INFO] 테스트용 사용자 {user_id} 생성 완료. [ {self.users[user_id]} ]")

        # QR 코드로 유저 등록 (주석처리된 코드)
        # while len(self.users) < self.expected_user_count:
        #     for client in self.clients:
        #         try:
        #             data = client.recv(BUFFER_SIZE).decode().strip()
        #             # 숫자만 포함된 데이터를 유저로 등록
        #             if data.isdigit():
        #                 user_id = data  # 숫자를 그대로 user_id로 사용
        #                 if user_id not in self.users:
        #                     self.users[user_id] = User(user_id)  # User 객체 생성
        #                     print(f"[INFO] {user_id} 사용자 등록 완료.")
        #                     client.send(f"User {user_id} created".encode())
        #                 else:
        #                     client.send(f"ERROR: {user_id} already exists".encode())
        #             else:
        #                 client.send("ERROR: Invalid user format".encode())
        #         except socket.error:
        #             print(f"[ERROR] 클라이언트와 통신 중 오류 발생")

        print("[INFO] 모든 유저가 등록되었습니다.")

    def handle_client_message(self, client: socket.socket):
        """클라이언트로부터 메시지를 처리"""
        while True:
            try:
                data = client.recv(BUFFER_SIZE).decode().strip()
                if not data:
                    break

                print(f"[INFO] 클라이언트 메시지: {data}")

                # PLAYER_CHECK 처리
                if data.startswith("PLAYER_CHECK:"):
                    user_id = data.split(":")[1]
                    if user_id in self.users:
                        user = self.users[user_id]
                        is_available = "true" if user.hp > 0 else "false"
                        client.send(f"MISSION_AVAILABLE:{is_available}".encode())
                    else:
                        client.send(f"ERROR: User {user_id} does not exist".encode())
            except socket.error:
                print(f"[ERROR] 클라이언트와 통신 중 오류 발생")
                break

    def start_game(self):
        """게임 시작"""
        print("[INFO] 게임 시작!")
        self.is_game_running.set()  # 게임 상태를 활성화

        # 클라이언트 메시지 처리 스레드 시작
        for client in self.clients:
            threading.Thread(target=self.handle_client_message, args=(client,), daemon=True).start()

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
            
            time.sleep(random.uniform(10, 20))

    def end_game(self):
        """게임 종료"""
        print("[INFO] 게임 종료!")
        self.is_game_running.clear()  # 게임 상태를 비활성화

        # 모든 유저 상태 출력
        print("\n[INFO] 게임 종료 시점의 유저 상태:")
        for user_id, user in self.users.items():
            print(f"  - {user}")  # User 클래스의 __str__ 메서드로 출력

        # 포인트 기준으로 우승자 계산
        max_point = max(user.point for user in self.users.values())
        winners = [user_id for user_id, user in self.users.items() if user.point == max_point]

        if len(winners) == 1:
            print(f"[INFO] 우승자: User{winners[0]} (Point: {max_point})")
        else:
            print(f"[INFO] 동점입니다. 동점 유저: {', '.join(winners)}")

        # 모든 클라이언트 종료 메시지 전송
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
        threading.Timer(10.0, self.end_game).start()


if __name__ == "__main__":
    server = GameServer()
    server.start()

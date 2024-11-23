import socket
import random
import time
import threading
from typing import List, Dict

# 상수 정의
HOST = 'localhost'
PORT = 1234
MAX_CLIENTS = 3  # 현재 1로 설정된 클라이언트 수 제한
BUFFER_SIZE = 1024  # 소켓 수신 버퍼 크기
MIN_WAIT_TIME = 10  # 최소 대기 시간
MAX_WAIT_TIME = 30  # 최대 대기 시간
CHECK_INTERVAL = 1  # 클라이언트 접속 확인 간격

class GameServer:
    def __init__(self, host=HOST, port=PORT):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        #접속한 클라이언트 저장
        self.clients: List[socket.socket] = []
        #게임 결과 저장(플레이어 아이디,리스트)
        self.mission_results: Dict[str, list] = {}
        self.game_timer = None
        self.is_game_running = True  # 추가
        
    def create_message_handler(self, client_socket):
        handler_thread = threading.Thread(
            target=self.handle_client_message,
            args=(client_socket,)
        )
        handler_thread.daemon = True
        handler_thread.start()

        
    def accept_clients(self):
        print("log:accept_clients")
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"새로운 클라이언트 접속: {addr}")
            self.clients.append(client_socket)
            
            self.create_message_handler(client_socket)
            
    def handle_client_message(self, client_socket: socket.socket):
        while True:
            try:
                message = client_socket.recv(BUFFER_SIZE).decode()
                if message:
                    if message.startswith("MISSION_RESULT:"):
                        _, data = message.split(":", 1)
                        mission, player_id, result = data.strip().split()
                        
                        if player_id not in self.mission_results:
                            self.mission_results[player_id] = []
                        self.mission_results[player_id].append({
                            'mission' : mission,
                            'result': result,
                            'timestamp': time.time()
                        })
                        
                        print(f"미션 결과 저장: 플레이어 {player_id}, 결과 {result}")
                        
            except socket.error:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
                    print(f"클라이언트 연결 종료: {client_socket.getpeername()}")
                break
            
    def send_random_start_game(self):
        print("log:send_random_start_game")
        while self.is_game_running:  # 수정
            if self.clients:
                # 무작위 클라이언트 선택
                random_client = random.choice(self.clients)
                try:
                    # start game 메시지 전송
                    random_client.send("START_MISSION".encode())
                    print("START_MISSION 메시지 전송 완료")
                except socket.error:
                    # 연결이 끊긴 클라이언트 제거
                    self.clients.remove(random_client)
            # 10~30초 무작위 대기
            time.sleep(random.uniform(MIN_WAIT_TIME, MAX_WAIT_TIME))
            
    def start(self):
        # 클라이언트 접속 수락 스레드
        accept_thread = threading.Thread(target=self.accept_clients)
        accept_thread.daemon = True
        accept_thread.start()
        
        # 클라이언트 3개 접속 대기 후 시작 메시지 전송 스레드
        def wait_and_start_game():
            while True:
                if len(self.clients) == MAX_CLIENTS:
                    print(f"{MAX_CLIENTS}개의 클라이언트가 접속되어 게임을 시작합니다.")
                    self.game_timer = threading.Timer(20.0, self.end_game)
                    self.game_timer.start()
                    self.send_random_start_game()
                    break
                time.sleep(CHECK_INTERVAL)
        
        wait_thread = threading.Thread(target=wait_and_start_game)
        wait_thread.daemon = True
        wait_thread.start()
    def end_game(self):
        print("게임 시간 종료!")
        self.is_game_running = False  # 추가
        
        # mission_results에서 각 플레이어의 성공 횟수 계산
        player_scores = {}
        for player_id, results in self.mission_results.items():
            success_count = sum(1 for result in results if result['result'] == 'SUCCESS')
            player_scores[player_id] = success_count
        
        # 점수 기준으로 정렬된 결과 생성
        sorted_scores = sorted(player_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 결과 메시지 생성
        result_message = "GAME_OVER"
        
        # 모든 클라이언트에게 결과 전송
        for client in self.clients:
            try:
                client.send(result_message.encode())
            except:
                print("[ERROR] 클라이언트에게 결과 전송 실패")
            
        for rank, (player_id, score) in enumerate(sorted_scores, 1):
            result_message += f"{rank}등: 플레이어 {player_id} - 성공 {score}회\n"
        
        print(result_message)  # 서버 콘솔에도 출력
        # 모든 클라이언트 소켓 닫기
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        
        self.server_socket.close()
        # 프로그램 강제 종료
        import sys
        sys.exit(0)
        

from game_server import GameServer

HOST = '0.0.0.0'  # 모든 네트워크 인터페이스에서 요청 수신
PORT = 1234        # 포트 번호

if __name__ == "__main__":
    # 서버 생성
    server = GameServer(host=HOST, port=PORT)
    
    print(f"서버가 {HOST}:{PORT}에서 시작되었습니다...")
    
    try:
        # 서버 시작
        server.start()
        
        # 메인 스레드가 종료되지 않도록 대기
        while True:
            input()  # 엔터를 누르면 서버 종료
    except KeyboardInterrupt:
        print("서버를 종료합니다...")

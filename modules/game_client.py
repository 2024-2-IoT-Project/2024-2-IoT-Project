import socket
import cv2
from qr_recog import recognize_qr_code
from cham_game_logic import cham_game
from rsp_game_logic import rsp_game
import random

# 서버 설정
SERVER_HOST = '59.187.203.169'  # 서버 IP. 추후 mDNS적용해보기.
SERVER_PORT = 1234

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_HOST, SERVER_PORT))
print("[INFO] 서버 연결됨.")

try:
    # 게임 시작 요청
    client.send("START_GAME".encode())

    while True:
        message = client.recv(1024).decode()

        if message.startswith("START_MISSION"):
        # if True:
            # TODO 미션을 받은 경우 LED 등을 켜는 등 게임이 가능함을 알려야 하지 않나?
            print("[INFO] 미션 시작 수신")

            # 카메라 초기화 (카메라 번호는 기본값 0)
            cap = cv2.VideoCapture(0)

            while not cap.isOpened():
                cap = cv2.VideoCapture(0)
            
            # qr 인식 후 사용자 식별해서 서버에 게임 가능 여부 조회
            player = recognize_qr_code(cap)
            print(player)
            client.send(f"PLAYER_CHECK:{player}".encode())

            # 게임 가능 여부 조회하고 결과 받을 때까지 대기
            while True:
                message = client.recv(1024).decode()
                if message.startswith("MISSION_AVAILABLE") and message.split(":")[1] == "true":
                # if True:
                    # TODO 게임 실행 및 결과 전송

                    # 랜덤으로 진행할 게임 결정
                    game_choice = random.randint(0, 1)
                    if game_choice == 0:
                        print("play cham")
                    else:
                        print("play rsp")
                    
                    if game_choice == 0:
                        game_result = cham_game(cap)
                        print("cham " + str(game_result))
                        if game_result:
                            client.send(f"MISSION_RESULT: cham {player} correct".encode())
                        else:
                            client.send(f"MISSION_RESULT: cham {player} wrong".encode())
                        break

                    else:
                        # TODO 가위바위보 게임 로직 구현
                        game_result = rsp_game(cap)
                        print("rsp " + str(game_result))

                        if game_result:
                            client.send(f"MISSION_RESULT: rsp {player} correct".encode())
                        else:
                            client.send(f"MISSION_RESULT: rsp {player} wrong".encode())

                else:
                    # 게임 실행 안 함
                    print("[ERROR] 사용자의 체력이 회복되지 않아 게임을 실행할 수 없습니다.")
                    break

        elif message == "GAME_OVER":
            print("[INFO] 게임 종료 신호 수신.")
            client.close()
            break

except Exception as e:
    print(f"[ERROR] 클라이언트 에러: {e}")
finally:
    try:
        client.close()
        pass
    except:
        pass

    print("[INFO] 서버 연결 종료.")

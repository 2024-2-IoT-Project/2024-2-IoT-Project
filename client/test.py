import socket
import threading

SERVER_HOST = '59.187.203.169'  # 라즈베리파이 공인 IP (공유기 IP)
SERVER_PORT = 1234            # 서버 포트 번호
BUFFER_SIZE = 1024         # 소켓 버퍼 크기

def receive_messages(client_socket):
   """서버로부터 오는 메시지를 수신하여 출력"""
   try:
      while True:
         message = client_socket.recv(BUFFER_SIZE).decode().strip()
         if not message:
               break  # 서버가 연결을 닫으면 종료
         print(f"[SERVER] {message}")  # 수신한 메시지 출력
   except Exception as e:
      print(f"[ERROR] 서버 메시지 수신 중 오류 발생: {e}")

def send_messages(client_socket):
   """사용자가 입력한 메시지를 서버로 전송"""
   try:
      while True:
         message = input("> ")  # 사용자로부터 메시지 입력
         if message.lower() == "exit":
               print("[INFO] 클라이언트를 종료합니다.")
               client_socket.send("DISCONNECT".encode())  # 종료 메시지 전송
               break
         client_socket.send(message.encode())  # 입력 메시지 서버로 전송
   except Exception as e:
      print(f"[ERROR] 서버로 메시지 전송 중 오류 발생: {e}")

def main():
   """클라이언트 실행"""
   try:
      # 서버에 연결
      client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      client_socket.connect((SERVER_HOST, SERVER_PORT))
      print("[INFO] 서버에 연결되었습니다.")

      # 서버 메시지 수신 스레드 시작
      threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

      # 사용자 메시지 전송 시작
      send_messages(client_socket)

   except Exception as e:
      print(f"[ERROR] 클라이언트 실행 중 오류 발생: {e}")
   finally:
      client_socket.close()
      print("[INFO] 클라이언트 연결이 종료되었습니다.")

if __name__ == "__main__":
   main()

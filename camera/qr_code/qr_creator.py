import qrcode

# QR 코드 생성 함수
def create_qr_code(user_id, filename="qr_code.png"):
    # QR 코드에 포함할 사용자 정보
    user_data = {
    "player1": "P1",
    "player2": "P2",
    "player3": "P3",
    "player4": "P4"
    }
    
    # 사용자 구분 데이터 확인
    if user_id in user_data:
        qr_data = f"{user_id}:{user_data[user_id]}"
    else:
        print("유효하지 않은 사용자 ID입니다.")
        return
    
    # QR 코드 생성
    qr = qrcode.QRCode(
        version=1,  # QR 코드 버전 (1은 작은 크기)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # QR 코드에 데이터 추가
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # 이미지 생성 및 저장
    img = qr.make_image(fill="black", back_color="white")
    img.save(filename)
    print(f"{filename} 파일로 QR 코드가 저장되었습니다.")

# 예시: 사용자 ID에 따라 QR 코드 생성
create_qr_code("player1", "player1_qr.png")
create_qr_code("player2", "player2_qr.png")
create_qr_code("player3", "player3_qr.png")
create_qr_code("player4", "player4_qr.png")

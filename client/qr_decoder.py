import cv2

def decode_qr(frame):
    detector = cv2.QRCodeDetector()

    # QR 코드 해석
    data, _, _ = detector.detectAndDecode(frame)
    if data:
        print(f"[DEBUG] QR 코드 인식 성공: {data}")
        return data  # QR 코드 데이터 반환 (예: userID)
    return None


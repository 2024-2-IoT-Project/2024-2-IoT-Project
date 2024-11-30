import os
import random
import tkinter as tk
from PIL import Image, ImageTk  # 이미지 처리를 위해 PIL 사용

# 이미지 폴더 경로 설정
IMAGE_FOLDER = './images'

os.environ["DISPLAY"] = ":0.0"
# 이미지와 정답 초기화
current_image_path = None
current_answer = None

# 랜덤 이미지 로드 함수
def load_random_image():
    global current_image_path, current_answer

    # 이미지 폴더에서 랜덤 이미지 선택
    files = [f for f in os.listdir(IMAGE_FOLDER) if f.endswith('.png')]
    if not files:
        result_label.config(text="이미지를 찾을 수 없습니다.", fg="red")
        return

    random_file = random.choice(files)
    current_image_path = os.path.join(IMAGE_FOLDER, random_file)
    current_answer = random_file.replace('.png', '')  # 파일명에서 확장자 제거

    # 이미지 표시
    image = Image.open(current_image_path)
    image = image.resize((300, 300))  # 적절한 크기로 조정
    tk_image = ImageTk.PhotoImage(image)
    image_label.config(image=tk_image)
    image_label.image = tk_image  # 참조 유지

    # 결과 초기화
    result_label.config(text="")

    # 보기 버튼 업데이트
    update_options()

# 보기 버튼 업데이트 함수
def update_options():
    # 정답 포함하여 보기 3개 생성
    options = [current_answer]
    while len(options) < 3:
        random_file = random.choice(os.listdir(IMAGE_FOLDER)).replace('.png', '')
        if random_file not in options:
            options.append(random_file)

    # 보기 섞기
    random.shuffle(options)

    # 버튼에 텍스트 설정
    for i, option in enumerate(options):
        option_buttons[i].config(text=option, command=lambda opt=option: check_answer(opt))

# 정답 확인 함수
def check_answer(selected_option):
    # 버튼 비활성화
    for btn in option_buttons:
        btn.config(state=tk.DISABLED)

    # 정답 확인
    if selected_option == current_answer:
        result_label.config(text="정답입니다!", fg="green")
    else:
        result_label.config(text=f"틀렸습니다. 정답은 '{current_answer}'입니다.", fg="red")

    # 3초 후 다음 문제로 넘어감과 버튼 활성화
    root.after(3000, lambda: (load_random_image(), enable_buttons()))

def enable_buttons():
    # 버튼 활성화
    for btn in option_buttons:
        btn.config(state=tk.NORMAL)

# Tkinter 기본 창 설정
root = tk.Tk()
root.title("티니핑 맞추기 게임")
root.attributes("-fullscreen",True)


# UI 요소 구성
title_label = tk.Label(root, text="티니핑 맞추기 게임", font=("Arial", 20))
title_label.pack(pady=10)

image_label = tk.Label(root)
image_label.pack(pady=10)

# 보기 버튼 3개 생성
option_buttons = []
for _ in range(3):
    btn = tk.Button(root, text="", font=("Arial", 12), width=20)
    btn.pack(pady=5)
    option_buttons.append(btn)

result_label = tk.Label(root, text="", font=("Arial", 14))
result_label.pack(pady=10)

# 첫 이미지 로드
load_random_image()

# Tkinter 메인 루프 실행
root.mainloop()


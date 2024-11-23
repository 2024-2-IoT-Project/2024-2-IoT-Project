def save_user_id(user_id):
    with open("user_ids.log", "a") as file:
        file.write(f"{user_id}\n")
    print(f"[INFO] userID {user_id} 저장 완료")


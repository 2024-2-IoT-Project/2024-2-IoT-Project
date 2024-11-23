class User:
    def __init__(self, user_id, hp=1, point=0):
        self.user_id = user_id  # 사용자 ID
        self.hp = hp            # 사용자 HP (기본값 1)
        self.point = point      # 사용자 포인트 (기본값 0)

    def update_hp(self, amount):
        """HP 업데이트"""
        self.hp += amount
        if self.hp < 0:
            self.hp = 0  # HP는 0 이하로 내려가지 않음
        print(f"[INFO] {self.user_id}의 HP가 {self.hp}로 변경되었습니다.")

    def update_point(self, amount):
        """포인트 업데이트"""
        self.point += amount
        print(f"[INFO] {self.user_id}의 포인트가 {self.point}로 변경되었습니다.")

    def __str__(self):
        """사용자 정보를 문자열로 반환"""
        return f"User(userID={self.user_id}, HP={self.hp}, Point={self.point})"

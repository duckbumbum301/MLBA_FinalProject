class User:
    def __init__(self, id: int, username: str, role: str):
        self.id = id
        self.username = username
        self.role = role

    def is_admin(self) -> bool:
        return self.role == 'Admin'

    def is_user(self) -> bool:
        return self.role != 'Admin'

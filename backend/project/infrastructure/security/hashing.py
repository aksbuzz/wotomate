from bcrypt import gensalt, hashpw, checkpw

from project.application.services import IPasswordHasher

class BCryptPasswordHasher(IPasswordHasher):
    def hash_password(self, password: str) -> str:
        return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

    def check_password(self, password: str, hashed_password: str) -> bool:
        return checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

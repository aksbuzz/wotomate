from flask_jwt_extended import create_access_token

from project.domain.repositories.user_repository import IUserRepository
from project.domain.models.user import User
from project.application.services import IPasswordHasher, IUnitOfWork


class AuthUseCases:
    def __init__(
        self, 
        user_repository: IUserRepository, 
        password_hasher: IPasswordHasher,
        uow: IUnitOfWork
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.uow = uow

    def register(self, data):
        with self.uow:
            email = data.get('email')
            password = data.get('password')

            if self.user_repository.get_by_email(email):
                raise ValueError('User already exists')

            hashed_password = self.password_hasher.hash_password(password)
            new_user = User(email=email, password_hash=hashed_password)
            
            self.user_repository.save(new_user)
            self.uow.commit()

    def login(self, data):
        email = data.get('email')
        password = data.get('password')

        user = self.user_repository.get_by_email(email)
        if not user:
            raise ValueError(f"User '{email}' not found")

        if self.password_hasher.check_password(password, user.password_hash):
            access_token = create_access_token(identity=str(user.id), expires_delta=False)
            return {'access_token': access_token, 'user_id': user.id, 'email': email}
        else:
            raise ValueError('Invalid credentials')

    def get_user_by_id(self, user_id):
        return self.user_repository.get_by_id(user_id)

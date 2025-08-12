from abc import ABC, abstractmethod
from project.domain.models.connection import EncryptedCredentials

class IUnitOfWork(ABC):
    @abstractmethod
    def __enter__(self): 
      pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb): 
      pass

    @abstractmethod
    def commit(self): 
      pass

    @abstractmethod
    def rollback(self): 
      pass

class IPasswordHasher(ABC):
  @abstractmethod
  def hash_password(self, password: str) -> str:
    pass

  @abstractmethod
  def check_password(self, password: str, hashed_password: str) -> bool:
    pass

class IEncryptionService(ABC):
  @abstractmethod
  def encrypt(self, data: dict) -> EncryptedCredentials:
    pass
  
  def decrypt(self, encrypted_creds: EncryptedCredentials) -> dict:
    pass
from abc import ABC, abstractmethod
from typing import Optional
from project.domain.models.user import User

class IUserRepository(ABC):
  @abstractmethod
  def save(self, user: User) -> User:
    pass
  
  @abstractmethod
  def get_by_email(self, email: str) -> Optional[User]:
    pass
  
  @abstractmethod
  def get_by_id(self, user_id: int) -> Optional[User]:
    pass
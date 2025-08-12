from typing import Optional
from flask_sqlalchemy.session import Session

from project.domain.repositories.user_repository import IUserRepository
from project.domain.models.user import User as DomainUser
from project.infrastructure.models.user import User as SQLUser


class SQLAlchemyUserRepository(IUserRepository):
  def __init__(self, session: Session):
    self.session = session
  
  def save(self, user: DomainUser):
    sql_user = SQLUser()
    UserMapper.from_domain(user, sql_user)
    
    self.session.add(sql_user)
  
  def get_by_email(self, email: str) -> Optional[DomainUser]:
    sql_user = self.session.query(SQLUser).filter_by(email=email).first()
    if not sql_user:
      return None
    
    return UserMapper.to_domain(sql_user)

  def get_by_id(self, id: str) -> Optional[DomainUser]:
    sql_user = self.session.query(SQLUser).filter_by(id=id).first()
    if not sql_user:
      return None
    
    return UserMapper.to_domain(sql_user) 
  

class UserMapper:
  @staticmethod
  def to_domain(sql_user: SQLUser) -> DomainUser:
    return DomainUser(
      id=sql_user.id,
      email=sql_user.email,
      password_hash=sql_user.password_hash,
    )
  
  @staticmethod
  def from_domain(domain_user: DomainUser, sql_user: SQLUser):
    sql_user.email = domain_user.email
    sql_user.password_hash = domain_user.password_hash

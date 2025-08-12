from project.application.services import IUnitOfWork
from project.config.database import db


class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session = db.session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
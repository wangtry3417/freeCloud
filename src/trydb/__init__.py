from sqlalchemy import Column, create_engine, String, Integer, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

Model = declarative_base()

class DataBase:
    def __init__(self, url: str, use_session: bool = True):
        self.engine = create_engine(url)
        self.Session = sessionmaker(bind=self.engine) if use_session else None

    def create_all(self):
        Model.metadata.create_all(self.engine)

    def get_session(self):
        if self.Session:
            return self.Session()
        else:
            raise Exception("Session not available. Ensure use_session is True.")
    def _close_session(self,session):
        if session:
            session.close()

__all__ = ["DataBase", "String", "Integer", "Boolean", "Model"]

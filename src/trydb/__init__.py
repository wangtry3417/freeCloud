from sqlalchemy import Column, create_engine, String, Integer, Boolean, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

Model = declarative_base()

class DataBase:
    def __init__(self, url: str, use_session: bool = True):
        self.engine = create_engine(url)
        self.Session = sessionmaker(bind=self.engine) if use_session else None
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)  # 反射獲取所有表

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
    def get_table(self, table_name):
        # 使用反射獲取表，確保表名為小寫
        return self.metadata.tables.get(table_name.lower())

__all__ = ["DataBase", "String", "Integer", "Boolean", "Model", "Column"]

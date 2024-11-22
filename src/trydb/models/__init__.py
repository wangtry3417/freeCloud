from sqlalchemy import Column, String, Integer, Boolean, DateTime
from .. import declarative_base

Model = declarative_base()

class BaseModel(Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
  
    def __repr__(self):
        return f"<BaseModel(id={self.id})>"

__all__ = ["BaseModel"]

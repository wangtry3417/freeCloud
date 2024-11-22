from .. import declarative_base,String,Integer,Boolean,Column,Model

class BaseModel(Model):
  id = Column(Integer,primary_key=True)
  #Add fields

__all__ = ["BaseModel"]

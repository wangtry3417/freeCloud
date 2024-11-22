from .. import declarative_base,String,Integer,Boolean,Column

Model = declarative_base()

class BaseModel(Model):
  id = Column(Integer,primary_key=True)
  

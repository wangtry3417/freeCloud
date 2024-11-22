from sqlalchemy import Column, create_engine, String, Integer, Boolean, Column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

Model = declarative_base()

def DataBase(url:str,useSession=True : bool):
  if useSession:
    engine = create_engine(url)
    return sessionmaker(bind=engine)
  else:
    return create_engine(url)

def _create_all():
  return Model.metadata.create_all(engine)

__all__ = ["DataBase","String","Integer","Boolean","Model","Column","_create_all"]

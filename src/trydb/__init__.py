from sqlalchemy import Column, create_engine, String, Integer, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

def DataBase(url:str,useSession=True : bool):
  if useSession:
    engine = create_engine(url)
    return sessionmaker(bind=engine)
  else:
    return create_engine(url)

__all__ = ["DataBase","String","Integer","Boolean","declarative_base"]

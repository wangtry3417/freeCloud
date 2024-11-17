from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def _app(appName=None):
  if appName != None:
    return Flask(appName)
  else:
    return Flask(__name__)

def find_db_file(filename) -> str:
  return "sqlite:///"+filename

db = SQLAlchemy()

__all__ = ["__app","find_db_file","db"]

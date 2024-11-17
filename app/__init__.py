from flask import Flask

def _app(appName=None):
  if appName != None:
    return Flask(appName)
  else:
    return Flask(__name__)

def find_db_file(filename) -> str:
  return "sqlite:///"+filename

__all__ = ["__app","find_db_file"]

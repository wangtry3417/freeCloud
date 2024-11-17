from flask import Flask

def __app(appName=None):
  if app != None:
    return Flask(appName)
  else:
    return Flask(__name__)

def find_db_file(filename):
  return filename

__all__ = ["__app","find_db_file"]

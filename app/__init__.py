from flask import Flask

def __app(appName=None):
  if app != None:
    return Flask(appName)
  else:
    return Flask(__name__)

__all__ = ["__app"]

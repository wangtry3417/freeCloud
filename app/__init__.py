from flask import Flask,request,render_template,jsonify
from flask_sqlalchemy import SQLAlchemy

def _app(appName=None):
  if appName != None:
    return Flask(appName,template_folder="pages")
  else:
    return Flask(__name__,template_folder="pages")

def find_db_file(filename) -> str:
  return "sqlite:///"+filename

db = SQLAlchemy()

__all__ = ["_app","find_db_file","db","request","render_template","jsonify"]

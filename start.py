import os

from app.models import BaseModel
from app import db
from app.server import app

class Users(BaseModel):
  __tablename__ = 'users'
  username = db.Column(db.String(50))
  active = db.Column(db.Boolean)
  gender = db.Column(db.String(10))
  age = db.Column(db.Integer)

with app.app_context(:
  Users.create(username='Jack',active=True,gender='M',age=19)
  Users.create(username='Ben',active=True,gender='M',age=23)
  Users.create(username='Ken',active=True,gender='M',age=32)
  Users.create(username='Crystal',active=True,gender='F',age=67)
  Users._commit()

if not os.path.exists("main.db"):
  open("main.db","a").close()

#啟動flask-app
if __name__ == "__main__":
  from app.server import run_app
  run_app()

"""
如果不想web server，也可以datatable
"""
"""
from app.models import BaseModel
from app import db

class User(BaseModel):
  __tablename__ = 'user'
  username = db.Column(db.String(50))
  email = db.Column(db.String(50))
User.create(username='testname',email='someone@example.com'))
User._commit()
"""

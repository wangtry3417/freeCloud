import os

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

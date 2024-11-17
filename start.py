import os

if not os.path.exists("main.db"):
  open("main.db","a").close()

#啟動flask-app
if __name__ == "__main__":
  from app.server import run_app
  run_app()

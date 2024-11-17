from app import run_app
import os

if not os.path.exists("main.db"):
  open("main.db","a").close()

#啟動flask-app
if __name__ == "__main__":
  run_app()

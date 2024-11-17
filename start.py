from .app import run_app

with open("main.db","a+") as fp:
  run_app()

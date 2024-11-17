from . import __app,find_db_file
from flask_sqlalchemy import SQLAlchemy

#可以設置app的名字
app = __app()
#輸入sqlite協定的database文件
dbFile = find_db_file("test.db")
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = dbFile
db.init_app(app)

@app.route("/")
def index():
  return "Hello Page"

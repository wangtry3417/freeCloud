from . import __app,find_db_file,db

#可以設置app的名字
app = _app()
#輸入sqlite協定的database文件
dbFile = find_db_file("test.db")
app.config['SQLALCHEMY_DATABASE_URI'] = dbFile
db.init_app(app)

@app.route("/")
def index():
  return "Hello Page"

@app.route("/query/<statement>",methods=["GET","POST"])
def do_event(statement):
  if 

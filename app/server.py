from . import __app,find_db_file,db,request,render_template
from .models.base_model import BaseModel

#可以設置app的名字
app = _app()
#輸入sqlite協定的database文件
dbFile = find_db_file("test.db")
app.config['SQLALCHEMY_DATABASE_URI'] = dbFile
db.init_app(app)

@app.route("/")
def index():
  return "Hello Page"

@app.route("/create_table", methods=["POST"])
def create_model():
    table_name = request.form.get("table_name")
    fields = request.form.get("fields").split(",")

    # 動態創建模型
    attributes = {'__tablename__': table_name.lower()}
    for field in fields:
        name, field_type = field.split(":")
        if field_type == "String":
            attributes[name] = db.Column(db.String(80))
        elif field_type == "Integer":
            attributes[name] = db.Column(db.Integer)
        elif field_type == "Float":
            attributes[name] = db.Column(db.Float)
        elif field_type == "Boolean"
            attributes[name] = db.Column(db.Boolean)

    # 創建新的模型類
    new_model = type(table_name, (BaseModel,), attributes)
    db.create_all()  # 創建資料表
    return f"資料表 '{table_name}' 已經建立這些欄位: {', '.join(fields)}"

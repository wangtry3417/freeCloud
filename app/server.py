from . import _app,find_db_file,db,request,render_template
from .models import BaseModel
from sqlalchemy import inspect

#可以設置app的名字
app = _app()
#輸入sqlite協定的database文件
dbFile = find_db_file("main.db")
app.config['SQLALCHEMY_DATABASE_URI'] = dbFile
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route("/")
def index():
  return render_template("index.html")

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
        elif field_type == "Boolean":
            attributes[name] = db.Column(db.Boolean)

    # 創建新的模型類
    new_model = type(table_name, (BaseModel,), attributes)
    db.create_all()  # 創建資料表
    return f"資料表 '{table_name}' 已經建立這些欄位: {', '.join(fields)}"

@app.route("/query", methods=["GET"])
@app.route("/query/<statement>", methods=["GET", "POST"])
def do_event(statement=None):
    if request.method == "GET":
        if statement is None:
            # 獲取所有資料表名稱
            tables = db.engine.table_names()
            if tables:
                return render_template("query.html", tables=tables)
            else:
                return render_template("query.html", message="目前沒有任何資料表。請返回主頁或稍後再試。", show_back_button=True)

        elif statement == "selectAll":
            table_name = request.args.get("table_name")
            records = db.session.execute(f"SELECT * FROM {table_name}").fetchall()
            return render_template("query.html", statement=statement, records=records, table_name=table_name)

        return render_template("query.html", statement=statement)
    
    elif request.method == "POST":
        if statement == "insert":
            table_name = request.form.get("table_name")
            data = request.form.to_dict(flat=False)
            columns = [k for k in data.keys() if k != 'table_name']
            values = [data[k][0] for k in columns]

            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in columns])})"
            db.session.execute(insert_query, values)
            db.session.commit()
            return render_template("query.html", statement="記錄已插入成功", table_name=table_name)

    return "請求方式不支援", 405  # 返回 405 方法不被允許

@app.route("/query/table/<table_name>")
def query_table(table_name):
    records = db.session.execute(f"SELECT * FROM {table_name}").fetchall()
    return render_template("query.html", table_name=table_name, records=records)

def run_app(port=5000):
  app.run(host="0.0.0.0",port=5000)

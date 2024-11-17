from . import _app, find_db_file, db, request, render_template
from .models import BaseModel
from sqlalchemy import inspect
import html

# 可以設置app的名字
app = _app()
# 輸入sqlite協定的database文件
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
    if not table_name:
        return "沒有找到資料表的名字"

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

@app.route("/query", methods=["GET", "POST"])
def do_event():
    if request.method == "GET":
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        return render_template("query.html", tables=tables)

    elif request.method == "POST":
        tryDB_input = request.form.get("tryDB_input")
        if tryDB_input:
            try:
                if "Insert" in tryDB_input:
                    parts = tryDB_input.split("->")
                    if len(parts) == 3:
                        table_name = parts[0].split()[1].strip()
                        values = [
                            html.unescape(value.strip().strip("'"))
                            for value in parts[2].strip().strip(';').split(",")
                        ]

                        # 動態加載模型
                        model = db.Model._decl_class_registry.get(table_name.lower())
                        if model is None:
                            return render_template("query.html", message=f"模型 {table_name} 不存在。")

                        # 創建新實例
                        new_entry = model(**{field.strip(): value for field, value in zip(parts[1].strip().split(","), values)})
                        db.session.add(new_entry)
                        db.session.commit()
                        return render_template("query.html", statement="記錄已插入成功", table_name=table_name)

                elif "using" in tryDB_input:
                    parts = tryDB_input.split(",")
                    table_name = parts[0].split()[1].strip()
                    select_fields = parts[1].strip().split()[2]
                    condition = parts[2].strip().split("where")[1] if "where" in parts[2] else ""

                    # 動態查詢模型
                    model = db.Model._decl_class_registry.get(table_name.lower())
                    if model is None:
                        return render_template("query.html", message=f"模型 {table_name} 不存在。")

                    # 執行查詢
                    query = db.session.query(model).filter(text(condition))
                    records = query.all()
                    return render_template("query.html", statement="查詢結果", records=records, table_name=table_name)

                else:
                    raise ValueError("不支援的指令格式。")
            except Exception as e:
                return render_template("query.html", message=f"錯誤: {str(e)}")

    return "請求方式不支援", 405  # 返回 405 方法不被允許

@app.route("/query/table/<table_name>")
def query_table(table_name):
    model = db.Model._decl_class_registry.get(table_name.lower())
    if model is None:
        return render_template("query.html", message=f"模型 {table_name} 不存在。")
    
    records = db.session.query(model).all()
    return render_template("query.html", table_name=table_name, records=records)
def run_app(port=5000):
  app.run(host="0.0.0.0",port=5000)

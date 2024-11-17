from . import _app, find_db_file, db, request, render_template, jsonify
from .models import BaseModel
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
import html

# 可以設置app的名字
app = _app()
# 輸入sqlite協定的database文件
dbFile = find_db_file("main.db")
app.config['SQLALCHEMY_DATABASE_URI'] = dbFile
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 用於存儲動態創建的模型
dynamic_models = {}

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
    dynamic_models[table_name.lower()] = new_model  # 保存到字典中
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

                        model = dynamic_models.get(table_name.lower())
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

                    model = dynamic_models.get(table_name.lower())
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
    model = dynamic_models.get(table_name.lower())
    if model is None:
        return render_template("query.html", message=f"模型 {table_name} 不存在。")

    records = db.session.query(model).all()
    return render_template("query.html", table_name=table_name, records=records)

@app.route("/trydb", methods=["POST"])
def try_db():
    tryDB_input = request.json.get("query")  # 從 JSON 請求中獲取查詢
    if not tryDB_input:
        return jsonify({"error": "找不到query。"}), 400

    try:
        # Create Table
        if "create table" in tryDB_input:
            parts = tryDB_input.split("->")
            if len(parts) == 2:
                table_name = parts[0].split()[2].strip()
                fields_str = parts[1].strip()

                # 使用正則表達式解析元組
                pattern = r"\('([^']+)',\s*'([^']+)'\)"
                fields = re.findall(pattern, fields_str)

                if not fields:
                    return jsonify({"error": "字段格式不正確，應該是元組列表。"}), 400

                attributes = {'__tablename__': table_name.lower()}

                for field, field_type in fields:
                    if field_type == "String":
                        attributes[field] = db.Column(db.String(80))
                    elif field_type == "Integer":
                        attributes[field] = db.Column(db.Integer)
                    elif field_type == "Float":
                        attributes[field] = db.Column(db.Float)
                    elif field_type == "Boolean":
                        attributes[field] = db.Column(db.Boolean)
                    else:
                        return jsonify({"error": f"不支援的字段類型: {field_type}。"}), 400

                # 創建新的模型類
                new_model = type(table_name, (BaseModel,), attributes)
                dynamic_models[table_name.lower()] = new_model
                db.create_all()

                return jsonify({"message": f"資料表 '{table_name}' 已經建立。"}), 201

        elif "Insert" in tryDB_input:
            parts = tryDB_input.split("->")
            if len(parts) == 3:
                table_name = parts[0].split()[1].strip()
                fields = [field.strip() for field in parts[1].strip().split(",")]
                values = [value.strip().strip("'") for value in parts[2].strip().split(",")]

                if len(fields) != len(values):
                    return jsonify({"error": "字段數量與值數量不匹配。"}), 400

                model = dynamic_models.get(table_name.lower())
                if model is None:
                    return jsonify({"error": f"資料表 '{table_name}' 不存在。"}), 404

                # 創建新實例
                new_entry = model(**{field: value for field, value in zip(fields, values)})
                db.session.add(new_entry)
                db.session.commit()

                return jsonify({"message": "記錄已插入成功。"}), 201

            else:
                return jsonify({"error": "INSERT 語句格式不正確。"}), 400

        # Delete Table
        elif "delete table" in tryDB_input:
            parts = tryDB_input.split("->")
            if len(parts) == 2:
                table_name = parts[1].strip()
                model = dynamic_models.get(table_name.lower())
                if model:
                    db.session.execute(f"DROP TABLE {table_name.lower()}")
                    del dynamic_models[table_name.lower()]
                    db.session.commit()
                    return jsonify({"message": f"資料表 '{table_name}' 已被刪除。"}), 200
                else:
                    return jsonify({"error": f"資料表 '{table_name}' 不存在。"}), 404

            elif "with" in parts[1]:
                table_name, condition = parts[1].strip().split("with")
                table_name = table_name.strip()
                condition = condition.strip()
                model = dynamic_models.get(table_name.lower())
                if model:
                    field_name, field_value = condition.split("==")
                    field_name = field_name.strip()
                    field_value = field_value.strip().strip("'")

                    # 刪除指定條件的行
                    deleted_count = db.session.query(model).filter(getattr(model, field_name) == field_value).delete()
                    db.session.commit()
                    if deleted_count > 0:
                        return jsonify({"message": f"資料表 '{table_name}' 中滿足條件的記錄已被刪除。"}), 200
                    else:
                        return jsonify({"message": "沒有找到滿足條件的記錄。"}), 404
                else:
                    return jsonify({"error": f"資料表 '{table_name}' 不存在。"}), 404

        # Update
        elif "using" in tryDB_input:
            parts = tryDB_input.split("->")
            if len(parts) == 2:
                table_name = parts[0].split()[1].strip()
                set_part, condition_part = parts[1].strip().split("with")
                set_field, set_value = set_part.split("=")
                set_field = set_field.strip()
                set_value = set_value.strip().strip("'")
                condition_field, condition_value = condition_part.split("==")
                condition_field = condition_field.strip()
                condition_value = condition_value.strip().strip("'")

                model = dynamic_models.get(table_name.lower())
                if model:
                    # 更新操作
                    updated_count = db.session.query(model).filter(getattr(model, condition_field) == condition_value).update({set_field: set_value})
                    db.session.commit()
                    if updated_count > 0:
                        return jsonify({"message": f"資料表 '{table_name}' 中滿足條件的記錄已被更新。"}), 200
                    else:
                        return jsonify({"message": "沒有找到滿足條件的記錄。"}), 404
                else:
                    return jsonify({"error": f"資料表 '{table_name}' 不存在。"}), 404

        else:
            return jsonify({"error": "不支援的指令格式。"}), 400

    except SQLAlchemyError as e:
        db.session.rollback()  # 回滾任何未提交的事務
        return jsonify({"error": f"數據庫錯誤: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"發生錯誤: {str(e)}"}), 500

def run_app(port=5000):
  app.run(host="0.0.0.0",port=5000)

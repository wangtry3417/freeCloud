from . import _app, find_db_file, db, request, render_template, jsonify
from .models import BaseModel
from sqlalchemy import inspect,text
from sqlalchemy.exc import SQLAlchemyError
import html,re

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
                    if len(parts) != 2:
                        return render_template("query.html", message="請使用正確格式: using <table_name>, select <fields> [where <condition>]")

                    table_name = parts[0].split()[1].strip()
                    select_part = parts[1].strip()

                    if not select_part.startswith("select "):
                        return render_template("query.html", message="請使用 'select' 開頭的查詢指令")

                    # 檢查是否有 where 條件
                    if "where" in select_part:
                        select_fields, condition_part = select_part.split("where", 1)
                        select_fields = select_fields.replace("select", "").strip()
                        condition_part = condition_part.strip()
                    else:
                        select_fields = select_part.replace("select", "").strip()
                        condition_part = ""

                    model = dynamic_models.get(table_name.lower())
                    if model is None:
                        return render_template("query.html", message=f"模型 {table_name} 不存在。")

                    # 構建查詢
                    if select_fields == "*":
                        query = db.session.query(model)
                    else:
                        fields = [field.strip() for field in select_fields.split(",")]
                        query = db.session.query(model).with_entities(*[getattr(model, field) for field in fields if hasattr(model, field)])

                    # 處理 where 條件
                    if condition_part:
                        condition_parts = condition_part.strip().split()
                        if len(condition_parts) == 3:
                            field_name, operator, value = condition_parts
                            field = getattr(model, field_name, None)
                            if field is None:
                                return render_template("query.html", message=f"字段 '{field_name}' 不存在。")

                            # 構建 filter 條件
                            if operator == "=":
                                query = query.filter(field == value.strip("'"))
                            elif operator == ">":
                                query = query.filter(field > value.strip("'"))
                            elif operator == "<":
                                query = query.filter(field < value.strip("'"))
                            # 可以擴展更多運算符
                            else:
                                return render_template("query.html", message=f"不支援的運算符 '{operator}'。")
                        else:
                            return render_template("query.html", message="where 條件格式不正確，應為 '<field> <operator> <value>'。")

                    records = query.all()
                    return render_template("query.html", statement="查詢結果", records=records, table_name=table_name)
                elif "create table" in tryDB_input:
                    parts = tryDB_input.split("->")
                    if len(parts) == 2:
                      table_name = parts[0].split()[2].strip()
                      fields_str = parts[1].strip()

                      # 使用正則表達式解析元組
                      pattern = r"\('([^']+)',\s*'([^']+)'\)"
                      fields = re.findall(pattern, fields_str)

                      if not fields:
                        return render_template("query.html", message="字段不存在。")

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

                else:
                    raise ValueError("不支援的指令格式。")
            except Exception as e:
                return render_template("query.html", message=f"錯誤: {str(e)}")

    return "請求方式不支援", 405  # 返回 405 方法不被允許

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
        #Insert
        elif "Insert" in tryDB_input:
          parts = tryDB_input.split("->")
          if len(parts) == 3:
            table_name = parts[0].split()[1].strip()
            fields = parts[1].strip().split(",")
            values = parts[2].strip().split(",")

            # 去除多餘的空格和引號
            fields = [field.strip() for field in fields]
            values = [value.strip().strip("'") for value in values]

            # 將布爾字符串轉換為布爾值
            for i in range(len(values)):
              if values[i] in ['True', 'true', 'Yes', 'yes', '1']:
                values[i] = True
              elif values[i] in ['False', 'false', 'No', 'no', '0']:
                values[i] = False

            model = dynamic_models.get(table_name.lower())
            if model:
              # 創建新實例
              new_entry = model(**{field: value for field, value in zip(fields, values)})
              db.session.add(new_entry)
              db.session.commit()
              return jsonify({"message": "記錄已插入成功"}), 200
            else:
              return jsonify({"error": f"模型 '{table_name}' 不存在。"}), 404
          else:
            return jsonify({"error": "請使用正確格式: Insert <table_name> -> <fields> -> <values>"}), 400
        # Delete Table
        elif "delete table" in tryDB_input:
            parts = tryDB_input.split("->")
            if len(parts) == 2:
                table_name = parts[1].strip()
                model = dynamic_models.get(table_name.lower())
                if model:
                    db.session.execute(text(f"DROP TABLE {table_name.lower()}"))
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

        # 使用 SELECT 查詢
        if "using" in tryDB_input:
            parts = tryDB_input.split(",")
            if len(parts) == 2:
                table_name = parts[0].split()[1].strip()
                select_part = parts[1].strip()

                # 解析 SELECT 部分
                select_parts = select_part.split("where")
                fields_part = select_parts[0].replace("select", "").strip()
                condition_part = select_parts[1].strip() if len(select_parts) > 1 else None

                model = dynamic_models.get(table_name.lower())
                if model is None:
                    return jsonify({"error": f"資料表 '{table_name}' 不存在。"}), 404

                # 構建查詢
                query = db.session.query(model)
                
                # 添加字段
                if fields_part == "*":
                    pass  # 查詢所有字段
                else:
                    fields = [field.strip() for field in fields_part.split(",")]
                    query = query.with_entities(*[getattr(model, field) for field in fields])

                # 添加條件
                if condition_part:
                    condition_parts = condition_part.split()
                    if len(condition_parts) == 3:
                        field_name, operator, value = condition_parts
                        field = getattr(model, field_name, None)
                        if field is None:
                            return jsonify({"error": f"字段 '{field_name}' 不存在。"}), 404
                        if operator == "=":
                            query = query.filter(field == value.strip("'"))
                        elif operator == ">":
                            query = query.filter(field > value.strip("'"))
                        elif operator == "<":
                            query = query.filter(field < value.strip("'"))
                        # 可以擴展更多運算符

                # 獲取查詢結果
                results = query.all()

                # 格式化結果
                output = [{field: getattr(row, field) for field in fields} for row in results] if fields_part != "*" else [{column.name: getattr(row, column.name) for column in model.__table__.columns} for row in results]

                return jsonify(output), 200
        else:
            return jsonify({"error": "不支援的指令格式。"}), 400

    except SQLAlchemyError as e:
        db.session.rollback()  # 回滾任何未提交的事務
        return jsonify({"error": f"數據庫錯誤: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"發生錯誤: {str(e)}"}), 500

def run_app(port=5000):
  app.run(host="0.0.0.0",port=5000)

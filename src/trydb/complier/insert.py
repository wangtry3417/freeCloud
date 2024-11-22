# compiler/insert.py
import html
from sqlalchemy.exc import SQLAlchemyError

def handle_insert(tryDB_input, db):
    parts = tryDB_input.split("->")
    if len(parts) != 3:
        return {"error": "請使用正確格式進行插入。"}

    table_name = parts[0].split()[1].strip()
    values = [
        html.unescape(value.strip().strip("'"))
        for value in parts[2].strip().strip(';').split(",")
    ]

    session = db.get_session()
    try:
        # 使用反射獲取模型
        model = db.get_model(table_name)  # 假設你有一個方法來獲取模型
        if model is None:
            return {"error": f"模型 {table_name} 不存在。"}

        new_entry = model(**{field.strip(): value for field, value in zip(parts[1].strip().split(","), values)})
        session.add(new_entry)
        session.commit()
        return {"message": "記錄已插入成功", "table_name": table_name}
    except SQLAlchemyError as e:
        session.rollback()
        return {"error": f"插入失敗: {e}"}
    finally:
        db._close_session(session)

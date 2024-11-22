# compiler/insert.py
import html
from sqlalchemy.exc import SQLAlchemyError

def handle_insert(tryDB_input, db):
    parts = tryDB_input.split("->")
    if len(parts) != 3:
        return {"message": "請使用正確格式進行插入。"}

    table_name = parts[0].split()[1].strip()
    values = [
        html.unescape(value.strip().strip("'"))
        for value in parts[2].strip().strip(';').split(",")
    ]

    model = db.get(table_name.lower())
    if model is None:
        return {"error": f"模型 {table_name} 不存在。"}

    new_entry = model(**{field.strip(): value for field, value in zip(parts[1].strip().split(","), values)})
    session = db.get_session()  # 獲取新的會話
    try:
        session.add(new_entry)
        session.commit()
        return {"message": "記錄已插入成功", "table_name": table_name}
    except SQLAlchemyError as e:
        session.rollback()
        return {"error": f"插入失敗: {e}"}
    finally:
        session.close()

# compiler/create_table.py
import re
from sqlalchemy import Column, String, Integer, Float, Boolean

def handle_create_table(tryDB_input, db):
    parts = tryDB_input.split("->")
    if len(parts) != 2:
        return {"error": "請使用正確格式創建表格。"}

    table_name = parts[0].split()[2].strip()
    fields_str = parts[1].strip()

    pattern = r"\('([^']+)',\s*'([^']+)'\)"
    fields = re.findall(pattern, fields_str)

    if not fields:
        return {"error": "字段不存在。"}

    attributes = {'__tablename__': table_name.lower()}

    for field, field_type in fields:
        if field_type == "String":
            attributes[field] = Column(String(80))
        elif field_type == "Integer":
            attributes[field] = Column(Integer)
        elif field_type == "Float":
            attributes[field] = Column(Float)
        elif field_type == "Boolean":
            attributes[field] = Column(Boolean)
        elif field_type == "Image":
            attributes[field] = Column(String(255))
        else:
            return {"error": f"不支援的字段類型: {field_type}。"}

    new_model = type(table_name, (BaseModel,), attributes)
    db[table_name.lower()] = new_model
    db.create_all()

    return {"message": f"資料表 '{table_name}' 已經建立。"}

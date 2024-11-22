# compiler/create_table.py
import re
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData

def handle_create_table(tryDB_input, db):
    parts = tryDB_input.split("->")
    if len(parts) != 2:
        return {"error": "請使用正確格式創建表格。"}

    table_name = parts[0].split()[2].strip()
    fields_str = parts[1].strip()

    # 正則表達式來解析字段
    pattern = r"\('([^']+)',\s*'([^']+)'\)"
    fields = re.findall(pattern, fields_str)

    if not fields:
        return {"error": "字段不存在。"}

    # 使用 MetaData 來管理表
    metadata = MetaData()

    # 定義新表的欄位
    columns = []
    for field, field_type in fields:
        if field_type == "String":
            columns.append(Column(field, String(80)))
        elif field_type == "Integer":
            columns.append(Column(field, Integer))
        elif field_type == "Float":
            columns.append(Column(field, Float))
        elif field_type == "Boolean":
            columns.append(Column(field, Boolean))
        elif field_type == "Image":
            columns.append(Column(field, String(255)))
        else:
            return {"error": f"不支援的字段類型: {field_type}。"}

    # 創建表
    new_table = Table(table_name.lower(), metadata, *columns)

    # 使用引擎創建表
    metadata.create_all(db.engine)

    return {"message": f"資料表 '{table_name}' 已經建立。"}

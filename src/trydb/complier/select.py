# trydb/select.py
from sqlalchemy import create_engine, Table, MetaData

def handle_select(tryDB_input, db):
    parts = tryDB_input.split(",")
    
    if len(parts) != 2:
        return {"error": "請使用正確格式進行查詢。"}

    # 提取表格和查詢部分
    table_name = parts[0].strip().split()[1]
    fields_part = parts[1].strip().replace("select", "").strip()

    # 確保表格存在
    session = db.get_session()
    try:
        metadata = MetaData(bind=db.engine)
        metadata.reflect()
        table = metadata.tables.get(table_name)

        if table is None:
            return {"error": f"表 {table_name} 不存在。"}

        # 確保字段存在
        fields = [field.strip() for field in fields_part.split(",")]
        query_fields = [table.c[field] for field in fields if field in table.c]

        if not query_fields:
            return {"error": "指定的字段不存在。"}

        # 執行查詢
        results = session.query(*query_fields).all()

        return {"results": [dict(row) for row in results]}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db._close_session(session)

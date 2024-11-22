# compiler/select.py
def handle_select(tryDB_input, db):
    parts = tryDB_input.split(",")
    if len(parts) != 2:
        return {"error": "請使用正確格式: using <table_name>, select <fields> [where <condition>]"}
    
    table_name = parts[0].split()[1].strip()
    select_part = parts[1].strip()

    session = db.get_session()
    try:
        table = db.get_table(table_name)
        if table is None:
            return {"error": f"表 {table_name} 不存在。"}

        # 構建查詢
        query = session.query(table)
        records = query.all()
        
        return {"message": "查詢結果", "records": [dict(record) for record in records]}
    finally:
        db._close_session(session)

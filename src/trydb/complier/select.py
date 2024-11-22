# compiler/select.py
def handle_select(tryDB_input, db):
    parts = tryDB_input.split(",")
    if len(parts) != 2:
        return {"error": "請使用正確格式: using <table_name>, select <fields> [where <condition>]"}
    
    table_name = parts[0].split()[1].strip()
    select_part = parts[1].strip()

    session = db.get_session()
    try:
        model = db.get_model(table_name)  # 假設你有一個方法來獲取模型
        if model is None:
            return {"error": f"模型 {table_name} 不存在。"}

        query = session.query(model)
        # 進行查詢邏輯處理（選擇字段、條件等）
        # ...
        
        records = query.all()
        return {"message": "查詢結果", "records": records}
    finally:
        db._close_session(session)

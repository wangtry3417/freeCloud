# compiler/select.py
def handle_select(tryDB_input, db):
    parts = tryDB_input.split(",")
    if len(parts) != 2:
        return {"error": "請使用正確格式: using <table_name>, select <fields> [where <condition>]"}
    
    table_name = parts[0].split()[1].strip()
    select_part = parts[1].strip()

    if not select_part.startswith("select "):
        return {"error": "請使用 'select' 開頭的查詢指令"}

    model = db.get(table_name.lower())
    if model is None:
        return {"error": f"模型 {table_name} 不存在。"}

    # 構建查詢
    session = db.get_session()
    try:
        if select_part == "*":
            query = session.query(model)
        else:
            fields = [field.strip() for field in select_part.replace("select", "").split(",")]
            query = session.query(model).with_entities(*[getattr(model, field) for field in fields if hasattr(model, field)])
        
        records = query.all()
        return {"message": "查詢結果", "records": records, "table_name": table_name}
    finally:
        session.close()

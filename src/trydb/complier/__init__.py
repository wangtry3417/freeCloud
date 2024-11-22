 # compiler/__init__.py
from .. import DataBase  # 假設 db_instance 在 init.py 中定義
from .insert import handle_insert
from .select import handle_select
from .create_table import handle_create_table

dynamic_models = {}

def tryDB(tryDB_input):
    if tryDB_input:
        try:
            if "Insert" in tryDB_input:
                return handle_insert(tryDB_input, dynamic_models)
            elif "using" in tryDB_input:
                return handle_select(tryDB_input, dynamic_models)
            elif "create table" in tryDB_input:
                return handle_create_table(tryDB_input, dynamic_models)
            else:
                return {"error": "不支援的指令格式。"}
        except Exception as e:
            return {"error": str(e)}
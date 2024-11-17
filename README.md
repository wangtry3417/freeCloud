# freeCloud
# -------------
FreeCloud 提供一個DataBase簡化語言"TryDB"
可以使用/trydb端點

關於tryDB 語法:
# Create table
```
  create table <table.name> -> ('fieldName','DataType'),()....
```
# Insert record
```
  insert <table.name> -> field1,field2... -> value1,value2...
```
# Select record
```
  using <table.name>, select <field>/*
```

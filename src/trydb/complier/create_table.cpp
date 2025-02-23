#include <regex>
#include <string>
#include <vector>

#include <sqlalchemy/table.h>
#include <sqlalchemy/column.h>
#include <sqlalchemy/string.h>
#include <sqlalchemy/integer.h>
#include <sqlalchemy/float.h>
#include <sqlalchemy/boolean.h>
#include <sqlalchemy/meta.h>

std::map<std::string, std::string> handle_create_table(std::string tryDB_input, Database db) {
    std::vector<std::string> parts;
    std::string delimiter = "->";
    size_t pos = 0;
    while ((pos = tryDB_input.find(delimiter)) != std::string::npos) {
        std::string part = tryDB_input.substr(0, pos);
        parts.push_back(part);
        tryDB_input.erase(0, pos + delimiter.length());
    }
    if (parts.size() != 2) {
        return {{"error", "請使用正確格式創建表格。"}};
    }

    std::string table_name = parts[0].substr(2).find(" ").substr(2);
    std::string fields_str = parts[1];

    // 正則表達式來解析字段
    std::regex pattern(R"(\('([^']+)',\s*'([^']+)'\))");
    std::smatch match;
    std::vector<std::pair<std::string, std::string>> fields;
    std::string::const_iterator searchStart(fields_str.cbegin());
    while (std::regex_search(searchStart, fields_str.cend(), match, pattern)) {
        fields.push_back(std::make_pair(match[1].str(), match[2].str()));
        searchStart = match.suffix().first;
    }

    if (fields.empty()) {
        return {{"error", "字段不存在。"}};
    }

    // 使用 MetaData 來管理表
    MetaData metadata;

    // 定義新表的欄位
    std::vector<Column> columns;
    for (const auto& field : fields) {
        if (field.second == "String") {
            columns.push_back(Column(field.first, String(80)));
        } else if (field.second == "Integer") {
            columns.push_back(Column(field.first, Integer));
        } else if (field.second == "Float") {
            columns.push_back(Column(field.first, Float));
        } else if (field.second == "Boolean") {
            columns.push_back(Column(field.first, Boolean));
        } else if (field.second == "Image") {
            columns.push_back(Column(field.first, String(255)));
        } else {
            return {{"error", "不支援的字段類型: " + field.second + "。"}};
        }
    }

    // 創建表
    Table new_table(table_name, metadata, columns);

    // 使用引擎創建表
    metadata.create_all(db.engine);

    return {{"message", "資料表 '" + table_name + "' 已經建立。"}};
}
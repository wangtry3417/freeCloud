# 使用官方 Python 映像作為基礎映像
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY . .

# 開放應用的端口
EXPOSE 5000

# 啟動 Flask 應用
CMD ["python", "main.py"]

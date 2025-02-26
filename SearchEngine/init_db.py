# 数据库初始化
import sqlite3

# 创建或连接 SQLite 数据库
conn = sqlite3.connect('history.db')
cursor = conn.cursor()

# 用户表：包含用户名和密码、三个兴趣关键词
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    interest1 TEXT,
    interest2 TEXT,
    interest3 TEXT
)
''')

# 历史记录表： 包含用户ID、查询内容、时间戳
cursor.execute('''
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    query TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

conn.commit()
conn.close()
print("数据库初始化成功！")
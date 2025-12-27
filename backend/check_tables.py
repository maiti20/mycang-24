import sqlite3

conn = sqlite3.connect('fitness.db')
cursor = conn.cursor()

# 检查所有表
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('数据库中的表:', tables)

# 检查user表
if ('user',) in tables:
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    print('用户数据:', users)
else:
    print('user表不存在')

conn.close()
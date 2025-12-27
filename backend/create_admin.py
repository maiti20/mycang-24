#!/usr/bin/env python3
"""
简单管理员账号创建脚本
直接使用SQLite创建管理员用户，避免Flask依赖问题
"""

import sqlite3
import hashlib
import os
from datetime import datetime

def hash_password(password):
    """使用SHA256加密密码"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin_user():
    """创建管理员用户"""
    db_path = 'fitness.db'
    
    # 如果数据库不存在，先创建基本的用户表
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                age INTEGER,
                gender VARCHAR(10),
                height FLOAT,
                weight FLOAT,
                fitness_goal TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("数据库表创建完成！")
    
    # 连接数据库并创建管理员用户
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查管理员用户是否已存在
        cursor.execute("SELECT id FROM user WHERE username = ?", ('admin',))
        existing_admin = cursor.fetchone()
        
        if existing_admin:
            print("管理员用户已存在！")
        else:
            # 创建管理员用户
            admin_data = {
                'username': 'admin',
                'email': 'admin@fitness.com',
                'password_hash': hash_password('admin123'),
                'age': 30,
                'gender': 'male',
                'height': 175.0,
                'weight': 70.0,
                'fitness_goal': '保持健康'
            }
            
            cursor.execute('''
                INSERT INTO user (username, email, password_hash, age, gender, height, weight, fitness_goal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                admin_data['username'],
                admin_data['email'],
                admin_data['password_hash'],
                admin_data['age'],
                admin_data['gender'],
                admin_data['height'],
                admin_data['weight'],
                admin_data['fitness_goal']
            ))
            
            conn.commit()
            print("✅ 管理员用户创建成功！")
            print("   用户名: admin")
            print("   密码: admin123")
            print("   邮箱: admin@fitness.com")
        
        # 同时创建测试用户
        cursor.execute("SELECT id FROM user WHERE username = ?", ('testuser',))
        existing_test = cursor.fetchone()
        
        if not existing_test:
            test_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password_hash': hash_password('password123'),
                'age': 25,
                'gender': 'female',
                'height': 165.0,
                'weight': 55.0,
                'fitness_goal': '减脂塑形'
            }
            
            cursor.execute('''
                INSERT INTO user (username, email, password_hash, age, gender, height, weight, fitness_goal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                test_data['username'],
                test_data['email'],
                test_data['password_hash'],
                test_data['age'],
                test_data['gender'],
                test_data['height'],
                test_data['weight'],
                test_data['fitness_goal']
            ))
            
            conn.commit()
            print("✅ 测试用户创建成功！")
            print("   用户名: testuser")
            print("   密码: password123")
            print("   邮箱: test@example.com")
        
        # 显示所有用户
        print("\n当前系统用户列表：")
        cursor.execute("SELECT id, username, email, created_at FROM user ORDER BY id")
        users = cursor.fetchall()
        
        for user in users:
            print(f"ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 创建时间: {user[3]}")
            
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("正在创建管理员账号...")
    create_admin_user()
    print("\n管理员账号设置完成！")
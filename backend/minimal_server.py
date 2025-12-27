#!/usr/bin/env python3
"""
最简化API服务器
完全不依赖外部库，仅使用Python标准库
"""

import json
import sqlite3
import hashlib
import base64
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import hmac

# 配置
SECRET_KEY = 'your-secret-key-here-change-in-production'
DB_PATH = 'fitness.db'

def encode_base64(data):
    """Base64编码"""
    return base64.b64encode(data.encode()).decode()

def decode_base64(data):
    """Base64解码"""
    return base64.b64decode(data.encode()).decode()

def create_simple_token(user_id, username, expires_hours=1):
    """创建简单的token（非JWT，仅用于演示）"""
    exp_time = int(time.time()) + (expires_hours * 3600)
    payload = f"{user_id}:{username}:{exp_time}"
    signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token = f"{payload}:{signature}"
    return encode_base64(token)

def verify_simple_token(token):
    """验证简单token"""
    try:
        decoded = decode_base64(token)
        parts = decoded.split(':')
        if len(parts) != 4:
            return None
        
        user_id, username, exp_time, signature = parts
        
        # 验证签名
        payload = f"{user_id}:{username}:{exp_time}"
        expected_signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return None
        
        # 验证过期时间
        if int(exp_time) < time.time():
            return None
        
        return {'user_id': int(user_id), 'username': username}
    except:
        return None

class MinimalFitnessAPI(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    
    def _send_json(self, data, status_code=200):
        self._set_headers(status_code)
        response = json.dumps(data, ensure_ascii=False)
        self.wfile.write(response.encode('utf-8'))
    
    def _get_request_data(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        return json.loads(post_data.decode('utf-8'))
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == '/api/auth/login':
                self.handle_login()
            elif path == '/api/auth/register':
                self.handle_register()
            elif path == '/api/auth/refresh':
                self.handle_refresh()
            else:
                self._send_json({'success': False, 'message': 'API endpoint not found'}, 404)
        except Exception as e:
            self._send_json({'success': False, 'message': f'Server error: {str(e)}'}, 500)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == '/api/auth/me':
                self.handle_get_current_user()
            elif path == '/health':
                self._send_json({'status': 'ok', 'timestamp': datetime.now().isoformat()})
            else:
                self._send_json({'success': False, 'message': 'API endpoint not found'}, 404)
        except Exception as e:
            self._send_json({'success': False, 'message': f'Server error: {str(e)}'}, 500)
    
    def handle_login(self):
        data = self._get_request_data()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            self._send_json({'success': False, 'message': '用户名和密码不能为空'}, 400)
            return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            self._send_json({'success': False, 'message': '用户名或密码错误'}, 401)
            return
        
        stored_password_hash = user[3]  # password_hash字段
        input_password_hash = self._hash_password(password)
        
        if stored_password_hash != input_password_hash:
            conn.close()
            self._send_json({'success': False, 'message': '用户名或密码错误'}, 401)
            return
        
        # 构建用户数据
        user_data = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'age': user[4],
            'gender': user[5],
            'height': user[6],
            'weight': user[7],
            'fitness_goal': user[8],
            'created_at': user[9],
            'updated_at': user[10]
        }
        
        access_token = create_simple_token(user_data['id'], user_data['username'], 1)
        refresh_token = create_simple_token(user_data['id'], user_data['username'], 720)  # 30天
        
        conn.close()
        
        self._send_json({
            'success': True,
            'message': '登录成功',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user_data
            }
        })
    
    def handle_register(self):
        data = self._get_request_data()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            self._send_json({'success': False, 'message': '用户名、邮箱和密码不能为空'}, 400)
            return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            self._send_json({'success': False, 'message': '用户名已存在'}, 400)
            return
        
        # 检查邮箱是否已存在
        cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            self._send_json({'success': False, 'message': '邮箱已存在'}, 400)
            return
        
        # 创建新用户
        password_hash = self._hash_password(password)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO user (username, email, password_hash, age, gender, height, weight, fitness_goal, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username, email, password_hash,
            data.get('age'), data.get('gender'), data.get('height'), data.get('weight'), data.get('fitness_goal'),
            current_time, current_time
        ))
        
        user_id = cursor.lastrowid
        
        # 获取新创建的用户数据
        cursor.execute("SELECT * FROM user WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        user_data = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'age': user[4],
            'gender': user[5],
            'height': user[6],
            'weight': user[7],
            'fitness_goal': user[8],
            'created_at': user[9],
            'updated_at': user[10]
        }
        
        access_token = create_simple_token(user_data['id'], user_data['username'], 1)
        refresh_token = create_simple_token(user_data['id'], user_data['username'], 720)  # 30天
        
        conn.commit()
        conn.close()
        
        self._send_json({
            'success': True,
            'message': '注册成功',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user_data
            }
        })
    
    def handle_refresh(self):
        data = self._get_request_data()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            self._send_json({'success': False, 'message': 'Refresh token is required'}, 400)
            return
        
        payload = verify_simple_token(refresh_token)
        if not payload:
            self._send_json({'success': False, 'message': 'Invalid refresh token'}, 401)
            return
        
        # 生成新的access token
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM user WHERE id = ?", (payload['user_id'],))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            self._send_json({'success': False, 'message': 'User not found'}, 404)
            return
        
        user_data = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'age': user[4],
            'gender': user[5],
            'height': user[6],
            'weight': user[7],
            'fitness_goal': user[8],
            'created_at': user[9],
            'updated_at': user[10]
        }
        
        access_token = create_simple_token(user_data['id'], user_data['username'], 1)
        
        conn.close()
        
        self._send_json({
            'success': True,
            'data': {'access_token': access_token}
        })
    
    def handle_get_current_user(self):
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            self._send_json({'success': False, 'message': 'Authorization header required'}, 401)
            return
        
        token = auth_header.split(' ')[1]
        payload = verify_simple_token(token)
        
        if not payload:
            self._send_json({'success': False, 'message': 'Invalid token'}, 401)
            return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM user WHERE id = ?", (payload['user_id'],))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            self._send_json({'success': False, 'message': 'User not found'}, 404)
            return
        
        user_data = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'age': user[4],
            'gender': user[5],
            'height': user[6],
            'weight': user[7],
            'fitness_goal': user[8],
            'created_at': user[9],
            'updated_at': user[10]
        }
        
        conn.close()
        
        self._send_json({
            'success': True,
            'data': user_data
        })

def run_server():
    server_address = ('', 5000)
    httpd = HTTPServer(server_address, MinimalFitnessAPI)
    print("🚀 最简化健身系统API服务器启动成功！")
    print("📍 地址: http://localhost:5000")
    print("⏰ 启动时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("🔧 仅使用Python标准库，无外部依赖")
    print("=" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器正在关闭...")
        httpd.shutdown()

if __name__ == '__main__':
    run_server()
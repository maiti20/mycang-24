#!/usr/bin/env python3
"""
增强版API服务器 - 包含统计功能和AI集成
支持用户认证、饮食记录、运动库、AI方案和统计数据
"""

import json
import sqlite3
import hashlib
import time
import urllib.request
import urllib.error
import urllib.parse
import os
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 配置
DB_PATH = 'fitness.db'

# 阿里云千问大模型配置
DASHSCOPE_API_KEY = 'sk-7ce6bcc3895849ff9a669e3a825b4589'
AI_BASE_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
AI_MODEL = 'qwen-plus'  # 可选: qwen-turbo(快速), qwen-plus(均衡), qwen-max(最强)

class EnhancedAPI(BaseHTTPRequestHandler):
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

    def _get_current_user_id(self):
        """从Authorization头获取当前用户ID"""
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer token_'):
            try:
                return int(auth_header.split('_')[1])
            except:
                pass
        return None

    def _get_user_profile(self, user_id):
        """获取用户完整画像信息"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT username, email, age, gender, height, weight, fitness_goal, created_at
                FROM user WHERE id = ?
            ''', (user_id,))

            user = cursor.fetchone()
            conn.close()

            if user:
                # 计算BMI
                bmi = None
                bmi_category = None
                if user[4] and user[5]:  # height and weight
                    height_m = user[4] / 100
                    bmi = round(user[5] / (height_m * height_m), 1)
                    if bmi < 18.5:
                        bmi_category = "偏瘦"
                    elif bmi < 24:
                        bmi_category = "正常"
                    elif bmi < 28:
                        bmi_category = "偏胖"
                    else:
                        bmi_category = "肥胖"

                return {
                    'username': user[0],
                    'age': user[2],
                    'gender': '男性' if user[3] == 'male' else ('女性' if user[3] == 'female' else user[3]),
                    'height': user[4],
                    'weight': user[5],
                    'bmi': bmi,
                    'bmi_category': bmi_category,
                    'fitness_goal': user[6],
                    'member_since': user[7]
                }
            return {}
        except Exception as e:
            print(f"获取用户画像失败: {e}")
            return {}

    def _get_user_activity_stats(self, user_id):
        """获取用户最近活动统计，用于了解用户习惯"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # 获取最近30天的饮食统计
            cursor.execute('''
                SELECT
                    COUNT(*) as total_records,
                    COALESCE(AVG(dr.quantity * f.calories_per_unit), 0) as avg_calories_per_meal,
                    COALESCE(SUM(dr.quantity * f.calories_per_unit), 0) as total_calories,
                    COALESCE(AVG(dr.quantity * f.protein), 0) as avg_protein
                FROM diet_record dr
                JOIN food f ON dr.food_id = f.id
                WHERE dr.user_id = ? AND dr.record_date >= datetime('now', '-30 days')
            ''', (user_id,))
            diet_stats = cursor.fetchone()

            # 获取最近30天的运动统计
            cursor.execute('''
                SELECT
                    COUNT(*) as total_exercises,
                    COALESCE(AVG(el.duration_minutes), 0) as avg_duration,
                    COALESCE(SUM(el.duration_minutes), 0) as total_minutes,
                    COALESCE(AVG(el.calories_burned), 0) as avg_calories_burned
                FROM exercise_log el
                WHERE el.user_id = ? AND el.log_date >= datetime('now', '-30 days')
            ''', (user_id,))
            exercise_stats = cursor.fetchone()

            # 获取用户偏好的运动类型
            cursor.execute('''
                SELECT e.category, COUNT(*) as count
                FROM exercise_log el
                JOIN exercise e ON el.exercise_id = e.id
                WHERE el.user_id = ? AND el.log_date >= datetime('now', '-30 days')
                GROUP BY e.category
                ORDER BY count DESC
                LIMIT 3
            ''', (user_id,))
            preferred_exercises = [row[0] for row in cursor.fetchall()]

            # 获取用户常吃的食物类别
            cursor.execute('''
                SELECT f.category, COUNT(*) as count
                FROM diet_record dr
                JOIN food f ON dr.food_id = f.id
                WHERE dr.user_id = ? AND dr.record_date >= datetime('now', '-30 days')
                GROUP BY f.category
                ORDER BY count DESC
                LIMIT 3
            ''', (user_id,))
            preferred_foods = [row[0] for row in cursor.fetchall()]

            conn.close()

            return {
                'diet': {
                    'total_records': diet_stats[0] if diet_stats else 0,
                    'avg_calories_per_meal': round(diet_stats[1], 0) if diet_stats else 0,
                    'total_calories': round(diet_stats[2], 0) if diet_stats else 0,
                    'avg_protein': round(diet_stats[3], 1) if diet_stats else 0
                },
                'exercise': {
                    'total_exercises': exercise_stats[0] if exercise_stats else 0,
                    'avg_duration': round(exercise_stats[1], 0) if exercise_stats else 0,
                    'total_minutes': exercise_stats[2] if exercise_stats else 0,
                    'avg_calories_burned': round(exercise_stats[3], 0) if exercise_stats else 0
                },
                'preferred_exercises': preferred_exercises,
                'preferred_foods': preferred_foods
            }
        except Exception as e:
            print(f"获取用户活动统计失败: {e}")
            return {'diet': {}, 'exercise': {}, 'preferred_exercises': [], 'preferred_foods': []}
    
    def do_OPTIONS(self):
        self._set_headers()

    def serve_static_file(self, path):
        """提供静态文件服务"""
        try:
            # 安全检查，防止路径遍历攻击
            if '..' in path:
                self.send_error(403, 'Forbidden')
                return

            # 构建文件路径
            file_path = os.path.join(os.path.dirname(__file__), path.lstrip('/'))

            if not os.path.exists(file_path):
                self.send_error(404, 'File not found')
                return

            # 获取文件类型
            ext = os.path.splitext(file_path)[1].lower()
            content_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            content_type = content_types.get(ext, 'application/octet-stream')

            # 读取并返回文件
            with open(file_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(content))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'max-age=86400')  # 缓存1天
            self.end_headers()
            self.wfile.write(content)

        except Exception as e:
            self.send_error(500, str(e))

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        try:
            # 静态文件服务 - 头像等上传文件
            if path.startswith('/uploads/'):
                self.serve_static_file(path)
            elif path == '/api/auth/me':
                self.handle_get_current_user()
            elif path == '/api/stats/today':
                self.handle_today_stats()
            elif path == '/api/stats/week':
                self.handle_week_stats()
            elif path.startswith('/api/stats/recent-activities'):
                self.handle_recent_activities(parsed_path)
            elif path == '/api/stats/streak-days':
                self.handle_streak_days()
            elif path == '/api/stats/ai-plans-count':
                self.handle_ai_plans_count()
            elif path.startswith('/api/foods'):
                self.handle_get_foods(parsed_path)
            elif path.startswith('/api/diet-records'):
                self.handle_get_diet_records(parsed_path)
            elif path.startswith('/api/exercises'):
                self.handle_get_exercises(parsed_path)
            elif path.startswith('/api/exercise-logs'):
                self.handle_get_exercise_logs(parsed_path)
            elif path.startswith('/api/ai-plans'):
                self.handle_get_ai_plans(parsed_path)
            else:
                self._send_json({'success': False, 'message': 'API endpoint not found'}, 404)
        except Exception as e:
            self._send_json({'success': False, 'message': f'Server error: {str(e)}'}, 500)
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        try:
            if path == '/api/auth/login':
                self.handle_login()
            elif path == '/api/auth/register':
                self.handle_register()
            elif path == '/api/auth/upload-avatar':
                self.handle_upload_avatar()
            elif path == '/api/diet-records':
                self.handle_create_diet_record()
            elif path == '/api/exercise-logs':
                self.handle_create_exercise_log()
            elif path == '/api/ai-plans/generate':
                self.handle_generate_ai_plan()
            elif path.startswith('/api/ai-plans/delete'):
                # POST 方式删除: /api/ai-plans/delete/{id}
                plan_id = path.split('/')[-1]
                if plan_id == 'delete':
                    # 从查询参数获取ID
                    query_params = parse_qs(parsed_path.query)
                    plan_id = query_params.get('id', [None])[0]
                self.handle_delete_ai_plan_by_id(plan_id if plan_id else '')
            elif path.startswith('/api/ai-plans'):
                self.handle_get_ai_plans(parsed_path)
            else:
                self._send_json({'success': False, 'message': 'API endpoint not found'}, 404)
        except Exception as e:
            self._send_json({'success': False, 'message': f'Server error: {str(e)}'}, 500)

    def do_PUT(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        try:
            if path == '/api/auth/profile' or path == '/api/user/profile':
                self.handle_update_profile()
            else:
                self._send_json({'success': False, 'message': 'API endpoint not found'}, 404)
        except Exception as e:
            self._send_json({'success': False, 'message': f'Server error: {str(e)}'}, 500)

    def do_DELETE(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        try:
            # 删除AI方案: /api/ai-plans/{id}
            if path.startswith('/api/ai-plans/'):
                plan_id = path.split('/')[-1]
                self.handle_delete_ai_plan_by_id(plan_id)
            else:
                self._send_json({'success': False, 'message': 'API endpoint not found'}, 404)
        except Exception as e:
            self._send_json({'success': False, 'message': f'Server error: {str(e)}'}, 500)

    def handle_delete_ai_plan_by_id(self, plan_id):
        """通过ID删除AI方案"""
        try:
            user_id = self._get_current_user_id()
            if not user_id:
                self._send_json({'success': False, 'message': '未登录'}, 401)
                return

            if not plan_id or not plan_id.isdigit():
                self._send_json({
                    'success': False,
                    'message': '无效的方案ID'
                }, 400)
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # 只删除属于当前用户的方案
            cursor.execute('DELETE FROM ai_plan WHERE id = ? AND user_id = ?', (plan_id, user_id))
            affected_rows = cursor.rowcount

            conn.commit()
            conn.close()

            if affected_rows > 0:
                print(f"[AI] 方案已删除, ID: {plan_id}, 用户: {user_id}")
                self._send_json({
                    'success': True,
                    'message': '方案删除成功'
                })
            else:
                self._send_json({
                    'success': False,
                    'message': '方案不存在或无权删除'
                }, 404)

        except Exception as e:
            self._send_json({
                'success': False,
                'message': f'删除方案失败: {str(e)}'
            }, 500)

    def handle_update_profile(self):
        try:
            data = self._get_request_data()
            auth_header = self.headers.get('Authorization', '')
            user_id = 1
            if auth_header.startswith('Bearer token_'):
                try:
                    user_id = int(auth_header.split('_')[1])
                except:
                    pass

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            update_fields = []
            params = []

            if 'email' in data and data['email']:
                update_fields.append('email = ?')
                params.append(data['email'])
            if 'age' in data and data['age'] is not None:
                update_fields.append('age = ?')
                params.append(data['age'])
            if 'gender' in data and data['gender']:
                update_fields.append('gender = ?')
                params.append(data['gender'])
            if 'height' in data and data['height'] is not None:
                update_fields.append('height = ?')
                params.append(data['height'])
            if 'weight' in data and data['weight'] is not None:
                update_fields.append('weight = ?')
                params.append(data['weight'])
            if 'fitness_goal' in data and data['fitness_goal']:
                update_fields.append('fitness_goal = ?')
                params.append(data['fitness_goal'])

            if update_fields:
                update_fields.append('updated_at = ?')
                params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                params.append(user_id)
                query = f"UPDATE user SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, params)
                conn.commit()

            # 使用字典方式查询以获取正确的字段
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, email, age, gender, height, weight, fitness_goal, avatar, created_at, updated_at FROM user WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                user_data = {
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'age': row['age'],
                    'gender': row['gender'],
                    'height': row['height'],
                    'weight': row['weight'],
                    'fitness_goal': row['fitness_goal'],
                    'avatar': row['avatar'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                self._send_json({'success': True, 'message': '资料更新成功', 'data': user_data})
            else:
                self._send_json({'success': False, 'message': '用户不存在'}, 404)
        except Exception as e:
            self._send_json({'success': False, 'message': f'更新失败: {str(e)}'}, 500)

    def handle_get_current_user(self):
        """获取当前登录用户信息"""
        try:
            auth_header = self.headers.get('Authorization', '')
            user_id = 1
            if auth_header.startswith('Bearer token_'):
                try:
                    user_id = int(auth_header.split('_')[1])
                except:
                    pass

            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row  # 使用字典方式访问列
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, email, age, gender, height, weight, fitness_goal, avatar, created_at, updated_at FROM user WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                user_data = {
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'age': row['age'],
                    'gender': row['gender'],
                    'height': row['height'],
                    'weight': row['weight'],
                    'fitness_goal': row['fitness_goal'],
                    'avatar': row['avatar'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                self._send_json({'success': True, 'data': user_data})
            else:
                self._send_json({'success': False, 'message': '用户不存在'}, 404)
        except Exception as e:
            self._send_json({'success': False, 'message': f'获取用户信息失败: {str(e)}'}, 500)

    def handle_upload_avatar(self):
        """处理头像上传"""
        user_id = self._get_current_user_id()
        if not user_id:
            self._send_json({'success': False, 'message': '未登录'}, 401)
            return

        try:
            import base64
            data = self._get_request_data()
            avatar_base64 = data.get('avatar')

            if not avatar_base64:
                self._send_json({'success': False, 'message': '未提供头像数据'}, 400)
                return

            # 创建 uploads 目录
            upload_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'avatars')
            os.makedirs(upload_dir, exist_ok=True)

            # 解析 base64 数据
            if ',' in avatar_base64:
                header, avatar_base64 = avatar_base64.split(',', 1)
                # 获取文件扩展名
                if 'png' in header:
                    ext = 'png'
                elif 'gif' in header:
                    ext = 'gif'
                else:
                    ext = 'jpg'
            else:
                ext = 'jpg'

            # 生成文件名
            filename = f'avatar_{user_id}_{int(time.time())}.{ext}'
            filepath = os.path.join(upload_dir, filename)

            # 保存文件
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(avatar_base64))

            # 更新数据库中的头像路径
            avatar_url = f'/uploads/avatars/{filename}'
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('UPDATE user SET avatar = ?, updated_at = ? WHERE id = ?',
                         (avatar_url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))
            conn.commit()
            conn.close()

            self._send_json({
                'success': True,
                'message': '头像上传成功',
                'data': {'avatar': avatar_url}
            })

        except Exception as e:
            self._send_json({'success': False, 'message': f'上传失败: {str(e)}'}, 500)

    def handle_login(self):
        data = self._get_request_data()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            self._send_json({'success': False, 'message': '用户名和密码不能为空'}, 400)
            return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            self._send_json({'success': False, 'message': '用户名或密码错误'}, 401)
            return
        
        stored_password_hash = user[3]
        input_password_hash = self._hash_password(password)

        if stored_password_hash != input_password_hash:
            conn.close()
            self._send_json({'success': False, 'message': '用户名或密码错误'}, 401)
            return

        # 使用字典方式重新查询以获取正确的字段
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, age, gender, height, weight, fitness_goal, avatar, created_at, updated_at FROM user WHERE id = ?', (user[0],))
        row = cursor.fetchone()

        user_data = {
            'id': row['id'],
            'username': row['username'],
            'email': row['email'],
            'age': row['age'],
            'gender': row['gender'],
            'height': row['height'],
            'weight': row['weight'],
            'fitness_goal': row['fitness_goal'],
            'avatar': row['avatar'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
        
        # 简单token
        access_token = f'token_{user_data["id"]}_{int(time.time())}'
        refresh_token = f'refresh_{user_data["id"]}_{int(time.time())}'
        
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
        
        cursor.execute('SELECT id FROM user WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            self._send_json({'success': False, 'message': '用户名已存在'}, 400)
            return
        
        cursor.execute('SELECT id FROM user WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            self._send_json({'success': False, 'message': '邮箱已存在'}, 400)
            return
        
        password_hash = self._hash_password(password)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO user (username, email, password_hash, age, gender, height, weight, fitness_goal, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, data.get('age'), data.get('gender'), 
              data.get('height'), data.get('weight'), data.get('fitness_goal'), current_time, current_time))
        
        user_id = cursor.lastrowid

        # 使用字典方式查询以获取正确的字段
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, age, gender, height, weight, fitness_goal, avatar, created_at, updated_at FROM user WHERE id = ?', (user_id,))
        row = cursor.fetchone()

        user_data = {
            'id': row['id'],
            'username': row['username'],
            'email': row['email'],
            'age': row['age'],
            'gender': row['gender'],
            'height': row['height'],
            'weight': row['weight'],
            'fitness_goal': row['fitness_goal'],
            'avatar': row['avatar'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
        
        access_token = f'token_{user_data["id"]}_{int(time.time())}'
        refresh_token = f'refresh_{user_data["id"]}_{int(time.time())}'
        
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
    
    def handle_today_stats(self):
        """获取今日统计数据"""
        user_id = self._get_current_user_id()
        if not user_id:
            self._send_json({'success': False, 'message': '未登录'}, 401)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        today = datetime.now().strftime('%Y-%m-%d')

        # 今日饮食统计 - 按用户过滤
        cursor.execute('''
            SELECT COALESCE(SUM(dr.quantity * f.calories_per_unit), 0) as calories,
                   COALESCE(SUM(dr.quantity * f.protein), 0) as protein,
                   COALESCE(SUM(dr.quantity * f.carbs), 0) as carbs,
                   COALESCE(SUM(dr.quantity * f.fat), 0) as fat
            FROM diet_record dr
            JOIN food f ON dr.food_id = f.id
            WHERE DATE(dr.record_date) = ? AND dr.user_id = ?
        ''', (today, user_id))

        diet_stats = cursor.fetchone()

        # 今日运动统计 - 按用户过滤
        cursor.execute('''
            SELECT COUNT(*) as exercise_count,
                   COALESCE(SUM(el.duration_minutes), 0) as total_minutes,
                   COALESCE(SUM(el.duration_minutes * e.calories_per_minute), 0) as calories_burned
            FROM exercise_log el
            JOIN exercise e ON el.exercise_id = e.id
            WHERE DATE(el.log_date) = ? AND el.user_id = ?
        ''', (today, user_id))

        exercise_stats = cursor.fetchone()

        conn.close()

        stats = {
            'calories': diet_stats[0] or 0,
            'protein': diet_stats[1] or 0,
            'carbs': diet_stats[2] or 0,
            'fat': diet_stats[3] or 0,
            'exercises': exercise_stats[0] or 0,
            'total_minutes': exercise_stats[1] or 0,
            'calories_burned': exercise_stats[2] or 0
        }

        self._send_json({
            'success': True,
            'data': stats
        })
    
    def handle_week_stats(self):
        """获取本周统计数据"""
        user_id = self._get_current_user_id()
        if not user_id:
            self._send_json({'success': False, 'message': '未登录'}, 401)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 本周起始日期（周一）和结束日期（下周一）
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start_str = week_start.strftime('%Y-%m-%d')
        week_end = week_start + timedelta(days=7)
        week_end_str = week_end.strftime('%Y-%m-%d')

        # 本周饮食统计 - 按用户过滤
        cursor.execute('''
            SELECT COALESCE(SUM(dr.quantity * f.calories_per_unit), 0) as calories,
                   COUNT(DISTINCT DATE(dr.record_date)) as diet_days
            FROM diet_record dr
            JOIN food f ON dr.food_id = f.id
            WHERE DATE(dr.record_date) >= ? AND DATE(dr.record_date) < ? AND dr.user_id = ?
        ''', (week_start_str, week_end_str, user_id))

        diet_stats = cursor.fetchone()

        # 本周运动统计 - 按用户过滤，使用明确的日期范围
        cursor.execute('''
            SELECT COUNT(*) as exercise_count,
                   COUNT(DISTINCT DATE(el.log_date)) as exercise_days,
                   COALESCE(SUM(el.duration_minutes), 0) as total_minutes,
                   COALESCE(SUM(el.calories_burned), 0) as calories_burned
            FROM exercise_log el
            WHERE DATE(el.log_date) >= ? AND DATE(el.log_date) < ? AND el.user_id = ?
        ''', (week_start_str, week_end_str, user_id))

        exercise_stats = cursor.fetchone()

        conn.close()

        stats = {
            'calories': diet_stats[0] or 0,
            'diet_days': diet_stats[1] or 0,
            'exercises': exercise_stats[0] or 0,
            'exercise_days': exercise_stats[1] or 0,
            'total_minutes': exercise_stats[2] or 0,
            'calories_burned': exercise_stats[3] or 0
        }

        self._send_json({
            'success': True,
            'data': stats
        })
    
    def handle_recent_activities(self, parsed_path):
        """获取最近活动记录"""
        user_id = self._get_current_user_id()
        if not user_id:
            self._send_json({'success': False, 'message': '未登录'}, 401)
            return

        query_params = parse_qs(parsed_path.query)
        limit = int(query_params.get('limit', [10])[0])

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        activities = []

        # 获取最近的饮食记录 - 按用户过滤
        cursor.execute('''
            SELECT 'diet' as type, dr.record_date, dr.meal_type, f.name, dr.quantity * f.calories_per_unit as calories
            FROM diet_record dr
            JOIN food f ON dr.food_id = f.id
            WHERE dr.user_id = ?
            ORDER BY dr.record_date DESC
            LIMIT ?
        ''', (user_id, limit))

        diet_records = cursor.fetchall()
        for record in diet_records:
            activities.append({
                'type': 'diet',
                'title': f'{record[3]} ({record[2]})',
                'description': f'摄入 {record[4]:.0f} 卡路里',
                'time': self._format_datetime(record[1]),
                'timestamp': record[1]
            })

        # 获取最近的运动记录 - 按用户过滤
        cursor.execute('''
            SELECT 'exercise' as type, el.log_date, e.name, el.duration_minutes, el.duration_minutes * e.calories_per_minute as calories
            FROM exercise_log el
            JOIN exercise e ON el.exercise_id = e.id
            WHERE el.user_id = ?
            ORDER BY el.log_date DESC
            LIMIT ?
        ''', (user_id, limit))

        exercise_records = cursor.fetchall()
        for record in exercise_records:
            activities.append({
                'type': 'exercise',
                'title': record[2],
                'description': f'运动 {record[3]} 分钟，消耗 {record[4]:.0f} 卡路里',
                'time': self._format_datetime(record[1]),
                'timestamp': record[1]
            })

        conn.close()

        # 按时间排序并限制数量
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        activities = activities[:limit]

        self._send_json({
            'success': True,
            'data': activities
        })

    def handle_streak_days(self):
        """获取连续打卡天数"""
        user_id = self._get_current_user_id()
        if not user_id:
            self._send_json({'success': False, 'message': '未登录'}, 401)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 获取有活动的日期 - 按用户过滤
        cursor.execute('''
            SELECT DISTINCT DATE(record_date) as date FROM diet_record WHERE user_id = ?
            UNION
            SELECT DISTINCT DATE(log_date) as date FROM exercise_log WHERE user_id = ?
            ORDER BY date DESC
        ''', (user_id, user_id))

        dates = [row[0] for row in cursor.fetchall()]
        conn.close()

        if not dates:
            streak = 0
        else:
            streak = self._calculate_streak(dates)

        self._send_json({
            'success': True,
            'data': {'streak_days': streak}
        })

    def handle_ai_plans_count(self):
        """获取AI方案数量"""
        user_id = self._get_current_user_id()
        if not user_id:
            self._send_json({'success': False, 'message': '未登录'}, 401)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 按用户过滤
        cursor.execute('SELECT COUNT(*) FROM ai_plan WHERE user_id = ?', (user_id,))
        count = cursor.fetchone()[0]

        conn.close()

        self._send_json({
            'success': True,
            'data': {'count': count}
        })
    
    def handle_get_foods(self, parsed_path):
        """获取食物列表"""
        query_params = parse_qs(parsed_path.query)
        search = query_params.get('search', [''])[0]
        category = query_params.get('category', [''])[0]
        page = int(query_params.get('page', ['1'])[0])
        limit = int(query_params.get('limit', ['20'])[0])
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append('(name LIKE ? OR category LIKE ?)')
            params.extend([f'%{search}%', f'%{search}%'])
        
        if category:
            where_conditions.append('category = ?')
            params.append(category)
        
        where_clause = 'WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
        
        # 获取总数
        count_query = f'SELECT COUNT(*) FROM food {where_clause}'
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # 分页查询
        offset = (page - 1) * limit
        query = f'''
            SELECT id, name, category, calories_per_unit, protein, carbs, fat, fiber, sugar, sodium, unit
            FROM food {where_clause}
            ORDER BY name ASC
            LIMIT ? OFFSET ?
        '''
        cursor.execute(query, params + [limit, offset])
        foods = cursor.fetchall()
        
        conn.close()
        
        # 格式化结果
        food_list = []
        for food in foods:
            food_list.append({
                'id': food[0],
                'name': food[1],
                'category': food[2],
                'calories_per_unit': food[3],
                'protein': food[4],
                'carbs': food[5],
                'fat': food[6],
                'fiber': food[7],
                'sugar': food[8],
                'sodium': food[9],
                'unit': food[10]
            })
        
        self._send_json({
            'success': True,
            'data': {
                'foods': food_list,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count,
                    'pages': (total_count + limit - 1) // limit
                }
            }
        })
    
    def handle_get_diet_records(self, parsed_path):
        """获取饮食记录"""
        user_id = self._get_current_user_id()
        if not user_id:
            self._send_json({'success': False, 'message': '未登录'}, 401)
            return

        query_params = parse_qs(parsed_path.query)
        date_from = query_params.get('date_from', [''])[0]
        date_to = query_params.get('date_to', [''])[0]
        page = int(query_params.get('page', ['1'])[0])
        limit = int(query_params.get('limit', ['20'])[0])

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 构建查询条件 - 使用当前登录用户
        where_conditions = ['user_id = ?']
        params = [user_id]
        
        if date_from:
            where_conditions.append('DATE(dr.record_date) >= ?')
            params.append(date_from)
        
        if date_to:
            where_conditions.append('DATE(dr.record_date) <= ?')
            params.append(date_to)
        
        where_clause = 'WHERE ' + ' AND '.join(where_conditions)
        
        # 获取总数
        count_query = f'SELECT COUNT(*) FROM diet_record dr {where_clause}'
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # 分页查询
        offset = (page - 1) * limit
        query = f'''
            SELECT dr.id, dr.food_id, dr.quantity, dr.meal_type, dr.record_date, dr.notes,
                   f.name, f.category, f.calories_per_unit, f.protein, f.carbs, f.fat, f.unit
            FROM diet_record dr
            JOIN food f ON dr.food_id = f.id
            {where_clause}
            ORDER BY dr.record_date DESC
            LIMIT ? OFFSET ?
        '''
        cursor.execute(query, params + [limit, offset])
        records = cursor.fetchall()
        
        conn.close()
        
        # 格式化结果
        record_list = []
        for record in records:
            # 计算营养成分
            multiplier = record[2]  # quantity
            record_list.append({
                'id': record[0],
                'food_id': record[1],
                'quantity': record[2],
                'meal_type': record[3],
                'record_date': record[4],
                'notes': record[5],
                'food': {
                    'name': record[6],
                    'category': record[7],
                    'calories_per_unit': record[8],
                    'protein': record[9],
                    'carbs': record[10],
                    'fat': record[11],
                    'unit': record[12]
                },
                'nutrition': {
                    'calories': record[8] * multiplier,
                    'protein': record[9] * multiplier,
                    'carbs': record[10] * multiplier,
                    'fat': record[11] * multiplier
                }
            })
        
        self._send_json({
            'success': True,
            'data': {
                'records': record_list,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count,
                    'pages': (total_count + limit - 1) // limit
                }
            }
        })
    
    def handle_create_diet_record(self):
        """创建饮食记录"""
        user_id = self._get_current_user_id()
        if not user_id:
            self._send_json({'success': False, 'message': '未登录'}, 401)
            return

        data = self._get_request_data()
        food_id = data.get('food_id')
        quantity = data.get('quantity')
        meal_type = data.get('meal_type')
        notes = data.get('notes', '')
        
        if not food_id or not quantity or not meal_type:
            self._send_json({'success': False, 'message': '食物ID、数量和餐次类型不能为空'}, 400)
            return
        
        try:
            quantity = float(quantity)
        except ValueError:
            self._send_json({'success': False, 'message': '数量必须是数字'}, 400)
            return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 验证食物是否存在
        cursor.execute('SELECT id FROM food WHERE id = ?', (food_id,))
        if not cursor.fetchone():
            conn.close()
            self._send_json({'success': False, 'message': '指定的食物不存在'}, 400)
            return
        
        # 插入饮食记录
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO diet_record (user_id, food_id, quantity, meal_type, record_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, food_id, quantity, meal_type, current_time, notes))
        
        record_id = cursor.lastrowid
        
        # 获取完整的记录信息
        cursor.execute('''
            SELECT dr.id, dr.food_id, dr.quantity, dr.meal_type, dr.record_date, dr.notes,
                   f.name, f.category, f.calories_per_unit, f.protein, f.carbs, f.fat, f.unit
            FROM diet_record dr
            JOIN food f ON dr.food_id = f.id
            WHERE dr.id = ?
        ''', (record_id,))
        
        record = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        if record:
            multiplier = record[2]
            result = {
                'id': record[0],
                'food_id': record[1],
                'quantity': record[2],
                'meal_type': record[3],
                'record_date': record[4],
                'notes': record[5],
                'food': {
                    'name': record[6],
                    'category': record[7],
                    'calories_per_unit': record[8],
                    'protein': record[9],
                    'carbs': record[10],
                    'fat': record[11],
                    'unit': record[12]
                },
                'nutrition': {
                    'calories': record[8] * multiplier,
                    'protein': record[9] * multiplier,
                    'carbs': record[10] * multiplier,
                    'fat': record[11] * multiplier
                }
            }
            
            self._send_json({
                'success': True,
                'message': '饮食记录添加成功',
                'data': result
            })
        else:
            self._send_json({'success': False, 'message': '记录创建失败'}, 500)
    
    def handle_get_exercises(self, parsed_path):
        """获取运动列表"""
        query_params = parse_qs(parsed_path.query)
        search = query_params.get('search', [''])[0]
        category = query_params.get('category', [''])[0]
        difficulty = query_params.get('difficulty', [''])[0]
        page = int(query_params.get('page', ['1'])[0])
        limit = int(query_params.get('limit', ['20'])[0])
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append('(name LIKE ? OR description LIKE ? OR category LIKE ?)')
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
        
        if category:
            where_conditions.append('category = ?')
            params.append(category)
        
        if difficulty:
            where_conditions.append('difficulty_level = ?')
            params.append(difficulty)
        
        where_clause = 'WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
        
        # 获取总数
        count_query = f'SELECT COUNT(*) FROM exercise {where_clause}'
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # 分页查询
        offset = (page - 1) * limit
        query = f'''
            SELECT id, name, category, description, difficulty_level, calories_per_minute,
                   muscle_groups, equipment_needed, tutorial_url, image_url
            FROM exercise {where_clause}
            ORDER BY name ASC
            LIMIT ? OFFSET ?
        '''
        cursor.execute(query, params + [limit, offset])
        exercises = cursor.fetchall()
        
        conn.close()
        
        # 格式化结果
        exercise_list = []
        for exercise in exercises:
            exercise_list.append({
                'id': exercise[0],
                'name': exercise[1],
                'category': exercise[2],
                'description': exercise[3],
                'difficulty_level': exercise[4],
                'calories_per_minute': exercise[5],
                'muscle_groups': exercise[6].split(',') if exercise[6] else [],
                'equipment_needed': exercise[7].split(',') if exercise[7] else [],
                'tutorial_url': exercise[8],
                'image_url': exercise[9]
            })
        
        self._send_json({
            'success': True,
            'data': {
                'exercises': exercise_list,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count,
                    'pages': (total_count + limit - 1) // limit
                }
            }
        })
    
    def handle_get_exercise_logs(self, parsed_path):
        """获取运动记录"""
        user_id = self._get_current_user_id()
        if not user_id:
            self._send_json({'success': False, 'message': '未登录'}, 401)
            return

        query_params = parse_qs(parsed_path.query)
        date_from = query_params.get('date_from', [''])[0]
        date_to = query_params.get('date_to', [''])[0]
        page = int(query_params.get('page', ['1'])[0])
        limit = int(query_params.get('limit', ['20'])[0])

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 构建查询条件 - 使用当前登录用户，添加表别名
        where_conditions = ['el.user_id = ?']
        params = [user_id]

        if date_from:
            where_conditions.append('DATE(el.log_date) >= ?')
            params.append(date_from)

        if date_to:
            where_conditions.append('DATE(el.log_date) <= ?')
            params.append(date_to)

        where_clause = 'WHERE ' + ' AND '.join(where_conditions)

        # 获取总数
        count_query = f'SELECT COUNT(*) FROM exercise_log el {where_clause}'
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]

        # 分页查询 - 使用 LEFT JOIN 确保即使运动被删除也能显示记录
        offset = (page - 1) * limit
        query = f'''
            SELECT el.id, el.exercise_id, el.duration_minutes, el.intensity_level, el.log_date, el.notes, el.calories_burned,
                   COALESCE(e.name, '未知运动'), COALESCE(e.category, '未知'), COALESCE(e.difficulty_level, '中级'),
                   COALESCE(e.calories_per_minute, 5), COALESCE(e.muscle_groups, '')
            FROM exercise_log el
            LEFT JOIN exercise e ON el.exercise_id = e.id
            {where_clause}
            ORDER BY el.log_date DESC
            LIMIT ? OFFSET ?
        '''
        cursor.execute(query, params + [limit, offset])
        logs = cursor.fetchall()

        conn.close()
        
        # 格式化结果
        log_list = []
        for log in logs:
            # 计算消耗卡路里（如果数据库中没有存储的话）
            calories_burned = log[6] if log[6] is not None else log[2] * log[10]
            
            log_list.append({
                'id': log[0],
                'exercise_id': log[1],
                'duration_minutes': log[2],
                'intensity_level': log[3],
                'log_date': log[4],
                'notes': log[5],
                'calories_burned': calories_burned,
                'exercise': {
                    'name': log[7],
                    'category': log[8],
                    'difficulty_level': log[9],
                    'calories_per_minute': log[10],
                    'muscle_groups': log[11].split(',') if log[11] else []
                }
            })
        
        self._send_json({
            'success': True,
            'data': {
                'logs': log_list,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count,
                    'pages': (total_count + limit - 1) // limit
                }
            }
        })
    
    def handle_create_exercise_log(self):
        """创建运动记录"""
        user_id = self._get_current_user_id()
        if not user_id:
            self._send_json({'success': False, 'message': '未登录'}, 401)
            return

        data = self._get_request_data()
        exercise_id = data.get('exercise_id')
        duration_minutes = data.get('duration_minutes')
        intensity_level = data.get('intensity_level', '中等')
        notes = data.get('notes', '')
        
        if not exercise_id or not duration_minutes:
            self._send_json({'success': False, 'message': '运动ID和持续时间不能为空'}, 400)
            return
        
        try:
            duration_minutes = int(duration_minutes)
        except ValueError:
            self._send_json({'success': False, 'message': '持续时间必须是整数'}, 400)
            return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 验证运动是否存在并获取卡路里消耗率
        cursor.execute('SELECT id, calories_per_minute FROM exercise WHERE id = ?', (exercise_id,))
        exercise = cursor.fetchone()
        
        if not exercise:
            conn.close()
            self._send_json({'success': False, 'message': '指定的运动不存在'}, 400)
            return
        
        # 计算消耗的卡路里
        calories_per_minute = exercise[1]
        intensity_multiplier = {
            '低': 0.8,
            '中等': 1.0,
            '高': 1.3
        }.get(intensity_level, 1.0)
        
        calories_burned = duration_minutes * calories_per_minute * intensity_multiplier
        
        # 插入运动记录
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO exercise_log (user_id, exercise_id, duration_minutes, intensity_level, log_date, notes, calories_burned)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, exercise_id, duration_minutes, intensity_level, current_time, notes, calories_burned))
        
        log_id = cursor.lastrowid
        
        # 获取完整的记录信息
        cursor.execute('''
            SELECT el.id, el.exercise_id, el.duration_minutes, el.intensity_level, el.log_date, el.notes, el.calories_burned,
                   e.name, e.category, e.difficulty_level, e.calories_per_minute, e.muscle_groups
            FROM exercise_log el
            JOIN exercise e ON el.exercise_id = e.id
            WHERE el.id = ?
        ''', (log_id,))
        
        log = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        if log:
            result = {
                'id': log[0],
                'exercise_id': log[1],
                'duration_minutes': log[2],
                'intensity_level': log[3],
                'log_date': log[4],
                'notes': log[5],
                'calories_burned': log[6],
                'exercise': {
                    'name': log[7],
                    'category': log[8],
                    'difficulty_level': log[9],
                    'calories_per_minute': log[10],
                    'muscle_groups': log[11].split(',') if log[11] else []
                }
            }
            
            self._send_json({
                'success': True,
                'message': '运动记录添加成功',
                'data': result
            })
        else:
            self._send_json({'success': False, 'message': '记录创建失败'}, 500)
    
    def _format_datetime(self, dt_str):
        """格式化日期时间"""
        try:
            dt = datetime.fromisoformat(dt_str)
            now = datetime.now()
            
            if dt.date() == now.date():
                return f'今天 {dt.strftime("%H:%M")}'
            elif dt.date() == (now - timedelta(days=1)).date():
                return f'昨天 {dt.strftime("%H:%M")}'
            else:
                return dt.strftime("%m-%d %H:%M")
        except:
            return dt_str
    
    def _calculate_streak(self, dates):
        """计算连续打卡天数"""
        if not dates:
            return 0
        
        streak = 0
        current_date = datetime.now().date()
        
        i = 0
        while i < len(dates):
            date_obj = datetime.strptime(dates[i], '%Y-%m-%d').date()
            
            if date_obj == current_date - timedelta(days=i):
                streak += 1
                i += 1
            else:
                break
        
        return streak
    
    def handle_generate_ai_plan(self):
        """生成AI健身方案"""
        try:
            user_id = self._get_current_user_id()
            if not user_id:
                self._send_json({'success': False, 'message': '未登录'}, 401)
                return

            data = self._get_request_data()

            # 获取用户输入参数
            fitness_goal = data.get('fitness_goal', '通用健身')
            experience_level = data.get('experience_level', '初学者')
            weekly_frequency = data.get('weekly_frequency', '3-4天')
            session_duration = data.get('session_duration', '30-60分钟')
            health_condition = data.get('health_condition', '良好')
            special_requirements = data.get('special_requirements', '')

            # 获取用户画像数据
            user_profile = self._get_user_profile(user_id)
            user_stats = self._get_user_activity_stats(user_id)

            print(f"[AI] 开始生成方案: 目标={fitness_goal}, 级别={experience_level}, 频率={weekly_frequency}")
            print(f"[AI] 用户画像: {user_profile}")
            print(f"[AI] 用户活动统计: {user_stats}")

            # 生成AI方案（传入用户画像）
            ai_plan = self.generate_ai_fitness_plan(
                fitness_goal, experience_level, weekly_frequency,
                session_duration, health_condition, user_id,
                user_profile, user_stats, special_requirements
            )

            # 打印方案内容用于调试
            print(f"[AI] 生成的方案: title={ai_plan.get('title')}")
            print(f"[AI] weekly_schedule keys: {list(ai_plan.get('weekly_schedule', {}).keys())}")
            print(f"[AI] tips count: {len(ai_plan.get('tips', []))}")

            # 保存到数据库
            plan_id = self.save_ai_plan_to_db(user_id, ai_plan)

            if plan_id:
                ai_plan['id'] = plan_id
                ai_plan['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self._send_json({
                    'success': True,
                    'message': 'AI健身方案生成成功',
                    'data': ai_plan
                })
            else:
                self._send_json({
                    'success': False,
                    'message': '方案保存失败'
                }, 500)

        except Exception as e:
            print(f"[AI] 生成方案失败: {e}")
            import traceback
            traceback.print_exc()
            self._send_json({
                'success': False,
                'message': f'生成方案失败: {str(e)}'
            }, 500)
    
    def handle_get_ai_plans(self, parsed_path):
        """获取AI方案列表"""
        try:
            user_id = self._get_current_user_id()
            if not user_id:
                self._send_json({'success': False, 'message': '未登录'}, 401)
                return

            query_params = parse_qs(parsed_path.query)
            page = int(query_params.get('page', ['1'])[0])
            limit = int(query_params.get('limit', ['10'])[0])

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # 获取总数
            cursor.execute('SELECT COUNT(*) FROM ai_plan WHERE user_id = ?', (user_id,))
            total_count = cursor.fetchone()[0]

            # 分页查询
            offset = (page - 1) * limit
            cursor.execute('''
                SELECT id, plan_name, plan_type, goals, recommendations, schedule_info, nutrition_advice, created_at
                FROM ai_plan
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (user_id, limit, offset))

            plans = cursor.fetchall()
            conn.close()

            # 格式化结果
            plan_list = []
            for plan in plans:
                # 正确解析字段:
                # plan[4] = recommendations = tips
                # plan[5] = schedule_info = weekly_schedule
                try:
                    tips = json.loads(plan[4]) if plan[4] else []
                except:
                    tips = []

                try:
                    weekly_schedule = json.loads(plan[5]) if plan[5] else {}
                except:
                    weekly_schedule = {}

                plan_list.append({
                    'id': plan[0],
                    'title': plan[1],
                    'description': plan[3],
                    'plan_type': plan[2],
                    'weekly_schedule': weekly_schedule,
                    'tips': tips,
                    'nutrition_advice': plan[6],
                    'created_at': plan[7]
                })

            self._send_json({
                'success': True,
                'data': {
                    'plans': plan_list,
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total': total_count,
                        'pages': (total_count + limit - 1) // limit
                    }
                }
            })

        except Exception as e:
            self._send_json({
                'success': False,
                'message': f'获取方案列表失败: {str(e)}'
            }, 500)
    
    def handle_delete_ai_plan(self, parsed_path):
        """删除AI方案"""
        try:
            query_params = parse_qs(parsed_path.query)
            plan_id = query_params.get('id', [None])[0]
            
            if not plan_id:
                self._send_json({
                    'success': False,
                    'message': '方案ID不能为空'
                }, 400)
                return
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM ai_plan WHERE id = ?', (plan_id,))
            affected_rows = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if affected_rows > 0:
                self._send_json({
                    'success': True,
                    'message': '方案删除成功'
                })
            else:
                self._send_json({
                    'success': False,
                    'message': '方案不存在'
                }, 404)
                
        except Exception as e:
            self._send_json({
                'success': False,
                'message': f'删除方案失败: {str(e)}'
            }, 500)
    
    def generate_ai_fitness_plan(self, fitness_goal, experience_level, weekly_frequency, session_duration, health_condition, user_id, user_profile=None, user_stats=None, special_requirements=''):
        """生成AI健身方案 - 基于用户画像的个性化方案"""
        try:
            # 构建用户画像描述
            profile_desc = self._build_user_profile_description(user_profile, user_stats)

            # 根据不同健身目标构建专门的指导策略
            goal_strategy = self._get_goal_specific_strategy(fitness_goal)

            # 构建优化的AI提示词
            system_prompt = f"""你是一位拥有10年经验的专业健身教练和注册营养师。你需要根据用户的具体情况，制定科学、安全、可执行的个性化健身方案。

【核心原则】
你必须严格按照用户选择的健身目标"{fitness_goal}"来设计方案，不能偏离目标。

{goal_strategy}

【输出格式要求】
你的回答必须严格遵循以下JSON格式，不要添加任何额外说明文字：
```json
{{
    "title": "方案标题（必须体现{fitness_goal}目标，如：{fitness_goal}专项计划）",
    "description": "方案整体描述（80-120字，说明为什么这个方案适合用户，预期效果和科学依据）",
    "weekly_schedule": {{
        "周一": {{
            "type": "训练类型（必须符合{fitness_goal}目标）",
            "activities": ["具体动作1 3组x12次", "具体动作2 4组x10次"],
            "duration": 训练时长数字,
            "intensity": "低/中/高",
            "notes": "训练要点和注意事项"
        }},
        "周二": {{ ... }},
        "周三": {{ ... }},
        ...根据用户选择的训练频率安排
    }},
    "nutrition_advice": "针对{fitness_goal}目标的详细营养建议，包括：每日热量目标、三大营养素比例（蛋白质/碳水/脂肪）、餐次安排、推荐食物清单、禁忌食物",
    "tips": ["针对{fitness_goal}的注意事项1", "注意事项2", "注意事项3", "注意事项4", "注意事项5"]
}}
```

【严格要求】
1. 所有训练动作必须服务于"{fitness_goal}"目标
2. 训练强度必须匹配"{experience_level}"水平
3. 训练频率必须符合"{weekly_frequency}"的要求
4. 每次训练时长控制在"{session_duration}"范围内
5. 考虑用户健康状况"{health_condition}"进行安全调整
6. 动作描述要具体，包含组数、次数或时长
7. 营养建议必须与{fitness_goal}目标高度匹配
8. 确保JSON格式正确可解析"""

            user_prompt = f"""请为我制定一个专业的个性化健身方案。

【我的个人资料】
{profile_desc}

【我的训练需求】
- 健身目标：{fitness_goal}（请严格按照这个目标设计所有内容！）
- 运动经验：{experience_level}
- 每周可训练天数：{weekly_frequency}
- 每次训练时长：{session_duration}
- 身体状况：{health_condition}
{f'- 特殊需求：{special_requirements}' if special_requirements else ''}

【重要提醒】
1. 我选择的目标是"{fitness_goal}"，请确保所有训练安排和营养建议都围绕这个目标
2. 请根据我的BMI和身体状况给出针对性建议
3. 如果我有运动历史记录，请参考我的偏好进行安排

请设计一套科学、完整的周训练计划，并给出详细的营养建议。只返回JSON格式数据。"""

            # 调用AI API
            ai_response = self.call_openai_api(system_prompt, user_prompt)

            # 解析AI响应
            structured_plan = self.parse_ai_response(ai_response, fitness_goal, experience_level)

            # 添加用户画像信息到方案中（供前端显示）
            if user_profile:
                structured_plan['user_profile_summary'] = {
                    'bmi': user_profile.get('bmi'),
                    'bmi_category': user_profile.get('bmi_category'),
                    'target_goal': fitness_goal
                }

            return structured_plan

        except Exception as e:
            print(f"AI方案生成失败: {e}")
            return self.get_default_fitness_plan(fitness_goal, experience_level)

    def _build_user_profile_description(self, user_profile, user_stats):
        """构建用户画像描述文本"""
        if not user_profile:
            return "（用户资料不完整，请根据通用情况制定方案）"

        desc_parts = []

        # 基本信息
        if user_profile.get('gender'):
            desc_parts.append(f"性别：{user_profile['gender']}")
        if user_profile.get('age'):
            desc_parts.append(f"年龄：{user_profile['age']}岁")
        if user_profile.get('height'):
            desc_parts.append(f"身高：{user_profile['height']}cm")
        if user_profile.get('weight'):
            desc_parts.append(f"体重：{user_profile['weight']}kg")
        if user_profile.get('bmi'):
            desc_parts.append(f"BMI：{user_profile['bmi']}（{user_profile.get('bmi_category', '未知')}）")

        # 用户既有的健身目标
        if user_profile.get('fitness_goal'):
            desc_parts.append(f"个人健身目标偏好：{user_profile['fitness_goal']}")

        # 活动统计
        if user_stats:
            exercise_data = user_stats.get('exercise', {})
            diet_data = user_stats.get('diet', {})

            if exercise_data.get('total_exercises', 0) > 0:
                desc_parts.append(f"近30天运动次数：{exercise_data['total_exercises']}次")
                desc_parts.append(f"平均每次运动时长：{exercise_data.get('avg_duration', 0)}分钟")

            if user_stats.get('preferred_exercises'):
                desc_parts.append(f"偏好的运动类型：{', '.join(user_stats['preferred_exercises'])}")

            if diet_data.get('total_records', 0) > 0:
                desc_parts.append(f"近30天饮食记录数：{diet_data['total_records']}条")
                desc_parts.append(f"平均每餐热量：{diet_data.get('avg_calories_per_meal', 0)}卡")

            if user_stats.get('preferred_foods'):
                desc_parts.append(f"常吃的食物类型：{', '.join(user_stats['preferred_foods'])}")

        if not desc_parts:
            return "（新用户，暂无历史数据）"

        return '\n'.join(f"- {part}" for part in desc_parts)

    def _get_goal_specific_strategy(self, fitness_goal):
        """根据健身目标返回专门的训练策略指导"""
        strategies = {
            "减脂塑形": """【减脂塑形专项策略】
- 训练重点：有氧运动为主（占60-70%），配合力量训练（占30-40%）
- 推荐动作：HIIT间歇训练、跑步、跳绳、波比跳、登山跑、深蹲、俯卧撑
- 训练强度：中高强度，心率保持在最大心率的65-85%
- 休息安排：每周安排1-2天主动恢复
- 营养原则：制造热量缺口（每日减少300-500卡），高蛋白（每公斤体重1.6-2.0g），控制碳水和脂肪
- 推荐食物：鸡胸肉、鱼虾、蛋白、蔬菜、全谷物
- 禁忌食物：油炸食品、甜饮料、高糖零食、精制碳水""",

            "增肌强体": """【增肌强体专项策略】
- 训练重点：力量训练为主（占80%），少量有氧（占20%）
- 推荐动作：深蹲、硬拉、卧推、划船、引体向上、肩推、弯举
- 训练强度：中高强度，采用渐进超负荷原则
- 休息安排：同一肌群训练间隔48-72小时
- 营养原则：热量盈余（每日多摄入300-500卡），高蛋白（每公斤体重1.8-2.2g），充足碳水
- 推荐食物：牛肉、鸡肉、鸡蛋、牛奶、米饭、燕麦、红薯
- 补充建议：训练后30分钟内补充蛋白质和碳水""",

            "提升耐力": """【提升耐力专项策略】
- 训练重点：有氧耐力训练为主，配合核心训练
- 推荐动作：长跑、游泳、骑行、跳绳、划船机、平板支撑
- 训练强度：中等强度为主，心率保持在最大心率的60-75%
- 休息安排：渐进增加运动时长和强度
- 营养原则：充足碳水化合物供能，适量蛋白质修复，注意补水
- 推荐食物：全谷物、香蕉、红薯、意面、瘦肉、豆类
- 补充建议：长时间运动注意电解质补充""",

            "增强柔韧性": """【增强柔韧性专项策略】
- 训练重点：拉伸和瑜伽为主，配合轻度力量训练
- 推荐动作：瑜伽体式、普拉提、动态拉伸、静态拉伸、泡沫轴放松
- 训练强度：低到中等强度，注重动作质量和呼吸
- 休息安排：可以每天进行，但要避免过度拉伸
- 营养原则：均衡饮食，适量蛋白质，充足水分
- 推荐食物：富含omega-3的鱼类、坚果、新鲜蔬果
- 注意事项：避免冷身体时进行深度拉伸""",

            "综合健康": """【综合健康专项策略】
- 训练重点：有氧、力量、柔韧性均衡发展
- 推荐动作：快走/慢跑、深蹲、俯卧撑、平板支撑、瑜伽拉伸
- 训练强度：中等强度为主，循序渐进
- 休息安排：每周2-3天休息，保证睡眠质量
- 营养原则：均衡饮食，控制总热量，保证营养多样性
- 推荐食物：全谷物、瘦肉、鱼类、蛋奶、新鲜蔬果
- 生活建议：保持规律作息，减少久坐，保持心情愉悦"""
        }

        return strategies.get(fitness_goal, strategies["综合健康"])
    
    def call_openai_api(self, system_prompt, user_prompt):
        """调用阿里云千问API (OpenAI兼容模式)"""
        headers = {
            'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': AI_MODEL,
            'messages': [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 0.8
        }

        try:
            # 使用urllib发送POST请求
            req_data = json.dumps(data).encode('utf-8')
            request = urllib.request.Request(
                f'{AI_BASE_URL}/chat/completions',
                data=req_data,
                headers=headers,
                method='POST'
            )

            with urllib.request.urlopen(request, timeout=60) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    content = result['choices'][0]['message']['content']
                    print(f"[AI] 千问响应成功，内容长度: {len(content)}")
                    return content
                else:
                    error_msg = response.read().decode('utf-8')
                    print(f"[AI] API请求失败: {response.status} - {error_msg}")
                    return self.get_fallback_response()

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else str(e)
            print(f"[AI] HTTP错误 {e.code}: {error_body}")
            return self.get_fallback_response()
        except urllib.error.URLError as e:
            print(f"[AI] 网络请求异常: {e}")
            return self.get_fallback_response()
        except Exception as e:
            print(f"[AI] 其他异常: {e}")
            return self.get_fallback_response()
    
    def get_fallback_response(self):
        """获取备用响应"""
        return """很抱歉，AI服务暂时不可用。以下是通用的健身建议：

## 基础健身方案

### 训练计划
- **频率**: 每周3-4次
- **时长**: 每次30-45分钟
- **强度**: 中等强度

### 推荐动作
1. **有氧运动**: 跑步、游泳、骑行
2. **力量训练**: 俯卧撑、深蹲、平板支撑
3. **拉伸运动**: 全身拉伸、瑜伽

### 营养建议
- 保持均衡饮食
- 充足蛋白质摄入
- 适量碳水化合物
- 多喝水

请稍后重试获取个性化方案。"""
    
    def parse_ai_response(self, ai_response, fitness_goal, experience_level):
        """解析AI响应"""
        try:
            # 移除可能的markdown代码块标记
            clean_response = ai_response
            if '```json' in clean_response:
                clean_response = clean_response.split('```json')[1]
            if '```' in clean_response:
                clean_response = clean_response.split('```')[0]

            # 尝试提取JSON部分
            start_idx = clean_response.find('{')
            end_idx = clean_response.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = clean_response[start_idx:end_idx]
                parsed_data = json.loads(json_str)

                # 确保必要字段存在
                if 'title' not in parsed_data:
                    parsed_data['title'] = f"{experience_level}健身方案 - {fitness_goal}"
                if 'description' not in parsed_data:
                    parsed_data['description'] = f"针对目标'{fitness_goal}'制定的{experience_level}健身方案"
                if 'weekly_schedule' not in parsed_data:
                    parsed_data['weekly_schedule'] = self.get_default_schedule(experience_level)
                if 'nutrition_advice' not in parsed_data:
                    parsed_data['nutrition_advice'] = self.get_default_nutrition_advice()
                if 'tips' not in parsed_data:
                    parsed_data['tips'] = ["坚持训练", "注意休息", "合理饮食"]

                print(f"[AI] 方案解析成功: {parsed_data.get('title', '未命名方案')}")
                return parsed_data
            else:
                print("[AI] 未找到有效JSON，使用默认方案")
                return self.get_default_fitness_plan(fitness_goal, experience_level)
                
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return self.get_default_fitness_plan(fitness_goal, experience_level)
    
    def get_default_schedule(self, experience_level):
        """获取默认训练安排"""
        schedules = {
            "初学者": {
                "周一": {
                    "type": "有氧训练",
                    "activities": ["快走 20分钟", "慢跑 10分钟", "拉伸放松 5分钟"],
                    "duration": 35,
                    "intensity": "低",
                    "notes": "注意保持呼吸均匀，心率控制在最大心率60-70%"
                },
                "周三": {
                    "type": "基础力量",
                    "activities": ["俯卧撑 3组x10次", "深蹲 3组x15次", "平板支撑 3组x30秒", "仰卧起坐 3组x15次"],
                    "duration": 30,
                    "intensity": "低",
                    "notes": "动作要标准，宁可少做也要做对"
                },
                "周五": {
                    "type": "综合训练",
                    "activities": ["热身跳绳 5分钟", "波比跳 2组x8次", "登山跑 2组x20次", "全身拉伸 10分钟"],
                    "duration": 40,
                    "intensity": "中",
                    "notes": "循序渐进，如感到不适请立即停止"
                },
                "周日": {
                    "type": "恢复日",
                    "activities": ["瑜伽拉伸 20分钟", "冥想放松 10分钟"],
                    "duration": 30,
                    "intensity": "低",
                    "notes": "主动恢复，促进肌肉修复"
                }
            },
            "中级": {
                "周一": {
                    "type": "胸肩训练",
                    "activities": ["俯卧撑 4组x15次", "哑铃飞鸟 4组x12次", "肩推 4组x12次", "侧平举 3组x15次"],
                    "duration": 50,
                    "intensity": "中",
                    "notes": "注意胸肌发力，肩部热身充分"
                },
                "周二": {
                    "type": "有氧HIIT",
                    "activities": ["热身 5分钟", "HIIT间歇跑 20分钟(30秒冲刺+60秒慢跑)", "放松拉伸 5分钟"],
                    "duration": 30,
                    "intensity": "高",
                    "notes": "根据自身状态调整冲刺强度"
                },
                "周四": {
                    "type": "背腿训练",
                    "activities": ["引体向上 4组x8次", "哑铃划船 4组x12次", "深蹲 4组x15次", "罗马尼亚硬拉 3组x12次"],
                    "duration": 55,
                    "intensity": "中",
                    "notes": "背部训练注意挺胸收腹"
                },
                "周六": {
                    "type": "核心腹肌",
                    "activities": ["平板支撑 4组x45秒", "俄罗斯转体 3组x20次", "卷腹 4组x20次", "抬腿 3组x15次"],
                    "duration": 40,
                    "intensity": "中",
                    "notes": "核心收紧，不要借力"
                }
            },
            "高级": {
                "周一": {
                    "type": "胸部专项",
                    "activities": ["杠铃卧推 5组x8次", "上斜哑铃卧推 4组x10次", "龙门架夹胸 4组x12次", "双杠臂屈伸 4组x力竭"],
                    "duration": 60,
                    "intensity": "高",
                    "notes": "大重量训练需要搭档保护"
                },
                "周二": {
                    "type": "背部专项",
                    "activities": ["引体向上 5组x10次", "杠铃划船 4组x10次", "坐姿划船 4组x12次", "直臂下拉 3组x15次"],
                    "duration": 60,
                    "intensity": "高",
                    "notes": "感受背阔肌收缩"
                },
                "周三": {
                    "type": "腿部专项",
                    "activities": ["深蹲 5组x8次", "腿举 4组x12次", "罗马尼亚硬拉 4组x10次", "腿弯举 3组x15次"],
                    "duration": 65,
                    "intensity": "高",
                    "notes": "腿部训练最消耗体能，注意补充能量"
                },
                "周四": {
                    "type": "肩部手臂",
                    "activities": ["推举 4组x10次", "侧平举 4组x12次", "杠铃弯举 4组x10次", "三头下压 4组x12次"],
                    "duration": 55,
                    "intensity": "中",
                    "notes": "小肌群训练可适当增加组数"
                },
                "周五": {
                    "type": "HIIT燃脂",
                    "activities": ["热身 5分钟", "战绳 4组x30秒", "跳箱 4组x10次", "波比跳 4组x10次", "拉伸 10分钟"],
                    "duration": 45,
                    "intensity": "高",
                    "notes": "高强度有氧，心率保持在85%以上"
                },
                "周六": {
                    "type": "核心力量",
                    "activities": ["悬挂抬腿 4组x12次", "负重平板支撑 4组x45秒", "俄罗斯转体(负重) 4组x20次", "健腹轮 4组x10次"],
                    "duration": 45,
                    "intensity": "高",
                    "notes": "核心是力量传导的关键"
                }
            }
        }

        return schedules.get(experience_level, schedules["初学者"])

    def get_default_schedule_by_goal(self, fitness_goal, experience_level):
        """根据目标和经验水平获取默认训练安排"""
        # 基于目标的训练模板
        goal_schedules = {
            "减脂塑形": {
                "初学者": {
                    "周一": {"type": "有氧燃脂", "activities": ["快走30分钟", "开合跳3组x20次", "拉伸10分钟"], "duration": 45, "intensity": "中", "notes": "保持心率在最大心率65-75%"},
                    "周三": {"type": "全身循环", "activities": ["深蹲3组x15次", "俯卧撑3组x10次", "波比跳2组x8次", "平板支撑3组x30秒"], "duration": 40, "intensity": "中", "notes": "动作间休息30秒"},
                    "周五": {"type": "HIIT燃脂", "activities": ["热身5分钟", "30秒冲刺+60秒慢走x8组", "拉伸10分钟"], "duration": 35, "intensity": "高", "notes": "根据体力调整冲刺强度"},
                    "周日": {"type": "主动恢复", "activities": ["瑜伽拉伸30分钟", "泡沫轴放松15分钟"], "duration": 45, "intensity": "低", "notes": "放松肌肉，促进恢复"}
                },
                "中级": {
                    "周一": {"type": "HIIT燃脂", "activities": ["波比跳4组x12次", "登山跑4组x30秒", "高抬腿4组x30秒", "跳绳5分钟x3组"], "duration": 45, "intensity": "高", "notes": "组间休息45秒"},
                    "周二": {"type": "力量塑形-上肢", "activities": ["俯卧撑4组x15次", "哑铃划船4组x12次", "肩推4组x12次", "三头下压3组x15次"], "duration": 50, "intensity": "中", "notes": "注重肌肉收缩"},
                    "周四": {"type": "力量塑形-下肢", "activities": ["深蹲4组x15次", "箭步蹲4组x12次", "罗马尼亚硬拉4组x12次", "臀桥4组x15次"], "duration": 50, "intensity": "中", "notes": "腿部训练燃脂效果最佳"},
                    "周五": {"type": "有氧耐力", "activities": ["慢跑40分钟", "拉伸10分钟"], "duration": 50, "intensity": "中", "notes": "保持稳定配速"},
                    "周六": {"type": "核心训练", "activities": ["平板支撑4组x60秒", "俄罗斯转体4组x20次", "卷腹4组x20次", "死虫4组x15次"], "duration": 35, "intensity": "中", "notes": "核心收紧全程"}
                },
                "高级": {
                    "周一": {"type": "高强度HIIT", "activities": ["波比跳5组x15次", "跳箱5组x12次", "战绳4组x30秒", "登山跑4组x45秒"], "duration": 50, "intensity": "高", "notes": "全力输出"},
                    "周二": {"type": "力量-推", "activities": ["卧推5组x10次", "上斜哑铃推5组x12次", "肩推4组x12次", "三头臂屈伸4组x15次"], "duration": 55, "intensity": "高", "notes": "大重量刺激"},
                    "周三": {"type": "有氧燃脂", "activities": ["变速跑45分钟", "核心训练20分钟"], "duration": 65, "intensity": "中高", "notes": "变速跑更高效燃脂"},
                    "周四": {"type": "力量-拉", "activities": ["引体向上5组x10次", "杠铃划船5组x10次", "面拉4组x15次", "弯举4组x12次"], "duration": 55, "intensity": "高", "notes": "注重背阔肌发力"},
                    "周五": {"type": "力量-腿", "activities": ["深蹲5组x10次", "腿举4组x12次", "腿弯举4组x12次", "小腿提踵4组x20次"], "duration": 60, "intensity": "高", "notes": "腿部是燃脂大引擎"},
                    "周六": {"type": "冲刺训练", "activities": ["热身10分钟", "100米冲刺x10组", "核心训练15分钟", "拉伸10分钟"], "duration": 45, "intensity": "高", "notes": "冲刺后走回恢复"}
                }
            },
            "增肌强体": {
                "初学者": {
                    "周一": {"type": "全身力量", "activities": ["深蹲3组x12次", "俯卧撑3组x10次", "哑铃划船3组x12次", "肩推3组x12次"], "duration": 45, "intensity": "中", "notes": "学习正确动作模式"},
                    "周三": {"type": "全身力量", "activities": ["罗马尼亚硬拉3组x12次", "哑铃卧推3组x12次", "哑铃弯举3组x12次", "平板支撑3组x30秒"], "duration": 45, "intensity": "中", "notes": "专注肌肉感受"},
                    "周五": {"type": "全身力量", "activities": ["保加利亚分腿蹲3组x10次", "引体向上辅助3组x8次", "侧平举3组x15次", "三头下压3组x12次"], "duration": 45, "intensity": "中", "notes": "渐进增加重量"}
                },
                "中级": {
                    "周一": {"type": "胸+三头", "activities": ["杠铃卧推4组x10次", "上斜哑铃推4组x12次", "龙门架夹胸4组x12次", "绳索下压4组x15次"], "duration": 55, "intensity": "中高", "notes": "胸肌发力为主"},
                    "周二": {"type": "背+二头", "activities": ["引体向上4组x8次", "杠铃划船4组x10次", "坐姿划船4组x12次", "杠铃弯举4组x10次"], "duration": 55, "intensity": "中高", "notes": "背阔肌收缩"},
                    "周四": {"type": "腿+核心", "activities": ["深蹲4组x10次", "腿举4组x12次", "罗马尼亚硬拉4组x10次", "悬垂抬腿4组x12次"], "duration": 60, "intensity": "高", "notes": "腿部训练促进睾酮分泌"},
                    "周五": {"type": "肩+手臂", "activities": ["推举4组x10次", "侧平举4组x15次", "面拉4组x15次", "锤式弯举4组x12次"], "duration": 50, "intensity": "中", "notes": "肩部热身充分"},
                    "周六": {"type": "弱项强化", "activities": ["根据自身弱项选择训练部位", "4-5个动作", "4组x10-12次"], "duration": 45, "intensity": "中", "notes": "专注提升弱势肌群"}
                },
                "高级": {
                    "周一": {"type": "胸部专项", "activities": ["杠铃卧推5组x6-8次", "上斜哑铃推5组x8-10次", "下斜哑铃推4组x10次", "龙门架夹胸4组x12次", "双杠臂屈伸4组x力竭"], "duration": 65, "intensity": "高", "notes": "大重量刺激"},
                    "周二": {"type": "背部专项", "activities": ["硬拉5组x5次", "引体向上5组x8次", "杠铃划船5组x8次", "单臂哑铃划船4组x10次", "直臂下拉3组x15次"], "duration": 65, "intensity": "高", "notes": "感受背阔肌发力"},
                    "周三": {"type": "腿部专项", "activities": ["深蹲5组x6次", "前蹲4组x8次", "腿举5组x12次", "腿弯举4组x12次", "小腿提踵5组x15次"], "duration": 70, "intensity": "高", "notes": "腿部需要更大重量刺激"},
                    "周四": {"type": "休息/轻有氧", "activities": ["轻度有氧20分钟", "全身拉伸20分钟"], "duration": 40, "intensity": "低", "notes": "促进恢复"},
                    "周五": {"type": "肩部专项", "activities": ["推举5组x8次", "阿诺德推举4组x10次", "侧平举5组x12次", "俯身飞鸟4组x12次", "耸肩4组x15次"], "duration": 55, "intensity": "高", "notes": "三角肌全面刺激"},
                    "周六": {"type": "手臂专项", "activities": ["杠铃弯举5组x8次", "锤式弯举4组x10次", "窄距卧推4组x10次", "绳索下压4组x12次", "头顶臂屈伸4组x12次"], "duration": 50, "intensity": "中高", "notes": "注重收缩顶峰"}
                }
            },
            "提升耐力": {
                "初学者": {
                    "周一": {"type": "有氧基础", "activities": ["快走/慢跑交替30分钟", "拉伸10分钟"], "duration": 40, "intensity": "低", "notes": "建立有氧基础"},
                    "周三": {"type": "核心耐力", "activities": ["平板支撑3组x30秒", "深蹲3组x15次", "开合跳3组x30秒", "仰卧起坐3组x15次"], "duration": 35, "intensity": "中", "notes": "核心支撑耐力"},
                    "周五": {"type": "持续有氧", "activities": ["慢跑25分钟", "快走10分钟", "拉伸10分钟"], "duration": 45, "intensity": "中", "notes": "保持稳定心率"},
                    "周日": {"type": "交叉训练", "activities": ["游泳或骑行30分钟", "拉伸15分钟"], "duration": 45, "intensity": "低", "notes": "变换运动形式"}
                },
                "中级": {
                    "周一": {"type": "长距离有氧", "activities": ["匀速跑45分钟", "拉伸10分钟"], "duration": 55, "intensity": "中", "notes": "建立有氧耐力"},
                    "周二": {"type": "间歇训练", "activities": ["热身10分钟", "400米快跑+400米慢跑x6组", "放松10分钟"], "duration": 50, "intensity": "高", "notes": "提升最大摄氧量"},
                    "周四": {"type": "节奏跑", "activities": ["热身10分钟", "配速跑30分钟", "放松10分钟"], "duration": 50, "intensity": "中高", "notes": "保持稳定配速"},
                    "周五": {"type": "核心+力量", "activities": ["平板支撑4组x45秒", "深蹲4组x15次", "弓箭步4组x12次", "登山跑4组x30秒"], "duration": 45, "intensity": "中", "notes": "增强跑步经济性"},
                    "周六": {"type": "长慢跑", "activities": ["轻松慢跑60分钟"], "duration": 60, "intensity": "低", "notes": "建立有氧基础"}
                },
                "高级": {
                    "周一": {"type": "LSD长距离", "activities": ["长慢跑75-90分钟"], "duration": 90, "intensity": "低", "notes": "周末长跑"},
                    "周二": {"type": "速度训练", "activities": ["热身15分钟", "200米冲刺x10组", "放松15分钟"], "duration": 50, "intensity": "高", "notes": "提升速度能力"},
                    "周三": {"type": "恢复跑", "activities": ["轻松跑40分钟"], "duration": 40, "intensity": "低", "notes": "促进恢复"},
                    "周四": {"type": "乳酸阈值跑", "activities": ["热身15分钟", "阈值配速跑25分钟", "放松10分钟"], "duration": 50, "intensity": "中高", "notes": "提升乳酸阈值"},
                    "周五": {"type": "核心力量", "activities": ["平板支撑变体4组x60秒", "单腿深蹲4组x10次", "臀桥4组x15次", "侧平板4组x30秒"], "duration": 45, "intensity": "中", "notes": "增强跑步稳定性"},
                    "周六": {"type": "间歇训练", "activities": ["热身15分钟", "1000米x5组(配速跑)", "放松15分钟"], "duration": 60, "intensity": "高", "notes": "比赛配速练习"}
                }
            },
            "增强柔韧性": {
                "初学者": {
                    "周一": {"type": "基础拉伸", "activities": ["颈部拉伸5分钟", "肩背拉伸10分钟", "腿部拉伸10分钟", "髋部拉伸10分钟"], "duration": 35, "intensity": "低", "notes": "每个动作保持30秒"},
                    "周三": {"type": "入门瑜伽", "activities": ["猫牛式", "下犬式", "婴儿式", "坐姿前屈", "仰卧扭转"], "duration": 40, "intensity": "低", "notes": "跟随呼吸节奏"},
                    "周五": {"type": "动态拉伸", "activities": ["腿摆动3组x15次", "手臂画圈3组x20次", "躯干旋转3组x15次", "动态弓箭步3组x10次"], "duration": 30, "intensity": "低", "notes": "动作幅度由小到大"},
                    "周日": {"type": "放松恢复", "activities": ["泡沫轴全身放松30分钟"], "duration": 30, "intensity": "低", "notes": "着重紧张部位"}
                },
                "中级": {
                    "周一": {"type": "流瑜伽", "activities": ["拜日式A x3轮", "站立体式串联15分钟", "坐姿体式15分钟", "放松5分钟"], "duration": 50, "intensity": "中", "notes": "呼吸与动作配合"},
                    "周二": {"type": "深度拉伸", "activities": ["髋屈肌拉伸", "梨状肌拉伸", "腘绳肌拉伸", "股四头肌拉伸"], "duration": 40, "intensity": "中", "notes": "每个动作保持1-2分钟"},
                    "周四": {"type": "普拉提", "activities": ["百次拍打", "卷腹起坐", "单腿画圈", "侧卧抬腿", "泳式"], "duration": 45, "intensity": "中", "notes": "核心稳定+柔韧"},
                    "周五": {"type": "阴瑜伽", "activities": ["蝴蝶式5分钟", "龙式5分钟", "天鹅式5分钟", "香蕉式5分钟"], "duration": 45, "intensity": "低", "notes": "深层结缔组织拉伸"},
                    "周六": {"type": "功能性拉伸", "activities": ["肩胛骨活动", "脊柱扭转", "髋关节打开", "踝关节活动"], "duration": 35, "intensity": "低", "notes": "关节活动度提升"}
                },
                "高级": {
                    "周一": {"type": "高级瑜伽", "activities": ["高级拜日式", "平衡体式（树式、鹰式、舞王式）", "后弯体式", "倒立体式"], "duration": 60, "intensity": "中", "notes": "安全第一"},
                    "周二": {"type": "功能性训练", "activities": ["土耳其起身4组x5次", "风车4组x8次", "俯卧撑+转体4组x10次"], "duration": 45, "intensity": "中", "notes": "力量+柔韧结合"},
                    "周三": {"type": "深度拉伸", "activities": ["前后劈叉练习", "横劈叉练习", "桥式练习"], "duration": 50, "intensity": "中", "notes": "循序渐进"},
                    "周四": {"type": "普拉提器械", "activities": ["核心滑盘训练", "弹力带抗阻拉伸", "瑜伽轮后弯"], "duration": 50, "intensity": "中", "notes": "辅助工具增强效果"},
                    "周五": {"type": "阴瑜伽深度", "activities": ["每个体式保持3-5分钟", "专注呼吸和放松"], "duration": 60, "intensity": "低", "notes": "深层组织释放"},
                    "周六": {"type": "综合练习", "activities": ["动态热身10分钟", "力量瑜伽30分钟", "静态拉伸20分钟"], "duration": 60, "intensity": "中", "notes": "综合提升"}
                }
            },
            "综合健康": {
                "初学者": {
                    "周一": {"type": "轻度有氧", "activities": ["快走30分钟", "拉伸10分钟"], "duration": 40, "intensity": "低", "notes": "建立运动习惯"},
                    "周三": {"type": "基础力量", "activities": ["深蹲3组x12次", "俯卧撑3组x8次", "平板支撑3组x20秒"], "duration": 30, "intensity": "中", "notes": "学习基础动作"},
                    "周五": {"type": "有氧+拉伸", "activities": ["慢跑20分钟", "全身拉伸15分钟"], "duration": 35, "intensity": "低", "notes": "循序渐进"},
                    "周日": {"type": "休闲运动", "activities": ["游泳/骑行/徒步30分钟"], "duration": 30, "intensity": "低", "notes": "享受运动乐趣"}
                },
                "中级": {
                    "周一": {"type": "有氧训练", "activities": ["跑步35分钟", "核心训练10分钟"], "duration": 45, "intensity": "中", "notes": "心肺功能提升"},
                    "周二": {"type": "上肢力量", "activities": ["俯卧撑4组x12次", "引体向上4组x6次", "肩推4组x10次"], "duration": 40, "intensity": "中", "notes": "上肢力量均衡"},
                    "周四": {"type": "下肢力量", "activities": ["深蹲4组x12次", "箭步蹲4组x10次", "臀桥4组x15次"], "duration": 40, "intensity": "中", "notes": "下肢力量基础"},
                    "周五": {"type": "HIIT", "activities": ["波比跳3组x10次", "登山跑3组x30秒", "开合跳3组x30秒"], "duration": 30, "intensity": "高", "notes": "高效燃脂"},
                    "周六": {"type": "瑜伽拉伸", "activities": ["全身瑜伽45分钟"], "duration": 45, "intensity": "低", "notes": "身心放松"}
                },
                "高级": {
                    "周一": {"type": "力量-推", "activities": ["卧推4组x10次", "推举4组x10次", "三头下压4组x12次"], "duration": 50, "intensity": "高", "notes": "推类动作"},
                    "周二": {"type": "有氧耐力", "activities": ["跑步50分钟", "核心15分钟"], "duration": 65, "intensity": "中", "notes": "心肺耐力"},
                    "周三": {"type": "力量-拉", "activities": ["引体向上4组x10次", "划船4组x10次", "弯举4组x12次"], "duration": 50, "intensity": "高", "notes": "拉类动作"},
                    "周四": {"type": "HIIT", "activities": ["高强度间歇训练40分钟"], "duration": 40, "intensity": "高", "notes": "代谢训练"},
                    "周五": {"type": "力量-腿", "activities": ["深蹲4组x10次", "硬拉4组x8次", "腿举4组x12次"], "duration": 55, "intensity": "高", "notes": "下肢力量"},
                    "周六": {"type": "柔韧恢复", "activities": ["瑜伽60分钟"], "duration": 60, "intensity": "低", "notes": "恢复与柔韧"}
                }
            }
        }

        goal_data = goal_schedules.get(fitness_goal, goal_schedules["综合健康"])
        return goal_data.get(experience_level, goal_data.get("初学者", {}))

    def get_default_nutrition_advice_by_goal(self, fitness_goal):
        """根据目标获取营养建议"""
        advices = {
            "减脂塑形": """## 减脂塑形营养方案

### 热量目标
- 每日热量缺口：300-500卡路里
- 计算公式：基础代谢 x 活动系数 - 300~500

### 宏量营养素配比
- 蛋白质：每公斤体重1.6-2.0g（占总热量25-30%）
- 碳水化合物：占总热量40-45%（优选复合碳水）
- 脂肪：占总热量25-30%（优选不饱和脂肪）

### 餐次安排
- 早餐（7:00-8:00）：占全天热量25%，高蛋白+复合碳水
- 午餐（12:00-13:00）：占全天热量35%，均衡搭配
- 加餐（15:00-16:00）：100-150卡，蛋白质为主
- 晚餐（18:00-19:00）：占全天热量25%，低碳水+高蛋白+蔬菜

### 推荐食物
- 蛋白质：鸡胸肉、鱼虾、蛋白、豆腐、希腊酸奶
- 碳水化合物：燕麦、糙米、红薯、全麦面包
- 蔬菜：西兰花、菠菜、芹菜、黄瓜、番茄
- 脂肪：牛油果、坚果（适量）、橄榄油

### 禁忌食物
- 油炸食品、甜饮料、糖果、蛋糕
- 精制碳水（白面包、白米饭过量）
- 高糖水果（葡萄、荔枝过量）""",

            "增肌强体": """## 增肌强体营养方案

### 热量目标
- 每日热量盈余：300-500卡路里
- 增肌期需要充足能量支持肌肉生长

### 宏量营养素配比
- 蛋白质：每公斤体重1.8-2.2g（占总热量25-30%）
- 碳水化合物：占总热量45-55%（训练前后增加）
- 脂肪：占总热量20-25%

### 餐次安排
- 早餐（7:00）：高蛋白+复合碳水（如燕麦+鸡蛋+牛奶）
- 加餐（10:00）：蛋白奶昔或坚果
- 午餐（12:00）：大份蛋白质+碳水+蔬菜
- 训练前（训练前1-2小时）：碳水为主
- 训练后（30分钟内）：快速蛋白+简单碳水
- 晚餐（19:00）：蛋白质+适量碳水+蔬菜
- 睡前（可选）：缓释蛋白（如酪蛋白）

### 推荐食物
- 蛋白质：牛肉、鸡肉、鸡蛋、三文鱼、虾、牛奶
- 碳水化合物：米饭、面条、土豆、红薯、香蕉
- 蔬菜：各类绿叶蔬菜
- 脂肪：鸡蛋黄、牛油果、橄榄油、坚果

### 补剂建议（可选）
- 乳清蛋白粉：方便补充蛋白质
- 肌酸：提升力量和肌肉体积
- 鱼油：抗炎和关节健康""",

            "提升耐力": """## 提升耐力营养方案

### 热量目标
- 根据训练量调整，长距离训练日增加热量摄入
- 保持能量平衡，避免训练能量不足

### 宏量营养素配比
- 碳水化合物：占总热量55-65%（耐力运动的主要燃料）
- 蛋白质：每公斤体重1.2-1.6g（占总热量15-20%）
- 脂肪：占总热量20-25%

### 餐次安排
- 训练前2-3小时：复合碳水为主的正餐
- 训练前30分钟：少量简单碳水（如香蕉）
- 训练中（超过60分钟）：运动饮料或能量胶
- 训练后30分钟：碳水+蛋白质（4:1比例）
- 日常三餐：均衡饮食，碳水充足

### 推荐食物
- 碳水化合物：燕麦、全麦面包、意面、米饭、香蕉、红薯
- 蛋白质：鸡肉、鱼肉、鸡蛋、豆类、牛奶
- 电解质来源：运动饮料、椰子水、盐
- 训练中补给：能量胶、运动饮料、香蕉

### 补水建议
- 每天至少2-3升水
- 训练前2小时饮水500ml
- 训练中每15-20分钟补充150-200ml
- 训练后根据体重损失补水（每减1kg补1.5L水）""",

            "增强柔韧性": """## 增强柔韧性营养方案

### 热量目标
- 保持能量平衡
- 柔韧性训练消耗相对较低，注意不要过量饮食

### 宏量营养素配比
- 蛋白质：每公斤体重1.0-1.4g（肌肉修复）
- 碳水化合物：占总热量45-55%
- 脂肪：占总热量25-30%（关节润滑需要健康脂肪）

### 营养重点
- 胶原蛋白：支持关节和结缔组织健康
- Omega-3脂肪酸：抗炎、关节健康
- 维生素C：促进胶原蛋白合成
- 水分：保持组织弹性

### 推荐食物
- 胶原蛋白来源：骨汤、鱼皮、猪蹄（适量）
- Omega-3来源：三文鱼、鲭鱼、核桃、亚麻籽
- 维生素C来源：橙子、猕猴桃、彩椒、西兰花
- 抗炎食物：姜黄、生姜、绿茶、浆果类
- 蛋白质：鸡肉、鱼肉、鸡蛋、豆腐

### 避免食物
- 加工食品（促炎）
- 过量糖分（影响关节健康）
- 酒精（影响恢复）""",

            "综合健康": """## 综合健康营养方案

### 热量目标
- 保持能量平衡，维持健康体重
- 根据活动量适当调整

### 宏量营养素配比
- 蛋白质：每公斤体重1.0-1.5g（占总热量15-20%）
- 碳水化合物：占总热量45-55%
- 脂肪：占总热量25-30%

### 餐次安排
- 早餐：占全天热量25-30%，营养全面
- 午餐：占全天热量35-40%，能量充足
- 晚餐：占全天热量25-30%，清淡为主
- 加餐：健康零食（水果、坚果）

### 推荐食物
- 主食：全谷物、杂粮、薯类
- 蛋白质：鱼禽蛋肉、豆类、奶制品
- 蔬菜：每天500g以上，种类多样
- 水果：每天200-350g
- 脂肪：植物油、坚果、深海鱼

### 健康饮食原则
- 少油少盐少糖
- 多蔬菜多纤维
- 规律饮食，定时定量
- 细嚼慢咽，七分饱
- 每天饮水1500-2000ml"""
        }

        return advices.get(fitness_goal, advices["综合健康"])
    
    def get_default_fitness_plan(self, fitness_goal, experience_level):
        """获取默认健身方案 - 基于目标生成"""
        # 根据目标生成专门的提示
        goal_tips = {
            "减脂塑形": [
                "保持热量缺口，每日减少300-500卡摄入",
                "有氧运动和力量训练结合效果最佳",
                "训练后30分钟内补充蛋白质",
                "保证充足睡眠，每晚7-8小时",
                "每周测量体重和围度，监控进展"
            ],
            "增肌强体": [
                "保持热量盈余，每日多摄入300-500卡",
                "蛋白质摄入每公斤体重1.8-2.2g",
                "同一肌群训练间隔48-72小时",
                "渐进超负荷，逐步增加训练重量",
                "训练后立即补充蛋白质和碳水"
            ],
            "提升耐力": [
                "循序渐进增加运动时长和强度",
                "保持稳定的训练节奏和呼吸",
                "注意补水和电解质平衡",
                "安排恢复跑促进身体恢复",
                "长距离训练前充分补充碳水"
            ],
            "增强柔韧性": [
                "避免冷身体时进行深度拉伸",
                "每个拉伸动作保持30秒以上",
                "注重呼吸，呼气时加深拉伸",
                "柔韧性提升需要持续练习",
                "结合力量训练防止关节不稳"
            ],
            "综合健康": [
                "保持规律运动，每周3-5次",
                "均衡饮食，营养多样化",
                "保证充足睡眠和休息",
                "避免久坐，增加日常活动量",
                "保持积极心态，享受运动"
            ]
        }

        return {
            "title": f"{fitness_goal}专项计划 - {experience_level}",
            "description": f"这是一套专为'{fitness_goal}'目标设计的{experience_level}健身方案。方案结合了科学的训练原理和营养指导，帮助您高效达成目标。请根据自身情况适当调整训练强度。",
            "weekly_schedule": self.get_default_schedule_by_goal(fitness_goal, experience_level),
            "nutrition_advice": self.get_default_nutrition_advice_by_goal(fitness_goal),
            "tips": goal_tips.get(fitness_goal, goal_tips["综合健康"])
        }
    
    def save_ai_plan_to_db(self, user_id, plan_data):
        """保存AI方案到数据库"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 正确映射字段:
            # recommendations -> tips (注意事项)
            # schedule_info -> weekly_schedule (训练安排)
            cursor.execute('''
                INSERT INTO ai_plan (user_id, plan_name, plan_type, goals, recommendations, schedule_info, nutrition_advice, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                plan_data.get('title', 'AI健身方案'),
                '个性化方案',
                plan_data.get('description', '个性化健身方案'),
                json.dumps(plan_data.get('tips', []), ensure_ascii=False),  # recommendations 存 tips
                json.dumps(plan_data.get('weekly_schedule', {}), ensure_ascii=False),  # schedule_info 存 weekly_schedule
                plan_data.get('nutrition_advice', ''),
                current_time,
                True
            ))

            plan_id = cursor.lastrowid
            conn.commit()
            conn.close()

            print(f"[AI] 方案已保存, ID: {plan_id}")
            return plan_id

        except Exception as e:
            print(f"保存AI方案失败: {e}")
            return None

def migrate_database():
    """数据库迁移 - 添加缺失的列"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 检查 user 表是否有 avatar 列
    cursor.execute("PRAGMA table_info(user)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'avatar' not in columns:
        print('[迁移] 添加 avatar 列到 user 表...')
        cursor.execute('ALTER TABLE user ADD COLUMN avatar TEXT')
        conn.commit()
        print('[迁移] avatar 列添加成功')

    conn.close()

def main():
    print('🚀 启动增强版API服务器...')

    # 执行数据库迁移
    try:
        migrate_database()
    except Exception as e:
        print(f'[迁移] 警告: {e}')

    server_address = ('', 5000)
    httpd = HTTPServer(server_address, EnhancedAPI)
    print('✅ 增强版API服务器已启动在端口5000')
    print('📊 支持统计功能API')
    print('⏰ 启动时间:', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('=' * 50)
    httpd.serve_forever()

if __name__ == '__main__':
    main()
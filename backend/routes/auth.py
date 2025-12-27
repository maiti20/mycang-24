from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt
)
from models import db, User
from datetime import datetime, timedelta
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# 用于存储撤销的令牌
revoked_tokens = set()

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': '用户名、邮箱和密码不能为空'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # 验证用户名格式
        if len(username) < 3 or len(username) > 20:
            return jsonify({'error': '用户名长度必须在3-20个字符之间'}), 400
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return jsonify({'error': '用户名只能包含字母、数字和下划线'}), 400
        
        # 验证邮箱格式
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({'error': '请输入有效的邮箱地址'}), 400
        
        # 验证密码强度
        if len(password) < 6:
            return jsonify({'error': '密码长度至少6位'}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 409
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({'error': '邮箱已被注册'}), 409
        
        # 创建新用户
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': '注册成功',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '注册失败，请稍后重试'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()

        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': '用户名和密码不能为空'}), 400

        username = data['username'].strip()
        password = data['password']

        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username) | (User.email == username.lower())
        ).first()

        if not user:
            print(f"[登录失败] 用户不存在: {username}")
            return jsonify({'error': '用户名或密码错误'}), 401

        if not user.check_password(password):
            print(f"[登录失败] 密码错误: {username}")
            return jsonify({'error': '用户名或密码错误'}), 401

        # 创建JWT令牌
        additional_claims = {'username': user.username}
        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=1)
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )

        print(f"[登录成功] 用户: {username}")
        return jsonify({
            'message': '登录成功',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'expires_in': 3600  # 1小时
        }), 200

    except Exception as e:
        print(f"[登录异常] 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '登录失败，请稍后重试'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        additional_claims = {'username': user.username}
        new_access_token = create_access_token(
            identity=current_user_id,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=1)
        )
        
        return jsonify({
            'access_token': new_access_token,
            'expires_in': 3600
        }), 200
        
    except Exception as e:
        return jsonify({'error': '令牌刷新失败'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    try:
        jti = get_jwt()['jti']  # JWT ID
        revoked_tokens.add(jti)
        
        return jsonify({'message': '登出成功'}), 200
        
    except Exception as e:
        return jsonify({'error': '登出失败'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户资料"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        return jsonify({
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': '获取用户资料失败'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息（别名）"""
    return get_profile()

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户资料"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.get_json()
        
        # 更新邮箱
        if 'email' in data:
            email = data['email'].strip().lower()
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            if not re.match(email_regex, email):
                return jsonify({'error': '请输入有效的邮箱地址'}), 400
            
            # 检查邮箱是否被其他用户使用
            existing_user = User.query.filter(User.email == email, User.id != current_user_id).first()
            if existing_user:
                return jsonify({'error': '邮箱已被其他用户使用'}), 409
            
            user.email = email
        
        # 更新密码
        if 'current_password' in data and 'new_password' in data:
            current_password = data['current_password']
            new_password = data['new_password']
            
            if not user.check_password(current_password):
                return jsonify({'error': '当前密码错误'}), 401
            
            if len(new_password) < 6:
                return jsonify({'error': '新密码长度至少6位'}), 400
            
            user.set_password(new_password)
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '资料更新成功',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '更新资料失败'}), 500

# 检查令牌是否被撤销的回调函数
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in revoked_tokens
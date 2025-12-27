from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import os
from dotenv import load_dotenv

# 导入路由模块
from routes.auth import auth_bp, check_if_token_revoked
from routes.diet import diet_bp
from routes.exercise import exercise_bp
from routes.ai_plan import ai_plan_bp

load_dotenv()

app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///fitness.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False  # 生产环境关闭SQL日志
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # 在路由中手动设置过期时间
app.config['JSON_AS_ASCII'] = False  # 支持中文输出

# 初始化扩展
db = SQLAlchemy(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})  # 更精确的CORS配置
jwt = JWTManager(app)

# 设置JWT令牌撤销检查
jwt.token_in_blocklist_loader(check_if_token_revoked)

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(diet_bp)
app.register_blueprint(exercise_bp)
app.register_blueprint(ai_plan_bp)

# 添加统计路由
@app.route('/api/stats/today', methods=['GET'])
@jwt_required()
def get_today_stats():
    """获取今日统计"""
    try:
        from flask_jwt_extended import get_jwt_identity
        from models import DietRecord, ExerciseLog
        from datetime import date

        current_user_id = get_jwt_identity()
        today = date.today()

        # 饮食统计
        diet_records = db.session.query(DietRecord).filter(
            DietRecord.user_id == current_user_id,
            DietRecord.recorded_at == today
        ).all()

        # 运动统计
        exercise_logs = db.session.query(ExerciseLog).filter(
            ExerciseLog.user_id == current_user_id,
            ExerciseLog.exercised_at == today
        ).all()

        return jsonify({
            'success': True,
            'data': {
                'date': today.isoformat(),
                'diet_records_count': len(diet_records),
                'exercise_logs_count': len(exercise_logs)
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': '获取今日统计失败'}), 500

@app.route('/api/stats/week', methods=['GET'])
@jwt_required()
def get_week_stats():
    """获取本周统计"""
    try:
        from flask_jwt_extended import get_jwt_identity
        from models import DietRecord, ExerciseLog
        from datetime import date, timedelta

        current_user_id = get_jwt_identity()
        end_date = date.today()
        start_date = end_date - timedelta(days=6)

        diet_records = db.session.query(DietRecord).filter(
            DietRecord.user_id == current_user_id,
            DietRecord.recorded_at >= start_date,
            DietRecord.recorded_at <= end_date
        ).all()

        exercise_logs = db.session.query(ExerciseLog).filter(
            ExerciseLog.user_id == current_user_id,
            ExerciseLog.exercised_at >= start_date,
            ExerciseLog.exercised_at <= end_date
        ).all()

        return jsonify({
            'success': True,
            'data': {
                'period': {'start_date': start_date.isoformat(), 'end_date': end_date.isoformat()},
                'diet_records_count': len(diet_records),
                'exercise_logs_count': len(exercise_logs)
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': '获取本周统计失败'}), 500

@app.route('/api/stats/recent-activities', methods=['GET'])
@jwt_required()
def get_recent_activities():
    """获取最近活动"""
    try:
        from flask_jwt_extended import get_jwt_identity
        from models import DietRecord, ExerciseLog
        from sqlalchemy import desc

        current_user_id = get_jwt_identity()
        limit = request.args.get('limit', 10, type=int)

        # 获取最近的饮食和运动记录
        recent_diets = db.session.query(DietRecord).filter(
            DietRecord.user_id == current_user_id
        ).order_by(desc(DietRecord.recorded_at)).limit(limit).all()

        recent_exercises = db.session.query(ExerciseLog).filter(
            ExerciseLog.user_id == current_user_id
        ).order_by(desc(ExerciseLog.exercised_at)).limit(limit).all()

        activities = []
        activities.extend([{'type': 'diet', 'data': record.to_dict()} for record in recent_diets])
        activities.extend([{'type': 'exercise', 'data': log.to_dict()} for log in recent_exercises])

        # 按日期排序
        activities.sort(key=lambda x: x['data'].get('recorded_at') or x['data'].get('exercised_at'), reverse=True)

        return jsonify({
            'success': True,
            'data': activities[:limit]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': '获取最近活动失败'}), 500

@app.route('/api/stats/streak-days', methods=['GET'])
@jwt_required()
def get_streak_days():
    """获取连续打卡天数"""
    try:
        from flask_jwt_extended import get_jwt_identity
        from models import ExerciseLog
        from datetime import date, timedelta
        from sqlalchemy import func

        current_user_id = get_jwt_identity()

        # 计算连续打卡天数
        streak = 0
        check_date = date.today()

        while True:
            log_exists = db.session.query(ExerciseLog).filter(
                ExerciseLog.user_id == current_user_id,
                ExerciseLog.exercised_at == check_date
            ).first()

            if log_exists:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        return jsonify({
            'success': True,
            'data': {'streak_days': streak}
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': '获取连续打卡天数失败'}), 500

@app.route('/api/stats/ai-plans-count', methods=['GET'])
@jwt_required()
def get_ai_plans_count():
    """获取AI方案数量"""
    try:
        from flask_jwt_extended import get_jwt_identity
        from models import AIPlan

        current_user_id = get_jwt_identity()
        count = db.session.query(AIPlan).filter(
            AIPlan.user_id == current_user_id
        ).count()

        return jsonify({
            'success': True,
            'data': {'count': count}
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': '获取AI方案数量失败'}), 500

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': '请求参数错误'}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': '未授权访问'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': '禁止访问'}), 403

# JWT错误处理
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': '令牌已过期'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': '令牌无效'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': '缺少访问令牌'}), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return jsonify({'error': '需要新的令牌'}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': '令牌已被撤销'}), 401

# 基础路由
@app.route('/')
def index():
    return jsonify({
        'message': '健身打卡系统API运行中',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/auth',
            'diet': '/diet',
            'exercise': '/exercise',
            'ai_plan': '/ai-plan'
        }
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'service': 'fitness-tracker-api',
        'database': 'connected' if db.engine else 'disconnected'
    })

@app.route('/api/info')
def api_info():
    return jsonify({
        'name': '健身打卡系统API',
        'description': '提供用户管理、饮食记录、运动追踪和AI健身方案的完整API服务',
        'features': [
            '用户认证与授权',
            '饮食记录与营养分析',
            '运动库管理与日志',
            'AI个性化健身方案',
            '数据统计与分析'
        ],
        'authentication': 'JWT Bearer Token',
        'documentation': '/api/docs (待实现)'
    })

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("数据库表创建成功！")
        except Exception as e:
            print(f"数据库操作失败: {e}")
    
    port = int(os.getenv('API_PORT', 5000))
    host = os.getenv('API_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"健身打卡系统API启动在 http://{host}:{port}")
    app.run(debug=debug, host=host, port=port)
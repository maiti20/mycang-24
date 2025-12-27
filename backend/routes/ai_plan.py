from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, AIPlan, DietRecord, ExerciseLog, User
from datetime import date, datetime, timedelta
from sqlalchemy import func, and_, desc
import json

# 导入AI服务
from services.ai_service import get_ai_service

ai_plan_bp = Blueprint('ai_plan', __name__, url_prefix='/api/ai-plan')

@ai_plan_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_ai_plan():
    """生成AI健身方案"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['goals', 'duration_weeks', 'difficulty_level']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} 不能为空'}), 400
        
        goals = data['goals'].strip()
        duration_weeks = data['duration_weeks']
        difficulty_level = data['difficulty_level']
        
        # 验证数据有效性
        if len(goals) < 10:
            return jsonify({'error': '目标描述过于简单，请详细描述您的健身目标'}), 400
        
        if duration_weeks < 1 or duration_weeks > 52:
            return jsonify({'error': '计划周期必须在1-52周之间'}), 400
        
        if difficulty_level not in ['初级', '中级', '高级']:
            return jsonify({'error': '难度级别必须是：初级、中级或高级'}), 400
        
        # 获取AI服务
        ai_svc = get_ai_service()
        if not ai_svc:
            return jsonify({'error': 'AI服务暂时不可用，请稍后重试'}), 503
        
        # 使用AI生成个性化方案
        plan_content = ai_svc.generate_personalized_fitness_plan(
            current_user_id, goals, duration_weeks, difficulty_level
        )
        
        # 创建AI方案记录
        ai_plan = AIPlan(
            user_id=current_user_id,
            title=plan_content.get('title', f"{difficulty_level}健身方案 - {duration_weeks}周"),
            description=plan_content.get('description', ''),
            goals=goals,
            duration_weeks=duration_weeks,
            difficulty_level=difficulty_level,
            weekly_schedule=plan_content.get('weekly_schedule', {}),
            nutrition_advice=plan_content.get('nutrition_advice', '')
        )
        
        db.session.add(ai_plan)
        db.session.commit()
        
        return jsonify({
            'message': 'AI健身方案生成成功',
            'plan': ai_plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '生成AI健身方案失败'}), 500

def analyze_user_data(user_id):
    """分析用户的历史数据"""
    try:
        # 获取最近30天的饮食数据
        thirty_days_ago = date.today() - timedelta(days=30)
        
        diet_stats = db.session.query(
            func.count(DietRecord.id).label('total_meals'),
            func.avg(DietRecord.quantity).label('avg_quantity')
        ).filter(
            and_(
                DietRecord.user_id == user_id,
                DietRecord.recorded_at >= thirty_days_ago
            )
        ).first()
        
        # 获取最近30天的运动数据
        exercise_stats = db.session.query(
            func.count(ExerciseLog.id).label('total_workouts'),
            func.sum(ExerciseLog.duration_minutes).label('total_duration')
        ).filter(
            and_(
                ExerciseLog.user_id == user_id,
                ExerciseLog.exercised_at >= thirty_days_ago
            )
        ).first()
        
        # 获取用户基本信息
        user = User.query.get(user_id)
        
        return {
            'recent_meals_count': diet_stats.total_meals or 0,
            'avg_meal_quantity': float(diet_stats.avg_quantity or 0),
            'recent_workouts_count': exercise_stats.total_workouts or 0,
            'total_recent_duration': int(exercise_stats.total_duration or 0),
            'experience_level': determine_experience_level(exercise_stats.total_workouts or 0),
            'registration_date': user.created_at.date() if user else None
        }
        
    except Exception as e:
        return {
            'recent_meals_count': 0,
            'avg_meal_quantity': 0,
            'recent_workouts_count': 0,
            'total_recent_duration': 0,
            'experience_level': '新手',
            'registration_date': None
        }

def determine_experience_level(workout_count):
    """根据运动次数确定经验水平"""
    if workout_count >= 20:
        return '有经验'
    elif workout_count >= 5:
        return '初级'
    else:
        return '新手'

def generate_personalized_plan(goals, duration_weeks, difficulty_level, user_analysis):
    """生成个性化的健身方案内容"""
    
    # 根据目标和难度生成训练计划
    weekly_schedule = generate_weekly_schedule(goals, difficulty_level, user_analysis)
    
    # 生成营养建议
    nutrition_advice = generate_nutrition_advice(goals, user_analysis)
    
    # 生成方案描述
    description = f"""这是一个为期{duration_weeks}周的{difficulty_level}健身方案，
专为您的目标："${goals}"而定制。
    
根据您的运动数据分析，我们为您量身打造了这个循序渐进的训练计划。
方案包含了详细的每周训练安排和专业的营养指导，帮助您科学有效地达成健身目标。"""
    
    return {
        'description': description,
        'weekly_schedule': weekly_schedule,
        'nutrition_advice': nutrition_advice
    }

def generate_weekly_schedule(goals, difficulty_level, user_analysis):
    """生成每周训练安排"""
    
    # 根据难度确定训练频率
    if difficulty_level == '初级':
        training_days = 3
        rest_days = ['周二', '周四', '周六', '周日']
    elif difficulty_level == '中级':
        training_days = 4
        rest_days = ['周三', '周日']
    else:  # 高级
        training_days = 5
        rest_days = ['周日']
    
    schedule = {}
    
    # 根据目标调整训练重点
    if '减脂' in goals or '瘦身' in goals:
        focus = 'cardio_heavy'
    elif '增肌' in goals or '力量' in goals:
        focus = 'strength_heavy'
    else:
        focus = 'balanced'
    
    week_days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    
    for i, day in enumerate(week_days):
        if day in rest_days:
            schedule[day] = {
                'type': '休息',
                'activities': ['轻度拉伸', '散步'],
                'duration': 30,
                'intensity': '低'
            }
        else:
            schedule[day] = generate_day_training(i % training_days, focus, difficulty_level)
    
    return schedule

def generate_day_training(day_index, focus, difficulty_level):
    """生成单日训练内容"""
    
    training_templates = {
        'cardio_heavy': [
            {
                'type': '有氧训练',
                'activities': ['跑步', '游泳', '骑行'],
                'duration': 45 if difficulty_level != '初级' else 30,
                'intensity': '中等' if difficulty_level == '中级' else '高'
            },
            {
                'type': '力量训练',
                'activities': ['俯卧撑', '深蹲', '平板支撑'],
                'duration': 20,
                'intensity': '中等'
            }
        ],
        'strength_heavy': [
            {
                'type': '力量训练',
                'activities': ['深蹲', '硬拉', '卧推', '引体向上'],
                'duration': 50,
                'intensity': '高' if difficulty_level == '高级' else '中等'
            },
            {
                'type': '核心训练',
                'activities': ['平板支撑', '卷腹', '俄罗斯转体'],
                'duration': 15,
                'intensity': '中等'
            }
        ],
        'balanced': [
            {
                'type': '综合训练',
                'activities': ['热身跑步', '力量循环', '拉伸放松'],
                'duration': 40,
                'intensity': '中等'
            }
        ]
    }
    
    templates = training_templates.get(focus, training_templates['balanced'])
    return templates[day_index % len(templates)]

def generate_nutrition_advice(goals, user_analysis):
    """生成营养建议"""
    
    base_advice = """
## 营养建议

### 基本原则
- 保持规律饮食，每天三餐定时定量
- 充足饮水，每天至少8杯水
- 控制油盐糖的摄入
- 选择新鲜天然的食材

### 三餐分配
- 早餐：占全天热量的30%，注重蛋白质摄入
- 午餐：占全天热量的40%，营养均衡
- 晚餐：占全天热量的30%，相对清淡
"""
    
    if '减脂' in goals or '瘦身' in goals:
        specific_advice = """
### 减脂期特别建议
- 控制总热量摄入，创造合理的热量缺口
- 增加蛋白质比例，保持肌肉量
- 选择低GI碳水化合物
- 多吃绿叶蔬菜，增加饱腹感
- 避免高糖高脂零食和饮料
"""
    elif '增肌' in goals or '力量' in goals:
        specific_advice = """
### 增肌期特别建议
- 适当增加热量摄入，支持肌肉生长
- 提高蛋白质比例，每公斤体重1.6-2.2g
- 训练前后补充优质蛋白
- 保证充足碳水化合物，提供训练能量
- 适量健康脂肪，维持激素水平
"""
    else:
        specific_advice = """
### 健康维持建议
- 保持均衡的营养结构
- 根据运动量调整热量摄入
- 注重微量营养素的补充
- 保持良好的饮食习惯
"""
    
    return base_advice + specific_advice

@ai_plan_bp.route('/plans', methods=['GET'])
@jwt_required()
def get_ai_plans():
    """获取用户的AI健身方案列表"""
    try:
        current_user_id = get_jwt_identity()
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        is_active = request.args.get('active')
        
        # 构建查询
        query = AIPlan.query.filter(AIPlan.user_id == current_user_id)
        
        if is_active is not None:
            active_filter = is_active.lower() == 'true'
            query = query.filter(AIPlan.is_active == active_filter)
        
        # 按创建时间倒序排列
        query = query.order_by(desc(AIPlan.created_at))
        
        # 分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        plans = pagination.items
        
        return jsonify({
            'plans': [plan.to_dict() for plan in plans],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': '获取AI健身方案失败'}), 500

@ai_plan_bp.route('/plans/<int:plan_id>', methods=['GET'])
@jwt_required()
def get_ai_plan(plan_id):
    """获取特定AI健身方案详情"""
    try:
        current_user_id = get_jwt_identity()
        
        plan = AIPlan.query.filter_by(id=plan_id, user_id=current_user_id).first()
        if not plan:
            return jsonify({'error': '健身方案不存在'}), 404
        
        return jsonify({
            'plan': plan.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': '获取健身方案详情失败'}), 500

@ai_plan_bp.route('/plans/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_ai_plan(plan_id):
    """更新AI健身方案"""
    try:
        current_user_id = get_jwt_identity()
        
        plan = AIPlan.query.filter_by(id=plan_id, user_id=current_user_id).first()
        if not plan:
            return jsonify({'error': '健身方案不存在'}), 404
        
        data = request.get_json()
        
        # 更新允许的字段
        if 'title' in data:
            plan.title = data['title'].strip()
        
        if 'is_active' in data:
            plan.is_active = bool(data['is_active'])
        
        if 'notes' in data:
            # 可以添加备注字段到模型中
            pass
        
        db.session.commit()
        
        return jsonify({
            'message': '健身方案更新成功',
            'plan': plan.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '更新健身方案失败'}), 500

@ai_plan_bp.route('/plans/<int:plan_id>', methods=['DELETE'])
@jwt_required()
def delete_ai_plan(plan_id):
    """删除AI健身方案"""
    try:
        current_user_id = get_jwt_identity()
        
        plan = AIPlan.query.filter_by(id=plan_id, user_id=current_user_id).first()
        if not plan:
            return jsonify({'error': '健身方案不存在'}), 404
        
        db.session.delete(plan)
        db.session.commit()
        
        return jsonify({'message': '健身方案删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除健身方案失败'}), 500

@ai_plan_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """获取个性化推荐"""
    try:
        current_user_id = get_jwt_identity()
        
        # 获取AI服务
        ai_svc = get_ai_service()
        if not ai_svc:
            return jsonify({'error': 'AI服务暂时不可用，请稍后重试'}), 503
        
        # 使用AI生成智能推荐
        recommendations = ai_svc.get_intelligent_recommendations(current_user_id)
        
        # 获取用户分析数据
        user_analysis = ai_svc.analyze_user_data(current_user_id)
        
        return jsonify({
            'recommendations': recommendations,
            'based_on': {
                'recent_workouts': user_analysis.get('exercise_analysis', {}).get('total_workouts', 0),
                'experience_level': user_analysis.get('overall_trends', {}).get('activity_level', '未知'),
                'consistency_score': user_analysis.get('overall_trends', {}).get('consistency_score', 0),
                'analysis_date': date.today().isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': '获取推荐失败'}), 500

def generate_recommendations(user_analysis):
    """生成个性化推荐"""
    
    recommendations = []
    
    # 基于运动经验的推荐
    if user_analysis['experience_level'] == '新手':
        recommendations.append({
            'type': 'training',
            'title': '新手入门建议',
            'content': '建议从基础动作开始，掌握正确姿势，逐步增加训练强度。',
            'priority': 'high'
        })
    elif user_analysis['experience_level'] == '有经验':
        recommendations.append({
            'type': 'training',
            'title': '进阶训练建议',
            'content': '可以尝试更高强度的训练组合，加入更多变化性的动作。',
            'priority': 'medium'
        })
    
    # 基于运动频率的推荐
    if user_analysis['recent_workouts_count'] < 4:
        recommendations.append({
            'type': 'consistency',
            'title': '提升运动频率',
            'content': '建议每周至少运动3-4次，保持运动的连续性。',
            'priority': 'high'
        })
    
    # 基于饮食记录的推荐
    if user_analysis['recent_meals_count'] < 20:
        recommendations.append({
            'type': 'nutrition',
            'title': '加强饮食记录',
            'content': '建议坚持记录每日饮食，更好地控制营养摄入。',
            'priority': 'medium'
        })
    
    return recommendations
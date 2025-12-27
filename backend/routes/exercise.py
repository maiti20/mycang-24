from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Exercise, ExerciseLog
from datetime import date, datetime, timedelta
from sqlalchemy import func, and_, desc

exercise_bp = Blueprint('exercise', __name__, url_prefix='/api/exercise')

@exercise_bp.route('/exercises', methods=['GET'])
def get_exercises():
    """获取运动列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('limit', 20, type=int), 100)
        category = request.args.get('category')
        difficulty_level = request.args.get('difficulty_level')
        muscle_group = request.args.get('muscle_group')
        search = request.args.get('search', '').strip()

        # 构建查询
        query = Exercise.query

        if category:
            query = query.filter(Exercise.category == category)

        if difficulty_level:
            query = query.filter(Exercise.difficulty_level == difficulty_level)

        if muscle_group:
            query = query.filter(Exercise.muscle_groups.contains(muscle_group))

        if search:
            query = query.filter(Exercise.name.contains(search))

        # 分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        exercises = pagination.items

        return jsonify({
            'success': True,
            'data': {
                'exercises': [exercise.to_dict() for exercise in exercises],
                'pagination': {
                    'page': page,
                    'limit': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': '获取运动列表失败'}), 500

@exercise_bp.route('/exercise-logs', methods=['GET'])
@jwt_required()
def get_all_exercise_logs():
    """获取运动记录列表（前端调用）"""
    try:
        current_user_id = get_jwt_identity()

        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('limit', 20, type=int), 100)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        exercise_id = request.args.get('exercise_id')

        # 构建查询
        query = ExerciseLog.query.filter(ExerciseLog.user_id == current_user_id)

        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(ExerciseLog.exercised_at >= date_from_obj)
            except ValueError:
                pass

        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(ExerciseLog.exercised_at <= date_to_obj)
            except ValueError:
                pass

        if exercise_id:
            query = query.filter(ExerciseLog.exercise_id == int(exercise_id))

        # 按日期倒序排列
        query = query.order_by(desc(ExerciseLog.exercised_at), desc(ExerciseLog.created_at))

        # 分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        logs = pagination.items

        return jsonify({
            'success': True,
            'data': {
                'logs': [log.to_dict() for log in logs],
                'pagination': {
                    'page': page,
                    'limit': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': '获取运动记录失败'}), 500

@exercise_bp.route('/exercise-logs', methods=['POST'])
@jwt_required()
def create_exercise_log_public():
    """创建运动记录（前端调用）"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # 验证必填字段
        if not data or not data.get('exercise_id') or not data.get('duration_minutes'):
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400

        exercise_id = data['exercise_id']
        duration_minutes = data['duration_minutes']

        # 验证数据有效性
        if duration_minutes <= 0:
            return jsonify({'success': False, 'error': '运动时长必须大于0'}), 400

        # 验证运动是否存在
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return jsonify({'success': False, 'error': '运动项目不存在'}), 404

        # 创建运动日志
        exercise_log = ExerciseLog(
            user_id=current_user_id,
            exercise_id=exercise_id,
            duration_minutes=duration_minutes,
            intensity_level=data.get('intensity_level', '中等'),
            notes=data.get('notes', ''),
            exercised_at=datetime.now().date()
        )

        db.session.add(exercise_log)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '运动记录创建成功',
            'data': exercise_log.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': '创建运动记录失败'}), 500

@exercise_bp.route('/exercise-logs/<int:log_id>', methods=['PUT'])
@jwt_required()
def update_exercise_log_public(log_id):
    """更新运动记录（前端调用）"""
    try:
        current_user_id = get_jwt_identity()

        log = ExerciseLog.query.filter_by(id=log_id, user_id=current_user_id).first()
        if not log:
            return jsonify({'success': False, 'error': '运动记录不存在'}), 404

        data = request.get_json()

        if 'duration_minutes' in data:
            log.duration_minutes = data['duration_minutes']
        if 'intensity_level' in data:
            log.intensity_level = data['intensity_level']
        if 'notes' in data:
            log.notes = data['notes']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '运动记录更新成功',
            'data': log.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': '更新运动记录失败'}), 500

@exercise_bp.route('/exercise-logs/<int:log_id>', methods=['DELETE'])
@jwt_required()
def delete_exercise_log_public(log_id):
    """删除运动记录（前端调用）"""
    try:
        current_user_id = get_jwt_identity()

        log = ExerciseLog.query.filter_by(id=log_id, user_id=current_user_id).first()
        if not log:
            return jsonify({'success': False, 'error': '运动记录不存在'}), 404

        db.session.delete(log)
        db.session.commit()

        return jsonify({'success': True, 'message': '运动记录删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': '删除运动记录失败'}), 500

@exercise_bp.route('/library', methods=['GET'])
@jwt_required()
def get_exercise_library():
    """获取运动库列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        muscle_group = request.args.get('muscle_group')
        search = request.args.get('search', '').strip()
        
        # 构建查询
        query = Exercise.query
        
        if category:
            query = query.filter(Exercise.category == category)
        
        if difficulty:
            query = query.filter(Exercise.difficulty_level == difficulty)
        
        if muscle_group:
            query = query.filter(Exercise.muscle_groups.contains(muscle_group))
        
        if search:
            query = query.filter(Exercise.name.contains(search))
        
        # 分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        exercises = pagination.items
        
        return jsonify({
            'exercises': [exercise.to_dict() for exercise in exercises],
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
        return jsonify({'error': '获取运动库失败'}), 500

@exercise_bp.route('/library/filters', methods=['GET'])
@jwt_required()
def get_exercise_filters():
    """获取运动库筛选选项"""
    try:
        # 获取所有分类
        categories = db.session.query(Exercise.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        # 获取所有难度级别
        difficulties = db.session.query(Exercise.difficulty_level).distinct().all()
        difficulty_list = [diff[0] for diff in difficulties if diff[0]]
        
        # 获取所有肌群（去重）
        all_muscle_groups = []
        exercises = Exercise.query.all()
        for exercise in exercises:
            if exercise.muscle_groups:
                groups = [group.strip() for group in exercise.muscle_groups.split(',')]
                all_muscle_groups.extend(groups)
        
        muscle_groups = sorted(list(set(all_muscle_groups)))
        
        return jsonify({
            'categories': sorted(category_list),
            'difficulties': sorted(difficulty_list),
            'muscle_groups': muscle_groups
        }), 200
        
    except Exception as e:
        return jsonify({'error': '获取筛选选项失败'}), 500

@exercise_bp.route('/logs', methods=['POST'])
@jwt_required()
def create_exercise_log():
    """创建运动日志"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['exercise_id', 'duration_minutes', 'exercised_at']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} 不能为空'}), 400
        
        exercise_id = data['exercise_id']
        duration_minutes = data['duration_minutes']
        exercised_at_str = data['exercised_at']
        
        # 验证数据有效性
        if duration_minutes <= 0:
            return jsonify({'error': '运动时长必须大于0'}), 400
        
        # 解析日期
        try:
            exercised_at = datetime.strptime(exercised_at_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '日期格式无效，请使用 YYYY-MM-DD 格式'}), 400
        
        # 验证运动是否存在
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return jsonify({'error': '运动项目不存在'}), 404
        
        # 可选字段验证
        sets = data.get('sets')
        reps = data.get('reps')
        weight = data.get('weight')
        notes = data.get('notes', '').strip()
        
        if sets is not None and sets <= 0:
            return jsonify({'error': '组数必须大于0'}), 400
        
        if reps is not None and reps <= 0:
            return jsonify({'error': '次数必须大于0'}), 400
        
        if weight is not None and weight < 0:
            return jsonify({'error': '重量不能为负数'}), 400
        
        # 创建运动日志
        exercise_log = ExerciseLog(
            user_id=current_user_id,
            exercise_id=exercise_id,
            duration_minutes=duration_minutes,
            sets=sets,
            reps=reps,
            weight=weight,
            notes=notes,
            exercised_at=exercised_at
        )
        
        db.session.add(exercise_log)
        db.session.commit()
        
        return jsonify({
            'message': '运动日志创建成功',
            'log': exercise_log.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '创建运动日志失败'}), 500

@exercise_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_exercise_logs():
    """获取运动日志列表"""
    try:
        current_user_id = get_jwt_identity()
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        exercise_category = request.args.get('category')
        
        # 构建查询
        query = ExerciseLog.query.filter(ExerciseLog.user_id == current_user_id)
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(ExerciseLog.exercised_at >= start_date_obj)
            except ValueError:
                return jsonify({'error': '开始日期格式无效'}), 400
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(ExerciseLog.exercised_at <= end_date_obj)
            except ValueError:
                return jsonify({'error': '结束日期格式无效'}), 400
        
        if exercise_category:
            query = query.join(Exercise).filter(Exercise.category == exercise_category)
        
        # 按日期倒序排列
        query = query.order_by(desc(ExerciseLog.exercised_at), desc(ExerciseLog.created_at))
        
        # 分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        logs = pagination.items
        
        return jsonify({
            'logs': [log.to_dict() for log in logs],
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
        return jsonify({'error': '获取运动日志失败'}), 500

@exercise_bp.route('/logs/<int:log_id>', methods=['PUT'])
@jwt_required()
def update_exercise_log(log_id):
    """更新运动日志"""
    try:
        current_user_id = get_jwt_identity()
        
        # 查找日志
        log = ExerciseLog.query.filter_by(id=log_id, user_id=current_user_id).first()
        if not log:
            return jsonify({'error': '运动日志不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'duration_minutes' in data:
            duration = data['duration_minutes']
            if duration <= 0:
                return jsonify({'error': '运动时长必须大于0'}), 400
            log.duration_minutes = duration
        
        if 'sets' in data:
            sets = data['sets']
            if sets is not None and sets <= 0:
                return jsonify({'error': '组数必须大于0'}), 400
            log.sets = sets
        
        if 'reps' in data:
            reps = data['reps']
            if reps is not None and reps <= 0:
                return jsonify({'error': '次数必须大于0'}), 400
            log.reps = reps
        
        if 'weight' in data:
            weight = data['weight']
            if weight is not None and weight < 0:
                return jsonify({'error': '重量不能为负数'}), 400
            log.weight = weight
        
        if 'notes' in data:
            log.notes = data['notes'].strip()
        
        if 'exercised_at' in data:
            exercised_at_str = data['exercised_at']
            try:
                exercised_at = datetime.strptime(exercised_at_str, '%Y-%m-%d').date()
                log.exercised_at = exercised_at
            except ValueError:
                return jsonify({'error': '日期格式无效，请使用 YYYY-MM-DD 格式'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': '运动日志更新成功',
            'log': log.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '更新运动日志失败'}), 500

@exercise_bp.route('/logs/<int:log_id>', methods=['DELETE'])
@jwt_required()
def delete_exercise_log(log_id):
    """删除运动日志"""
    try:
        current_user_id = get_jwt_identity()
        
        # 查找日志
        log = ExerciseLog.query.filter_by(id=log_id, user_id=current_user_id).first()
        if not log:
            return jsonify({'error': '运动日志不存在'}), 404
        
        db.session.delete(log)
        db.session.commit()
        
        return jsonify({'message': '运动日志删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除运动日志失败'}), 500

@exercise_bp.route('/statistics/daily', methods=['GET'])
@jwt_required()
def get_daily_exercise_statistics():
    """获取每日运动统计"""
    try:
        current_user_id = get_jwt_identity()
        target_date = request.args.get('date')
        
        if not target_date:
            target_date = date.today().isoformat()
        
        try:
            target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '日期格式无效'}), 400
        
        # 查询当日运动日志
        logs = db.session.query(ExerciseLog, Exercise).join(
            Exercise, ExerciseLog.exercise_id == Exercise.id
        ).filter(
            and_(
                ExerciseLog.user_id == current_user_id,
                ExerciseLog.exercised_at == target_date_obj
            )
        ).all()
        
        # 统计数据
        total_duration = sum(log.duration_minutes for log, exercise in logs)
        total_calories = sum(exercise.calories_per_minute * log.duration_minutes for log, exercise in logs)
        
        # 按运动类别统计
        category_stats = {}
        for log, exercise in logs:
            category = exercise.category
            if category not in category_stats:
                category_stats[category] = {
                    'duration': 0,
                    'calories': 0,
                    'count': 0
                }
            category_stats[category]['duration'] += log.duration_minutes
            category_stats[category]['calories'] += exercise.calories_per_minute * log.duration_minutes
            category_stats[category]['count'] += 1
        
        return jsonify({
            'date': target_date,
            'total_duration': total_duration,
            'total_calories': round(total_calories, 2),
            'category_breakdown': category_stats,
            'total_workouts': len(logs)
        }), 200
        
    except Exception as e:
        return jsonify({'error': '获取运动统计失败'}), 500

@exercise_bp.route('/statistics/weekly', methods=['GET'])
@jwt_required()
def get_weekly_exercise_statistics():
    """获取每周运动统计"""
    try:
        current_user_id = get_jwt_identity()
        end_date = request.args.get('end_date')
        
        if not end_date:
            end_date = date.today()
        else:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '结束日期格式无效'}), 400
        
        start_date = end_date - timedelta(days=6)
        
        # 查询一周内的运动日志
        daily_stats = []
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            
            logs = db.session.query(ExerciseLog, Exercise).join(
                Exercise, ExerciseLog.exercise_id == Exercise.id
            ).filter(
                and_(
                    ExerciseLog.user_id == current_user_id,
                    ExerciseLog.exercised_at == current_date
                )
            ).all()
            
            total_duration = sum(log.duration_minutes for log, exercise in logs)
            total_calories = sum(exercise.calories_per_minute * log.duration_minutes for log, exercise in logs)
            
            daily_stats.append({
                'date': current_date.isoformat(),
                'duration': total_duration,
                'calories': round(total_calories, 2),
                'workout_count': len(logs)
            })
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'daily_stats': daily_stats,
            'total_weekly_duration': sum(day['duration'] for day in daily_stats),
            'total_weekly_calories': round(sum(day['calories'] for day in daily_stats), 2),
            'average_daily_duration': round(
                sum(day['duration'] for day in daily_stats) / 7, 2
            ) if daily_stats else 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': '获取周运动统计失败'}), 500

@exercise_bp.route('/favorites', methods=['POST'])
@jwt_required()
def add_favorite_exercise():
    """添加收藏运动（简化版，实际可能需要单独的收藏表）"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'exercise_id' not in data:
            return jsonify({'error': '运动ID不能为空'}), 400
        
        exercise_id = data['exercise_id']
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            return jsonify({'error': '运动项目不存在'}), 404
        
        # 这里简化处理，实际应该有专门的收藏表
        return jsonify({
            'message': '收藏功能待完善',
            'exercise': exercise.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': '添加收藏失败'}), 500
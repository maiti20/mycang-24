from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Food, DietRecord
from datetime import date, datetime, timedelta
from sqlalchemy import func, and_

diet_bp = Blueprint('diet', __name__, url_prefix='/api/diet')

@diet_bp.route('/foods', methods=['GET'])
def get_public_foods():
    """获取食物列表（公开接口）"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('limit', 20, type=int), 100)
        category = request.args.get('category')
        search = request.args.get('search', '').strip()

        # 构建查询
        query = Food.query

        if category:
            query = query.filter(Food.category == category)

        if search:
            query = query.filter(Food.name.contains(search))

        # 分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        foods = pagination.items

        return jsonify({
            'success': True,
            'data': {
                'foods': [food.to_dict() for food in foods],
                'pagination': {
                    'page': page,
                    'limit': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': '获取食物列表失败'}), 500

@diet_bp.route('/diet-records', methods=['GET'])
@jwt_required()
def get_public_diet_records():
    """获取饮食记录列表（前端调用）"""
    try:
        current_user_id = get_jwt_identity()

        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('limit', 20, type=int), 100)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        # 构建查询
        query = DietRecord.query.filter(DietRecord.user_id == current_user_id)

        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(DietRecord.recorded_at >= date_from_obj)
            except ValueError:
                pass

        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(DietRecord.recorded_at <= date_to_obj)
            except ValueError:
                pass

        # 按日期倒序排列
        query = query.order_by(DietRecord.recorded_at.desc(), DietRecord.created_at.desc())

        # 分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        records = pagination.items

        return jsonify({
            'success': True,
            'data': {
                'records': [record.to_dict() for record in records],
                'pagination': {
                    'page': page,
                    'limit': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': '获取饮食记录失败'}), 500

@diet_bp.route('/diet-records', methods=['POST'])
@jwt_required()
def create_public_diet_record():
    """创建饮食记录（前端调用）"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # 验证必填字段
        if not data or not data.get('food_id') or not data.get('quantity'):
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400

        food_id = data['food_id']
        quantity = data['quantity']
        meal_type = data.get('meal_type', '加餐')

        # 验证数据有效性
        if quantity <= 0:
            return jsonify({'success': False, 'error': '摄入量必须大于0'}), 400

        # 验证食物是否存在
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'success': False, 'error': '食物不存在'}), 404

        # 创建饮食记录
        diet_record = DietRecord(
            user_id=current_user_id,
            food_id=food_id,
            quantity=quantity,
            meal_type=meal_type,
            recorded_at=datetime.now().date()
        )

        db.session.add(diet_record)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '饮食记录创建成功',
            'data': diet_record.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': '创建饮食记录失败'}), 500

@diet_bp.route('/diet-records/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_public_diet_record(record_id):
    """更新饮食记录（前端调用）"""
    try:
        current_user_id = get_jwt_identity()

        record = DietRecord.query.filter_by(id=record_id, user_id=current_user_id).first()
        if not record:
            return jsonify({'success': False, 'error': '记录不存在'}), 404

        data = request.get_json()

        if 'quantity' in data:
            record.quantity = data['quantity']
        if 'meal_type' in data:
            record.meal_type = data['meal_type']
        if 'notes' in data:
            record.notes = data['notes']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '饮食记录更新成功',
            'data': record.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': '更新饮食记录失败'}), 500

@diet_bp.route('/diet-records/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_public_diet_record(record_id):
    """删除饮食记录（前端调用）"""
    try:
        current_user_id = get_jwt_identity()

        record = DietRecord.query.filter_by(id=record_id, user_id=current_user_id).first()
        if not record:
            return jsonify({'success': False, 'error': '记录不存在'}), 404

        db.session.delete(record)
        db.session.commit()

        return jsonify({'success': True, 'message': '饮食记录删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': '删除饮食记录失败'}), 500

@diet_bp.route('/foods', methods=['GET'])
@jwt_required()
def get_foods():
    """获取食物列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        category = request.args.get('category')
        search = request.args.get('search', '').strip()
        
        # 构建查询
        query = Food.query
        
        if category:
            query = query.filter(Food.category == category)
        
        if search:
            query = query.filter(Food.name.contains(search))
        
        # 分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        foods = pagination.items
        
        return jsonify({
            'foods': [food.to_dict() for food in foods],
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
        return jsonify({'error': '获取食物列表失败'}), 500

@diet_bp.route('/foods/categories', methods=['GET'])
@jwt_required()
def get_food_categories():
    """获取食物分类列表"""
    try:
        categories = db.session.query(Food.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({
            'categories': sorted(category_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': '获取食物分类失败'}), 500

@diet_bp.route('/records', methods=['POST'])
@jwt_required()
def create_diet_record():
    """创建饮食记录"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['food_id', 'quantity', 'meal_type', 'recorded_at']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} 不能为空'}), 400
        
        food_id = data['food_id']
        quantity = data['quantity']
        meal_type = data['meal_type']
        recorded_at_str = data['recorded_at']
        
        # 验证数据有效性
        if quantity <= 0:
            return jsonify({'error': '摄入量必须大于0'}), 400
        
        if meal_type not in ['早餐', '午餐', '晚餐', '加餐']:
            return jsonify({'error': '餐次类型无效'}), 400
        
        # 解析日期
        try:
            recorded_at = datetime.strptime(recorded_at_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '日期格式无效，请使用 YYYY-MM-DD 格式'}), 400
        
        # 验证食物是否存在
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'error': '食物不存在'}), 404
        
        # 创建饮食记录
        diet_record = DietRecord(
            user_id=current_user_id,
            food_id=food_id,
            quantity=quantity,
            meal_type=meal_type,
            recorded_at=recorded_at
        )
        
        db.session.add(diet_record)
        db.session.commit()
        
        return jsonify({
            'message': '饮食记录创建成功',
            'record': diet_record.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '创建饮食记录失败'}), 500

@diet_bp.route('/records', methods=['GET'])
@jwt_required()
def get_diet_records():
    """获取饮食记录列表"""
    try:
        current_user_id = get_jwt_identity()
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        meal_type = request.args.get('meal_type')
        
        # 构建查询
        query = DietRecord.query.filter(DietRecord.user_id == current_user_id)
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(DietRecord.recorded_at >= start_date_obj)
            except ValueError:
                return jsonify({'error': '开始日期格式无效'}), 400
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(DietRecord.recorded_at <= end_date_obj)
            except ValueError:
                return jsonify({'error': '结束日期格式无效'}), 400
        
        if meal_type:
            query = query.filter(DietRecord.meal_type == meal_type)
        
        # 按日期倒序排列
        query = query.order_by(DietRecord.recorded_at.desc(), DietRecord.created_at.desc())
        
        # 分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        records = pagination.items
        
        return jsonify({
            'records': [record.to_dict() for record in records],
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
        return jsonify({'error': '获取饮食记录失败'}), 500

@diet_bp.route('/records/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_diet_record(record_id):
    """更新饮食记录"""
    try:
        current_user_id = get_jwt_identity()
        
        # 查找记录
        record = DietRecord.query.filter_by(id=record_id, user_id=current_user_id).first()
        if not record:
            return jsonify({'error': '记录不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'quantity' in data:
            quantity = data['quantity']
            if quantity <= 0:
                return jsonify({'error': '摄入量必须大于0'}), 400
            record.quantity = quantity
        
        if 'meal_type' in data:
            meal_type = data['meal_type']
            if meal_type not in ['早餐', '午餐', '晚餐', '加餐']:
                return jsonify({'error': '餐次类型无效'}), 400
            record.meal_type = meal_type
        
        if 'recorded_at' in data:
            recorded_at_str = data['recorded_at']
            try:
                recorded_at = datetime.strptime(recorded_at_str, '%Y-%m-%d').date()
                record.recorded_at = recorded_at
            except ValueError:
                return jsonify({'error': '日期格式无效，请使用 YYYY-MM-DD 格式'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': '饮食记录更新成功',
            'record': record.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '更新饮食记录失败'}), 500

@diet_bp.route('/records/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_diet_record(record_id):
    """删除饮食记录"""
    try:
        current_user_id = get_jwt_identity()
        
        # 查找记录
        record = DietRecord.query.filter_by(id=record_id, user_id=current_user_id).first()
        if not record:
            return jsonify({'error': '记录不存在'}), 404
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({'message': '饮食记录删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除饮食记录失败'}), 500

@diet_bp.route('/statistics/daily', methods=['GET'])
@jwt_required()
def get_daily_statistics():
    """获取每日营养统计"""
    try:
        current_user_id = get_jwt_identity()
        target_date = request.args.get('date')
        
        if not target_date:
            target_date = date.today().isoformat()
        
        try:
            target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '日期格式无效'}), 400
        
        # 查询当日饮食记录
        records = db.session.query(DietRecord, Food).join(
            Food, DietRecord.food_id == Food.id
        ).filter(
            and_(
                DietRecord.user_id == current_user_id,
                DietRecord.recorded_at == target_date_obj
            )
        ).all()
        
        # 统计数据
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_fiber = 0
        
        meal_stats = {
            '早餐': {'calories': 0, 'count': 0},
            '午餐': {'calories': 0, 'count': 0},
            '晚餐': {'calories': 0, 'count': 0},
            '加餐': {'calories': 0, 'count': 0}
        }
        
        for record, food in records:
            multiplier = record.quantity / 100
            
            total_calories += food.calories_per_100g * multiplier
            total_protein += food.protein_g * multiplier
            total_carbs += food.carbs_g * multiplier
            total_fat += food.fat_g * multiplier
            total_fiber += food.fiber_g * multiplier
            
            meal_stats[record.meal_type]['calories'] += food.calories_per_100g * multiplier
            meal_stats[record.meal_type]['count'] += 1
        
        return jsonify({
            'date': target_date,
            'total_nutrition': {
                'calories': round(total_calories, 2),
                'protein': round(total_protein, 2),
                'carbs': round(total_carbs, 2),
                'fat': round(total_fat, 2),
                'fiber': round(total_fiber, 2)
            },
            'meal_breakdown': meal_stats,
            'total_records': len(records)
        }), 200
        
    except Exception as e:
        return jsonify({'error': '获取统计数据失败'}), 500

@diet_bp.route('/statistics/weekly', methods=['GET'])
@jwt_required()
def get_weekly_statistics():
    """获取每周营养统计"""
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
        
        # 查询一周内的饮食记录
        daily_stats = []
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            
            records = db.session.query(DietRecord, Food).join(
                Food, DietRecord.food_id == Food.id
            ).filter(
                and_(
                    DietRecord.user_id == current_user_id,
                    DietRecord.recorded_at == current_date
                )
            ).all()
            
            total_calories = sum(
                (food.calories_per_100g * record.quantity / 100) 
                for record, food in records
            )
            
            daily_stats.append({
                'date': current_date.isoformat(),
                'calories': round(total_calories, 2),
                'records_count': len(records)
            })
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'daily_stats': daily_stats,
            'average_daily_calories': round(
                sum(day['calories'] for day in daily_stats) / 7, 2
            ) if daily_stats else 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': '获取周统计数据失败'}), 500
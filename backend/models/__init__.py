from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    diet_records = db.relationship('DietRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    exercise_logs = db.relationship('ExerciseLog', backref='user', lazy=True, cascade='all, delete-orphan')
    ai_plans = db.relationship('AIPlan', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """设置密码"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        """验证密码"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Food(db.Model):
    """食物模型"""
    __tablename__ = 'food'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    calories_per_100g = db.Column(db.Float, nullable=False)
    protein_g = db.Column(db.Float, default=0)
    carbs_g = db.Column(db.Float, default=0)
    fat_g = db.Column(db.Float, default=0)
    fiber_g = db.Column(db.Float, default=0)
    category = db.Column(db.String(50))  # 分类：主食、蔬菜、水果、肉类等
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'calories_per_100g': self.calories_per_100g,
            'protein_g': self.protein_g,
            'carbs_g': self.carbs_g,
            'fat_g': self.fat_g,
            'fiber_g': self.fiber_g,
            'category': self.category
        }

class DietRecord(db.Model):
    """饮食记录模型"""
    __tablename__ = 'diet_record'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # 摄入量(克)
    meal_type = db.Column(db.String(20), nullable=False)  # 早餐、午餐、晚餐、加餐
    recorded_at = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联食物信息
    food = db.relationship('Food', backref='diet_records')
    
    @property
    def total_calories(self):
        """计算总热量"""
        return (self.food.calories_per_100g * self.quantity) / 100
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'food_id': self.food_id,
            'quantity': self.quantity,
            'meal_type': self.meal_type,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'total_calories': self.total_calories,
            'food': self.food.to_dict() if self.food else None
        }

class Exercise(db.Model):
    """运动模型"""
    __tablename__ = 'exercise'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    muscle_groups = db.Column(db.String(200))  # 目标肌群
    equipment_needed = db.Column(db.String(200))  # 所需器材
    difficulty_level = db.Column(db.String(20))  # 初级、中级、高级
    calories_per_minute = db.Column(db.Float, default=0)  # 每分钟消耗热量
    video_url = db.Column(db.String(500))  # 教学视频链接
    image_url = db.Column(db.String(500))  # 示意图链接
    category = db.Column(db.String(50))  # 分类：有氧、力量、拉伸等
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'muscle_groups': self.muscle_groups,
            'equipment_needed': self.equipment_needed,
            'difficulty_level': self.difficulty_level,
            'calories_per_minute': self.calories_per_minute,
            'video_url': self.video_url,
            'image_url': self.image_url,
            'category': self.category
        }

class ExerciseLog(db.Model):
    """运动日志模型"""
    __tablename__ = 'exercise_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer)  # 组数
    reps = db.Column(db.Integer)  # 次数
    weight = db.Column(db.Float)  # 重量(kg)
    notes = db.Column(db.Text)  # 备注
    exercised_at = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联运动信息
    exercise = db.relationship('Exercise', backref='exercise_logs')
    
    @property
    def total_calories(self):
        """计算总消耗热量"""
        return self.exercise.calories_per_minute * self.duration_minutes
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exercise_id': self.exercise_id,
            'duration_minutes': self.duration_minutes,
            'sets': self.sets,
            'reps': self.reps,
            'weight': self.weight,
            'notes': self.notes,
            'exercised_at': self.exercised_at.isoformat() if self.exercised_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'total_calories': self.total_calories,
            'exercise': self.exercise.to_dict() if self.exercise else None
        }

class AIPlan(db.Model):
    """AI健身方案模型"""
    __tablename__ = 'ai_plan'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    goals = db.Column(db.String(500))  # 健身目标
    duration_weeks = db.Column(db.Integer)  # 计划周期(周)
    difficulty_level = db.Column(db.String(20))
    weekly_schedule = db.Column(db.JSON)  # 每周训练安排(JSON格式)
    nutrition_advice = db.Column(db.Text)  # 营养建议
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'goals': self.goals,
            'duration_weeks': self.duration_weeks,
            'difficulty_level': self.difficulty_level,
            'weekly_schedule': self.weekly_schedule,
            'nutrition_advice': self.nutrition_advice,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
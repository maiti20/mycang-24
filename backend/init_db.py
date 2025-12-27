#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表和插入初始数据
"""

import sys
import os
from datetime import date, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Food, Exercise

def init_database():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        print("正在创建数据库表...")
        db.create_all()
        print("数据库表创建完成！")
        
        # 插入初始食物数据
        print("正在插入食物数据...")
        foods_data = [
            # 主食类
            {"name": "米饭", "calories_per_100g": 116, "protein_g": 2.6, "carbs_g": 25.9, "fat_g": 0.3, "fiber_g": 0.4, "category": "主食"},
            {"name": "全麦面包", "calories_per_100g": 247, "protein_g": 13.2, "carbs_g": 41.0, "fat_g": 4.2, "fiber_g": 6.8, "category": "主食"},
            {"name": "燕麦片", "calories_per_100g": 389, "protein_g": 16.9, "carbs_g": 66.3, "fat_g": 6.9, "fiber_g": 10.6, "category": "主食"},
            
            # 蛋白质类
            {"name": "鸡胸肉", "calories_per_100g": 165, "protein_g": 31.0, "carbs_g": 0, "fat_g": 3.6, "fiber_g": 0, "category": "蛋白质"},
            {"name": "鸡蛋", "calories_per_100g": 155, "protein_g": 13.0, "carbs_g": 1.1, "fat_g": 11.0, "fiber_g": 0, "category": "蛋白质"},
            {"name": "三文鱼", "calories_per_100g": 208, "protein_g": 20.0, "carbs_g": 0, "fat_g": 13.0, "fiber_g": 0, "category": "蛋白质"},
            {"name": "豆腐", "calories_per_100g": 76, "protein_g": 8.1, "carbs_g": 1.9, "fat_g": 4.8, "fiber_g": 0.4, "category": "蛋白质"},
            
            # 蔬菜类
            {"name": "西兰花", "calories_per_100g": 34, "protein_g": 2.8, "carbs_g": 7.0, "fat_g": 0.4, "fiber_g": 2.6, "category": "蔬菜"},
            {"name": "菠菜", "calories_per_100g": 23, "protein_g": 2.9, "carbs_g": 3.6, "fat_g": 0.4, "fiber_g": 2.2, "category": "蔬菜"},
            {"name": "胡萝卜", "calories_per_100g": 41, "protein_g": 0.9, "carbs_g": 10.0, "fat_g": 0.2, "fiber_g": 2.8, "category": "蔬菜"},
            {"name": "番茄", "calories_per_100g": 18, "protein_g": 0.9, "carbs_g": 3.9, "fat_g": 0.2, "fiber_g": 1.2, "category": "蔬菜"},
            
            # 水果类
            {"name": "苹果", "calories_per_100g": 52, "protein_g": 0.3, "carbs_g": 14.0, "fat_g": 0.2, "fiber_g": 2.4, "category": "水果"},
            {"name": "香蕉", "calories_per_100g": 89, "protein_g": 1.1, "carbs_g": 23.0, "fat_g": 0.3, "fiber_g": 2.6, "category": "水果"},
            {"name": "橙子", "calories_per_100g": 47, "protein_g": 0.9, "carbs_g": 12.0, "fat_g": 0.1, "fiber_g": 2.4, "category": "水果"},
            {"name": "蓝莓", "calories_per_100g": 57, "protein_g": 0.7, "carbs_g": 14.0, "fat_g": 0.3, "fiber_g": 2.4, "category": "水果"},
            
            # 坚果类
            {"name": "杏仁", "calories_per_100g": 579, "protein_g": 21.0, "carbs_g": 22.0, "fat_g": 50.0, "fiber_g": 12.5, "category": "坚果"},
            {"name": "核桃", "calories_per_100g": 654, "protein_g": 15.0, "carbs_g": 14.0, "fat_g": 65.0, "fiber_g": 6.7, "category": "坚果"},
        ]
        
        for food_data in foods_data:
            existing_food = Food.query.filter_by(name=food_data['name']).first()
            if not existing_food:
                food = Food(**food_data)
                db.session.add(food)
        
        db.session.commit()
        print(f"已插入 {len(foods_data)} 种食物数据！")
        
        # 插入初始运动数据
        print("正在插入运动数据...")
        exercises_data = [
            # 有氧运动
            {
                "name": "跑步",
                "description": "最经典的有氧运动，能够有效提高心肺功能和燃烧脂肪",
                "muscle_groups": "全身,腿部,核心",
                "equipment_needed": "跑鞋",
                "difficulty_level": "初级",
                "calories_per_minute": 10.0,
                "video_url": "https://example.com/running",
                "category": "有氧"
            },
            {
                "name": "游泳",
                "description": "全身性低冲击运动，适合各个年龄段的人群",
                "muscle_groups": "全身,肩部,背部,腿部",
                "equipment_needed": "游泳池,泳衣",
                "difficulty_level": "中级",
                "calories_per_minute": 11.0,
                "video_url": "https://example.com/swimming",
                "category": "有氧"
            },
            {
                "name": "骑行",
                "description": "低冲击有氧运动，能够增强下肢力量和耐力",
                "muscle_groups": "腿部,臀部,核心",
                "equipment_needed": "自行车",
                "difficulty_level": "初级",
                "calories_per_minute": 8.0,
                "video_url": "https://example.com/cycling",
                "category": "有氧"
            },
            
            # 力量训练
            {
                "name": "俯卧撑",
                "description": "经典的上肢力量训练动作，主要锻炼胸部、肩膀和手臂",
                "muscle_groups": "胸部,肩膀,手臂,核心",
                "equipment_needed": "无",
                "difficulty_level": "初级",
                "calories_per_minute": 7.0,
                "video_url": "https://example.com/pushup",
                "category": "力量"
            },
            {
                "name": "深蹲",
                "description": "下肢力量训练之王，全面锻炼腿部和臀部肌肉",
                "muscle_groups": "腿部,臀部,核心",
                "equipment_needed": "无",
                "difficulty_level": "初级",
                "calories_per_minute": 6.0,
                "video_url": "https://example.com/squat",
                "category": "力量"
            },
            {
                "name": "引体向上",
                "description": "上肢拉力训练，主要锻炼背阔肌和手臂",
                "muscle_groups": "背部,手臂,肩膀",
                "equipment_needed": "单杠",
                "difficulty_level": "高级",
                "calories_per_minute": 8.0,
                "video_url": "https://example.com/pullup",
                "category": "力量"
            },
            {
                "name": "平板支撑",
                "description": "核心稳定性训练，强化腹部和下背部肌肉",
                "muscle_groups": "核心,腹部,背部",
                "equipment_needed": "瑜伽垫",
                "difficulty_level": "初级",
                "calories_per_minute": 5.0,
                "video_url": "https://example.com/plank",
                "category": "力量"
            },
            
            # 拉伸运动
            {
                "name": "瑜伽",
                "description": "身心结合的运动，提高柔韧性和平衡能力",
                "muscle_groups": "全身",
                "equipment_needed": "瑜伽垫",
                "difficulty_level": "初级",
                "calories_per_minute": 3.0,
                "video_url": "https://example.com/yoga",
                "category": "拉伸"
            },
            {
                "name": "拉伸放松",
                "description": "运动后的恢复性拉伸，预防肌肉酸痛",
                "muscle_groups": "全身",
                "equipment_needed": "无",
                "difficulty_level": "初级",
                "calories_per_minute": 2.0,
                "video_url": "https://example.com/stretching",
                "category": "拉伸"
            }
        ]
        
        for exercise_data in exercises_data:
            existing_exercise = Exercise.query.filter_by(name=exercise_data['name']).first()
            if not existing_exercise:
                exercise = Exercise(**exercise_data)
                db.session.add(exercise)
        
        db.session.commit()
        print(f"已插入 {len(exercises_data)} 个运动项目！")
        
        # 创建管理员用户
        print("正在创建管理员用户...")
        admin_user = User(
            username="admin",
            email="admin@fitness.com",
            age=30,
            gender="male",
            height=175,
            weight=70,
            fitness_goal="保持健康"
        )
        admin_user.set_password("admin123")
        
        existing_admin = User.query.filter_by(username="admin").first()
        if not existing_admin:
            db.session.add(admin_user)
            db.session.commit()
            print("管理员用户创建完成！用户名: admin, 密码: admin123")
        else:
            print("管理员用户已存在！")
        
        # 创建测试用户
        print("正在创建测试用户...")
        test_user = User(
            username="testuser",
            email="test@example.com",
            age=25,
            gender="female",
            height=165,
            weight=55,
            fitness_goal="减脂塑形"
        )
        test_user.set_password("password123")
        
        existing_user = User.query.filter_by(username="testuser").first()
        if not existing_user:
            db.session.add(test_user)
            db.session.commit()
            print("测试用户创建完成！用户名: testuser, 密码: password123")
        else:
            print("测试用户已存在！")
        
        print("\n数据库初始化完成！")

if __name__ == "__main__":
    init_database()
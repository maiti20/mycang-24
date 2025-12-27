"""
AI服务模块
负责与OpenAI GPT模型对接，提供智能健身方案生成和个性化推荐服务
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import date, datetime, timedelta
from models import db, DietRecord, ExerciseLog, User


class AIService:
    """AI服务类，封装与大语言模型的交互"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = os.getenv('AI_BASE_URL', 'https://api.openai.com/v1')
        self.model = os.getenv('AI_MODEL', 'gpt-3.5-turbo')

        if not self.api_key:
            raise ValueError("OpenAI API key 未配置，请在.env文件中设置OPENAI_API_KEY")

        print(f"[AI服务] AI服务初始化成功 - 模型: {self.model}")
    
    def _make_api_request(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """发送API请求到OpenAI"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': 2000
        }

        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                error_msg = f"API请求失败: {response.status_code} - {response.text}"
                print(f"[AI服务] {error_msg}")
                return self._get_fallback_response()

        except requests.exceptions.Timeout:
            print(f"[AI服务] API请求超时")
            return self._get_fallback_response()
        except requests.exceptions.RequestException as e:
            print(f"[AI服务] 网络请求异常: {e}")
            return self._get_fallback_response()
        except Exception as e:
            print(f"[AI服务] 未知错误: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """获取备用响应，当API调用失败时使用"""
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
    
    def analyze_user_data(self, user_id: int) -> Dict[str, Any]:
        """深度分析用户数据"""
        try:
            # 获取用户基本信息
            user = User.query.get(user_id)
            if not user:
                return {}
            
            # 获取最近30天的数据
            thirty_days_ago = date.today() - timedelta(days=30)
            
            # 饮食数据分析
            diet_records = db.session.query(DietRecord).filter(
                DietRecord.user_id == user_id,
                DietRecord.recorded_at >= thirty_days_ago
            ).all()
            
            # 运动数据分析
            exercise_logs = db.session.query(ExerciseLog).filter(
                ExerciseLog.user_id == user_id,
                ExerciseLog.exercised_at >= thirty_days_ago
            ).all()
            
            # 计算统计数据
            total_calories_consumed = sum(
                record.total_calories for record in diet_records
            )
            total_calories_burned = sum(
                log.total_calories for log in exercise_logs
            )
            
            avg_daily_calories = total_calories_consumed / 30 if diet_records else 0
            workout_frequency = len(set(log.exercised_at for log in exercise_logs))
            
            # 分析偏好
            meal_preferences = {}
            for record in diet_records:
                meal_type = record.meal_type
                if meal_type not in meal_preferences:
                    meal_preferences[meal_type] = 0
                meal_preferences[meal_type] += 1
            
            exercise_preferences = {}
            for log in exercise_logs:
                if log.exercise:
                    category = log.exercise.category
                    if category not in exercise_preferences:
                        exercise_preferences[category] = 0
                    exercise_preferences[category] += 1
            
            return {
                'user_info': {
                    'id': user.id,
                    'username': user.username,
                    'registration_date': user.created_at.date(),
                    'days_since_registration': (date.today() - user.created_at.date()).days
                },
                'diet_analysis': {
                    'total_records': len(diet_records),
                    'total_calories': round(total_calories_consumed, 2),
                    'avg_daily_calories': round(avg_daily_calories, 2),
                    'meal_preferences': meal_preferences
                },
                'exercise_analysis': {
                    'total_workouts': len(exercise_logs),
                    'total_calories_burned': round(total_calories_burned, 2),
                    'workout_frequency': workout_frequency,
                    'exercise_preferences': exercise_preferences
                },
                'overall_trends': {
                    'net_calories': round(total_calories_consumed - total_calories_burned, 2),
                    'activity_level': self._assess_activity_level(workout_frequency),
                    'consistency_score': self._calculate_consistency_score(diet_records, exercise_logs)
                }
            }
            
        except Exception as e:
            print(f"用户数据分析失败: {e}")
            return {}
    
    def _assess_activity_level(self, workout_frequency: int) -> str:
        """评估活动水平"""
        if workout_frequency >= 20:
            return "非常活跃"
        elif workout_frequency >= 12:
            return "活跃"
        elif workout_frequency >= 6:
            return "中等活跃"
        elif workout_frequency >= 3:
            return "轻度活跃"
        else:
            return "久坐"
    
    def _calculate_consistency_score(self, diet_records: List, exercise_logs: List) -> float:
        """计算一致性评分"""
        # 简化的一致性评分算法
        diet_days = len(set(record.recorded_at for record in diet_records))
        exercise_days = len(set(log.exercised_at for log in exercise_logs))
        
        # 过去30天的一致性
        consistency_score = ((diet_days + exercise_days) / 60) * 100
        return min(round(consistency_score, 1), 100)
    
    def generate_personalized_fitness_plan(self, user_id: int, goals: str, duration_weeks: int, difficulty_level: str) -> Dict[str, Any]:
        """使用AI生成个性化健身方案"""
        try:
            print(f"[AI服务] 开始为用户 {user_id} 生成个性化健身方案")
            print(f"[AI服务] 目标: {goals}, 时长: {duration_weeks}周, 难度: {difficulty_level}")

            # 分析用户数据
            user_analysis = self.analyze_user_data(user_id)

            # 构建提示词
            system_prompt = self._build_system_prompt(user_analysis, goals, duration_weeks, difficulty_level)
            user_prompt = self._build_user_prompt(goals, duration_weeks, difficulty_level, user_analysis)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # 调用AI API
            print(f"[AI服务] 正在调用AI API生成方案...")
            ai_response = self._make_api_request(messages, temperature=0.8)

            # 解析AI响应
            structured_plan = self._parse_ai_response(ai_response, goals, duration_weeks, difficulty_level)

            print(f"[AI服务] 个性化健身方案生成成功")
            return structured_plan

        except Exception as e:
            print(f"[AI服务] 生成个性化健身方案失败: {e}")
            return self._get_default_plan(goals, duration_weeks, difficulty_level)
    
    def _build_system_prompt(self, user_analysis: Dict, goals: str, duration_weeks: int, difficulty_level: str) -> str:
        """构建系统提示词"""
        return f"""你是一位专业的健身教练和营养师，拥有丰富的经验。请根据以下信息为用户制定个性化的健身方案。

用户背景信息：
{json.dumps(user_analysis, indent=2, ensure_ascii=False)}

要求：
1. 方案要符合用户的实际情况和偏好
2. 考虑用户的运动经验和习惯
3. 结合用户的饮食模式和运动偏好
4. 制定切实可行的目标和计划
5. 提供科学的营养建议

请用中文回答，格式清晰，内容专业且实用。"""
    
    def _build_user_prompt(self, goals: str, duration_weeks: int, difficulty_level: str, user_analysis: Dict) -> str:
        """构建用户提示词"""
        return f"""请为我制定一个为期{duration_weeks}周的{difficulty_level}健身方案。

我的健身目标：{goals}

请提供以下内容：
1. 详细的训练计划（每周安排）
2. 科学的营养建议
3. 注意事项和建议
4. 进度跟踪方法

请以JSON格式返回，包含以下字段：
- title: 方案标题
- description: 方案描述
- weekly_schedule: 每周训练安排（对象格式，键为星期几）
- nutrition_advice: 营养建议（字符串）
- tips: 注意事项（数组）

weekly_schedule格式示例：
{{
    "周一": {{
        "type": "训练类型",
        "activities": ["动作1", "动作2"],
        "duration": 时长（分钟）,
        "intensity": "强度等级",
        "notes": "注意事项"
    }}
}}

请确保返回的是有效的JSON格式，不要包含任何额外的文字说明，只返回JSON数据。"""
    
    def _parse_ai_response(self, ai_response: str, goals: str, duration_weeks: int, difficulty_level: str) -> Dict[str, Any]:
        """解析AI响应"""
        try:
            # 尝试提取JSON部分
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = ai_response[start_idx:end_idx]
                parsed_data = json.loads(json_str)

                # 确保必要字段存在
                if 'title' not in parsed_data:
                    parsed_data['title'] = f"{difficulty_level}健身方案 - {duration_weeks}周"
                if 'description' not in parsed_data:
                    parsed_data['description'] = f"针对目标'{goals}'制定的{duration_weeks}周{difficulty_level}健身方案"
                if 'weekly_schedule' not in parsed_data:
                    parsed_data['weekly_schedule'] = self._get_default_schedule(difficulty_level)
                if 'nutrition_advice' not in parsed_data:
                    parsed_data['nutrition_advice'] = self._get_default_nutrition_advice()
                if 'tips' not in parsed_data:
                    parsed_data['tips'] = ["坚持训练", "注意休息", "合理饮食"]

                print(f"[AI服务] 成功解析AI响应")
                return parsed_data
            else:
                # 如果无法解析JSON，使用默认方案
                print(f"[AI服务] 无法从响应中提取JSON，使用默认方案")
                return self._get_default_plan(goals, duration_weeks, difficulty_level)

        except json.JSONDecodeError as e:
            print(f"[AI服务] JSON解析失败: {e}")
            return self._get_default_plan(goals, duration_weeks, difficulty_level)
        except Exception as e:
            print(f"[AI服务] 解析AI响应时发生错误: {e}")
            return self._get_default_plan(goals, duration_weeks, difficulty_level)
    
    def _get_default_schedule(self, difficulty_level: str) -> Dict:
        """获取默认训练安排"""
        schedules = {
            "初级": {
                "周一": {"type": "有氧训练", "activities": ["快走", "慢跑"], "duration": 30, "intensity": "低"},
                "周三": {"type": "力量训练", "activities": ["俯卧撑", "深蹲"], "duration": 30, "intensity": "低"},
                "周五": {"type": "综合训练", "activities": ["热身", "基础训练", "拉伸"], "duration": 40, "intensity": "低"}
            },
            "中级": {
                "周一": {"type": "力量训练", "activities": ["深蹲", "卧推", "划船"], "duration": 45, "intensity": "中"},
                "周二": {"type": "有氧训练", "activities": ["跑步", "HIIT"], "duration": 30, "intensity": "中"},
                "周四": {"type": "力量训练", "activities": ["硬拉", "推举", "引体向上"], "duration": 45, "intensity": "中"},
                "周六": {"type": "有氧训练", "activities": ["游泳", "骑行"], "duration": 40, "intensity": "中"}
            },
            "高级": {
                "周一": {"type": "力量训练", "activities": ["复合动作", "大重量训练"], "duration": 60, "intensity": "高"},
                "周二": {"type": "有氧训练", "activities": ["高强度间歇", "冲刺跑"], "duration": 45, "intensity": "高"},
                "周三": {"type": "力量训练", "activities": ["分化训练", "专项练习"], "duration": 60, "intensity": "高"},
                "周四": {"type": "有氧训练", "activities": ["长距离有氧", "功能性训练"], "duration": 50, "intensity": "中"},
                "周五": {"type": "力量训练", "activities": ["爆发力训练", "核心训练"], "duration": 60, "intensity": "高"},
                "周六": {"type": "综合训练", "activities": ["交叉训练", "体能测试"], "duration": 45, "intensity": "中"}
            }
        }
        
        return schedules.get(difficulty_level, schedules["初级"])
    
    def _get_default_nutrition_advice(self) -> str:
        """获取默认营养建议"""
        return """## 营养建议

### 基本原则
- 保持规律饮食，每天三餐定时定量
- 充足饮水，每天至少8杯水
- 控制油盐糖的摄入
- 选择新鲜天然的食材

### 三餐分配
- 早餐：占全天热量的30%
- 午餐：占全天热量的40%
- 晚餐：占全天热量的30%

### 营养素搭配
- 蛋白质：每公斤体重1.2-2.0g
- 碳水化合物：占总热量的45-65%
- 脂肪：占总热量的20-35%
- 维生素和矿物质：通过多样化蔬果摄入"""
    
    def _get_default_plan(self, goals: str, duration_weeks: int, difficulty_level: str) -> Dict[str, Any]:
        """获取默认健身方案"""
        return {
            "title": f"{difficulty_level}健身方案 - {duration_weeks}周",
            "description": f"针对目标'{goals}'制定的{duration_weeks}周{difficulty_level}健身方案",
            "weekly_schedule": self._get_default_schedule(difficulty_level),
            "nutrition_advice": self._get_default_nutrition_advice(),
            "tips": [
                "坚持训练，循序渐进",
                "注意充分休息和恢复",
                "保持合理的饮食习惯",
                "定期监测身体指标",
                "根据身体状况调整计划"
            ]
        }
    
    def get_intelligent_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """获取智能推荐"""
        try:
            user_analysis = self.analyze_user_data(user_id)
            
            # 构建推荐提示词
            prompt = f"""基于以下用户数据分析，提供3-5条个性化健身建议：

{json.dumps(user_analysis, indent=2, ensure_ascii=False)}

请以JSON数组格式返回建议，每个建议包含：
- type: 建议类型（training/nutrition/lifestyle）
- title: 建议标题
- content: 详细内容
- priority: 优先级（high/medium/low）

示例格式：
[
    {{
        "type": "training",
        "title": "建议标题",
        "content": "详细内容",
        "priority": "high"
    }}
]"""
            
            messages = [
                {"role": "system", "content": "你是专业的健身顾问，请根据用户数据提供实用的个性化建议。"},
                {"role": "user", "content": prompt}
            ]
            
            ai_response = self._make_api_request(messages, temperature=0.7)
            
            # 解析推荐结果
            try:
                start_idx = ai_response.find('[')
                end_idx = ai_response.rfind(']') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = ai_response[start_idx:end_idx]
                    recommendations = json.loads(json_str)
                    
                    # 验证和修正推荐数据
                    validated_recommendations = []
                    for rec in recommendations[:5]:  # 最多5条建议
                        if isinstance(rec, dict) and 'title' in rec and 'content' in rec:
                            validated_recommendations.append({
                                'type': rec.get('type', 'general'),
                                'title': rec['title'],
                                'content': rec['content'],
                                'priority': rec.get('priority', 'medium')
                            })
                    
                    return validated_recommendations
            except:
                pass
            
            # 如果AI解析失败，返回基于规则的推荐
            return self._get_rule_based_recommendations(user_analysis)
            
        except Exception as e:
            print(f"获取智能推荐失败: {e}")
            return []
    
    def _get_rule_based_recommendations(self, user_analysis: Dict) -> List[Dict[str, Any]]:
        """基于规则的推荐系统"""
        recommendations = []
        
        if not user_analysis:
            return [{
                'type': 'general',
                'title': '开始记录数据',
                'content': '建议开始记录您的饮食和运动数据，以便获得更准确的个性化建议。',
                'priority': 'high'
            }]
        
        exercise_analysis = user_analysis.get('exercise_analysis', {})
        workout_frequency = exercise_analysis.get('workout_frequency', 0)
        
        # 基于运动频率的推荐
        if workout_frequency < 3:
            recommendations.append({
                'type': 'training',
                'title': '增加运动频率',
                'content': '建议每周至少进行3次运动，以提高身体素质和健康水平。',
                'priority': 'high'
            })
        elif workout_frequency > 20:
            recommendations.append({
                'type': 'training',
                'title': '注意休息恢复',
                'content': '您的运动频率很高，请注意合理安排休息日，避免过度训练。',
                'priority': 'medium'
            })
        
        # 基于一致性的推荐
        overall_trends = user_analysis.get('overall_trends', {})
        consistency_score = overall_trends.get('consistency_score', 0)
        
        if consistency_score < 50:
            recommendations.append({
                'type': 'lifestyle',
                'title': '提高一致性',
                'content': '建议养成规律的饮食和运动习惯，提高生活的一致性。',
                'priority': 'high'
            })
        
        # 基于活动水平的推荐
        activity_level = overall_trends.get('activity_level', '')
        if activity_level == '久坐':
            recommendations.append({
                'type': 'lifestyle',
                'title': '减少久坐时间',
                'content': '建议每小时起身活动5-10分钟，减少久坐对健康的影响。',
                'priority': 'medium'
            })
        
        return recommendations[:5]  # 最多返回5条推荐


# 全局AI服务实例
ai_service = None

def get_ai_service():
    """获取AI服务实例"""
    global ai_service
    if ai_service is None:
        try:
            ai_service = AIService()
        except ValueError as e:
            print(f"AI服务初始化失败: {e}")
            return None
    return ai_service
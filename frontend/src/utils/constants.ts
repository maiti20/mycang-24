/**
 * Application Constants
 */

// Nutrition daily targets
export const NUTRITION_TARGETS = {
  CALORIES: 2000,
  PROTEIN: 60,      // grams
  CARBS: 300,       // grams
  FAT: 65,          // grams
  FIBER: 25,        // grams
  SODIUM: 2300,     // mg
  WATER: 2000       // ml
} as const

// Meal types
export const MEAL_TYPES = [
  { value: 'breakfast', label: '早餐', icon: 'bi-sunrise' },
  { value: 'lunch', label: '午餐', icon: 'bi-sun' },
  { value: 'dinner', label: '晚餐', icon: 'bi-moon' },
  { value: 'snack', label: '加餐', icon: 'bi-cup-hot' }
] as const

// Exercise intensity levels
export const INTENSITY_LEVELS = [
  { value: '低', label: '低强度', multiplier: 0.8, color: 'success' },
  { value: '中等', label: '中等强度', multiplier: 1.0, color: 'warning' },
  { value: '高', label: '高强度', multiplier: 1.3, color: 'danger' }
] as const

// Exercise categories
export const EXERCISE_CATEGORIES = [
  { value: '有氧运动', label: '有氧运动', icon: 'bi-heart-pulse', color: 'danger' },
  { value: '力量训练', label: '力量训练', icon: 'bi-lightning', color: 'primary' },
  { value: '拉伸放松', label: '拉伸放松', icon: 'bi-flower1', color: 'success' },
  { value: 'HIIT', label: 'HIIT', icon: 'bi-fire', color: 'warning' }
] as const

// Difficulty levels
export const DIFFICULTY_LEVELS = [
  { value: '初级', label: '初级', color: 'success' },
  { value: '中等', label: '中级', color: 'warning' },
  { value: '中级', label: '中级', color: 'warning' },
  { value: '高级', label: '高级', color: 'danger' },
  { value: '高', label: '高级', color: 'danger' }
] as const

// Fitness goals
export const FITNESS_GOALS = [
  { value: '减脂塑形', label: '减脂塑形', icon: 'bi-graph-down-arrow' },
  { value: '增肌增重', label: '增肌增重', icon: 'bi-graph-up-arrow' },
  { value: '保持健康', label: '保持健康', icon: 'bi-heart' },
  { value: '提升体能', label: '提升体能', icon: 'bi-lightning-charge' },
  { value: '康复训练', label: '康复训练', icon: 'bi-bandaid' }
] as const

// Experience levels for AI plan
export const EXPERIENCE_LEVELS = [
  { value: '初学者', label: '初学者', description: '刚开始健身或健身经验少于3个月' },
  { value: '中级', label: '中级', description: '有6个月以上健身经验' },
  { value: '高级', label: '高级', description: '有2年以上系统训练经验' }
] as const

// Weekly frequency options
export const WEEKLY_FREQUENCY = [
  { value: '1-2天', label: '1-2天/周' },
  { value: '3-4天', label: '3-4天/周' },
  { value: '5-6天', label: '5-6天/周' },
  { value: '每天', label: '每天' }
] as const

// Session duration options
export const SESSION_DURATIONS = [
  { value: '15-30分钟', label: '15-30分钟' },
  { value: '30-45分钟', label: '30-45分钟' },
  { value: '45-60分钟', label: '45-60分钟' },
  { value: '60分钟以上', label: '60分钟以上' }
] as const

// Food categories
export const FOOD_CATEGORIES = [
  { value: '主食', label: '主食', icon: 'bi-basket', color: '#ffc107' },
  { value: '蛋白质', label: '蛋白质', icon: 'bi-egg-fried', color: '#dc3545' },
  { value: '蔬菜', label: '蔬菜', icon: 'bi-flower2', color: '#28a745' },
  { value: '水果', label: '水果', icon: 'bi-apple', color: '#ff6b6b' },
  { value: '奶制品', label: '奶制品', icon: 'bi-cup', color: '#17a2b8' },
  { value: '坚果', label: '坚果', icon: 'bi-nut', color: '#8b4513' }
] as const

// Achievement types
export const ACHIEVEMENTS = [
  { id: 'first_login', name: '初次登录', icon: 'bi-door-open', description: '首次登录系统' },
  { id: 'streak_7', name: '坚持一周', icon: 'bi-calendar-week', description: '连续打卡7天' },
  { id: 'streak_30', name: '月度达人', icon: 'bi-calendar-month', description: '连续打卡30天' },
  { id: 'burn_1000', name: '燃烧战士', icon: 'bi-fire', description: '累计消耗1000卡路里' },
  { id: 'burn_10000', name: '燃脂大师', icon: 'bi-flame', description: '累计消耗10000卡路里' },
  { id: 'exercise_10', name: '运动新手', icon: 'bi-bicycle', description: '完成10次运动记录' },
  { id: 'exercise_100', name: '运动达人', icon: 'bi-trophy', description: '完成100次运动记录' },
  { id: 'ai_plan', name: 'AI助手', icon: 'bi-robot', description: '生成首个AI健身方案' }
] as const

// Chart colors
export const CHART_COLORS = {
  primary: '#667eea',
  secondary: '#764ba2',
  success: '#28a745',
  warning: '#ffc107',
  danger: '#dc3545',
  info: '#17a2b8',
  calories: '#ff6b6b',
  protein: '#4ecdc4',
  carbs: '#ffd93d',
  fat: '#95e1d3'
} as const

// Week days
export const WEEK_DAYS = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'] as const

// Months
export const MONTHS = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'] as const

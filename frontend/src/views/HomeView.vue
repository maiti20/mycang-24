<template>
  <div class="home-view">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner bg-primary text-white py-5 mb-4">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="display-4 fw-bold mb-3">
              欢迎回来，{{ user?.username }}！
            </h1>
            <p class="lead mb-3">
              今天是您健身之旅的第 {{ daysSinceJoined }} 天，让我们一起变得更健康！
            </p>
            <!-- 当前称号 -->
            <div class="mb-3">
              <span class="title-badge" :style="{ background: currentTitle.gradient }">
                <i :class="currentTitle.icon" class="me-1"></i>{{ currentTitle.name }}
              </span>
              <span class="text-white-50 ms-2 small">连续打卡 {{ streakDays }} 天</span>
            </div>
            <p class="fs-5 fst-italic opacity-75">
              "将来的你，一定会感谢现在努力的自己"
            </p>
          </div>
          <div class="col-md-4 text-center">
            <div class="title-icon-home" :style="{ background: currentTitle.gradient }">
              <i :class="currentTitle.icon"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速统计卡片 -->
    <div class="container mb-5">
      <div class="row g-4">
        <!-- 今日摄入 -->
        <div class="col-md-4 col-lg-2">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-warning mb-2">
                <i class="bi bi-fire" style="font-size: 2rem;"></i>
              </div>
              <h3 class="card-title">{{ Math.round(todayStats.calories) }}</h3>
              <p class="card-text text-muted small">今日摄入卡路里</p>
            </div>
          </div>
        </div>

        <!-- 今日运动时间 -->
        <div class="col-md-4 col-lg-2">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-info mb-2">
                <i class="bi bi-stopwatch" style="font-size: 2rem;"></i>
              </div>
              <h3 class="card-title">{{ todayStats.total_minutes }}</h3>
              <p class="card-text text-muted small">今日运动(分钟)</p>
            </div>
          </div>
        </div>

        <!-- 今日消耗卡路里 -->
        <div class="col-md-4 col-lg-2">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-danger mb-2">
                <i class="bi bi-lightning-charge" style="font-size: 2rem;"></i>
              </div>
              <h3 class="card-title">{{ Math.round(todayStats.calories_burned) }}</h3>
              <p class="card-text text-muted small">今日消耗卡路里</p>
            </div>
          </div>
        </div>

        <!-- 本周运动 -->
        <div class="col-md-4 col-lg-2">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-primary mb-2">
                <i class="bi bi-bicycle" style="font-size: 2rem;"></i>
              </div>
              <h3 class="card-title">{{ weekStats.exercises }}</h3>
              <p class="card-text text-muted small">本周运动次数</p>
            </div>
          </div>
        </div>

        <!-- 连续打卡 -->
        <div class="col-md-4 col-lg-2">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-success mb-2">
                <i class="bi bi-calendar-check" style="font-size: 2rem;"></i>
              </div>
              <h3 class="card-title">{{ streakDays }}</h3>
              <p class="card-text text-muted small">连续打卡天数</p>
            </div>
          </div>
        </div>

        <!-- AI方案 -->
        <div class="col-md-4 col-lg-2">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-purple mb-2">
                <i class="bi bi-robot" style="font-size: 2rem;"></i>
              </div>
              <h3 class="card-title">{{ aiPlansCount }}</h3>
              <p class="card-text text-muted small">AI健身方案</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能模块 -->
    <div class="container mb-5">
      <h2 class="mb-4">功能模块</h2>
      <div class="row g-4">
        <!-- 饮食记录 -->
        <div class="col-md-6">
          <div class="card h-100 border-0 shadow-sm hover-card">
            <div class="card-body">
              <div class="d-flex align-items-center mb-3">
                <div class="icon-box bg-warning bg-opacity-10 text-warning rounded-circle p-3 me-3">
                  <i class="bi bi-egg-fried fs-4"></i>
                </div>
                <div>
                  <h4 class="card-title mb-1">饮食记录</h4>
                  <p class="card-text text-muted mb-0">记录每日饮食，追踪营养摄入</p>
                </div>
              </div>
              <button class="btn btn-warning" @click="$router.push('/diet')">
                进入饮食管理
              </button>
            </div>
          </div>
        </div>

        <!-- 运动库 -->
        <div class="col-md-6">
          <div class="card h-100 border-0 shadow-sm hover-card">
            <div class="card-body">
              <div class="d-flex align-items-center mb-3">
                <div class="icon-box bg-info bg-opacity-10 text-info rounded-circle p-3 me-3">
                  <i class="bi bi-activity fs-4"></i>
                </div>
                <div>
                  <h4 class="card-title mb-1">运动库</h4>
                  <p class="card-text text-muted mb-0">浏览运动教程，记录运动数据</p>
                </div>
              </div>
              <button class="btn btn-info" @click="$router.push('/exercise')">
                浏览运动库
              </button>
            </div>
          </div>
        </div>

        <!-- AI健身方案 -->
        <div class="col-md-6">
          <div class="card h-100 border-0 shadow-sm hover-card">
            <div class="card-body">
              <div class="d-flex align-items-center mb-3">
                <div class="icon-box bg-primary bg-opacity-10 text-primary rounded-circle p-3 me-3">
                  <i class="bi bi-robot fs-4"></i>
                </div>
                <div>
                  <h4 class="card-title mb-1">AI健身方案</h4>
                  <p class="card-text text-muted mb-0">智能生成个性化健身计划</p>
                </div>
              </div>
              <button class="btn btn-primary" @click="$router.push('/ai-plan')">
                获取AI方案
              </button>
            </div>
          </div>
        </div>

        <!-- 个人中心 -->
        <div class="col-md-6">
          <div class="card h-100 border-0 shadow-sm hover-card">
            <div class="card-body">
              <div class="d-flex align-items-center mb-3">
                <div class="icon-box bg-success bg-opacity-10 text-success rounded-circle p-3 me-3">
                  <i class="bi bi-person-gear fs-4"></i>
                </div>
                <div>
                  <h4 class="card-title mb-1">个人中心</h4>
                  <p class="card-text text-muted mb-0">管理个人信息和偏好设置</p>
                </div>
              </div>
              <button class="btn btn-success" @click="$router.push('/profile')">
                个人设置
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 今日活动 -->
    <div class="container mb-5">
      <h2 class="mb-4">今日活动</h2>
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <div v-if="todayActivities.length === 0" class="text-center py-4 text-muted">
            <i class="bi bi-inbox fs-1 mb-3"></i>
            <p>今天还没有活动记录，开始记录您的饮食或运动吧！</p>
          </div>
          <div v-else class="timeline">
            <div v-for="(activity, index) in todayActivities" :key="index" class="timeline-item">
              <div class="timeline-marker"></div>
              <div class="timeline-content">
                <h6>{{ activity.title }}</h6>
                <p class="text-muted mb-1">{{ activity.description }}</p>
                <small class="text-muted">{{ activity.time }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { statsApi } from '@/utils/api'

const authStore = useAuthStore()

// 计算属性
const user = computed(() => authStore.user)

// 加入天数
const daysSinceJoined = computed(() => {
  if (!user.value) return 0
  const joinDate = new Date(user.value.created_at)
  const today = new Date()
  const diffTime = Math.abs(today.getTime() - joinDate.getTime())
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
})

// 加载状态
const loading = ref(true)
const error = ref<string>('')

// 今日统计
const todayStats = ref({
  calories: 0,
  protein: 0,
  carbs: 0,
  fat: 0,
  exercises: 0,
  total_minutes: 0,
  calories_burned: 0
})

// 本周统计
const weekStats = ref({
  calories: 0,
  diet_days: 0,
  exercises: 0,
  exercise_days: 0,
  total_minutes: 0,
  calories_burned: 0
})

// 连续打卡天数
const streakDays = ref(0)

// 称号系统定义
const allTitles = [
  { days: 0, name: '健身小白', icon: 'bi bi-egg', gradient: 'linear-gradient(135deg, #a8a8a8, #6b6b6b)' },
  { days: 3, name: '初露锋芒', icon: 'bi bi-star', gradient: 'linear-gradient(135deg, #4ade80, #22c55e)' },
  { days: 7, name: '周冠达人', icon: 'bi bi-award', gradient: 'linear-gradient(135deg, #60a5fa, #3b82f6)' },
  { days: 14, name: '毅力新星', icon: 'bi bi-lightning-charge', gradient: 'linear-gradient(135deg, #22d3ee, #06b6d4)' },
  { days: 30, name: '月度冠军', icon: 'bi bi-trophy', gradient: 'linear-gradient(135deg, #a855f7, #9333ea)' },
  { days: 60, name: '钢铁意志', icon: 'bi bi-shield-check', gradient: 'linear-gradient(135deg, #f97316, #ea580c)' },
  { days: 90, name: '健身达人', icon: 'bi bi-fire', gradient: 'linear-gradient(135deg, #ef4444, #dc2626)' },
  { days: 180, name: '传奇人物', icon: 'bi bi-gem', gradient: 'linear-gradient(135deg, #fbbf24, #f59e0b)' },
  { days: 365, name: '年度王者', icon: 'bi bi-crown', gradient: 'linear-gradient(135deg, #fcd34d, #f59e0b, #ef4444)' }
]

// 当前称号
const currentTitle = computed(() => {
  for (let i = allTitles.length - 1; i >= 0; i--) {
    if (streakDays.value >= allTitles[i].days) {
      return allTitles[i]
    }
  }
  return allTitles[0]
})

// AI方案数量
const aiPlansCount = ref(0)

// 最近活动
const recentActivities = ref<Array<{
  type: string
  title: string
  description: string
  time: string
  timestamp: string
}>>([])

// 今日活动（只显示今天的活动）
const todayActivities = computed(() => {
  const today = new Date()
  const todayStr = today.toISOString().split('T')[0] // 格式: YYYY-MM-DD

  return recentActivities.value.filter(activity => {
    if (!activity.timestamp) return false
    const activityDate = activity.timestamp.split(' ')[0] // 提取日期部分
    return activityDate === todayStr
  })
})

// 加载统计数据
const loadStatsData = async () => {
  try {
    loading.value = true
    error.value = ''
    
    // 并行加载所有统计数据
    const [todayRes, weekRes, activitiesRes, streakRes, aiPlansRes] = await Promise.allSettled([
      statsApi.getTodayStats(),
      statsApi.getWeekStats(),
      statsApi.getRecentActivities(10),
      statsApi.getStreakDays(),
      statsApi.getAiPlansCount()
    ])
    
    // 处理今日统计
    if (todayRes.status === 'fulfilled' && todayRes.value.success) {
      todayStats.value = todayRes.value.data
    }
    
    // 处理本周统计
    if (weekRes.status === 'fulfilled' && weekRes.value.success) {
      weekStats.value = weekRes.value.data
    }
    
    // 处理最近活动
    if (activitiesRes.status === 'fulfilled' && activitiesRes.value.success) {
      recentActivities.value = activitiesRes.value.data
    }
    
    // 处理连续打卡天数
    if (streakRes.status === 'fulfilled' && streakRes.value.success) {
      streakDays.value = streakRes.value.data.streak_days
    }
    
    // 处理AI方案数量
    if (aiPlansRes.status === 'fulfilled' && aiPlansRes.value.success) {
      aiPlansCount.value = aiPlansRes.value.data.count
    }
    
  } catch (err: any) {
    console.error('加载统计数据失败:', err)
    error.value = err.message || '加载统计数据失败'
  } finally {
    loading.value = false
  }
}

// 页面加载时的操作
onMounted(async () => {
  if (user.value) {
    await loadStatsData()
  }
})
</script>

<style scoped>
.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  margin-left: 15px;
  margin-right: 15px;
}

.text-purple {
  color: #764ba2;
}

.hover-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.hover-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
}

.icon-box {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: #e9ecef;
}

.timeline-item {
  position: relative;
  margin-bottom: 25px;
}

.timeline-marker {
  position: absolute;
  left: -22px;
  top: 5px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #667eea;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #e9ecef;
}

.timeline-content {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 3px solid #667eea;
}

.card {
  border-radius: 12px;
}

.btn {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease-in-out;
}

.btn:hover {
  transform: translateY(-2px);
}

/* 称号徽章样式 */
.title-badge {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 20px;
  color: white;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.title-icon-home {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  animation: pulse 2s infinite;
}

.title-icon-home i {
  font-size: 4rem;
  color: white;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

@keyframes pulse {
  0% { transform: scale(1); box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
  50% { transform: scale(1.05); box-shadow: 0 6px 25px rgba(0,0,0,0.4); }
  100% { transform: scale(1); box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
}
</style>
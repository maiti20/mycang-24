<template>
  <div class="profile-view">
    <div class="profile-header">
      <div class="container">
        <div class="row align-items-center py-5">
          <div class="col-md-3 text-center">
            <div class="avatar-container">
              <div class="avatar" @click="triggerAvatarUpload">
                <img v-if="user?.avatar" :src="getAvatarUrl(user.avatar)" alt="头像" class="avatar-img">
                <i v-else class="bi bi-person-fill"></i>
                <div class="avatar-overlay">
                  <i class="bi bi-camera"></i>
                </div>
              </div>
              <input
                type="file"
                ref="avatarInput"
                accept="image/*"
                @change="handleAvatarChange"
                style="display: none"
              >
              <small class="text-white-50 d-block mt-2">点击更换头像</small>
            </div>
          </div>
          <div class="col-md-9">
            <h1 class="text-white mb-2">{{ user?.username || '用户' }}</h1>
            <p class="text-white-50 mb-3">
              <i class="bi bi-calendar3 me-2"></i>加入时间: {{ formatDate(user?.created_at) }}
            </p>
            <div class="d-flex gap-3 flex-wrap">
              <span class="badge bg-light text-dark">
                <i class="bi bi-bullseye me-1"></i>{{ user?.fitness_goal || '未设置目标' }}
              </span>
              <span class="badge bg-light text-dark" v-if="bmiInfo">
                <i class="bi bi-heart-pulse me-1"></i>BMI: {{ bmiInfo.value }} ({{ bmiInfo.status }})
              </span>
              <!-- 称号徽章 -->
              <span class="badge title-badge" :style="{ background: currentTitle.gradient }">
                <i :class="currentTitle.icon" class="me-1"></i>{{ currentTitle.name }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container py-4">
      <div v-if="successMessage" class="alert alert-success alert-dismissible fade show">
        <i class="bi bi-check-circle me-2"></i>{{ successMessage }}
        <button type="button" class="btn-close" @click="successMessage = ''"></button>
      </div>
      <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show">
        <i class="bi bi-exclamation-circle me-2"></i>{{ errorMessage }}
        <button type="button" class="btn-close" @click="errorMessage = ''"></button>
      </div>

      <div class="row g-4">
        <div class="col-md-4">
          <div class="card stat-card h-100">
            <div class="card-body text-center">
              <div class="stat-icon bg-primary bg-opacity-10 text-primary"><i class="bi bi-calendar-check"></i></div>
              <h3 class="mt-3">{{ streakDays }}</h3>
              <p class="text-muted mb-0">连续打卡天数</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card stat-card h-100">
            <div class="card-body text-center">
              <div class="stat-icon bg-success bg-opacity-10 text-success"><i class="bi bi-lightning-charge"></i></div>
              <h3 class="mt-3">{{ totalExercises }}</h3>
              <p class="text-muted mb-0">本周运动次数</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card stat-card h-100">
            <div class="card-body text-center">
              <div class="stat-icon bg-danger bg-opacity-10 text-danger"><i class="bi bi-fire"></i></div>
              <h3 class="mt-3">{{ formatNumber(totalCaloriesBurned) }}</h3>
              <p class="text-muted mb-0">本周消耗卡路里</p>
            </div>
          </div>
        </div>

        <!-- 称号奖励卡片 -->
        <div class="col-12">
          <div class="card title-card">
            <div class="card-body">
              <div class="row align-items-center">
                <div class="col-md-4 text-center mb-3 mb-md-0">
                  <div class="title-icon-wrapper" :style="{ background: currentTitle.gradient }">
                    <i :class="currentTitle.icon" class="title-main-icon"></i>
                  </div>
                  <h4 class="mt-3 mb-1">{{ currentTitle.name }}</h4>
                  <p class="text-muted small mb-0">{{ currentTitle.description }}</p>
                </div>
                <div class="col-md-8">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="fw-bold">当前连续打卡: {{ streakDays }} 天</span>
                    <span class="text-muted" v-if="nextTitle">下一称号: {{ nextTitle.name }} ({{ nextTitle.days }}天)</span>
                    <span class="text-success" v-else><i class="bi bi-check-circle me-1"></i>已达最高称号!</span>
                  </div>
                  <div class="progress mb-3" style="height: 12px;">
                    <div
                      class="progress-bar"
                      :style="{ width: titleProgress + '%', background: currentTitle.gradient }"
                      role="progressbar"
                    ></div>
                  </div>
                  <div class="title-list">
                    <div
                      v-for="title in allTitles"
                      :key="title.days"
                      class="title-item"
                      :class="{ 'active': streakDays >= title.days, 'current': currentTitle.days === title.days }"
                    >
                      <div class="title-item-icon" :style="streakDays >= title.days ? { background: title.gradient } : {}">
                        <i :class="title.icon"></i>
                      </div>
                      <div class="title-item-info">
                        <span class="title-item-name">{{ title.name }}</span>
                        <span class="title-item-days">{{ title.days }}天</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-8">
          <div class="card">
            <div class="card-header"><h5 class="mb-0"><i class="bi bi-person-gear me-2"></i>基本信息</h5></div>
            <div class="card-body">
              <form @submit.prevent="handleSubmit">
                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label">用户名</label>
                    <input type="text" class="form-control" v-model="formData.username" readonly>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">邮箱</label>
                    <input type="email" class="form-control" v-model="formData.email" required>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">年龄</label>
                    <input type="number" class="form-control" v-model.number="formData.age" min="10" max="120">
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">性别</label>
                    <select class="form-select" v-model="formData.gender">
                      <option value="">请选择</option>
                      <option value="male">男</option>
                      <option value="female">女</option>
                    </select>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">健身目标</label>
                    <select class="form-select" v-model="formData.fitness_goal">
                      <option value="">请选择</option>
                      <option value="减脂塑形">减脂塑形</option>
                      <option value="增肌增重">增肌增重</option>
                      <option value="保持健康">保持健康</option>
                    </select>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">身高</label>
                    <div class="input-group">
                      <input type="number" class="form-control" v-model.number="formData.height" step="0.1">
                      <span class="input-group-text">cm</span>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">体重</label>
                    <div class="input-group">
                      <input type="number" class="form-control" v-model.number="formData.weight" step="0.1">
                      <span class="input-group-text">kg</span>
                    </div>
                  </div>
                </div>
                <div v-if="formBMI" class="mt-4 p-3 rounded" :class="`bg-${formBMI.color} bg-opacity-10`">
                  <div class="d-flex align-items-center">
                    <i class="bi bi-heart-pulse fs-3 me-3" :class="`text-${formBMI.color}`"></i>
                    <div><div class="fw-bold">BMI: {{ formBMI.value }}</div><div class="small text-muted">{{ formBMI.status }}</div></div>
                  </div>
                </div>
                <div class="mt-4">
                  <button type="submit" class="btn btn-primary" :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    {{ loading ? '保存中...' : '保存更改' }}
                  </button>
                  <button type="button" class="btn btn-outline-secondary ms-2" @click="resetForm">重置</button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card mb-4">
            <div class="card-header"><h5 class="mb-0"><i class="bi bi-lightning me-2"></i>快速操作</h5></div>
            <div class="card-body">
              <div class="d-grid gap-2">
                <button class="btn btn-outline-primary" @click="$router.push('/diet/record')"><i class="bi bi-plus-circle me-2"></i>记录饮食</button>
                <button class="btn btn-outline-success" @click="$router.push('/exercise/log')"><i class="bi bi-activity me-2"></i>记录运动</button>
                <button class="btn btn-outline-info" @click="$router.push('/ai-plan')"><i class="bi bi-robot me-2"></i>AI健身方案</button>
              </div>
            </div>
          </div>
          <div class="card">
            <div class="card-header"><h5 class="mb-0"><i class="bi bi-info-circle me-2"></i>账户信息</h5></div>
            <div class="card-body">
              <div class="info-item"><span class="text-muted">注册时间</span><span>{{ formatDate(user?.created_at) }}</span></div>
              <div class="info-item"><span class="text-muted">用户ID</span><span>#{{ user?.id }}</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { statsApi, authApi, getUploadBaseUrl } from '@/utils/api'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

const formData = reactive({
  username: '', email: '', age: undefined as number | undefined,
  gender: '', height: undefined as number | undefined,
  weight: undefined as number | undefined, fitness_goal: ''
})

const loading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const streakDays = ref(0)
const totalExercises = ref(0)
const totalCaloriesBurned = ref(0)
const avatarInput = ref<HTMLInputElement | null>(null)
const uploadingAvatar = ref(false)

// 称号系统定义
const allTitles = [
  { days: 0, name: '健身小白', icon: 'bi bi-egg', gradient: 'linear-gradient(135deg, #a8a8a8, #6b6b6b)', description: '每个人都是从零开始' },
  { days: 3, name: '初露锋芒', icon: 'bi bi-star', gradient: 'linear-gradient(135deg, #4ade80, #22c55e)', description: '坚持3天，好的开始' },
  { days: 7, name: '周冠达人', icon: 'bi bi-award', gradient: 'linear-gradient(135deg, #60a5fa, #3b82f6)', description: '坚持一周，养成习惯' },
  { days: 14, name: '毅力新星', icon: 'bi bi-lightning-charge', gradient: 'linear-gradient(135deg, #22d3ee, #06b6d4)', description: '两周坚持，毅力可嘉' },
  { days: 30, name: '月度冠军', icon: 'bi bi-trophy', gradient: 'linear-gradient(135deg, #a855f7, #9333ea)', description: '一个月！了不起的成就' },
  { days: 60, name: '钢铁意志', icon: 'bi bi-shield-check', gradient: 'linear-gradient(135deg, #f97316, #ea580c)', description: '60天，意志如钢' },
  { days: 90, name: '健身达人', icon: 'bi bi-fire', gradient: 'linear-gradient(135deg, #ef4444, #dc2626)', description: '90天，真正的达人' },
  { days: 180, name: '传奇人物', icon: 'bi bi-gem', gradient: 'linear-gradient(135deg, #fbbf24, #f59e0b)', description: '半年坚持，堪称传奇' },
  { days: 365, name: '年度王者', icon: 'bi bi-crown', gradient: 'linear-gradient(135deg, #fcd34d, #f59e0b, #ef4444)', description: '一整年！你就是王者' }
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

// 下一个称号
const nextTitle = computed(() => {
  const currentIndex = allTitles.findIndex(t => t.days === currentTitle.value.days)
  if (currentIndex < allTitles.length - 1) {
    return allTitles[currentIndex + 1]
  }
  return null
})

// 称号进度百分比
const titleProgress = computed(() => {
  if (!nextTitle.value) return 100
  const current = currentTitle.value.days
  const next = nextTitle.value.days
  const progress = ((streakDays.value - current) / (next - current)) * 100
  return Math.min(Math.max(progress, 0), 100)
})

function calculateBMI(height: number, weight: number) {
  const bmi = weight / ((height/100) ** 2)
  if (bmi < 18.5) return { value: Math.round(bmi*10)/10, status: '偏瘦', color: 'info' }
  if (bmi < 24) return { value: Math.round(bmi*10)/10, status: '正常', color: 'success' }
  if (bmi < 28) return { value: Math.round(bmi*10)/10, status: '偏胖', color: 'warning' }
  return { value: Math.round(bmi*10)/10, status: '肥胖', color: 'danger' }
}

const bmiInfo = computed(() => user.value?.height && user.value?.weight ? calculateBMI(user.value.height, user.value.weight) : null)
const formBMI = computed(() => formData.height && formData.weight ? calculateBMI(formData.height, formData.weight) : null)

function formatDate(d?: string) { return d ? new Date(d).toLocaleDateString('zh-CN') : '-' }
function formatNumber(n: number) { return n.toLocaleString('zh-CN') }

function getAvatarUrl(avatar: string) {
  if (!avatar) return ''
  if (avatar.startsWith('http')) return avatar
  return getUploadBaseUrl() + avatar  // 支持外网访问
}

function triggerAvatarUpload() {
  avatarInput.value?.click()
}

async function handleAvatarChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  // 检查文件大小（限制2MB）
  if (file.size > 2 * 1024 * 1024) {
    errorMessage.value = '图片大小不能超过2MB'
    return
  }

  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    errorMessage.value = '请选择图片文件'
    return
  }

  uploadingAvatar.value = true
  errorMessage.value = ''

  try {
    // 读取文件为Base64
    const reader = new FileReader()
    reader.onload = async (e) => {
      const base64 = e.target?.result as string
      try {
        const response = await authApi.uploadAvatar(base64)
        if (response.success) {
          successMessage.value = '头像上传成功'
          // 刷新用户信息
          await authStore.fetchUser()
        } else {
          errorMessage.value = response.message || '上传失败'
        }
      } catch (err: any) {
        errorMessage.value = err.message || '上传失败'
      } finally {
        uploadingAvatar.value = false
      }
    }
    reader.readAsDataURL(file)
  } catch (err: any) {
    errorMessage.value = err.message || '读取文件失败'
    uploadingAvatar.value = false
  }

  // 清空input，允许重复选择同一文件
  input.value = ''
}

function loadFormData() {
  if (user.value) {
    Object.assign(formData, {
      username: user.value.username, email: user.value.email, age: user.value.age,
      gender: user.value.gender || '', height: user.value.height, weight: user.value.weight,
      fitness_goal: user.value.fitness_goal || ''
    })
  }
}

function resetForm() { loadFormData() }

async function loadStats() {
  try {
    const [s, w] = await Promise.allSettled([statsApi.getStreakDays(), statsApi.getWeekStats()])
    if (s.status === 'fulfilled' && s.value.success) streakDays.value = s.value.data.streak_days
    if (w.status === 'fulfilled' && w.value.success) {
      totalExercises.value = w.value.data.exercises || 0
      totalCaloriesBurned.value = w.value.data.calories_burned || 0
    }
  } catch(e) { console.error(e) }
}

async function handleSubmit() {
  loading.value = true; errorMessage.value = ''; successMessage.value = ''
  try {
    const r = await authStore.updateProfile({
      email: formData.email, age: formData.age, gender: formData.gender as any,
      height: formData.height, weight: formData.weight, fitness_goal: formData.fitness_goal
    })
    if (r.success) successMessage.value = '更新成功！'
    else errorMessage.value = r.error || '更新失败'
  } catch(e: any) { errorMessage.value = e.message || '更新失败' }
  finally { loading.value = false }
}

onMounted(() => { loadFormData(); loadStats() })
</script>

<style scoped>
.profile-header {
  background: linear-gradient(135deg, #667eea, #764ba2);
  margin-top: -1rem;
  border-radius: 0 0 20px 20px;
  margin-left: 15px;
  margin-right: 15px;
}
.avatar-container { position: relative; display: inline-block; }
.avatar {
  width: 120px; height: 120px; background: rgba(255,255,255,.2);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  border: 4px solid rgba(255,255,255,.5); margin: 0 auto;
  cursor: pointer; position: relative; overflow: hidden;
  transition: all 0.3s ease;
}
.avatar:hover { border-color: #fff; transform: scale(1.05); }
.avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
.avatar i { font-size: 4rem; color: white; }
.avatar-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); display: flex; align-items: center;
  justify-content: center; opacity: 0; transition: opacity 0.3s;
  border-radius: 50%;
}
.avatar:hover .avatar-overlay { opacity: 1; }
.avatar-overlay i { font-size: 2rem; color: white; }
.stat-card { border: none; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,.08); transition: transform .2s; }
.stat-card:hover { transform: translateY(-5px); }
.stat-icon { width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; }
.stat-icon i { font-size: 1.5rem; }
.card { border: none; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,.08); }
.card-header { background: transparent; border-bottom: 1px solid #eee; }
.form-label { font-weight: 600; color: #495057; }
.info-item { display: flex; justify-content: space-between; padding: .75rem 0; border-bottom: 1px solid #eee; }
.info-item:last-child { border-bottom: none; }
.btn { border-radius: 8px; }

/* 称号徽章样式 */
.title-badge {
  color: white;
  font-weight: 600;
  padding: 6px 12px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

/* 称号卡片样式 */
.title-card {
  border: none;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  overflow: hidden;
}

.title-icon-wrapper {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.title-main-icon {
  font-size: 3rem;
  color: white;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.title-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.title-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: #f3f4f6;
  border-radius: 20px;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.title-item.active {
  opacity: 1;
}

.title-item.current {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.title-item-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #d1d5db;
}

.title-item-icon i {
  font-size: 0.75rem;
  color: white;
}

.title-item-info {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.title-item-name {
  font-size: 0.75rem;
  font-weight: 600;
}

.title-item-days {
  font-size: 0.65rem;
  color: #6b7280;
}

.progress {
  border-radius: 10px;
  background: #e5e7eb;
  overflow: hidden;
}

.progress-bar {
  border-radius: 10px;
  transition: width 0.5s ease;
}
</style>

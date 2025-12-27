<template>
  <div class="exercise-library container py-4">
    <!-- 页面标题 -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <h1 class="mb-0">
              <i class="bi bi-trophy me-2"></i>运动库
            </h1>
            <p class="mb-0 mt-2 opacity-75">探索各种运动项目，记录你的训练成果</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速操作区域 -->
    <div class="row mb-4">
      <div class="col-md-6 col-lg-3 mb-3">
        <div class="card h-100 border-success">
          <div class="card-body text-center">
            <i class="bi bi-plus-circle fs-1 text-success mb-2"></i>
            <h5 class="card-title">快速记录</h5>
            <button class="btn btn-success" @click="showQuickAddModal = true">
              添加运动记录
            </button>
          </div>
        </div>
      </div>
      <div class="col-md-6 col-lg-3 mb-3">
        <div class="card h-100 border-info">
          <div class="card-body text-center">
            <i class="bi bi-calendar-week fs-1 text-info mb-2"></i>
            <h5 class="card-title">本周运动</h5>
            <h3 class="text-info">{{ weekStats.total_duration }}分钟</h3>
            <small class="text-muted">{{ weekStats.total_sessions }}次训练</small>
          </div>
        </div>
      </div>
      <div class="col-md-6 col-lg-3 mb-3">
        <div class="card h-100 border-warning">
          <div class="card-body text-center">
            <i class="bi bi-fire fs-1 text-warning mb-2"></i>
            <h5 class="card-title">消耗卡路里</h5>
            <h3 class="text-warning">{{ weekStats.total_calories }}</h3>
            <small class="text-muted">千卡</small>
          </div>
        </div>
      </div>
      <div class="col-md-6 col-lg-3 mb-3">
        <div class="card h-100 border-danger">
          <div class="card-body text-center">
            <i class="bi bi-graph-up fs-1 text-danger mb-2"></i>
            <h5 class="card-title">连续打卡</h5>
            <h3 class="text-danger">{{ streakDays }}天</h3>
            <small class="text-muted">坚持就是胜利</small>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="card mb-4">
      <div class="card-header">
        <h5 class="mb-0">
          <i class="bi bi-search me-2"></i>搜索运动
        </h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="searchExercises">
          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label">关键词</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="searchForm.search"
                placeholder="搜索运动名称、描述..."
              >
            </div>
            <div class="col-md-3">
              <label class="form-label">类别</label>
              <select class="form-select" v-model="searchForm.category">
                <option value="">全部类别</option>
                <option v-for="cat in categories" :key="cat" :value="cat">
                  {{ cat }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">难度</label>
              <select class="form-select" v-model="searchForm.difficulty">
                <option value="">全部难度</option>
                <option value="初级">初级</option>
                <option value="中级">中级</option>
                <option value="高级">高级</option>
              </select>
            </div>
            <div class="col-md-2 d-flex align-items-end">
              <button type="submit" class="btn btn-primary w-100">
                <i class="bi bi-search me-1"></i>搜索
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- 运动列表 -->
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-list-ul me-2"></i>
              {{ showOnlyMyExercises ? '我的运动记录' : '全部运动项目' }}
            </h5>
            <div class="d-flex align-items-center gap-3">
              <div class="btn-group" role="group">
                <button
                  type="button"
                  class="btn btn-sm"
                  :class="showOnlyMyExercises ? 'btn-primary' : 'btn-outline-primary'"
                  @click="showOnlyMyExercises = true"
                >
                  <i class="bi bi-person-check me-1"></i>我的运动
                </button>
                <button
                  type="button"
                  class="btn btn-sm"
                  :class="!showOnlyMyExercises ? 'btn-primary' : 'btn-outline-primary'"
                  @click="showOnlyMyExercises = false"
                >
                  <i class="bi bi-grid me-1"></i>全部运动
                </button>
              </div>
              <span class="badge bg-secondary">
                {{ displayedExercises.length }} 个运动
              </span>
            </div>
          </div>
          <div class="card-body p-0">
            <!-- 加载状态 -->
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
              </div>
              <p class="mt-2 text-muted">正在加载运动数据...</p>
            </div>

            <!-- 运动网格 -->
            <div v-else-if="displayedExercises.length > 0" class="p-3">
              <div class="row g-4">
                <div
                  v-for="exercise in displayedExercises"
                  :key="exercise.id"
                  class="col-md-6 col-lg-4"
                >
                  <div class="card h-100 exercise-card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                      <h6 class="card-title mb-0">{{ exercise.name }}</h6>
                      <span 
                        class="badge"
                        :class="getDifficultyBadgeClass(exercise.difficulty_level)"
                      >
                        {{ exercise.difficulty_level }}
                      </span>
                    </div>
                    <div class="card-body">
                      <div class="mb-2">
                        <span class="badge bg-light text-dark me-1">
                          {{ exercise.category }}
                        </span>
                        <span class="badge bg-info text-white">
                          {{ exercise.calories_per_minute }} 千卡/分钟
                        </span>
                      </div>
                      
                      <p class="card-text small text-muted">
                        {{ exercise.description }}
                      </p>
                      
                      <div class="mb-2">
                        <strong class="text-muted">目标肌群：</strong>
                        <div class="mt-1">
                          <span 
                            v-for="muscle in exercise.muscle_groups.slice(0, 3)" 
                            :key="muscle"
                            class="badge bg-secondary me-1 mb-1"
                          >
                            {{ muscle }}
                          </span>
                          <span 
                            v-if="exercise.muscle_groups.length > 3"
                            class="badge bg-secondary"
                          >
                            +{{ exercise.muscle_groups.length - 3 }}
                          </span>
                        </div>
                      </div>
                      
                      <div v-if="exercise.equipment_needed.length > 0" class="mb-3">
                        <strong class="text-muted">所需器材：</strong>
                        <div class="mt-1">
                          <span 
                            v-for="equipment in exercise.equipment_needed" 
                            :key="equipment"
                            class="badge bg-warning text-dark me-1 mb-1"
                          >
                            {{ equipment }}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div class="card-footer bg-transparent">
                      <div class="btn-group w-100" role="group">
                        <button 
                          class="btn btn-outline-primary btn-sm"
                          @click="viewExerciseDetail(exercise)"
                        >
                          <i class="bi bi-eye me-1"></i>详情
                        </button>
                        <button 
                          class="btn btn-success btn-sm"
                          @click="quickAddExercise(exercise)"
                        >
                          <i class="bi bi-plus-circle me-1"></i>记录
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 分页 -->
              <nav aria-label="运动列表分页" class="mt-4">
                <ul class="pagination justify-content-center">
                  <li class="page-item" :class="{ disabled: pagination.page <= 1 }">
                    <button 
                      class="page-link" 
                      @click="changePage(pagination.page - 1)"
                      :disabled="pagination.page <= 1"
                    >
                      上一页
                    </button>
                  </li>
                  
                  <li 
                    v-for="page in visiblePages" 
                    :key="page"
                    class="page-item"
                    :class="{ active: page === pagination.page }"
                  >
                    <button 
                      class="page-link" 
                      @click="changePage(page)"
                    >
                      {{ page }}
                    </button>
                  </li>
                  
                  <li class="page-item" :class="{ disabled: pagination.page >= pagination.pages }">
                    <button 
                      class="page-link" 
                      @click="changePage(pagination.page + 1)"
                      :disabled="pagination.page >= pagination.pages"
                    >
                      下一页
                    </button>
                  </li>
                </ul>
              </nav>
            </div>

            <!-- 空状态 -->
            <div v-else class="text-center py-5">
              <i class="bi bi-search fs-1 text-muted mb-3"></i>
              <h5 class="text-muted">
                {{ showOnlyMyExercises ? '您还没有记录过运动' : '没有找到相关运动' }}
              </h5>
              <p class="text-muted">
                {{ showOnlyMyExercises ? '点击"全部运动"浏览运动库，添加您的第一个运动记录吧！' : '尝试调整搜索条件或查看全部运动' }}
              </p>
              <div class="d-flex justify-content-center gap-2">
                <button v-if="showOnlyMyExercises" class="btn btn-primary" @click="showOnlyMyExercises = false">
                  <i class="bi bi-grid me-1"></i>浏览全部运动
                </button>
                <button v-else class="btn btn-outline-primary" @click="resetSearch">
                  重置搜索
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速添加模态框 -->
    <QuickAddExerciseModal 
      v-if="showQuickAddModal"
      :exercise="selectedExerciseForQuickAdd"
      @close="showQuickAddModal = false"
      @added="onExerciseAdded"
    />

    <!-- 运动详情模态框 -->
    <ExerciseDetailModal 
      v-if="showDetailModal"
      :exercise="selectedExercise"
      @close="showDetailModal = false"
      @add-record="quickAddExercise"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { exerciseApi, statsApi } from '@/utils/api'
import QuickAddExerciseModal from '@/components/QuickAddExerciseModal.vue'
import ExerciseDetailModal from '@/components/ExerciseDetailModal.vue'

interface Exercise {
  id: number
  name: string
  category: string
  description: string
  difficulty_level: string
  calories_per_minute: number
  muscle_groups: string[]
  equipment_needed: string[]
  tutorial_url?: string
  image_url?: string
}

interface WeekStats {
  total_duration: number
  total_sessions: number
  total_calories: number
}

// 响应式数据
const loading = ref(true)
const exercises = ref<Exercise[]>([])
const myExerciseIds = ref<Set<number>>(new Set()) // 用户记录过的运动ID
const categories = ref<string[]>([])
const weekStats = ref<WeekStats>({
  total_duration: 0,
  total_sessions: 0,
  total_calories: 0
})
const streakDays = ref(0)
const showOnlyMyExercises = ref(true) // 默认只显示我的运动

// 搜索表单
const searchForm = reactive({
  search: '',
  category: '',
  difficulty: ''
})

// 分页
const pagination = reactive({
  page: 1,
  limit: 12,
  total: 0,
  pages: 0
})

// 模态框状态
const showQuickAddModal = ref(false)
const showDetailModal = ref(false)
const selectedExerciseForQuickAdd = ref<Exercise | null>(null)
const selectedExercise = ref<Exercise | null>(null)

// 计算属性 - 根据模式过滤显示的运动
const displayedExercises = computed(() => {
  if (showOnlyMyExercises.value) {
    return exercises.value.filter(e => myExerciseIds.value.has(e.id))
  }
  return exercises.value
})

const visiblePages = computed(() => {
  const current = pagination.page
  const total = pagination.pages
  const delta = 2

  const range = []
  const rangeWithDots = []

  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    range.push(i)
  }

  if (current - delta > 2) {
    rangeWithDots.push(1, '...')
  } else {
    rangeWithDots.push(1)
  }

  rangeWithDots.push(...range)

  if (current + delta < total - 1) {
    rangeWithDots.push('...', total)
  } else {
    rangeWithDots.push(total)
  }

  return rangeWithDots.filter((page, index, arr) => arr.indexOf(page) === index)
})

// 方法
const loadExercises = async () => {
  try {
    loading.value = true

    const params = {
      page: pagination.page.toString(),
      limit: '100', // 获取更多以便过滤
      ...(searchForm.search && { search: searchForm.search }),
      ...(searchForm.category && { category: searchForm.category }),
      ...(searchForm.difficulty && { difficulty: searchForm.difficulty })
    }

    const response = await exerciseApi.getExercises(params)

    if (response.success) {
      exercises.value = response.data.exercises
      pagination.total = response.data.pagination.total
      pagination.pages = response.data.pagination.pages

      // 提取类别
      const uniqueCategories = [...new Set(exercises.value.map(e => e.category))]
      categories.value = uniqueCategories.sort()
    }
  } catch (error) {
    console.error('加载运动列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载用户记录过的运动
const loadMyExercises = async () => {
  try {
    const response = await exerciseApi.getExerciseLogs({ limit: 1000 })
    if (response.success) {
      const ids = new Set<number>()
      response.data.logs.forEach((log: any) => {
        ids.add(log.exercise_id)
      })
      myExerciseIds.value = ids
    }
  } catch (error) {
    console.error('加载我的运动失败:', error)
  }
}

const loadWeekStats = async () => {
  try {
    const response = await statsApi.getWeekStats()
    if (response.success) {
      weekStats.value = {
        total_duration: response.data.total_minutes || 0,
        total_sessions: response.data.exercises || 0,
        total_calories: Math.round(response.data.calories_burned || 0)
      }
    }
  } catch (error) {
    console.error('加载本周统计失败:', error)
  }
}

const loadStreakDays = async () => {
  try {
    const response = await statsApi.getStreakDays()
    if (response.success) {
      streakDays.value = response.data.streak_days
    }
  } catch (error) {
    console.error('加载连续打卡天数失败:', error)
  }
}

const searchExercises = () => {
  pagination.page = 1
  loadExercises()
}

const resetSearch = () => {
  searchForm.search = ''
  searchForm.category = ''
  searchForm.difficulty = ''
  pagination.page = 1
  loadExercises()
}

const changePage = (page: number) => {
  if (page >= 1 && page <= pagination.pages) {
    pagination.page = page
    loadExercises()
  }
}

const getDifficultyBadgeClass = (difficulty: string) => {
  switch (difficulty) {
    case '初级':
      return 'bg-success'
    case '中级':
      return 'bg-warning'
    case '高级':
      return 'bg-danger'
    default:
      return 'bg-secondary'
  }
}

const viewExerciseDetail = (exercise: Exercise) => {
  selectedExercise.value = exercise
  showDetailModal.value = true
}

const quickAddExercise = (exercise: Exercise) => {
  selectedExerciseForQuickAdd.value = exercise
  showQuickAddModal.value = true
}

const onExerciseAdded = () => {
  showQuickAddModal.value = false
  selectedExerciseForQuickAdd.value = null
  // 刷新统计数据和我的运动列表
  loadWeekStats()
  loadStreakDays()
  loadMyExercises()
}

const toggleShowMode = () => {
  showOnlyMyExercises.value = !showOnlyMyExercises.value
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadExercises(),
    loadMyExercises(),
    loadWeekStats(),
    loadStreakDays()
  ])
})
</script>

<style scoped>
.exercise-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.exercise-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.btn-group .btn {
  flex: 1;
}

.pagination .page-link {
  cursor: pointer;
}

.badge {
  font-size: 0.75em;
}
</style>
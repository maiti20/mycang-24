<template>
  <div class="exercise-log-view container py-4">
    <!-- 页面标题 -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card border-0 bg-gradient-primary text-white">
          <div class="card-body">
            <h1 class="mb-2">
              <i class="bi bi-activity me-2"></i>
              运动记录日志
            </h1>
            <p class="mb-0 opacity-75">查看和管理您的运动记录，追踪健身进度</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速操作区域 -->
    <div class="row mb-4">
      <div class="col-md-6 col-lg-3 mb-3">
        <div class="card h-100 border-0 shadow-sm hover-lift">
          <div class="card-body text-center">
            <div class="text-primary mb-3">
              <i class="bi bi-plus-circle fs-1"></i>
            </div>
            <h5 class="card-title">快速记录</h5>
            <p class="card-text text-muted small">立即记录今天的运动</p>
            <button class="btn btn-primary btn-sm" @click="showQuickAddModal">
              开始记录
            </button>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 col-lg-3 mb-3">
        <div class="card h-100 border-0 shadow-sm hover-lift">
          <div class="card-body text-center">
            <div class="text-success mb-3">
              <i class="bi bi-calendar-week fs-1"></i>
            </div>
            <h5 class="card-title">本周统计</h5>
            <p class="card-text text-muted small">查看本周运动数据</p>
            <div class="fw-bold text-success">{{ weekStats.totalDuration }} 分钟</div>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 col-lg-3 mb-3">
        <div class="card h-100 border-0 shadow-sm hover-lift">
          <div class="card-body text-center">
            <div class="text-warning mb-3">
              <i class="bi bi-fire fs-1"></i>
            </div>
            <h5 class="card-title">消耗卡路里</h5>
            <p class="card-text text-muted small">本周总消耗</p>
            <div class="fw-bold text-warning">{{ weekStats.totalCalories }} 千卡</div>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 col-lg-3 mb-3">
        <div class="card h-100 border-0 shadow-sm hover-lift">
          <div class="card-body text-center">
            <div class="text-info mb-3">
              <i class="bi bi-trophy fs-1"></i>
            </div>
            <h5 class="card-title">运动次数</h5>
            <p class="card-text text-muted small">本周运动次数</p>
            <div class="fw-bold text-info">{{ weekStats.totalSessions }} 次</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="row g-3 align-items-end">
              <div class="col-md-3">
                <label class="form-label fw-semibold">搜索运动</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-search"></i></span>
                  <input 
                    type="text" 
                    class="form-control" 
                    placeholder="输入运动名称..."
                    v-model="filters.search"
                    @input="handleSearch"
                  >
                </div>
              </div>
              
              <div class="col-md-2">
                <label class="form-label fw-semibold">运动类型</label>
                <select class="form-select" v-model="filters.category" @change="fetchExerciseLogs">
                  <option value="">全部类型</option>
                  <option value="有氧运动">有氧运动</option>
                  <option value="力量训练">力量训练</option>
                  <option value="HIIT">HIIT</option>
                  <option value="拉伸放松">拉伸放松</option>
                </select>
              </div>
              
              <div class="col-md-2">
                <label class="form-label fw-semibold">开始日期</label>
                <input 
                  type="date" 
                  class="form-control" 
                  v-model="filters.dateFrom"
                  @change="fetchExerciseLogs"
                >
              </div>
              
              <div class="col-md-2">
                <label class="form-label fw-semibold">结束日期</label>
                <input 
                  type="date" 
                  class="form-control" 
                  v-model="filters.dateTo"
                  @change="fetchExerciseLogs"
                >
              </div>
              
              <div class="col-md-3">
                <div class="d-flex gap-2">
                  <button class="btn btn-outline-secondary flex-fill" @click="resetFilters">
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    重置
                  </button>
                  <button class="btn btn-primary flex-fill" @click="fetchExerciseLogs">
                    <i class="bi bi-funnel me-1"></i>
                    筛选
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 运动记录列表 -->
    <div class="row">
      <div class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="mb-0 fw-semibold">
                <i class="bi bi-list-ul me-2"></i>
                运动记录列表
              </h5>
              <span class="badge bg-primary rounded-pill">
                {{ pagination.total }} 条记录
              </span>
            </div>
          </div>
          <div class="card-body p-0">
            <!-- 加载状态 -->
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
              </div>
              <p class="mt-2 text-muted">正在加载运动记录...</p>
            </div>
            
            <!-- 记录列表 -->
            <div v-else-if="exerciseLogs.length > 0" class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th>运动名称</th>
                    <th>类型</th>
                    <th>时长</th>
                    <th>强度</th>
                    <th>消耗卡路里</th>
                    <th>记录时间</th>
                    <th>备注</th>
                    <th width="120">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="log in exerciseLogs" :key="log.id">
                    <td>
                      <div class="d-flex align-items-center">
                        <div class="avatar avatar-sm bg-primary bg-opacity-10 text-primary rounded-circle me-2 d-flex align-items-center justify-content-center">
                          <i class="bi bi-activity"></i>
                        </div>
                        <div>
                          <div class="fw-semibold">{{ log.exercise.name }}</div>
                          <small class="text-muted">{{ log.exercise.muscle_groups.join(', ') }}</small>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span class="badge bg-light text-dark">
                        {{ log.exercise.category }}
                      </span>
                    </td>
                    <td>
                      <div class="fw-semibold">{{ log.duration_minutes }} 分钟</div>
                    </td>
                    <td>
                      <span 
                        class="badge"
                        :class="getIntensityBadgeClass(log.intensity_level)"
                      >
                        {{ log.intensity_level }}
                      </span>
                    </td>
                    <td>
                      <div class="fw-semibold text-danger">
                        <i class="bi bi-fire"></i>
                        {{ Math.round(log.calories_burned) }} 千卡
                      </div>
                    </td>
                    <td>
                      <div>{{ formatDate(log.log_date) }}</div>
                      <small class="text-muted">{{ formatTime(log.log_date) }}</small>
                    </td>
                    <td>
                      <div class="text-truncate" style="max-width: 150px;">
                        {{ log.notes || '-' }}
                      </div>
                    </td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button 
                          class="btn btn-outline-primary"
                          @click="editLog(log)"
                          title="编辑"
                        >
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button 
                          class="btn btn-outline-danger"
                          @click="deleteLog(log.id)"
                          title="删除"
                        >
                          <i class="bi bi-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- 空状态 -->
            <div v-else class="text-center py-5">
              <div class="text-muted mb-3">
                <i class="bi bi-inbox fs-1"></i>
              </div>
              <h5 class="text-muted">暂无运动记录</h5>
              <p class="text-muted">开始记录您的第一次运动吧！</p>
              <button class="btn btn-primary" @click="showQuickAddModal">
                <i class="bi bi-plus-circle me-2"></i>
                添加运动记录
              </button>
            </div>
          </div>
          
          <!-- 分页 -->
          <div v-if="exerciseLogs.length > 0" class="card-footer bg-white border-top">
            <nav aria-label="运动记录分页">
              <ul class="pagination pagination-sm justify-content-center mb-0">
                <li class="page-item" :class="{ disabled: pagination.page <= 1 }">
                  <a 
                    class="page-link" 
                    href="#" 
                    @click.prevent="changePage(pagination.page - 1)"
                  >
                    <i class="bi bi-chevron-left"></i>
                  </a>
                </li>
                
                <li 
                  v-for="page in visiblePages" 
                  :key="page"
                  class="page-item"
                  :class="{ active: page === pagination.page }"
                >
                  <a 
                    class="page-link" 
                    href="#"
                    @click.prevent="changePage(page)"
                  >
                    {{ page }}
                  </a>
                </li>
                
                <li class="page-item" :class="{ disabled: pagination.page >= pagination.pages }">
                  <a 
                    class="page-link" 
                    href="#" 
                    @click.prevent="changePage(pagination.page + 1)"
                  >
                    <i class="bi bi-chevron-right"></i>
                  </a>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速添加运动记录模态框 -->
    <QuickAddExerciseModal 
      v-if="showQuickAdd"
      :show="showQuickAdd"
      @close="hideQuickAddModal"
      @added="onExerciseAdded"
    />

    <!-- 编辑运动记录模态框 -->
    <div 
      class="modal fade" 
      :class="{ show: showEditModal }" 
      :style="{ display: showEditModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">编辑运动记录</h5>
            <button type="button" class="btn-close" @click="hideEditModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateLog">
              <div class="mb-3">
                <label class="form-label">运动名称</label>
                <input type="text" class="form-control" :value="editingLog?.exercise?.name" readonly>
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">运动时长（分钟）</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model.number="editingForm.duration_minutes"
                    min="1"
                    required
                  >
                </div>
                
                <div class="col-md-6 mb-3">
                  <label class="form-label">运动强度</label>
                  <select class="form-select" v-model="editingForm.intensity_level">
                    <option value="低">低强度</option>
                    <option value="中等">中等强度</option>
                    <option value="高">高强度</option>
                  </select>
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label">备注</label>
                <textarea 
                  class="form-control" 
                  rows="3" 
                  v-model="editingForm.notes"
                  placeholder="记录运动感受或其他信息..."
                ></textarea>
              </div>
              
              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-secondary" @click="hideEditModal">
                  取消
                </button>
                <button type="submit" class="btn btn-primary" :disabled="updating">
                  <span v-if="updating" class="spinner-border spinner-border-sm me-1"></span>
                  保存更改
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { exerciseApi } from '@/utils/api'
import QuickAddExerciseModal from '@/components/QuickAddExerciseModal.vue'

interface ExerciseLog {
  id: number
  exercise_id: number
  duration_minutes: number
  intensity_level: string
  log_date: string
  notes: string
  calories_burned: number
  exercise: {
    name: string
    category: string
    muscle_groups: string[]
  }
}

interface Pagination {
  page: number
  limit: number
  total: number
  pages: number
}

interface WeekStats {
  totalDuration: number
  totalCalories: number
  totalSessions: number
}

const loading = ref(false)
const updating = ref(false)
const exerciseLogs = ref<ExerciseLog[]>([])
const pagination = ref<Pagination>({
  page: 1,
  limit: 10,
  total: 0,
  pages: 0
})

const weekStats = ref<WeekStats>({
  totalDuration: 0,
  totalCalories: 0,
  totalSessions: 0
})

const showQuickAdd = ref(false)
const showEditModal = ref(false)
const editingLog = ref<ExerciseLog | null>(null)

const filters = reactive({
  search: '',
  category: '',
  dateFrom: '',
  dateTo: ''
})

const editingForm = reactive({
  duration_minutes: 0,
  intensity_level: '中等',
  notes: ''
})

const visiblePages = computed(() => {
  const current = pagination.value.page
  const total = pagination.value.pages
  const delta = 2
  
  const range = []
  const rangeWithDots = []
  
  for (
    let i = Math.max(2, current - delta);
    i <= Math.min(total - 1, current + delta);
    i++
  ) {
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
  
  return rangeWithDots.filter((item, index, arr) => 
    item !== '...' || arr[index - 1] !== '...'
  )
})

const fetchExerciseLogs = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.value.page,
      limit: pagination.value.limit
    }
    
    if (filters.search) params.search = filters.search
    if (filters.category) params.category = filters.category
    if (filters.dateFrom) params.date_from = filters.dateFrom
    if (filters.dateTo) params.date_to = filters.dateTo
    
    const response = await exerciseApi.getExerciseLogs(params)
    
    if (response.success) {
      exerciseLogs.value = response.data.logs
      pagination.value = response.data.pagination
      
      // 计算本周统计
      calculateWeekStats()
    }
  } catch (error) {
    console.error('获取运动记录失败:', error)
  } finally {
    loading.value = false
  }
}

const calculateWeekStats = () => {
  const now = new Date()
  const weekStart = new Date(now.setDate(now.getDate() - now.getDay()))
  weekStart.setHours(0, 0, 0, 0)
  
  const weekLogs = exerciseLogs.value.filter(log => {
    const logDate = new Date(log.log_date)
    return logDate >= weekStart
  })
  
  weekStats.value = {
    totalDuration: weekLogs.reduce((sum, log) => sum + log.duration_minutes, 0),
    totalCalories: Math.round(weekLogs.reduce((sum, log) => sum + log.calories_burned, 0)),
    totalSessions: weekLogs.length
  }
}

const changePage = (page: number) => {
  if (page >= 1 && page <= pagination.value.pages) {
    pagination.value.page = page
    fetchExerciseLogs()
  }
}

const handleSearch = () => {
  pagination.value.page = 1
  fetchExerciseLogs()
}

const resetFilters = () => {
  filters.search = ''
  filters.category = ''
  filters.dateFrom = ''
  filters.dateTo = ''
  pagination.value.page = 1
  fetchExerciseLogs()
}

const showQuickAddModal = () => {
  showQuickAdd.value = true
}

const hideQuickAddModal = () => {
  showQuickAdd.value = false
}

const onExerciseAdded = () => {
  fetchExerciseLogs()
}

const editLog = (log: ExerciseLog) => {
  editingLog.value = log
  editingForm.duration_minutes = log.duration_minutes
  editingForm.intensity_level = log.intensity_level
  editingForm.notes = log.notes
  showEditModal.value = true
}

const hideEditModal = () => {
  showEditModal.value = false
  editingLog.value = null
}

const updateLog = async () => {
  if (!editingLog.value) return
  
  updating.value = true
  try {
    const response = await exerciseApi.updateExerciseLog(editingLog.value.id, editingForm)
    
    if (response.success) {
      fetchExerciseLogs()
      hideEditModal()
    }
  } catch (error) {
    console.error('更新运动记录失败:', error)
  } finally {
    updating.value = false
  }
}

const deleteLog = async (id: number) => {
  if (!confirm('确定要删除这条运动记录吗？')) return
  
  try {
    const response = await exerciseApi.deleteExerciseLog(id)
    
    if (response.success) {
      fetchExerciseLogs()
    }
  } catch (error) {
    console.error('删除运动记录失败:', error)
  }
}

const getIntensityBadgeClass = (level: string) => {
  switch (level) {
    case '低':
      return 'bg-success'
    case '中等':
      return 'bg-warning'
    case '高':
      return 'bg-danger'
    default:
      return 'bg-secondary'
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  fetchExerciseLogs()
})
</script>

<style scoped>
.hover-lift {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.avatar-sm {
  width: 32px;
  height: 32px;
  font-size: 14px;
}

.modal.show {
  background-color: rgba(0, 0, 0, 0.5);
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
}

.badge {
  font-size: 0.75em;
}

.btn-group-sm > .btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
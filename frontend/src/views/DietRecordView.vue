<template>
  <div class="diet-record-view">
    <!-- 页面标题 -->
    <div class="page-header bg-success text-white py-4 mb-4">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="display-5 fw-bold mb-2">
              <i class="bi bi-egg-fried me-3"></i>饮食记录
            </h1>
            <p class="lead mb-0">记录每日饮食，追踪营养摄入，保持健康生活</p>
          </div>
          <div class="col-md-4 text-end">
            <button class="btn btn-light btn-lg" @click="showAddModal = true">
              <i class="bi bi-plus-circle me-2"></i>添加记录
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- 今日营养统计 -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white">
              <h5 class="card-title mb-0">
                <i class="bi bi-pie-chart-fill text-success me-2"></i>
                今日营养摄入
              </h5>
            </div>
            <div class="card-body">
              <div class="row text-center">
                <div class="col-md-3 col-6 mb-3">
                  <div class="nutrition-stat">
                    <div class="stat-icon text-warning mb-2">
                      <i class="bi bi-fire" style="font-size: 2rem;"></i>
                    </div>
                    <h3 class="stat-value">{{ todayNutrition.calories.toFixed(0) }}</h3>
                    <p class="stat-label text-muted mb-0">卡路里</p>
                    <div class="progress mt-2" style="height: 4px;">
                      <div class="progress-bar bg-warning" :style="{width: `${Math.min((todayNutrition.calories / 2000) * 100, 100)}%`}"></div>
                    </div>
                  </div>
                </div>
                <div class="col-md-3 col-6 mb-3">
                  <div class="nutrition-stat">
                    <div class="stat-icon text-info mb-2">
                      <i class="bi bi-droplet" style="font-size: 2rem;"></i>
                    </div>
                    <h3 class="stat-value">{{ todayNutrition.protein.toFixed(1) }}g</h3>
                    <p class="stat-label text-muted mb-0">蛋白质</p>
                    <div class="progress mt-2" style="height: 4px;">
                      <div class="progress-bar bg-info" :style="{width: `${Math.min((todayNutrition.protein / 50) * 100, 100)}%`}"></div>
                    </div>
                  </div>
                </div>
                <div class="col-md-3 col-6 mb-3">
                  <div class="nutrition-stat">
                    <div class="stat-icon text-primary mb-2">
                      <i class="bi bi-wheat" style="font-size: 2rem;"></i>
                    </div>
                    <h3 class="stat-value">{{ todayNutrition.carbs.toFixed(1) }}g</h3>
                    <p class="stat-label text-muted mb-0">碳水化合物</p>
                    <div class="progress mt-2" style="height: 4px;">
                      <div class="progress-bar bg-primary" :style="{width: `${Math.min((todayNutrition.carbs / 300) * 100, 100)}%`}"></div>
                    </div>
                  </div>
                </div>
                <div class="col-md-3 col-6 mb-3">
                  <div class="nutrition-stat">
                    <div class="stat-icon text-secondary mb-2">
                      <i class="bi bi-droplet-half" style="font-size: 2rem;"></i>
                    </div>
                    <h3 class="stat-value">{{ todayNutrition.fat.toFixed(1) }}g</h3>
                    <p class="stat-label text-muted mb-0">脂肪</p>
                    <div class="progress mt-2" style="height: 4px;">
                      <div class="progress-bar bg-secondary" :style="{width: `${Math.min((todayNutrition.fat / 65) * 100, 100)}%`}"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="row mb-4">
        <div class="col-md-6">
          <div class="input-group">
            <span class="input-group-text">
              <i class="bi bi-search"></i>
            </span>
            <input 
              type="text" 
              class="form-control" 
              placeholder="搜索食物..."
              v-model="searchQuery"
              @input="handleSearch"
            >
          </div>
        </div>
        <div class="col-md-3">
          <select class="form-select" v-model="selectedCategory" @change="handleFilter">
            <option value="">所有分类</option>
            <option value="主食">主食</option>
            <option value="蛋白质">蛋白质</option>
            <option value="蔬菜">蔬菜</option>
            <option value="水果">水果</option>
            <option value="奶制品">奶制品</option>
            <option value="坚果">坚果</option>
          </select>
        </div>
        <div class="col-md-3">
          <select class="form-select" v-model="selectedMealType" @change="handleFilter">
            <option value="">所有餐次</option>
            <option value="早餐">早餐</option>
            <option value="午餐">午餐</option>
            <option value="晚餐">晚餐</option>
            <option value="加餐">加餐</option>
          </select>
        </div>
      </div>

      <!-- 饮食记录列表 -->
      <div class="row">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white d-flex justify-content-between align-items-center">
              <h5 class="card-title mb-0">
                <i class="bi bi-list-ul text-success me-2"></i>
                饮食记录
              </h5>
              <div class="btn-group" role="group">
                <button 
                  class="btn btn-outline-success btn-sm" 
                  :class="{ active: viewMode === 'list' }"
                  @click="viewMode = 'list'"
                >
                  <i class="bi bi-list"></i> 列表
                </button>
                <button 
                  class="btn btn-outline-success btn-sm" 
                  :class="{ active: viewMode === 'grid' }"
                  @click="viewMode = 'grid'"
                >
                  <i class="bi bi-grid"></i> 网格
                </button>
              </div>
            </div>
            <div class="card-body">
              <!-- 加载状态 -->
              <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-success" role="status">
                  <span class="visually-hidden">加载中...</span>
                </div>
                <p class="mt-2 text-muted">正在加载饮食记录...</p>
              </div>

              <!-- 错误状态 -->
              <div v-else-if="error" class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle me-2"></i>
                {{ error }}
              </div>

              <!-- 空状态 -->
              <div v-else-if="filteredRecords.length === 0" class="text-center py-5">
                <i class="bi bi-inbox fs-1 text-muted mb-3"></i>
                <h5 class="text-muted">暂无饮食记录</h5>
                <p class="text-muted">点击上方"添加记录"按钮开始记录您的第一餐</p>
              </div>

              <!-- 记录列表 -->
              <div v-else>
                <!-- 列表视图 -->
                <div v-if="viewMode === 'list'" class="record-list">
                  <div 
                    v-for="record in filteredRecords" 
                    :key="record.id"
                    class="record-item border-bottom pb-3 mb-3"
                  >
                    <div class="row align-items-center">
                      <div class="col-md-8">
                        <div class="d-flex align-items-start">
                          <div class="meal-badge me-3">
                            <span class="badge" :class="getMealBadgeClass(record.meal_type)">
                              {{ record.meal_type }}
                            </span>
                          </div>
                          <div class="flex-grow-1">
                            <h6 class="mb-1">{{ record.food.name }}</h6>
                            <p class="text-muted mb-1">
                              <small>{{ record.food.category }} • {{ record.quantity }} {{ record.food.unit }}</small>
                            </p>
                            <div class="nutrition-summary">
                              <span class="badge bg-warning me-1">{{ record.nutrition.calories.toFixed(0) }} kcal</span>
                              <span class="badge bg-info me-1">P: {{ record.nutrition.protein.toFixed(1) }}g</span>
                              <span class="badge bg-primary me-1">C: {{ record.nutrition.carbs.toFixed(1) }}g</span>
                              <span class="badge bg-secondary">F: {{ record.nutrition.fat.toFixed(1) }}g</span>
                            </div>
                            <p v-if="record.notes" class="text-muted mt-2 mb-0">
                              <small><i class="bi bi-chat-quote me-1"></i>{{ record.notes }}</small>
                            </p>
                          </div>
                        </div>
                      </div>
                      <div class="col-md-4 text-end">
                        <small class="text-muted d-block mb-2">{{ formatDateTime(record.record_date) }}</small>
                        <div class="btn-group btn-group-sm">
                          <button class="btn btn-outline-primary" @click="editRecord(record)">
                            <i class="bi bi-pencil"></i>
                          </button>
                          <button class="btn btn-outline-danger" @click="deleteRecord(record.id)">
                            <i class="bi bi-trash"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 网格视图 -->
                <div v-else class="row">
                  <div 
                    v-for="record in filteredRecords" 
                    :key="record.id"
                    class="col-md-6 col-lg-4 mb-3"
                  >
                    <div class="card h-100 border-success">
                      <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                          <span class="badge" :class="getMealBadgeClass(record.meal_type)">
                            {{ record.meal_type }}
                          </span>
                          <small class="text-muted">{{ formatTime(record.record_date) }}</small>
                        </div>
                        <h6 class="card-title">{{ record.food.name }}</h6>
                        <p class="card-text text-muted">
                          <small>{{ record.food.category }} • {{ record.quantity }} {{ record.food.unit }}</small>
                        </p>
                        <div class="nutrition-mini">
                          <div class="row text-center">
                            <div class="col-3">
                              <small class="text-warning d-block">{{ record.nutrition.calories.toFixed(0) }}</small>
                              <small class="text-muted">kcal</small>
                            </div>
                            <div class="col-3">
                              <small class="text-info d-block">{{ record.nutrition.protein.toFixed(1) }}</small>
                              <small class="text-muted">P</small>
                            </div>
                            <div class="col-3">
                              <small class="text-primary d-block">{{ record.nutrition.carbs.toFixed(1) }}</small>
                              <small class="text-muted">C</small>
                            </div>
                            <div class="col-3">
                              <small class="text-secondary d-block">{{ record.nutrition.fat.toFixed(1) }}</small>
                              <small class="text-muted">F</small>
                            </div>
                          </div>
                        </div>
                        <div class="btn-group btn-group-sm w-100 mt-2">
                          <button class="btn btn-outline-primary" @click="editRecord(record)">
                            <i class="bi bi-pencil"></i>
                          </button>
                          <button class="btn btn-outline-danger" @click="deleteRecord(record.id)">
                            <i class="bi bi-trash"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 分页 -->
                <nav v-if="pagination.pages > 1" aria-label="记录分页">
                  <ul class="pagination justify-content-center">
                    <li class="page-item" :class="{ disabled: pagination.page === 1 }">
                      <button class="page-link" @click="changePage(pagination.page - 1)">上一页</button>
                    </li>
                    <li 
                      v-for="page in pagination.pages" 
                      :key="page"
                      class="page-item" 
                      :class="{ active: pagination.page === page }"
                    >
                      <button class="page-link" @click="changePage(page)">{{ page }}</button>
                    </li>
                    <li class="page-item" :class="{ disabled: pagination.page === pagination.pages }">
                      <button class="page-link" @click="changePage(pagination.page + 1)">下一页</button>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑记录模态框 -->
    <div class="modal fade" :class="{ show: showAddModal }" :style="{ display: showAddModal ? 'block' : 'none' }">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-plus-circle me-2"></i>
              {{ editingRecord ? '编辑饮食记录' : '添加饮食记录' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveRecord">
              <div class="row">
                <div class="col-md-6">
                  <label class="form-label">选择食物</label>
                  <div class="input-group mb-3">
                    <input 
                      type="text" 
                      class="form-control" 
                      placeholder="搜索食物..."
                      v-model="foodSearchQuery"
                      @input="searchFoods"
                    >
                    <button class="btn btn-outline-secondary" type="button">
                      <i class="bi bi-search"></i>
                    </button>
                  </div>
                  
                  <!-- 食物搜索结果 -->
                  <div v-if="searchResults.length > 0" class="food-search-results mb-3">
                    <div class="list-group">
                      <button 
                        v-for="food in searchResults.slice(0, 5)" 
                        :key="food.id"
                        type="button"
                        class="list-group-item list-group-item-action"
                        @click="selectFood(food)"
                        :class="{ active: selectedFood?.id === food.id }"
                      >
                        <div class="d-flex justify-content-between">
                          <strong>{{ food.name }}</strong>
                          <span class="badge bg-warning">{{ food.calories_per_unit }} kcal/{{ food.unit }}</span>
                        </div>
                        <small class="text-muted">{{ food.category }}</small>
                      </button>
                    </div>
                  </div>

                  <!-- 选中的食物信息 -->
                  <div v-if="selectedFood" class="selected-food mb-3 p-3 bg-light rounded">
                    <h6>{{ selectedFood.name }}</h6>
                    <div class="row text-center">
                      <div class="col-3">
                        <small class="text-warning d-block">{{ selectedFood.calories_per_unit }}</small>
                        <small class="text-muted">kcal</small>
                      </div>
                      <div class="col-3">
                        <small class="text-info d-block">{{ selectedFood.protein }}</small>
                        <small class="text-muted">P(g)</small>
                      </div>
                      <div class="col-3">
                        <small class="text-primary d-block">{{ selectedFood.carbs }}</small>
                        <small class="text-muted">C(g)</small>
                      </div>
                      <div class="col-3">
                        <small class="text-secondary d-block">{{ selectedFood.fat }}</small>
                        <small class="text-muted">F(g)</small>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">数量</label>
                    <div class="input-group">
                      <input 
                        type="number" 
                        class="form-control" 
                        v-model.number="formData.quantity"
                        min="0.1"
                        step="0.1"
                        required
                      >
                      <span class="input-group-text">{{ selectedFood?.unit || '份' }}</span>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label">餐次</label>
                    <select class="form-select" v-model="formData.meal_type" required>
                      <option value="">请选择餐次</option>
                      <option value="早餐">早餐</option>
                      <option value="午餐">午餐</option>
                      <option value="晚餐">晚餐</option>
                      <option value="加餐">加餐</option>
                    </select>
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label">备注</label>
                    <textarea 
                      class="form-control" 
                      rows="3" 
                      v-model="formData.notes"
                      placeholder="添加备注信息..."
                    ></textarea>
                  </div>
                  
                  <!-- 营养预览 -->
                  <div v-if="selectedFood && formData.quantity" class="nutrition-preview p-3 bg-light rounded">
                    <h6>营养预览</h6>
                    <div class="row text-center">
                      <div class="col-3">
                        <small class="text-warning d-block">{{ calculateNutrition().calories.toFixed(0) }}</small>
                        <small class="text-muted">kcal</small>
                      </div>
                      <div class="col-3">
                        <small class="text-info d-block">{{ calculateNutrition().protein.toFixed(1) }}</small>
                        <small class="text-muted">P(g)</small>
                      </div>
                      <div class="col-3">
                        <small class="text-primary d-block">{{ calculateNutrition().carbs.toFixed(1) }}</small>
                        <small class="text-muted">C(g)</small>
                      </div>
                      <div class="col-3">
                        <small class="text-secondary d-block">{{ calculateNutrition().fat.toFixed(1) }}</small>
                        <small class="text-muted">F(g)</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">取消</button>
            <button type="button" class="btn btn-success" @click="saveRecord" :disabled="!canSave">
              <i class="bi bi-check-circle me-1"></i>
              {{ editingRecord ? '更新' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { dietApi } from '@/utils/api'

// 响应式数据
const loading = ref(true)
const error = ref('')
const records = ref([])
const foods = ref([])
const searchResults = ref([])

// 搜索和筛选
const searchQuery = ref('')
const selectedCategory = ref('')
const selectedMealType = ref('')
const viewMode = ref<'list' | 'grid'>('list')

// 分页
const pagination = ref({
  page: 1,
  limit: 20,
  total: 0,
  pages: 0
})

// 今日营养统计
const todayNutrition = ref({
  calories: 0,
  protein: 0,
  carbs: 0,
  fat: 0
})

// 模态框状态
const showAddModal = ref(false)
const editingRecord = ref(null)

// 表单数据
const formData = ref({
  food_id: null,
  quantity: 1,
  meal_type: '',
  notes: ''
})

// 食物搜索
const foodSearchQuery = ref('')
const selectedFood = ref(null)

// 计算属性
const filteredRecords = computed(() => {
  let filtered = records.value

  if (searchQuery.value) {
    filtered = filtered.filter(record => 
      record.food.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      record.notes?.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (selectedCategory.value) {
    filtered = filtered.filter(record => record.food.category === selectedCategory.value)
  }

  if (selectedMealType.value) {
    filtered = filtered.filter(record => record.meal_type === selectedMealType.value)
  }

  return filtered
})

const canSave = computed(() => {
  return selectedFood.value && formData.value.quantity > 0 && formData.value.meal_type
})

// 方法
const loadRecords = async () => {
  try {
    loading.value = true
    const response = await dietApi.getDietRecords({
      page: pagination.value.page,
      limit: pagination.value.limit
    })
    
    if (response.success) {
      records.value = response.data.records
      pagination.value = response.data.pagination
      calculateTodayNutrition()
    } else {
      error.value = response.message || '加载饮食记录失败'
    }
  } catch (err: any) {
    error.value = err.message || '网络错误'
  } finally {
    loading.value = false
  }
}

const loadFoods = async () => {
  try {
    const response = await dietApi.getFoods({ limit: 100 })
    if (response.success) {
      foods.value = response.data.foods
    }
  } catch (err) {
    console.error('加载食物列表失败:', err)
  }
}

const searchFoods = async () => {
  if (!foodSearchQuery.value.trim()) {
    searchResults.value = []
    return
  }

  try {
    const response = await dietApi.getFoods({
      search: foodSearchQuery.value,
      limit: 10
    })
    
    if (response.success) {
      searchResults.value = response.data.foods
    }
  } catch (err) {
    console.error('搜索食物失败:', err)
  }
}

const selectFood = (food: any) => {
  selectedFood.value = food
  formData.value.food_id = food.id
  foodSearchQuery.value = food.name
  searchResults.value = []
}

const calculateNutrition = () => {
  if (!selectedFood.value || !formData.value.quantity) {
    return { calories: 0, protein: 0, carbs: 0, fat: 0 }
  }

  const multiplier = formData.value.quantity
  return {
    calories: selectedFood.value.calories_per_unit * multiplier,
    protein: selectedFood.value.protein * multiplier,
    carbs: selectedFood.value.carbs * multiplier,
    fat: selectedFood.value.fat * multiplier
  }
}

const calculateTodayNutrition = () => {
  const today = new Date().toDateString()
  const todayRecords = records.value.filter(record => 
    new Date(record.record_date).toDateString() === today
  )

  todayNutrition.value = todayRecords.reduce((acc, record) => {
    acc.calories += record.nutrition.calories
    acc.protein += record.nutrition.protein
    acc.carbs += record.nutrition.carbs
    acc.fat += record.nutrition.fat
    return acc
  }, { calories: 0, protein: 0, carbs: 0, fat: 0 })
}

const saveRecord = async () => {
  if (!canSave.value) return

  try {
    const data = {
      food_id: formData.value.food_id,
      quantity: formData.value.quantity,
      meal_type: formData.value.meal_type,
      notes: formData.value.notes
    }

    let response
    if (editingRecord.value) {
      // 编辑记录
      response = await dietApi.updateDietRecord(editingRecord.value.id, data)
    } else {
      // 新增记录
      response = await dietApi.createDietRecord(data)
    }

    if (response.success) {
      closeModal()
      await loadRecords()
    } else {
      error.value = response.message || '保存失败'
    }
  } catch (err: any) {
    error.value = err.message || '网络错误'
  }
}

const editRecord = (record: any) => {
  editingRecord.value = record
  selectedFood.value = record.food
  formData.value = {
    food_id: record.food_id,
    quantity: record.quantity,
    meal_type: record.meal_type,
    notes: record.notes || ''
  }
  foodSearchQuery.value = record.food.name
  showAddModal.value = true
}

const deleteRecord = async (id: number) => {
  if (!confirm('确定要删除这条记录吗？')) return

  try {
    const response = await dietApi.deleteDietRecord(id)
    if (response.success) {
      await loadRecords()
    } else {
      error.value = response.message || '删除失败'
    }
  } catch (err: any) {
    error.value = err.message || '网络错误'
  }
}

const closeModal = () => {
  showAddModal.value = false
  editingRecord.value = null
  selectedFood.value = null
  formData.value = {
    food_id: null,
    quantity: 1,
    meal_type: '',
    notes: ''
  }
  foodSearchQuery.value = ''
  searchResults.value = []
}

const changePage = (page: number) => {
  if (page >= 1 && page <= pagination.value.pages) {
    pagination.value.page = page
    loadRecords()
  }
}

const handleSearch = () => {
  // 搜索功能由计算属性处理
}

const handleFilter = () => {
  // 筛选功能由计算属性处理
}

const getMealBadgeClass = (mealType: string) => {
  const classes = {
    '早餐': 'bg-warning',
    '午餐': 'bg-success',
    '晚餐': 'bg-primary',
    '加餐': 'bg-info'
  }
  return classes[mealType] || 'bg-secondary'
}

const formatDateTime = (dateTimeStr: string) => {
  const date = new Date(dateTimeStr)
  const today = new Date()
  
  if (date.toDateString() === today.toDateString()) {
    return `今天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`
  }
  
  return date.toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatTime = (dateTimeStr: string) => {
  return new Date(dateTimeStr).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 监听搜索输入
watch(foodSearchQuery, (newValue) => {
  if (newValue && newValue !== selectedFood.value?.name) {
    searchFoods()
  }
})

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadRecords(),
    loadFoods()
  ])
})
</script>

<style scoped>
.diet-record-view {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.page-header {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  border-radius: 20px;
  margin-left: 15px;
  margin-right: 15px;
}

.nutrition-stat {
  padding: 1rem;
  border-radius: 0.5rem;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s ease-in-out;
}

.nutrition-stat:hover {
  transform: translateY(-2px);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 0.875rem;
}

.record-item:last-child {
  border-bottom: none !important;
}

.meal-badge .badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.nutrition-summary .badge {
  font-size: 0.7rem;
}

.food-search-results {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
}

.selected-food {
  border: 1px solid #28a745;
}

.nutrition-preview {
  border: 1px solid #dee2e6;
}

.modal.show {
  display: block !important;
  background-color: rgba(0,0,0,0.5);
}

.progress {
  background-color: #e9ecef;
}

.card {
  border-radius: 0.5rem;
  transition: box-shadow 0.2s ease-in-out;
}

.card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.btn {
  border-radius: 0.375rem;
}

.form-control, .form-select {
  border-radius: 0.375rem;
}

.list-group-item {
  border-radius: 0.375rem;
  margin-bottom: 0.25rem;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

@media (max-width: 768px) {
  .nutrition-stat {
    margin-bottom: 1rem;
  }
  
  .stat-value {
    font-size: 1.25rem;
  }
}
</style>
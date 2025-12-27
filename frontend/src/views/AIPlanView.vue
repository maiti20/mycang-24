<template>
  <div class="ai-plan-view container py-4">
    <!-- 页面标题 -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card border-0 bg-gradient-ai text-white">
          <div class="card-body">
            <h1 class="mb-2">
              <i class="bi bi-robot me-2"></i>
              AI健身方案
            </h1>
            <p class="mb-0 opacity-75">基于您的个人数据和健身目标，AI为您量身定制专属健身方案</p>
          </div>
        </div>
      </div>
    </div>

    <!-- AI方案生成卡片 -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h5 class="mb-0 fw-semibold">
              <i class="bi bi-magic me-2"></i>
              生成新的AI健身方案
            </h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="generateAIPlan">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-semibold">健身目标</label>
                  <select class="form-select" v-model="planForm.fitnessGoal" required>
                    <option value="">请选择健身目标</option>
                    <option value="减脂塑形">减脂塑形</option>
                    <option value="增肌强体">增肌强体</option>
                    <option value="提升耐力">提升耐力</option>
                    <option value="增强柔韧性">增强柔韧性</option>
                    <option value="综合健康">综合健康</option>
                  </select>
                </div>
                
                <div class="col-md-6">
                  <label class="form-label fw-semibold">运动经验</label>
                  <select class="form-select" v-model="planForm.experienceLevel" required>
                    <option value="">请选择运动经验</option>
                    <option value="初学者">初学者</option>
                    <option value="中级">中级</option>
                    <option value="高级">高级</option>
                  </select>
                </div>
                
                <div class="col-md-6">
                  <label class="form-label fw-semibold">每周运动天数</label>
                  <select class="form-select" v-model="planForm.weeklyFrequency" required>
                    <option value="">请选择频率</option>
                    <option value="2-3天">2-3天</option>
                    <option value="3-4天">3-4天</option>
                    <option value="4-5天">4-5天</option>
                    <option value="5-6天">5-6天</option>
                    <option value="每天">每天</option>
                  </select>
                </div>
                
                <div class="col-md-6">
                  <label class="form-label fw-semibold">每次运动时长</label>
                  <select class="form-select" v-model="planForm.sessionDuration" required>
                    <option value="">请选择时长</option>
                    <option value="30分钟以内">30分钟以内</option>
                    <option value="30-60分钟">30-60分钟</option>
                    <option value="60-90分钟">60-90分钟</option>
                    <option value="90分钟以上">90分钟以上</option>
                  </select>
                </div>
                
                <div class="col-md-6">
                  <label class="form-label fw-semibold">偏好运动类型</label>
                  <select class="form-select" v-model="planForm.preferredTypes">
                    <option value="">无特殊偏好</option>
                    <option value="有氧运动为主">有氧运动为主</option>
                    <option value="力量训练为主">力量训练为主</option>
                    <option value="混合训练">混合训练</option>
                    <option value="瑜伽普拉提">瑜伽普拉提</option>
                  </select>
                </div>
                
                <div class="col-md-6">
                  <label class="form-label fw-semibold">健康状况</label>
                  <select class="form-select" v-model="planForm.healthCondition">
                    <option value="良好">良好</option>
                    <option value="有关节问题">有关节问题</option>
                    <option value="有心血管问题">有心血管问题</option>
                    <option value="恢复期">恢复期</option>
                    <option value="其他">其他</option>
                  </select>
                </div>
                
                <div class="col-12">
                  <label class="form-label fw-semibold">特殊需求或限制</label>
                  <textarea 
                    class="form-control" 
                    rows="3" 
                    v-model="planForm.specialRequirements"
                    placeholder="如有特殊的身体状况、运动限制或具体需求，请在此说明..."
                  ></textarea>
                </div>
                
                <div class="col-12">
                  <div class="d-flex justify-content-end gap-2">
                    <button type="button" class="btn btn-outline-secondary" @click="resetForm">
                      <i class="bi bi-arrow-clockwise me-1"></i>
                      重置
                    </button>
                    <button type="submit" class="btn btn-primary" :disabled="generating">
                      <span v-if="generating" class="spinner-border spinner-border-sm me-1"></span>
                      <i class="bi bi-stars me-1"></i>
                      {{ generating ? 'AI正在思考中...' : '生成AI方案' }}
                    </button>
                  </div>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- 我的AI方案列表 -->
    <div class="row">
      <div class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="mb-0 fw-semibold">
                <i class="bi bi-collection me-2"></i>
                我的AI健身方案
              </h5>
              <span class="badge bg-primary rounded-pill">
                {{ aiPlans.length }} 个方案
              </span>
            </div>
          </div>
          <div class="card-body p-0">
            <!-- 加载状态 -->
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
              </div>
              <p class="mt-2 text-muted">正在加载AI健身方案...</p>
            </div>
            
            <!-- 方案列表 -->
            <div v-else-if="aiPlans.length > 0" class="p-3">
              <div class="row g-3">
                <div 
                  v-for="plan in aiPlans" 
                  :key="plan.id" 
                  class="col-md-6 col-lg-4"
                >
                  <div class="card h-100 border-0 shadow-sm hover-lift">
                    <div class="card-header bg-gradient-light border-bottom">
                      <div class="d-flex justify-content-between align-items-start">
                        <div>
                          <h6 class="card-title mb-1 fw-semibold">
                            {{ plan.title }}
                          </h6>
                          <small class="text-muted">
                            {{ formatDate(plan.created_at) }}
                          </small>
                        </div>
                        <span 
                          class="badge"
                          :class="getStatusBadgeClass(plan.status)"
                        >
                          {{ plan.status }}
                        </span>
                      </div>
                    </div>
                    
                    <div class="card-body">
                      <div class="mb-3">
                        <div class="d-flex align-items-center mb-2">
                          <i class="bi bi-target text-primary me-2"></i>
                          <small class="text-muted">目标：</small>
                          <span class="ms-1 fw-medium">{{ plan.fitness_goal }}</span>
                        </div>
                        
                        <div class="d-flex align-items-center mb-2">
                          <i class="bi bi-calendar-week text-success me-2"></i>
                          <small class="text-muted">频率：</small>
                          <span class="ms-1 fw-medium">{{ plan.weekly_frequency }}</span>
                        </div>
                        
                        <div class="d-flex align-items-center mb-2">
                          <i class="bi bi-clock text-warning me-2"></i>
                          <small class="text-muted">时长：</small>
                          <span class="ms-1 fw-medium">{{ plan.session_duration }}</span>
                        </div>
                        
                        <div class="d-flex align-items-center">
                          <i class="bi bi-bar-chart text-info me-2"></i>
                          <small class="text-muted">难度：</small>
                          <span class="ms-1 fw-medium">{{ plan.experience_level }}</span>
                        </div>
                      </div>
                      
                      <div class="plan-preview">
                        <p class="card-text text-muted small mb-0">
                          {{ truncateText(plan.description || plan.plan_content || '点击查看详情', 100) }}
                        </p>
                      </div>
                    </div>
                    
                    <div class="card-footer bg-white border-top">
                      <div class="btn-group w-100" role="group">
                        <button 
                          class="btn btn-outline-primary btn-sm"
                          @click="viewPlan(plan)"
                        >
                          <i class="bi bi-eye me-1"></i>
                          查看
                        </button>
                        <button 
                          class="btn btn-outline-success btn-sm"
                          @click="startPlan(plan)"
                          v-if="plan.status === '已生成'"
                        >
                          <i class="bi bi-play-circle me-1"></i>
                          开始
                        </button>
                        <button 
                          class="btn btn-outline-danger btn-sm"
                          @click="deletePlan(plan.id)"
                        >
                          <i class="bi bi-trash me-1"></i>
                          删除
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 空状态 -->
            <div v-else class="text-center py-5">
              <div class="text-muted mb-3">
                <i class="bi bi-robot fs-1"></i>
              </div>
              <h5 class="text-muted">还没有AI健身方案</h5>
              <p class="text-muted">让AI为您量身定制第一个专属健身方案吧！</p>
              <button class="btn btn-primary" @click="scrollToGenerator">
                <i class="bi bi-stars me-2"></i>
                生成AI方案
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI方案详情模态框 -->
    <div 
      class="modal fade" 
      :class="{ show: showPlanModal }" 
      :style="{ display: showPlanModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-robot me-2"></i>
              {{ selectedPlan?.title }}
            </h5>
            <button type="button" class="btn-close" @click="hidePlanModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedPlan" class="ai-plan-detail">
              <!-- 基本信息 -->
              <div class="row mb-4">
                <div class="col-md-3">
                  <div class="card border-0 bg-light">
                    <div class="card-body text-center">
                      <i class="bi bi-target text-primary fs-3 mb-2"></i>
                      <h6 class="card-title">健身目标</h6>
                      <p class="card-text fw-semibold">{{ selectedPlan.fitness_goal }}</p>
                    </div>
                  </div>
                </div>
                
                <div class="col-md-3">
                  <div class="card border-0 bg-light">
                    <div class="card-body text-center">
                      <i class="bi bi-person-walking text-success fs-3 mb-2"></i>
                      <h6 class="card-title">运动经验</h6>
                      <p class="card-text fw-semibold">{{ selectedPlan.experience_level }}</p>
                    </div>
                  </div>
                </div>
                
                <div class="col-md-3">
                  <div class="card border-0 bg-light">
                    <div class="card-body text-center">
                      <i class="bi bi-calendar-week text-warning fs-3 mb-2"></i>
                      <h6 class="card-title">运动频率</h6>
                      <p class="card-text fw-semibold">{{ selectedPlan.weekly_frequency }}</p>
                    </div>
                  </div>
                </div>
                
                <div class="col-md-3">
                  <div class="card border-0 bg-light">
                    <div class="card-body text-center">
                      <i class="bi bi-clock text-info fs-3 mb-2"></i>
                      <h6 class="card-title">运动时长</h6>
                      <p class="card-text fw-semibold">{{ selectedPlan.session_duration }}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 详细方案内容 -->
              <div class="card border-0 mb-3">
                <div class="card-header bg-light">
                  <h6 class="mb-0 fw-semibold">
                    <i class="bi bi-calendar-week me-2"></i>
                    每周训练安排
                  </h6>
                </div>
                <div class="card-body">
                  <div v-if="selectedPlan.weekly_schedule" class="row g-3">
                    <div v-for="(schedule, day) in selectedPlan.weekly_schedule" :key="day" class="col-md-6 col-lg-4">
                      <div class="card h-100 border-primary border-opacity-25">
                        <div class="card-header bg-primary bg-opacity-10 py-2">
                          <strong>{{ day }}</strong>
                          <span class="badge bg-primary float-end">{{ schedule.type }}</span>
                        </div>
                        <div class="card-body py-2">
                          <div class="small">
                            <p class="mb-1"><i class="bi bi-clock me-1"></i>{{ schedule.duration }}分钟 | 强度: {{ schedule.intensity }}</p>
                            <p class="mb-1 fw-medium">训练内容：</p>
                            <ul class="mb-1 ps-3">
                              <li v-for="(activity, idx) in schedule.activities" :key="idx">{{ activity }}</li>
                            </ul>
                            <p v-if="schedule.notes" class="mb-0 text-muted"><i class="bi bi-info-circle me-1"></i>{{ schedule.notes }}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="plan-content" v-html="formatPlanContent(selectedPlan.plan_content || selectedPlan.description || '')"></div>
                </div>
              </div>

              <!-- 营养建议 -->
              <div v-if="selectedPlan.nutrition_advice" class="card border-0 mb-3">
                <div class="card-header bg-success bg-opacity-10">
                  <h6 class="mb-0 fw-semibold text-success">
                    <i class="bi bi-egg-fried me-2"></i>
                    营养建议
                  </h6>
                </div>
                <div class="card-body">
                  <div class="plan-content" v-html="formatPlanContent(selectedPlan.nutrition_advice)"></div>
                </div>
              </div>

              <!-- 注意事项 -->
              <div v-if="selectedPlan.tips && selectedPlan.tips.length" class="card border-0">
                <div class="card-header bg-warning bg-opacity-10">
                  <h6 class="mb-0 fw-semibold text-warning">
                    <i class="bi bi-lightbulb me-2"></i>
                    注意事项
                  </h6>
                </div>
                <div class="card-body">
                  <ul class="mb-0">
                    <li v-for="(tip, idx) in selectedPlan.tips" :key="idx" class="mb-1">{{ tip }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-outline-danger me-auto"
              @click="selectedPlan && deletePlan(selectedPlan.id)"
            >
              <i class="bi bi-trash me-1"></i>
              删除方案
            </button>
            <button type="button" class="btn btn-secondary" @click="hidePlanModal">
              关闭
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="startPlan(selectedPlan!)"
              v-if="selectedPlan?.status === '已生成'"
            >
              <i class="bi bi-play-circle me-1"></i>
              开始执行此方案
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { aiPlanApi } from '@/utils/api'

interface AIPlan {
  id: number
  user_id?: number
  title: string
  description?: string
  plan_type?: string
  fitness_goal?: string
  experience_level?: string
  weekly_frequency?: string
  session_duration?: string
  preferred_types?: string
  health_condition?: string
  special_requirements?: string
  plan_content?: string
  weekly_schedule?: Record<string, any>
  nutrition_advice?: string
  tips?: string[]
  status?: string
  created_at: string
  updated_at?: string
}

const router = useRouter()

const loading = ref(false)
const generating = ref(false)
const aiPlans = ref<AIPlan[]>([])
const showPlanModal = ref(false)
const selectedPlan = ref<AIPlan | null>(null)

const planForm = reactive({
  fitnessGoal: '',
  experienceLevel: '',
  weeklyFrequency: '',
  sessionDuration: '',
  preferredTypes: '',
  healthCondition: '良好',
  specialRequirements: ''
})

const fetchAIPlans = async () => {
  loading.value = true
  try {
    const response = await aiPlanApi.getPlans()
    if (response.success || response.plans) {
      aiPlans.value = response.plans || response.data?.plans || []
    } else {
      aiPlans.value = []
    }
  } catch (error) {
    console.error('获取AI方案失败:', error)
    aiPlans.value = []
  } finally {
    loading.value = false
  }
}

const generateAIPlan = async () => {
  generating.value = true
  try {
    const requestData = {
      fitness_goal: planForm.fitnessGoal,
      experience_level: planForm.experienceLevel,
      weekly_frequency: planForm.weeklyFrequency,
      session_duration: planForm.sessionDuration,
      preferred_types: planForm.preferredTypes || undefined,
      health_condition: planForm.healthCondition,
      special_requirements: planForm.specialRequirements || undefined
    }

    const response = await aiPlanApi.generatePlan(requestData)

    if (response.success && response.data) {
      // 直接显示生成的方案
      const newPlan: AIPlan = {
        id: response.data.id,
        title: response.data.title,
        description: response.data.description,
        weekly_schedule: response.data.weekly_schedule,
        nutrition_advice: response.data.nutrition_advice,
        tips: response.data.tips,
        created_at: response.data.created_at || new Date().toISOString()
      }

      // 添加到列表顶部
      aiPlans.value.unshift(newPlan)

      // 显示方案详情
      selectedPlan.value = newPlan
      showPlanModal.value = true

      resetForm()
    } else {
      throw new Error(response.message || '生成失败')
    }
  } catch (error) {
    console.error('生成AI方案失败:', error)
    alert('生成AI方案失败，请稍后重试。错误信息：' + (error as Error).message)
  } finally {
    generating.value = false
  }
}

const resetForm = () => {
  planForm.fitnessGoal = ''
  planForm.experienceLevel = ''
  planForm.weeklyFrequency = ''
  planForm.sessionDuration = ''
  planForm.preferredTypes = ''
  planForm.healthCondition = '良好'
  planForm.specialRequirements = ''
}

const viewPlan = (plan: AIPlan) => {
  selectedPlan.value = plan
  showPlanModal.value = true
}

const hidePlanModal = () => {
  showPlanModal.value = false
  selectedPlan.value = null
}

const startPlan = (plan: AIPlan) => {
  // 跳转到运动记录页面，并传递方案信息
  router.push({
    name: 'ExerciseLog',
    query: { planId: plan.id.toString() }
  })
}

const deletePlan = async (id: number) => {
  if (!confirm('确定要删除这个AI健身方案吗？删除后无法恢复。')) return

  try {
    const response = await aiPlanApi.deletePlan(id)
    if (response.success) {
      // 从列表中移除
      aiPlans.value = aiPlans.value.filter(p => p.id !== id)

      // 如果正在查看的方案被删除，关闭模态框
      if (selectedPlan.value?.id === id) {
        hidePlanModal()
      }
    } else {
      throw new Error(response.message || '删除失败')
    }
  } catch (error) {
    console.error('删除AI方案失败:', error)
    alert('删除AI方案失败: ' + (error as Error).message)
  }
}

const scrollToGenerator = () => {
  const element = document.querySelector('.card-header')
  element?.scrollIntoView({ behavior: 'smooth' })
}

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case '已生成':
      return 'bg-success'
    case '生成中':
      return 'bg-warning'
    case '进行中':
      return 'bg-primary'
    default:
      return 'bg-secondary'
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const truncateText = (text: string, maxLength: number) => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const formatPlanContent = (content: string) => {
  if (!content) return ''
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/###\s*(.*?)(<br>|$)/g, '<h6 class="mt-3 mb-2 fw-bold">$1</h6>')
    .replace(/##\s*(.*?)(<br>|$)/g, '<h5 class="mt-3 mb-2 fw-bold text-primary">$1</h5>')
    .replace(/-\s*(.*?)(<br>|$)/g, '<li class="ms-3">$1</li>')
}

onMounted(() => {
  fetchAIPlans()
})
</script>

<style scoped>
.bg-gradient-ai {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.bg-gradient-light {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.hover-lift {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
}

.modal.show {
  background-color: rgba(0, 0, 0, 0.5);
}

.plan-preview {
  max-height: 60px;
  overflow: hidden;
}

.plan-content {
  line-height: 1.6;
}

.plan-content :deep(strong) {
  color: #495057;
  font-weight: 600;
}

.card {
  transition: all 0.2s ease-in-out;
}

.btn-group .btn {
  flex: 1;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

.form-label {
  color: #495057;
  font-weight: 500;
}

.form-select:focus,
.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}
</style>
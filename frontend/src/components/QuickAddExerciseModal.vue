<template>
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-plus-circle me-2"></i>
            {{ exercise?.name || '添加运动记录' }}
          </h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- 运动信息展示 -->
            <div v-if="exercise" class="alert alert-info mb-4">
              <div class="row">
                <div class="col-md-6">
                  <strong>运动类型：</strong>{{ exercise.category }}<br>
                  <strong>难度等级：</strong>
                  <span class="badge" :class="getDifficultyBadgeClass(exercise.difficulty_level)">
                    {{ exercise.difficulty_level }}
                  </span>
                </div>
                <div class="col-md-6">
                  <strong>消耗热量：</strong>{{ exercise.calories_per_minute }} 千卡/分钟<br>
                  <strong>目标肌群：</strong>{{ exercise.muscle_groups.join(', ') }}
                </div>
              </div>
            </div>

            <!-- 运动选择 -->
            <div class="mb-3">
              <label class="form-label">选择运动 *</label>
              <select 
                class="form-select" 
                v-model="formData.exercise_id" 
                :disabled="!!exercise"
                required
              >
                <option value="">请选择运动</option>
                <option 
                  v-for="ex in availableExercises" 
                  :key="ex.id" 
                  :value="ex.id"
                >
                  {{ ex.name }} ({{ ex.category }} - {{ ex.calories_per_minute }}千卡/分钟)
                </option>
              </select>
            </div>

            <!-- 运动时长 -->
            <div class="mb-3">
              <label class="form-label">运动时长 (分钟) *</label>
              <div class="input-group">
                <input 
                  type="number" 
                  class="form-control" 
                  v-model.number="formData.duration_minutes"
                  min="1"
                  max="999"
                  required
                  @input="calculateCalories"
                >
                <span class="input-group-text">分钟</span>
              </div>
              <small class="text-muted">建议运动时长：10-120分钟</small>
            </div>

            <!-- 强度等级 -->
            <div class="mb-3">
              <label class="form-label">运动强度 *</label>
              <select class="form-select" v-model="formData.intensity_level" required>
                <option value="">请选择强度</option>
                <option value="低强度">低强度</option>
                <option value="中等强度">中等强度</option>
                <option value="高强度">高强度</option>
                <option value="极限强度">极限强度</option>
              </select>
            </div>

            <!-- 预计消耗热量 -->
            <div class="mb-3">
              <label class="form-label">预计消耗热量</label>
              <div class="input-group">
                <input 
                  type="number" 
                  class="form-control" 
                  v-model.number="estimatedCalories"
                  readonly
                >
                <span class="input-group-text">千卡</span>
              </div>
              <small class="text-muted">系统会根据运动类型、时长和强度自动计算</small>
            </div>

            <!-- 运动日期和时间 -->
            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label">运动日期 *</label>
                <input 
                  type="date" 
                  class="form-control" 
                  v-model="formData.exercise_date"
                  required
                >
              </div>
              <div class="col-md-6">
                <label class="form-label">运动时间</label>
                <input 
                  type="time" 
                  class="form-control" 
                  v-model="formData.exercise_time"
                >
              </div>
            </div>

            <!-- 备注 -->
            <div class="mb-3">
              <label class="form-label">备注</label>
              <textarea 
                class="form-control" 
                v-model="formData.notes"
                rows="3"
                placeholder="记录运动感受、身体状况等信息..."
              ></textarea>
            </div>

            <!-- 心率监测 -->
            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label">平均心率</label>
                <div class="input-group">
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model.number="formData.avg_heart_rate"
                    min="40"
                    max="220"
                  >
                  <span class="input-group-text">bpm</span>
                </div>
              </div>
              <div class="col-md-6">
                <label class="form-label">最大心率</label>
                <div class="input-group">
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model.number="formData.max_heart_rate"
                    min="40"
                    max="220"
                  >
                  <span class="input-group-text">bpm</span>
                </div>
              </div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">
            取消
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="handleSubmit"
            :disabled="submitting"
          >
            <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
            {{ submitting ? '保存中...' : '保存记录' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { exerciseApi } from '@/utils/api'

interface Exercise {
  id: number
  name: string
  category: string
  calories_per_minute: number
  difficulty_level: string
  muscle_groups: string[]
}

interface Props {
  exercise?: Exercise | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  added: []
}>()

// 表单数据
const formData = reactive({
  exercise_id: props.exercise?.id || '',
  duration_minutes: 30,
  intensity_level: '中等强度',
  exercise_date: new Date().toISOString().split('T')[0],
  exercise_time: new Date().toTimeString().slice(0, 5),
  notes: '',
  avg_heart_rate: null as number | null,
  max_heart_rate: null as number | null
})

// 组件状态
const submitting = ref(false)
const availableExercises = ref<Exercise[]>([])

// 计算属性
const estimatedCalories = computed(() => {
  if (!formData.exercise_id || !formData.duration_minutes) return 0
  
  const exercise = availableExercises.value.find(ex => ex.id === formData.exercise_id)
  if (!exercise) return 0
  
  let baseCalories = exercise.calories_per_minute * formData.duration_minutes
  
  // 根据强度调整系数
  const intensityMultiplier = {
    '低强度': 0.8,
    '中等强度': 1.0,
    '高强度': 1.3,
    '极限强度': 1.6
  }
  
  const multiplier = intensityMultiplier[formData.intensity_level as keyof typeof intensityMultiplier] || 1.0
  return Math.round(baseCalories * multiplier)
})

// 监听器
watch(() => props.exercise, (newExercise) => {
  if (newExercise) {
    formData.exercise_id = newExercise.id
  }
}, { immediate: true })

// 方法
const loadExercises = async () => {
  try {
    const response = await exerciseApi.getExercises({ limit: '100' })
    if (response.success) {
      availableExercises.value = response.data.exercises
    }
  } catch (error) {
    console.error('加载运动列表失败:', error)
  }
}

const calculateCalories = () => {
  // 触发重新计算
  // 由于使用了computed属性，这里不需要额外操作
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

const validateForm = () => {
  if (!formData.exercise_id) {
    throw new Error('请选择运动项目')
  }
  if (!formData.duration_minutes || formData.duration_minutes <= 0) {
    throw new Error('请输入有效的运动时长')
  }
  if (!formData.intensity_level) {
    throw new Error('请选择运动强度')
  }
  if (!formData.exercise_date) {
    throw new Error('请选择运动日期')
  }
  
  // 心率合理性检查
  if (formData.avg_heart_rate && formData.max_heart_rate) {
    if (formData.avg_heart_rate > formData.max_heart_rate) {
      throw new Error('平均心率不能大于最大心率')
    }
  }
}

const handleSubmit = async () => {
  try {
    submitting.value = true
    validateForm()
    
    const submitData = {
      exercise_id: formData.exercise_id,
      duration_minutes: formData.duration_minutes,
      intensity_level: formData.intensity_level,
      exercise_date: formData.exercise_date,
      exercise_time: formData.exercise_time || null,
      notes: formData.notes || null,
      avg_heart_rate: formData.avg_heart_rate || null,
      max_heart_rate: formData.max_heart_rate || null
    }
    
    const response = await exerciseApi.createExerciseLog(submitData)
    
    if (response.success) {
      emit('added')
      emit('close')
    } else {
      throw new Error(response.message || '添加运动记录失败')
    }
  } catch (error) {
    console.error('提交运动记录失败:', error)
    alert(error instanceof Error ? error.message : '添加运动记录失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 生命周期
onMounted(() => {
  loadExercises()
})
</script>

<style scoped>
.modal {
  z-index: 1055;
}

.modal-dialog {
  margin-top: 5vh;
}

.form-label {
  font-weight: 600;
  color: #495057;
}

.input-group-text {
  background-color: #f8f9fa;
  border-color: #ced4da;
}

.alert {
  border-left: 4px solid #0dcaf0;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}
</style>
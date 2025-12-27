<template>
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-trophy me-2"></i>
            {{ exercise?.name || '运动详情' }}
          </h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <div v-if="exercise" class="row">
            <!-- 左侧：基本信息 -->
            <div class="col-md-6">
              <div class="card mb-3">
                <div class="card-header">
                  <h6 class="mb-0">
                    <i class="bi bi-info-circle me-2"></i>基本信息
                  </h6>
                </div>
                <div class="card-body">
                  <table class="table table-borderless">
                    <tbody>
                      <tr>
                        <td><strong>运动类别：</strong></td>
                        <td>
                          <span class="badge bg-primary">{{ exercise.category }}</span>
                        </td>
                      </tr>
                      <tr>
                        <td><strong>难度等级：</strong></td>
                        <td>
                          <span 
                            class="badge"
                            :class="getDifficultyBadgeClass(exercise.difficulty_level)"
                          >
                            {{ exercise.difficulty_level }}
                          </span>
                        </td>
                      </tr>
                      <tr>
                        <td><strong>热量消耗：</strong></td>
                        <td>
                          <span class="badge bg-info text-white">
                            {{ exercise.calories_per_minute }} 千卡/分钟
                          </span>
                        </td>
                      </tr>
                      <tr>
                        <td><strong>建议时长：</strong></td>
                        <td>{{ getRecommendedDuration(exercise.difficulty_level) }} 分钟</td>
                      </tr>
                    </tbody>
                  </table>
                  
                  <div class="mt-3">
                    <h6>运动描述</h6>
                    <p class="text-muted">{{ exercise.description }}</p>
                  </div>
                </div>
              </div>

              <!-- 目标肌群 -->
              <div class="card mb-3">
                <div class="card-header">
                  <h6 class="mb-0">
                    <i class="bi bi-person-arms-up me-2"></i>目标肌群
                  </h6>
                </div>
                <div class="card-body">
                  <div class="d-flex flex-wrap gap-2">
                    <span 
                      v-for="muscle in exercise.muscle_groups" 
                      :key="muscle"
                      class="badge bg-secondary"
                    >
                      {{ muscle }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- 所需器材 -->
              <div v-if="exercise.equipment_needed.length > 0" class="card mb-3">
                <div class="card-header">
                  <h6 class="mb-0">
                    <i class="bi bi-tools me-2"></i>所需器材
                  </h6>
                </div>
                <div class="card-body">
                  <div class="d-flex flex-wrap gap-2">
                    <span 
                      v-for="equipment in exercise.equipment_needed" 
                      :key="equipment"
                      class="badge bg-warning text-dark"
                    >
                      {{ equipment }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 右侧：详细信息和操作 -->
            <div class="col-md-6">
              <!-- 运动教程 -->
              <div class="card mb-3">
                <div class="card-header">
                  <h6 class="mb-0">
                    <i class="bi bi-play-circle me-2"></i>运动教程
                  </h6>
                </div>
                <div class="card-body">
                  <div v-if="exercise.tutorial_url" class="ratio ratio-16x9">
                    <iframe 
                      :src="getEmbedUrl(exercise.tutorial_url)"
                      frameborder="0"
                      allowfullscreen
                    ></iframe>
                  </div>
                  <div v-else class="text-center py-4">
                    <i class="bi bi-youtube fs-1 text-muted mb-3"></i>
                    <p class="text-muted">暂无视频教程</p>
                    <small class="text-muted">
                      建议在专业教练指导下进行训练，确保动作标准
                    </small>
                  </div>
                </div>
              </div>

              <!-- 卡路里计算器 -->
              <div class="card mb-3">
                <div class="card-header">
                  <h6 class="mb-0">
                    <i class="bi bi-calculator me-2"></i>卡路里计算器
                  </h6>
                </div>
                <div class="card-body">
                  <div class="mb-3">
                    <label class="form-label">运动时长（分钟）</label>
                    <input 
                      type="range" 
                      class="form-range" 
                      v-model.number="calculatorMinutes"
                      min="5"
                      max="120"
                      step="5"
                    >
                    <div class="d-flex justify-content-between">
                      <small>5分钟</small>
                      <strong>{{ calculatorMinutes }} 分钟</strong>
                      <small>120分钟</small>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label">运动强度</label>
                    <select class="form-select" v-model="calculatorIntensity">
                      <option value="低强度">低强度</option>
                      <option value="中等强度">中等强度</option>
                      <option value="高强度">高强度</option>
                      <option value="极限强度">极限强度</option>
                    </select>
                  </div>
                  
                  <div class="alert alert-info mb-0">
                    <h6 class="alert-heading">预计消耗热量</h6>
                    <h3 class="mb-0">{{ calculatedCalories }} 千卡</h3>
                    <small class="text-muted">
                      基础值 × 强度系数 ({{ getIntensityMultiplier(calculatorIntensity) }})
                    </small>
                  </div>
                </div>
              </div>

              <!-- 安全提示 -->
              <div class="card">
                <div class="card-header">
                  <h6 class="mb-0">
                    <i class="bi bi-shield-exclamation me-2"></i>安全提示
                  </h6>
                </div>
                <div class="card-body">
                  <ul class="list-unstyled mb-0">
                    <li class="mb-2">
                      <i class="bi bi-check-circle text-success me-2"></i>
                      运动前进行充分热身，预防运动损伤
                    </li>
                    <li class="mb-2">
                      <i class="bi bi-check-circle text-success me-2"></i>
                      保持正确的姿势和呼吸节奏
                    </li>
                    <li class="mb-2">
                      <i class="bi bi-check-circle text-success me-2"></i>
                      循序渐进增加运动强度和时长
                    </li>
                    <li class="mb-2">
                      <i class="bi bi-check-circle text-success me-2"></i>
                      如感不适立即停止运动并咨询医生
                    </li>
                    <li class="mb-0">
                      <i class="bi bi-check-circle text-success me-2"></i>
                      运动后进行适当拉伸放松
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">
            关闭
          </button>
          <button 
            type="button" 
            class="btn btn-success"
            @click="$emit('add-record', exercise)"
          >
            <i class="bi bi-plus-circle me-2"></i>
            添加运动记录
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

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

interface Props {
  exercise?: Exercise | null
}

defineProps<Props>()
const emit = defineEmits<{
  close: []
  addRecord: [exercise: Exercise]
}>()

// 计算器状态
const calculatorMinutes = ref(30)
const calculatorIntensity = ref('中等强度')

// 计算属性
const calculatedCalories = computed(() => {
  if (!props.exercise) return 0
  
  const baseCalories = props.exercise.calories_per_minute * calculatorMinutes.value
  const multiplier = getIntensityMultiplier(calculatorIntensity.value)
  return Math.round(baseCalories * multiplier)
})

// 方法
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

const getRecommendedDuration = (difficulty: string) => {
  switch (difficulty) {
    case '初级':
      return '20-30'
    case '中级':
      return '30-45'
    case '高级':
      return '45-60'
    default:
      return '30'
  }
}

const getIntensityMultiplier = (intensity: string) => {
  const multipliers = {
    '低强度': 0.8,
    '中等强度': 1.0,
    '高强度': 1.3,
    '极限强度': 1.6
  }
  return multipliers[intensity as keyof typeof multipliers] || 1.0
}

const getEmbedUrl = (url: string) => {
  // 将YouTube链接转换为嵌入格式
  if (url.includes('youtube.com/watch?v=')) {
    const videoId = url.split('v=')[1]?.split('&')[0]
    return `https://www.youtube.com/embed/${videoId}`
  }
  if (url.includes('youtu.be/')) {
    const videoId = url.split('youtu.be/')[1]?.split('?')[0]
    return `https://www.youtube.com/embed/${videoId}`
  }
  return url
}
</script>

<style scoped>
.modal {
  z-index: 1055;
}

.modal-dialog {
  margin-top: 3vh;
}

.table td {
  padding: 0.5rem;
  vertical-align: middle;
}

.badge {
  font-size: 0.8em;
}

.form-range::-webkit-slider-thumb {
  background: #0d6efd;
}

.form-range::-moz-range-thumb {
  background: #0d6efd;
}

.ratio iframe {
  border-radius: 0.375rem;
}

.list-unstyled li {
  font-size: 0.9rem;
  line-height: 1.5;
}

.alert-info {
  border-left: 4px solid #0dcaf0;
}
</style>
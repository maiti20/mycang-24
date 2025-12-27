<template>
  <div class="auth-container min-vh-100 d-flex align-items-center justify-content-center bg-light">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
          <div class="card shadow-lg border-0">
            <div class="card-body p-5">
              <!-- Logo和标题 -->
              <div class="text-center mb-4">
                <div class="mb-3">
                  <i class="bi bi-heart-pulse-fill text-primary" style="font-size: 3rem;"></i>
                </div>
                <h2 class="fw-bold text-dark">加入我们</h2>
                <p class="text-muted">创建您的健身账户，开启健康生活</p>
              </div>

              <!-- 错误提示 -->
              <div v-if="errorMessage" class="alert alert-danger d-flex align-items-center" role="alert">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                {{ errorMessage }}
              </div>

              <!-- 注册表单 -->
              <form @submit.prevent="handleRegister">
                <div class="row">
                  <!-- 基本信息 -->
                  <div class="col-12">
                    <h5 class="mb-3 text-primary">
                      <i class="bi bi-person-badge me-2"></i>基本信息
                    </h5>
                  </div>

                  <!-- 用户名 -->
                  <div class="col-md-6 mb-3">
                    <label for="username" class="form-label fw-semibold">
                      <i class="bi bi-person me-1"></i>用户名 *
                    </label>
                    <input
                      type="text"
                      class="form-control"
                      id="username"
                      v-model="formData.username"
                      :class="{ 'is-invalid': errors.username }"
                      placeholder="请输入用户名"
                      required
                    >
                    <div v-if="errors.username" class="invalid-feedback">
                      {{ errors.username }}
                    </div>
                  </div>

                  <!-- 邮箱 -->
                  <div class="col-md-6 mb-3">
                    <label for="email" class="form-label fw-semibold">
                      <i class="bi bi-envelope me-1"></i>邮箱 *
                    </label>
                    <input
                      type="email"
                      class="form-control"
                      id="email"
                      v-model="formData.email"
                      :class="{ 'is-invalid': errors.email }"
                      placeholder="请输入邮箱地址"
                      required
                    >
                    <div v-if="errors.email" class="invalid-feedback">
                      {{ errors.email }}
                    </div>
                  </div>

                  <!-- 密码 -->
                  <div class="col-md-6 mb-3">
                    <label for="password" class="form-label fw-semibold">
                      <i class="bi bi-lock me-1"></i>密码 *
                    </label>
                    <div class="input-group">
                      <input
                        :type="showPassword ? 'text' : 'password'"
                        class="form-control"
                        id="password"
                        v-model="formData.password"
                        :class="{ 'is-invalid': errors.password }"
                        placeholder="请输入密码"
                        required
                      >
                      <button
                        type="button"
                        class="btn btn-outline-secondary"
                        @click="togglePassword"
                      >
                        <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                      </button>
                    </div>
                    <div v-if="errors.password" class="invalid-feedback">
                      {{ errors.password }}
                    </div>
                  </div>

                  <!-- 确认密码 -->
                  <div class="col-md-6 mb-3">
                    <label for="confirmPassword" class="form-label fw-semibold">
                      <i class="bi bi-lock-fill me-1"></i>确认密码 *
                    </label>
                    <input
                      type="password"
                      class="form-control"
                      id="confirmPassword"
                      v-model="formData.confirmPassword"
                      :class="{ 'is-invalid': errors.confirmPassword }"
                      placeholder="请再次输入密码"
                      required
                    >
                    <div v-if="errors.confirmPassword" class="invalid-feedback">
                      {{ errors.confirmPassword }}
                    </div>
                  </div>
                </div>

                <!-- 可选信息 -->
                <div class="row mt-4">
                  <div class="col-12">
                    <h5 class="mb-3 text-primary">
                      <i class="bi bi-sliders me-2"></i>可选信息（有助于个性化推荐）
                    </h5>
                  </div>

                  <!-- 年龄 -->
                  <div class="col-md-4 mb-3">
                    <label for="age" class="form-label fw-semibold">
                      <i class="bi bi-calendar me-1"></i>年龄
                    </label>
                    <input
                      type="number"
                      class="form-control"
                      id="age"
                      v-model.number="formData.age"
                      :class="{ 'is-invalid': errors.age }"
                      placeholder="请输入年龄"
                      min="1"
                      max="120"
                    >
                    <div v-if="errors.age" class="invalid-feedback">
                      {{ errors.age }}
                    </div>
                  </div>

                  <!-- 性别 -->
                  <div class="col-md-4 mb-3">
                    <label for="gender" class="form-label fw-semibold">
                      <i class="bi bi-gender-ambiguous me-1"></i>性别
                    </label>
                    <select
                      class="form-select"
                      id="gender"
                      v-model="formData.gender"
                    >
                      <option value="">请选择</option>
                      <option value="male">男性</option>
                      <option value="female">女性</option>
                    </select>
                  </div>

                  <!-- 身高 -->
                  <div class="col-md-4 mb-3">
                    <label for="height" class="form-label fw-semibold">
                      <i class="bi bi-rulers me-1"></i>身高(cm)
                    </label>
                    <input
                      type="number"
                      class="form-control"
                      id="height"
                      v-model.number="formData.height"
                      :class="{ 'is-invalid': errors.height }"
                      placeholder="请输入身高"
                      min="50"
                      max="250"
                    >
                    <div v-if="errors.height" class="invalid-feedback">
                      {{ errors.height }}
                    </div>
                  </div>

                  <!-- 体重 -->
                  <div class="col-md-6 mb-3">
                    <label for="weight" class="form-label fw-semibold">
                      <i class="bi bi-speedometer2 me-1"></i>体重(kg)
                    </label>
                    <input
                      type="number"
                      class="form-control"
                      id="weight"
                      v-model.number="formData.weight"
                      :class="{ 'is-invalid': errors.weight }"
                      placeholder="请输入体重"
                      min="20"
                      max="300"
                      step="0.1"
                    >
                    <div v-if="errors.weight" class="invalid-feedback">
                      {{ errors.weight }}
                    </div>
                  </div>

                  <!-- 健身目标 -->
                  <div class="col-md-6 mb-3">
                    <label for="fitnessGoal" class="form-label fw-semibold">
                      <i class="bi bi-trophy me-1"></i>健身目标
                    </label>
                    <select
                      class="form-select"
                      id="fitnessGoal"
                      v-model="formData.fitness_goal"
                    >
                      <option value="">请选择健身目标</option>
                      <option value="减脂塑形">减脂塑形</option>
                      <option value="增肌增重">增肌增重</option>
                      <option value="保持健康">保持健康</option>
                      <option value="提升体能">提升体能</option>
                      <option value="康复训练">康复训练</option>
                    </select>
                  </div>
                </div>

                <!-- 服务条款 -->
                <div class="mb-4">
                  <div class="form-check">
                    <input
                      type="checkbox"
                      class="form-check-input"
                      id="terms"
                      v-model="agreeTerms"
                      :class="{ 'is-invalid': errors.agreeTerms }"
                      required
                    >
                    <label class="form-check-label" for="terms">
                      我已阅读并同意<a href="#" class="text-primary">服务条款</a>和<a href="#" class="text-primary">隐私政策</a>
                    </label>
                    <div v-if="errors.agreeTerms" class="invalid-feedback">
                      {{ errors.agreeTerms }}
                    </div>
                  </div>
                </div>

                <!-- 注册按钮 -->
                <button
                  type="submit"
                  class="btn btn-primary btn-lg w-100 py-3 mb-3"
                  :disabled="isLoading"
                >
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ isLoading ? '注册中...' : '立即注册' }}
                </button>

                <!-- 分割线 -->
                <div class="position-relative my-4">
                  <hr>
                  <div class="position-absolute top-50 start-50 translate-middle bg-white px-3 text-muted">
                    或
                  </div>
                </div>

                <!-- 登录链接 -->
                <div class="text-center">
                  <span class="text-muted">已有账户？</span>
                  <router-link to="/login" class="text-decoration-none text-primary fw-semibold">
                    立即登录
                  </router-link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 表单数据
const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  age: undefined as number | undefined,
  gender: undefined as 'male' | 'female' | undefined,
  height: undefined as number | undefined,
  weight: undefined as number | undefined,
  fitness_goal: ''
})

// 表单验证错误
const errors = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  age: '',
  height: '',
  weight: '',
  agreeTerms: ''
})

// 组件状态
const isLoading = ref(false)
const errorMessage = ref('')
const showPassword = ref(false)
const agreeTerms = ref(false)

// 切换密码显示
const togglePassword = () => {
  showPassword.value = !showPassword.value
}

// 表单验证
const validateForm = () => {
  // 清空之前的错误
  Object.keys(errors).forEach(key => {
    errors[key as keyof typeof errors] = ''
  })

  let isValid = true

  // 用户名验证
  if (!formData.username.trim()) {
    errors.username = '请输入用户名'
    isValid = false
  } else if (formData.username.length < 3) {
    errors.username = '用户名至少3个字符'
    isValid = false
  } else if (formData.username.length > 20) {
    errors.username = '用户名最多20个字符'
    isValid = false
  }

  // 邮箱验证
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!formData.email.trim()) {
    errors.email = '请输入邮箱地址'
    isValid = false
  } else if (!emailRegex.test(formData.email)) {
    errors.email = '请输入有效的邮箱地址'
    isValid = false
  }

  // 密码验证
  if (!formData.password) {
    errors.password = '请输入密码'
    isValid = false
  } else if (formData.password.length < 6) {
    errors.password = '密码至少6个字符'
    isValid = false
  } else if (formData.password.length > 50) {
    errors.password = '密码最多50个字符'
    isValid = false
  }

  // 确认密码验证
  if (!formData.confirmPassword) {
    errors.confirmPassword = '请确认密码'
    isValid = false
  } else if (formData.password !== formData.confirmPassword) {
    errors.confirmPassword = '两次输入的密码不一致'
    isValid = false
  }

  // 年龄验证
  if (formData.age !== undefined) {
    if (formData.age < 1 || formData.age > 120) {
      errors.age = '请输入有效的年龄（1-120岁）'
      isValid = false
    }
  }

  // 身高验证
  if (formData.height !== undefined) {
    if (formData.height < 50 || formData.height > 250) {
      errors.height = '请输入有效的身高（50-250cm）'
      isValid = false
    }
  }

  // 体重验证
  if (formData.weight !== undefined) {
    if (formData.weight < 20 || formData.weight > 300) {
      errors.weight = '请输入有效的体重（20-300kg）'
      isValid = false
    }
  }

  // 服务条款验证
  if (!agreeTerms.value) {
    errors.agreeTerms = '请同意服务条款和隐私政策'
    isValid = false
  }

  return isValid
}

// 处理注册
const handleRegister = async () => {
  if (!validateForm()) {
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    // 准备注册数据（排除confirmPassword）
    const { confirmPassword, ...registerData } = formData
    
    const result = await authStore.register(registerData)
    
    if (result.success) {
      // 注册成功，跳转到首页
      router.push('/')
    } else {
      errorMessage.value = result.error || '注册失败，请重试'
    }
  } catch (error: any) {
    errorMessage.value = error.message || '注册过程中发生错误，请重试'
  } finally {
    isLoading.value = false
  }
}

// 页面加载时检查是否已登录
onMounted(async () => {
  await authStore.initializeAuth()
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})
</script>

<style scoped>
.auth-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card {
  border-radius: 15px;
  overflow: hidden;
}

.form-control:focus,
.form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: transform 0.2s ease-in-out;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.text-primary {
  color: #667eea !important;
}

.bi-heart-pulse-fill {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .card-body {
    padding: 2rem !important;
  }
  
  h5 {
    font-size: 1rem;
  }
}
</style>
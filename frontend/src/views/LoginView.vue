<template>
  <div class="auth-container min-vh-100 d-flex align-items-center justify-content-center bg-light">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow-lg border-0">
            <div class="card-body p-5">
              <!-- Logo和标题 -->
              <div class="text-center mb-4">
                <div class="mb-3">
                  <i class="bi bi-heart-pulse-fill text-primary" style="font-size: 3rem;"></i>
                </div>
                <h2 class="fw-bold text-dark">健身打卡系统</h2>
                <p class="text-muted">欢迎回来，请登录您的账户</p>
              </div>

              <!-- 错误提示 -->
              <div v-if="errorMessage" class="alert alert-danger d-flex align-items-center" role="alert">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                {{ errorMessage }}
              </div>

              <!-- 登录表单 -->
              <form @submit.prevent="handleLogin">
                <!-- 用户名 -->
                <div class="mb-3">
                  <label for="username" class="form-label fw-semibold">
                    <i class="bi bi-person me-1"></i>用户名
                  </label>
                  <input
                    type="text"
                    class="form-control form-control-lg"
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

                <!-- 密码 -->
                <div class="mb-4">
                  <label for="password" class="form-label fw-semibold">
                    <i class="bi bi-lock me-1"></i>密码
                  </label>
                  <div class="input-group">
                    <input
                      :type="showPassword ? 'text' : 'password'"
                      class="form-control form-control-lg"
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

                <!-- 记住我和忘记密码 -->
                <div class="d-flex justify-content-between align-items-center mb-4">
                  <div class="form-check">
                    <input
                      type="checkbox"
                      class="form-check-input"
                      id="remember"
                      v-model="rememberMe"
                    >
                    <label class="form-check-label" for="remember">
                      记住我
                    </label>
                  </div>
                  <a href="#" class="text-decoration-none text-primary">
                    忘记密码？
                  </a>
                </div>

                <!-- 登录按钮 -->
                <button
                  type="submit"
                  class="btn btn-primary btn-lg w-100 py-3 mb-3"
                  :disabled="isLoading"
                >
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ isLoading ? '登录中...' : '登录' }}
                </button>

                <!-- 分割线 -->
                <div class="position-relative my-4">
                  <hr>
                  <div class="position-absolute top-50 start-50 translate-middle bg-white px-3 text-muted">
                    或
                  </div>
                </div>

                <!-- 注册链接 -->
                <div class="text-center">
                  <span class="text-muted">还没有账户？</span>
                  <router-link to="/register" class="text-decoration-none text-primary fw-semibold">
                    立即注册
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
  password: ''
})

// 表单验证错误
const errors = reactive({
  username: '',
  password: ''
})

// 组件状态
const isLoading = ref(false)
const errorMessage = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)

// 切换密码显示
const togglePassword = () => {
  showPassword.value = !showPassword.value
}

// 表单验证
const validateForm = () => {
  errors.username = ''
  errors.password = ''

  let isValid = true

  if (!formData.username.trim()) {
    errors.username = '请输入用户名'
    isValid = false
  } else if (formData.username.length < 3) {
    errors.username = '用户名至少3个字符'
    isValid = false
  }

  if (!formData.password) {
    errors.password = '请输入密码'
    isValid = false
  } else if (formData.password.length < 6) {
    errors.password = '密码至少6个字符'
    isValid = false
  }

  return isValid
}

// 处理登录
const handleLogin = async () => {
  if (!validateForm()) {
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const result = await authStore.login(formData)
    
    if (result.success) {
      // 登录成功，跳转到首页
      router.push('/')
    } else {
      errorMessage.value = result.error || '登录失败，请重试'
    }
  } catch (error: any) {
    errorMessage.value = error.message || '登录过程中发生错误，请重试'
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

.form-control:focus {
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
</style>
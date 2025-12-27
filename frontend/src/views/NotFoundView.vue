<template>
  <div class="not-found-page min-vh-100 d-flex align-items-center justify-content-center bg-light">
    <div class="container text-center">
      <div class="row justify-content-center">
        <div class="col-lg-6">
          <!-- 404图标 -->
          <div class="mb-4">
            <i class="bi bi-emoji-dizzy text-muted" style="font-size: 6rem;"></i>
          </div>
          
          <!-- 错误代码 -->
          <h1 class="display-1 fw-bold text-muted mb-3">404</h1>
          
          <!-- 错误信息 -->
          <h2 class="h3 mb-3">页面未找到</h2>
          <p class="text-muted mb-4">
            抱歉，您访问的页面不存在或已被移除。<br>
            请检查网址是否正确，或返回首页继续浏览。
          </p>
          
          <!-- 操作按钮 -->
          <div class="d-flex gap-3 justify-content-center flex-wrap">
            <router-link to="/" class="btn btn-primary btn-lg">
              <i class="bi bi-house-door me-2"></i>返回首页
            </router-link>
            <button class="btn btn-outline-secondary btn-lg" @click="goBack">
              <i class="bi bi-arrow-left me-2"></i>返回上页
            </button>
          </div>
          
          <!-- 快速链接 -->
          <div class="mt-5 pt-5 border-top">
            <h5 class="text-muted mb-3">您可能在寻找：</h5>
            <div class="row g-3">
              <div class="col-md-3 col-6">
                <router-link to="/diet" class="text-decoration-none quick-link">
                  <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body text-center">
                      <i class="bi bi-egg-fried text-warning fs-3 mb-2"></i>
                      <p class="mb-0 small">饮食记录</p>
                    </div>
                  </div>
                </router-link>
              </div>
              <div class="col-md-3 col-6">
                <router-link to="/exercise" class="text-decoration-none quick-link">
                  <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body text-center">
                      <i class="bi bi-activity text-info fs-3 mb-2"></i>
                      <p class="mb-0 small">运动库</p>
                    </div>
                  </div>
                </router-link>
              </div>
              <div class="col-md-3 col-6">
                <router-link to="/ai-plan" class="text-decoration-none quick-link">
                  <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body text-center">
                      <i class="bi bi-robot text-primary fs-3 mb-2"></i>
                      <p class="mb-0 small">AI健身方案</p>
                    </div>
                  </div>
                </router-link>
              </div>
              <div class="col-md-3 col-6">
                <router-link to="/profile" class="text-decoration-none quick-link">
                  <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body text-center">
                      <i class="bi bi-person-gear text-success fs-3 mb-2"></i>
                      <p class="mb-0 small">个人中心</p>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

// 返回上一页
const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
.not-found-page {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.quick-link {
  transition: transform 0.2s ease-in-out;
}

.quick-link:hover {
  transform: translateY(-5px);
}

.quick-link .card {
  transition: all 0.2s ease-in-out;
  border-radius: 12px;
}

.quick-link:hover .card {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
}

.btn {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease-in-out;
}

.btn:hover {
  transform: translateY(-2px);
}

/* 动画效果 */
@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

.display-1 {
  animation: bounce 2s infinite;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .display-1 {
    font-size: 4rem;
  }
  
  .h3 {
    font-size: 1.5rem;
  }
  
  .btn-lg {
    padding: 12px 24px;
    font-size: 1rem;
  }
}
</style>
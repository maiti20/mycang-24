<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary sticky-top">
    <div class="container">
      <!-- 品牌 -->
      <router-link class="navbar-brand d-flex align-items-center" to="/">
        <i class="bi bi-heart-pulse-fill me-2"></i>
        <span class="fw-bold">健身打卡系统</span>
      </router-link>

      <!-- 移动端切换按钮 -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- 导航内容 -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <!-- 左侧导航 -->
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/" :class="{ active: $route.name === 'Home' }">
              <i class="bi bi-house-door me-1"></i>首页
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/diet" :class="{ active: $route.path.startsWith('/diet') }">
              <i class="bi bi-egg-fried me-1"></i>饮食记录
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/exercise" :class="{ active: $route.path.startsWith('/exercise') }">
              <i class="bi bi-activity me-1"></i>运动库
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/ai-plan" :class="{ active: $route.path.startsWith('/ai-plan') }">
              <i class="bi bi-robot me-1"></i>AI健身方案
            </router-link>
          </li>
        </ul>

        <!-- 右侧用户菜单 -->
        <ul class="navbar-nav">
          <li class="nav-item dropdown" v-if="isAuthenticated">
            <!-- 用户头像和名称 -->
            <a
              class="nav-link dropdown-toggle d-flex align-items-center"
              href="#"
              id="navbarDropdown"
              role="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <div class="user-avatar me-2">
                <img v-if="user?.avatar" :src="getAvatarUrl(user.avatar)" alt="头像" class="avatar-img">
                <i v-else class="bi bi-person-circle"></i>
              </div>
              <span>{{ user?.username }}</span>
            </a>

            <!-- 下拉菜单 -->
            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
              <li>
                <router-link class="dropdown-item" to="/profile">
                  <i class="bi bi-person-gear me-2"></i>个人中心
                </router-link>
              </li>
              <li><hr class="dropdown-divider"></li>
              <li>
                <a class="dropdown-item" href="#" @click.prevent="handleLogout">
                  <i class="bi bi-box-arrow-right me-2"></i>退出登录
                </a>
              </li>
            </ul>
          </li>

          <!-- 未登录状态 -->
          <li class="nav-item" v-else>
            <router-link class="nav-link" to="/login">
              <i class="bi bi-box-arrow-in-right me-1"></i>登录
            </router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 计算属性
const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)

// 获取头像URL (使用代理)
const getAvatarUrl = (avatar: string) => {
  if (!avatar) return ''
  if (avatar.startsWith('http')) return avatar
  return avatar  // 使用代理，直接返回路径
}

// 处理登出
const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
    // 即使登出失败也清除本地状态并跳转
    authStore.clearTokens()
    router.push('/login')
  }
}
</script>

<style scoped>
.navbar-brand {
  font-size: 1.25rem;
  font-weight: 700;
  transition: transform 0.2s ease-in-out;
}

.navbar-brand:hover {
  transform: scale(1.05);
}

.nav-link {
  font-weight: 500;
  transition: all 0.2s ease-in-out;
  border-radius: 6px;
  margin: 0 2px;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.nav-link.active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  overflow: hidden;
}

.user-avatar .avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.dropdown-menu {
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border-radius: 12px;
  padding: 8px;
  margin-top: 8px;
}

.dropdown-item {
  border-radius: 8px;
  padding: 10px 16px;
  transition: all 0.2s ease-in-out;
  font-weight: 500;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
  transform: translateX(4px);
}

.dropdown-divider {
  margin: 8px 0;
  border-color: #e9ecef;
}

/* 响应式调整 */
@media (max-width: 992px) {
  .navbar-nav {
    padding-top: 1rem;
  }
  
  .nav-item {
    margin-bottom: 0.5rem;
  }
  
  .dropdown-menu {
    position: static !important;
    transform: none !important;
    border: none;
    box-shadow: none;
    background-color: transparent;
    padding: 0;
  }
  
  .dropdown-item {
    color: rgba(255, 255, 255, 0.8) !important;
    padding: 8px 16px;
  }
  
  .dropdown-item:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: white !important;
  }
  
  .dropdown-divider {
    border-color: rgba(255, 255, 255, 0.1);
  }
}

/* 动画效果 */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-menu.show {
  animation: slideDown 0.2s ease-out;
}

/* 心跳动画 */
.bi-heart-pulse-fill {
  animation: heartbeat 1.5s ease-in-out infinite;
}

@keyframes heartbeat {
  0% { transform: scale(1); }
  14% { transform: scale(1.1); }
  28% { transform: scale(1); }
  42% { transform: scale(1.1); }
  70% { transform: scale(1); }
}
</style>
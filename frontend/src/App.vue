<template>
  <div id="app">
    <!-- 导航栏 -->
    <AppNavbar v-if="showNavbar" />
    
    <!-- 主要内容区域 -->
    <main :class="{ 'container-fluid': !showContainerPadding, 'container mt-4': showContainerPadding }">
      <router-view />
    </main>
    
    <!-- 页脚 -->
    <AppFooter v-if="showFooter" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppNavbar from '@/components/AppNavbar.vue'
import AppFooter from '@/components/AppFooter.vue'

const route = useRoute()
const authStore = useAuthStore()

// 控制导航栏显示（登录和注册页面不显示）
const showNavbar = computed(() => {
  return !route.meta?.guest
})

// 控制页脚显示（登录和注册页面不显示）
const showFooter = computed(() => {
  return !route.meta?.guest
})

// 控制主容器的padding
const showContainerPadding = computed(() => {
  return !route.meta?.guest
})

// 应用初始化
onMounted(async () => {
  // 初始化认证状态
  await authStore.initializeAuth()
})
</script>

<style>
/* 全局样式 */
html, body {
  height: auto;
  min-height: 100vh;
  overflow-x: hidden;
  overflow-y: auto;
}

#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #333;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1 0 auto;
}

footer {
  flex-shrink: 0;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}

/* Bootstrap自定义 */
.btn {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease-in-out;
}

.card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.2s ease-in-out;
}

.card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.form-control,
.form-select {
  border-radius: 8px;
  border: 1px solid #dee2e6;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-control:focus,
.form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.navbar {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 响应式优化 */
@media (max-width: 768px) {
  .container {
    padding-left: 15px;
    padding-right: 15px;
  }
}
</style>
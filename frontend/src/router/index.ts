import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 导入页面组件
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import DietRecordView from '@/views/DietRecordView.vue'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { guest: true }
  },
  // 饮食记录相关路由
  {
    path: '/diet',
    name: 'Diet',
    component: DietRecordView,
    meta: { requiresAuth: true }
  },
  {
    path: '/diet/record',
    name: 'DietRecord',
    component: DietRecordView,
    meta: { requiresAuth: true }
  },
  // 运动库相关路由
  {
    path: '/exercise',
    name: 'Exercise',
    component: () => import('@/views/ExerciseLibraryView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/exercise/log',
    name: 'ExerciseLog',
    component: () => import('@/views/ExerciseLogView.vue'),
    meta: { requiresAuth: true }
  },
  // AI健身方案相关路由
  {
    path: '/ai-plan',
    name: 'AIPlan',
    component: () => import('@/views/AIPlanView.vue'),
    meta: { requiresAuth: true }
  },
  // 个人中心路由
	  {
	    path: '/profile',
	    name: 'Profile',
	    component: () => import('@/views/ProfileView.vue'),
	    meta: { requiresAuth: true }
	  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue')
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  
  // 如果用户已经登录但没有用户信息，尝试初始化
  if (authStore.accessToken && !authStore.user) {
    try {
      await authStore.initializeAuth()
    } catch (error) {
      console.warn('Failed to initialize auth:', error)
    }
  }

  // 检查路由是否需要认证
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // 未登录，重定向到登录页
      next({
        name: 'Login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }

  // 检查路由是否是访客页面（已登录用户不应访问）
  if (to.meta.guest && authStore.isAuthenticated) {
    // 已登录用户访问登录/注册页，重定向到首页
    next({ name: 'Home' })
    return
  }

  next()
})

export default router
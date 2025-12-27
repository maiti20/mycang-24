<template>
  <footer class="bg-dark text-light py-5 mt-auto">
    <div class="container">
      <div class="row">
        <!-- 公司信息 -->
        <div class="col-lg-4 mb-4 mb-lg-0">
          <div class="d-flex align-items-center mb-3">
            <i class="bi bi-heart-pulse-fill text-primary me-2" style="font-size: 1.5rem;"></i>
            <h5 class="mb-0 fw-bold">健身打卡系统</h5>
          </div>
          <p class="text-muted">
            您的专属健康管理助手，通过科学的饮食记录、运动追踪和AI智能推荐，
            帮助您达成健身目标，享受健康生活。
          </p>
          <div class="d-flex gap-3">
            <a href="#" class="text-light social-icon">
              <i class="bi bi-facebook fs-5"></i>
            </a>
            <a href="#" class="text-light social-icon">
              <i class="bi bi-twitter fs-5"></i>
            </a>
            <a href="#" class="text-light social-icon">
              <i class="bi bi-instagram fs-5"></i>
            </a>
            <a href="#" class="text-light social-icon">
              <i class="bi bi-youtube fs-5"></i>
            </a>
          </div>
        </div>

        <!-- 快速链接 -->
        <div class="col-lg-2 col-md-6 mb-4 mb-lg-0">
          <h6 class="text-uppercase mb-3 fw-semibold">快速链接</h6>
          <ul class="list-unstyled">
            <li class="mb-2">
              <router-link to="/" class="text-muted text-decoration-none footer-link">
                首页
              </router-link>
            </li>
            <li class="mb-2">
              <router-link to="/diet" class="text-muted text-decoration-none footer-link">
                饮食记录
              </router-link>
            </li>
            <li class="mb-2">
              <router-link to="/exercise" class="text-muted text-decoration-none footer-link">
                运动库
              </router-link>
            </li>
            <li class="mb-2">
              <router-link to="/ai-plan" class="text-muted text-decoration-none footer-link">
                AI健身方案
              </router-link>
            </li>
          </ul>
        </div>

        <!-- 支持帮助 -->
        <div class="col-lg-2 col-md-6 mb-4 mb-lg-0">
          <h6 class="text-uppercase mb-3 fw-semibold">支持帮助</h6>
          <ul class="list-unstyled">
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none footer-link">使用指南</a>
            </li>
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none footer-link">常见问题</a>
            </li>
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none footer-link">联系客服</a>
            </li>
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none footer-link">意见反馈</a>
            </li>
          </ul>
        </div>

        <!-- 关于我们 -->
        <div class="col-lg-2 col-md-6 mb-4 mb-lg-0">
          <h6 class="text-uppercase mb-3 fw-semibold">关于我们</h6>
          <ul class="list-unstyled">
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none footer-link">公司介绍</a>
            </li>
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none footer-link">团队成员</a>
            </li>
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none footer-link">发展历程</a>
            </li>
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none footer-link">加入我们</a>
            </li>
          </ul>
        </div>

        <!-- 法律信息 -->
        <div class="col-lg-2 col-md-6 mb-4 mb-lg-0">
          <h6 class="text-uppercase mb-3 fw-semibold">法律信息</h6>
          <ul class="list-unstyled">
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none footer-link">服务条款</a>
            </li>
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none footer-link">隐私政策</a>
            </li>
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none footer-link">Cookie政策</a>
            </li>
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none footer-link">免责声明</a>
            </li>
          </ul>
        </div>
      </div>

      <!-- 分割线 -->
      <hr class="border-secondary my-4">

      <!-- 版权信息 -->
      <div class="row align-items-center">
        <div class="col-md-6">
          <p class="mb-0 text-muted">
            © {{ currentYear }} 健身打卡系统. All rights reserved.
          </p>
        </div>
        <div class="col-md-6 text-md-end">
          <p class="mb-0 text-muted">
            Made with <i class="bi bi-heart-fill text-danger"></i> by Fitness Team
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// 当前年份
const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.footer-link {
  transition: all 0.2s ease-in-out;
  display: inline-block;
  color: rgba(255, 255, 255, 0.75) !important;
}

.footer-link:hover {
  color: #fff !important;
  transform: translateX(4px);
}

/* 让描述文字更明显 */
.text-muted {
  color: rgba(255, 255, 255, 0.6) !important;
}

.social-icon {
  transition: all 0.2s ease-in-out;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.1);
}

.social-icon:hover {
  background-color: #667eea;
  transform: translateY(-3px);
  color: #fff !important;
}

h6 {
  letter-spacing: 0.5px;
}

/* 心跳动画 */
.bi-heart-fill {
  animation: heartbeat 1.5s ease-in-out infinite;
}

@keyframes heartbeat {
  0% { transform: scale(1); }
  14% { transform: scale(1.1); }
  28% { transform: scale(1); }
  42% { transform: scale(1.1); }
  70% { transform: scale(1); }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .text-md-end {
    text-align: center !important;
  }
  
  .social-icon {
    width: 35px;
    height: 35px;
  }
  
  h5 {
    font-size: 1.1rem;
  }
  
  h6 {
    font-size: 0.9rem;
  }
}

/* 滚动显示动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

footer {
  opacity: 1;
  visibility: visible;
}
</style>
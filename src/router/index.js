/**
 * WaveTune 前端路由配置
 * 基于 Vue Router 4 实现的单页应用路由管理
 */

import { createRouter, createWebHashHistory } from 'vue-router'

// 路由配置
const routes = [
  // 首页
  {
    path: '/',
    name: 'home',
    component: () => import(/* webpackChunkName: "home" */ '../views/HomeView.vue'),
    meta: { requiresAuth: true } // 需要登录才能访问
  },
  // 登录页
  {
    path: '/login',
    name: 'login',
    component: () => import(/* webpackChunkName: "auth" */ '../views/LoginView.vue'),
    meta: { requiresGuest: true } // 仅游客可访问
  },
  // 注册页
  {
    path: '/register',
    name: 'register',
    component: () => import(/* webpackChunkName: "auth" */ '../views/RegisterView.vue'),
    meta: { requiresGuest: true } // 仅游客可访问
  },
  // 快速检测选择页
  {
    path: '/quick-detection',
    name: 'quick-detection',
    component: () => import(/* webpackChunkName: "fatigue" */ '../views/QuickDetectionChoiceView.vue')
  },
  // 2-back 实验页
  {
    path: '/quick-detection/two-back',
    name: 'two-back-experiment',
    component: () => import(/* webpackChunkName: "fatigue" */ '../views/TwoBackExperimentView.vue')
  },
  // 音乐推荐页
  {
    path: '/music-recommendation',
    name: 'music-recommendation',
    component: () => import(/* webpackChunkName: "music" */ '../views/MusicRecommendationView.vue')
  },
  // 信号监测页
  {
    path: '/signal-monitor',
    name: 'signal-monitor',
    component: () => import(/* webpackChunkName: "signal" */ '../views/SignalMonitorView.vue')
  },
  // 用户反馈页
  {
    path: '/user',
    name: 'user',
    component: () => import(/* webpackChunkName: "user" */ '../views/UserFeedbackView.vue'),
    meta: { requiresAuth: true } // 需要登录才能访问
  },
  // 用户中心页
  {
    path: '/user-center',
    name: 'user-center',
    component: () => import(/* webpackChunkName: "user" */ '../views/UserCenterView.vue'),
    meta: { requiresAuth: true } // 需要登录才能访问
  },
  // 联邦学习贡献页
  {
    path: '/federated',
    redirect: '/federated/contribute' // 重定向到贡献页
  },
  {
    path: '/federated/contribute',
    name: 'federated-contribute',
    component: () => import(/* webpackChunkName: "federated" */ '../views/FederatedContributeView.vue')
  },
  // 关于页
  {
    path: '/about',
    name: 'about',
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  // 管理员界面路由
  {
    path: '/admin',
    component: () => import(/* webpackChunkName: "admin" */ '../views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true }, // 需要登录才能访问
    children: [
      // 管理员首页重定向
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      // 管理员仪表盘
      {
        path: 'dashboard',
        name: 'admin-dashboard',
        component: () => import(/* webpackChunkName: "admin" */ '../views/admin/DashboardView.vue')
      },
      // 音乐管理
      {
        path: 'music',
        name: 'admin-music',
        component: () => import(/* webpackChunkName: "admin" */ '../views/admin/MusicManagementView.vue')
      },
      // 用户管理
      {
        path: 'users',
        name: 'admin-users',
        component: () => import(/* webpackChunkName: "admin" */ '../views/admin/UserManagementView.vue')
      },
      // 反馈管理
      {
        path: 'feedback',
        name: 'admin-feedback',
        component: () => import(/* webpackChunkName: "admin" */ '../views/admin/FeedbackManagementView.vue')
      },
      // 系统配置
      {
        path: 'config',
        name: 'admin-config',
        component: () => import(/* webpackChunkName: "admin" */ '../views/admin/SystemConfigView.vue')
      },
      // 联邦学习管理
      {
        path: 'federated',
        name: 'admin-federated',
        component: () => import(/* webpackChunkName: "admin" */ '../views/admin/FederatedManagementView.vue')
      }
    ]
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHashHistory(), // 使用哈希模式
  routes // 路由配置
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 获取用户令牌
  const token = localStorage.getItem('session_token')
  // 检查是否已认证
  const isAuthenticated = !!token
  
  // 处理需要认证的路由
  if (to.meta.requiresAuth && !isAuthenticated) {
    // 未登录用户重定向到登录页
    next('/login')
    return
  }
  
  // 处理需要游客状态的路由
  if (to.meta.requiresGuest && isAuthenticated) {
    // 已登录用户重定向到首页
    next('/')
    return
  }
  
  // 管理员权限检查
  if (to.path.startsWith('/admin/') || to.path.startsWith('/analytics/')) {
    try {
      // 从本地存储获取用户信息
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      // 检查用户角色是否为管理员
      if (user.role !== 'admin') {
        // 非管理员重定向到用户中心
        next('/user-center')
        return
      }
    } catch (error) {
      // 解析失败，重定向到用户中心
      next('/user-center')
      return
    }
  }
  
  // 允许路由导航
  next()
})

// 导出路由实例
export default router

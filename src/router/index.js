import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import(/* webpackChunkName: "home" */ '../views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import(/* webpackChunkName: "auth" */ '../views/LoginView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import(/* webpackChunkName: "auth" */ '../views/RegisterView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/quick-detection',
    name: 'quick-detection',
    component: () => import(/* webpackChunkName: "fatigue" */ '../views/QuickDetectionChoiceView.vue')
  },
  {
    path: '/quick-detection/direct',
    name: 'direct-detection',
    component: () => import(/* webpackChunkName: "fatigue" */ '../views/FatigueResultView.vue')
  },
  {
    path: '/quick-detection/two-back',
    name: 'two-back-experiment',
    component: () => import(/* webpackChunkName: "fatigue" */ '../views/TwoBackExperimentView.vue')
  },
  {
    path: '/music-recommendation',
    name: 'music-recommendation',
    component: () => import(/* webpackChunkName: "music" */ '../views/MusicRecommendationView.vue')
  },
  {
    path: '/signal-monitor',
    name: 'signal-monitor',
    component: () => import(/* webpackChunkName: "signal" */ '../views/SignalMonitorView.vue')
  },
  {
    path: '/user',
    name: 'user',
    component: () => import(/* webpackChunkName: "user" */ '../views/UserFeedbackView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user-center',
    name: 'user-center',
    component: () => import(/* webpackChunkName: "user" */ '../views/UserCenterView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/federated',
    redirect: '/federated/status'
  },
  {
    path: '/federated/status',
    name: 'federated-status',
    component: () => import(/* webpackChunkName: "federated" */ '../views/federated/FederatedStatusView.vue')
  },
  {
    path: '/federated/progress',
    name: 'federated-progress',
    component: () => import(/* webpackChunkName: "federated" */ '../views/federated/FederatedProgressView.vue')
  },
  {
    path: '/federated/devices',
    name: 'federated-devices',
    component: () => import(/* webpackChunkName: "federated" */ '../views/federated/FederatedDevicesView.vue')
  },
  {
    path: '/about',
    name: 'about',
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  // 管理员界面路由
  {
    path: '/admin',
    component: () => import(/* webpackChunkName: "admin" */ '../views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'admin-dashboard',
        component: () => import(/* webpackChunkName: "admin" */ '../views/admin/DashboardView.vue')
      },
      {
        path: 'music',
        name: 'admin-music',
        component: () => import(/* webpackChunkName: "admin" */ '../views/admin/MusicManagementView.vue')
      },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import(/* webpackChunkName: "admin" */ '../views/admin/UserManagementView.vue')
      },
      {
        path: 'feedback',
        name: 'admin-feedback',
        component: () => import(/* webpackChunkName: "admin" */ '../views/admin/FeedbackManagementView.vue')
      },
      {
        path: 'config',
        name: 'admin-config',
        component: () => import(/* webpackChunkName: "admin" */ '../views/admin/SystemConfigView.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('session_token')
  const isAuthenticated = !!token
  
  // 需要认证的路由
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }
  
  // 需要游客状态的路由（已登录用户不能访问）
  if (to.meta.requiresGuest && isAuthenticated) {
    next('/')
    return
  }
  
  // 管理员权限检查
  if (to.path.startsWith('/admin/') || to.path.startsWith('/analytics/')) {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      if (user.role !== 'admin') {
        next('/user-center')
        return
      }
    } catch (error) {
      next('/user-center')
      return
    }
  }
  
  next()
})

export default router

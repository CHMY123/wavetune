/**
 * WaveTune 前端应用入口文件
 * 基于 Vue 3 + Element Plus + Pinia 构建的脑疲劳检测与音乐干预系统
 */

// 导入核心依赖
import { createApp } from 'vue'
import { createPinia } from 'pinia' // 状态管理
import ElementPlus from 'element-plus' // UI组件库
import 'element-plus/dist/index.css' // Element Plus 样式
import * as ElementPlusIconsVue from '@element-plus/icons-vue' // Element Plus 图标
import App from './App.vue' // 根组件
import router from './router' // 路由配置
import axios from 'axios' // HTTP 客户端
import { setupErrorHandler } from './utils/errorHandler.js' // 全局错误处理
import './assets/styles/_variables.scss' // 全局变量
import './assets/styles/_design_tokens.scss' // 设计令牌

// 设置全局错误处理
setupErrorHandler()

// 创建 Vue 应用实例
const app = createApp(App)
// 创建 Pinia 实例
const pinia = createPinia()

// 注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册插件
app.use(pinia) // 使用状态管理
app.use(ElementPlus) // 使用 UI 组件库
app.use(router) // 使用路由

// 创建 axios 实例
const axiosInstance = axios.create({
  baseURL: '', // 基础 URL，根据环境自动配置
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json' // 默认 Content-Type
  }
})

// 挂载 axios 到 Vue 原型，便于组件中使用
app.config.globalProperties.$axios = axiosInstance

// Vue 应用级别的错误处理
app.config.errorHandler = (err, vm, info) => {
  // 忽略 ResizeObserver 错误（常见的浏览器兼容性问题）
  if (err.message && err.message.includes('ResizeObserver loop completed with undelivered notifications')) {
    return false
  }
  // 记录其他错误
  console.error('Vue Error:', err, info)
}

// 挂载应用到 DOM
app.mount('#app')

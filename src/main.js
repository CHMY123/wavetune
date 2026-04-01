import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { setupErrorHandler } from './utils/errorHandler.js'
import './assets/styles/_variables.scss'
import './assets/styles/_design_tokens.scss'

// 设置错误处理
setupErrorHandler()

const app = createApp(App)
const pinia = createPinia()

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(ElementPlus)
app.use(router)

// 创建 axios 实例
const axiosInstance = axios.create({
  baseURL: '',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 挂载 axios 到 Vue 原型
app.config.globalProperties.$axios = axiosInstance

// Vue 应用级别的错误处理
app.config.errorHandler = (err, vm, info) => {
  if (err.message && err.message.includes('ResizeObserver loop completed with undelivered notifications')) {
    return false // 忽略 ResizeObserver 错误
  }
  console.error('Vue Error:', err, info)
}

app.mount('#app')

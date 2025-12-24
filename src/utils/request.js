import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import Cookies from 'js-cookie'

// 1. 创建Axios实例
// 兼容 Vite 和 Vue-CLI（webpack）两种环境变量写法：
// - Vite 使用 import.meta.env.VITE_API_BASE_URL
// - Vue CLI 使用 process.env.VUE_APP_API_BASE_URL
let baseURL = '/api'
try {
  // 在支持 import.meta.env 的环境（例如 Vite）中使用
  if (import.meta && import.meta.env && import.meta.env.VITE_API_BASE_URL) {
    baseURL = import.meta.env.VITE_API_BASE_URL
  }
} catch (e) {
  // ignore
}
// Vue CLI / webpack 环境变量回退
if (!baseURL || baseURL === '/api') {
  baseURL = process.env.VUE_APP_API_BASE_URL || process.env.VITE_API_BASE_URL || baseURL
  // 如果是本地开发环境且未配置代理或显式 BASE URL，则回退到后端默认地址，避免请求落到前端静态服务（产生 404）
  try {
    if (process && process.env && process.env.NODE_ENV !== 'production' && (baseURL === '/api' || !baseURL)) {
      baseURL = 'http://127.0.0.1:8000/api'
      // eslint-disable-next-line no-console
      console.warn('[request] no API base configured, defaulting to', baseURL)
    }
  } catch (e) {
    // ignore in browser contexts where process may be undefined
  }
}

const request = axios.create({
  baseURL, // 从环境变量获取基础URL
  timeout: 10000,  // 超时时间（10秒）
  headers: {
    'Content-Type': 'application/json;charset=utf-8'  // 默认请求头
  }
})

// 2. 请求拦截器：添加令牌、处理请求前逻辑
request.interceptors.request.use(
  (config) => {
    // 从 cookie 或 localStorage 获取令牌（登录后存储）
    // 一些旧代码将 token 存到 localStorage，所以这里同时兼容两种情况
    const token = Cookies.get('session_token') || window.localStorage.getItem('session_token')
    if (token) {
      // 添加令牌到请求头（后端通过Authorization获取）
      config.headers.Authorization = `Bearer ${token}`
    }
    // 如果请求体是 FormData，删除默认 Content-Type，让浏览器/axios 自动设置 boundary
    if (config.data && typeof FormData !== 'undefined' && config.data instanceof FormData) {
      try {
        delete config.headers['Content-Type']
      } catch (e) {}
    }
    return config
  },
  (error) => {
    // 请求错误（如网络中断）
    ElMessage.error('请求发送失败，请检查网络')
    return Promise.reject(error)
  }
)

// 3. 响应拦截器：统一处理响应、错误码
request.interceptors.response.use(
  (response) => {
    const res = response.data  // 后端返回的JSON数据

    // 3.1 处理成功响应（根据后端约定的code判断）
    if (res.code === 200) {
      return res  // 直接返回数据，组件中可直接使用res.data
    }

    // 3.2 处理业务错误（后端返回非200状态码）
    ElMessage.error(res.msg || '操作失败')
    return Promise.reject(new Error(res.msg || 'Error'))
  },
  (error) => {
    // 4. 处理HTTP错误（如401、500等）
    const status = error.response?.status

    switch (status) {
      case 401:
        Cookies.remove('session_token')
        ElMessageBox.alert('登录状态已失效，请重新登录', '提示', {
            confirmButtonText: '确定',
            // 改为async回调，动态导入router
            callback: async () => {
            // 动态导入路由模块，打破循环依赖
            const { default: router } = await import('@/router')
            router.push('/login')  // 动态获取router后再使用
            }
        })
        break
      case 403:
        ElMessage.error('没有权限执行此操作')
        break
      case 404:
        ElMessage.error('请求的接口不存在')
        break
      case 500:
        ElMessage.error('服务器内部错误，请稍后重试')
        break
      default:
        ElMessage.error(`请求失败（${status || '未知错误'}）`)
    }

    return Promise.reject(error)
  }
)

// 4. 封装常用请求方法（可选，简化组件调用）
export const requestMethod = {
  // GET请求
  get: (url, params = {}) => {
    return request({
      url,
      method: 'get',
      params
    })
  },

  // POST请求（JSON格式）
  post: (url, data = {}, params = {}) => {
    return request({
      url,
      method: 'post',
      data,
      params
    })
  },

  // PUT请求
  put: (url, data = {}, params = {}) => {
    return request({
      url,
      method: 'put',
      data,
      params
    })
  },

  // DELETE请求
  delete: (url, params = {}) => {
    return request({
      url,
      method: 'delete',
      params
    })
  },

  // 表单提交（如文件上传）
  postForm: (url, data = {}, params = {}) => {
    return request({
      url,
      method: 'post',
      data,
      params,
      // 不手动设置 Content-Type，让浏览器/axios 为 FormData 自动添加 boundary
    })
  }
}

export default request
/**
 * WaveTune 前端请求工具
 * 基于 Axios 封装的 HTTP 请求客户端，处理认证、错误处理等通用逻辑
 */

import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import Cookies from 'js-cookie'

// 1. 创建 Axios 实例
// 彻底兼容 Vue CLI（webpack），消除 process is not defined 报错
let baseURL = '/api'

// 核心修复：所有 process 访问都包裹在 try/catch + window 兜底
try {
  // 优先读取 Vue CLI 注入的 process.env（通过 window 访问，避免裸引用）
  const env = window.process?.env || {};
  // 读取 VUE_APP_API_BASE_URL（你的环境变量）
  if (env.VUE_APP_API_BASE_URL) {
    baseURL = env.VUE_APP_API_BASE_URL;
  }
  // 本地开发环境兜底（避免未配置时请求404）
  else if (env.NODE_ENV === 'development' && baseURL === '/api') {
    // 检查是否通过内网穿透访问
    const currentHost = window.location.host;
    const isCpolar = currentHost.includes('cpolar.top');
    
    if (isCpolar) {
      // 通过内网穿透访问时，直接指向本地后端服务
      baseURL = 'http://localhost:8000/api';
      console.warn('[request] 内网穿透模式，API地址：', baseURL);
    } else {
      // 本地直接访问时，使用代理地址
      baseURL = '/api';
      console.warn('[request] 本地开发模式，默认API地址：', baseURL);
    }
  }
} catch (e) {
  // 浏览器环境无 process 时，直接用代理地址 /api（依赖 vue.config.js 代理）
  baseURL = '/api';
  console.warn('[request] 环境变量读取失败，使用代理地址：', baseURL);
}

// 创建 Axios 实例
const request = axios.create({
  baseURL, // 从环境变量/兜底获取基础URL
  timeout: 150000, // 请求超时时间（150秒）
  headers: {
    'Content-Type': 'application/json;charset=utf-8' // 默认 Content-Type
  }
})

// 2. 请求拦截器：添加令牌、处理请求前逻辑
request.interceptors.request.use(
  (config) => {
    // 从 cookie 或 localStorage 获取令牌（登录后存储）
    // 兼容两种存储方式，确保令牌获取的可靠性
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
    const res = response.data;

    // 兼容两种响应格式：
    // 1. 标准格式：{ code: 200, data, msg }
    // 2. AI直出格式：{ response, recommended_music }

    // 如果是标准格式，正常校验
    if (res.code !== undefined) {
      if (res.code === 200) {
        return res;
      }
      ElMessage.error(res.msg || '操作失败');
      return Promise.reject(new Error(res.msg || 'Error'));
    }

    // 如果没有code字段 → 判定为AI直出接口，直接放行
    // 不做校验，不报错，保持健壮性
    return res;
  },
  (error) => {
    const status = error.response?.status;
    const errorData = error.response?.data;
    
    // 优先显示后端返回的详细错误信息
    const errorMessage = errorData?.detail || errorData?.msg || error.message || '操作失败';

    // 处理常见错误状态码
    switch (status) {
      case 401:
        // 未授权，清除令牌并跳转到登录页
        Cookies.remove('session_token');
        ElMessageBox.alert('登录状态已失效，请重新登录', '提示', {
          confirmButtonText: '确定',
          callback: async () => {
            const { default: router } = await import('@/router');
            router.push('/login');
          }
        });
        break;
      case 403:
        // 禁止访问
        ElMessage.error('没有权限执行此操作');
        break;
      case 404:
        // 接口不存在
        ElMessage.error('请求的接口不存在');
        break;
      case 500:
        // 服务器内部错误
        ElMessage.error('服务器内部错误，请稍后重试');
        break;
      default:
        // 其他错误
        ElMessage.error(errorMessage);
    }

    return Promise.reject(error);
  }
);

// 4. 封装常用请求方法（可选，简化组件调用）
export const requestMethod = {
  /**
   * GET 请求
   * @param {string} url - 请求地址
   * @param {object} params - URL 参数
   * @returns {Promise} - 返回 Promise 对象
   */
  get: (url, params = {}) => {
    return request({
      url,
      method: 'get',
      params
    })
  },

  /**
   * POST 请求（JSON 格式）
   * @param {string} url - 请求地址
   * @param {object} data - 请求体数据
   * @param {object} params - URL 参数
   * @returns {Promise} - 返回 Promise 对象
   */
  post: (url, data = {}, params = {}) => {
    return request({
      url,
      method: 'post',
      data,
      params
    })
  },

  /**
   * PUT 请求
   * @param {string} url - 请求地址
   * @param {object} data - 请求体数据
   * @param {object} params - URL 参数
   * @returns {Promise} - 返回 Promise 对象
   */
  put: (url, data = {}, params = {}) => {
    return request({
      url,
      method: 'put',
      data,
      params
    })
  },

  /**
   * DELETE 请求
   * @param {string} url - 请求地址
   * @param {object} params - URL 参数
   * @returns {Promise} - 返回 Promise 对象
   */
  delete: (url, params = {}) => {
    return request({
      url,
      method: 'delete',
      params
    })
  },

  /**
   * 表单提交（如文件上传）
   * @param {string} url - 请求地址
   * @param {FormData} data - FormData 对象
   * @param {object} params - URL 参数
   * @param {object} config - 额外配置
   * @returns {Promise} - 返回 Promise 对象
   */
  postForm: (url, data = {}, params = {}, config = {}) => {
    return request({
      url,
      method: 'post',
      data,
      params,
      // 不手动设置 Content-Type，让浏览器/axios 为 FormData 自动添加 boundary
      ...config
    })
  }
}

// 导出默认请求实例
export default request
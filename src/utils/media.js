// 媒体 URL 解析工具
// - 如果传入的是完整 URL（以 http 开头），直接返回
// - 如果是相对路径（以 / 开头），尝试根据环境推断后端主机并拼接为绝对 URL
export function resolveMedia(url) {
  if (!url) return url
  try {
    const s = String(url)
    if (s.startsWith('http')) return s
    // 保证以 / 开头
    const path = s.startsWith('/') ? s : `/${s}`

    // 优先使用前端注入的 API 基础地址（VUE_APP_API_BASE_URL）
    try {
      const env = window.process?.env || {}
      let apiBase = env.VUE_APP_API_BASE_URL || null
      if (!apiBase) {
        // 回退到当前站点 origin
        apiBase = window.location.origin
      }
      apiBase = String(apiBase).replace(/\/$/, '')
      // 如果以 /api 结尾，去掉以指向主机根路径
      apiBase = apiBase.replace(/\/api$/, '')
      return apiBase + path
    } catch (e) {
      return path
    }
  } catch (e) {
    return url
  }
}

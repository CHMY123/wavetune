/**
 * WaveTune 前端错误处理工具
 * 提供全局错误处理和安全的 ResizeObserver 包装器
 */

/**
 * 设置全局错误处理器
 * 主要用于处理 ResizeObserver 相关的错误，避免控制台出现大量无用错误信息
 */
export function setupErrorHandler() {
  // 处理全局错误
  const originalError = window.onerror
  window.onerror = function(message, source, lineno, colno, error) {
    // 抑制 ResizeObserver 循环错误
    if (message && message.includes('ResizeObserver loop completed with undelivered notifications')) {
      console.warn('ResizeObserver error suppressed:', message)
      return true // 阻止默认的错误处理
    }
    // 调用原始的错误处理器
    if (originalError) {
      return originalError.apply(this, arguments)
    }
    return false
  }

  // 处理未捕获的 Promise 错误
  const originalUnhandledRejection = window.onunhandledrejection
  window.onunhandledrejection = function(event) {
    // 抑制 ResizeObserver 相关的 Promise 错误
    if (event.reason && event.reason.message && 
        event.reason.message.includes('ResizeObserver loop completed with undelivered notifications')) {
      console.warn('ResizeObserver promise error suppressed:', event.reason.message)
      event.preventDefault()
      return true
    }
    // 调用原始的未处理拒绝处理器
    if (originalUnhandledRejection) {
      return originalUnhandledRejection.apply(this, arguments)
    }
  }

  // 监听全局错误事件
  window.addEventListener('error', (event) => {
    // 抑制 ResizeObserver 错误事件
    if (event.message && event.message.includes('ResizeObserver loop completed with undelivered notifications')) {
      event.preventDefault()
      event.stopPropagation()
      console.warn('ResizeObserver error event suppressed:', event.message)
      return false
    }
  })

  // 监听未处理的 Promise 拒绝事件
  window.addEventListener('unhandledrejection', (event) => {
    // 抑制 ResizeObserver 相关的未处理拒绝
    if (event.reason && event.reason.message && 
        event.reason.message.includes('ResizeObserver loop completed with undelivered notifications')) {
      event.preventDefault()
      console.warn('ResizeObserver unhandled rejection suppressed:', event.reason.message)
      return false
    }
  })
}

/**
 * 创建一个安全的 ResizeObserver 包装器
 * 避免 ResizeObserver 循环错误导致的问题
 * @param {Function} callback - ResizeObserver 回调函数
 * @returns {ResizeObserver|null} - 返回 ResizeObserver 实例或 null（如果不支持）
 */
export function createSafeResizeObserver(callback) {
  try {
    return new ResizeObserver((entries, observer) => {
      // 使用 setTimeout 来延迟回调执行，避免循环问题
      setTimeout(() => {
        try {
          callback(entries, observer)
        } catch (error) {
          // 只记录非 ResizeObserver 循环错误的其他错误
          if (!error.message.includes('ResizeObserver loop completed with undelivered notifications')) {
            console.error('ResizeObserver callback error:', error)
          }
        }
      }, 0)
    })
  } catch (error) {
    console.warn('ResizeObserver not supported:', error)
    return null
  }
}








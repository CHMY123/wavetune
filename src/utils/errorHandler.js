// 错误处理工具
export function setupErrorHandler() {
  // 处理 ResizeObserver 错误
  const originalError = window.onerror
  window.onerror = function(message, source, lineno, colno, error) {
    if (message && message.includes('ResizeObserver loop completed with undelivered notifications')) {
      console.warn('ResizeObserver error suppressed:', message)
      return true // 阻止默认的错误处理
    }
    if (originalError) {
      return originalError.apply(this, arguments)
    }
    return false
  }

  // 处理未捕获的 Promise 错误
  const originalUnhandledRejection = window.onunhandledrejection
  window.onunhandledrejection = function(event) {
    if (event.reason && event.reason.message && 
        event.reason.message.includes('ResizeObserver loop completed with undelivered notifications')) {
      console.warn('ResizeObserver promise error suppressed:', event.reason.message)
      event.preventDefault()
      return true
    }
    if (originalUnhandledRejection) {
      return originalUnhandledRejection.apply(this, arguments)
    }
  }

  // 监听错误事件
  window.addEventListener('error', (event) => {
    if (event.message && event.message.includes('ResizeObserver loop completed with undelivered notifications')) {
      event.preventDefault()
      event.stopPropagation()
      console.warn('ResizeObserver error event suppressed:', event.message)
      return false
    }
  })

  // 监听未处理的 Promise 拒绝
  window.addEventListener('unhandledrejection', (event) => {
    if (event.reason && event.reason.message && 
        event.reason.message.includes('ResizeObserver loop completed with undelivered notifications')) {
      event.preventDefault()
      console.warn('ResizeObserver unhandled rejection suppressed:', event.reason.message)
      return false
    }
  })
}

// 创建一个安全的 ResizeObserver 包装器
export function createSafeResizeObserver(callback) {
  try {
    return new ResizeObserver((entries, observer) => {
      // 使用 setTimeout 来延迟回调执行，避免循环问题
      setTimeout(() => {
        try {
          callback(entries, observer)
        } catch (error) {
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








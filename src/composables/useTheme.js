import { ref, computed, onMounted, onUnmounted } from 'vue'

export function useTheme() {
  const isDarkMode = ref(false)

  // 初始化主题
  const initTheme = () => {
    try {
      const storedTheme = localStorage.getItem('theme')
      if (storedTheme === 'dark') {
        isDarkMode.value = true
        document.documentElement.classList.add('theme-dark')
      } else if (storedTheme === 'light') {
        isDarkMode.value = false
        document.documentElement.classList.remove('theme-dark')
      } else {
        // 如果没有localStorage设置，使用系统颜色方案
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        isDarkMode.value = prefersDark
        if (prefersDark) {
          document.documentElement.classList.add('theme-dark')
        }
      }
    } catch (e) {
      console.error('初始化主题失败:', e)
    }
  }

  // 切换主题
  const toggleTheme = () => {
    try {
      isDarkMode.value = !isDarkMode.value
      if (isDarkMode.value) {
        document.documentElement.classList.add('theme-dark')
        localStorage.setItem('theme', 'dark')
      } else {
        document.documentElement.classList.remove('theme-dark')
        localStorage.setItem('theme', 'light')
      }
      // 触发全局事件方便其他组件响应
      window.dispatchEvent(new Event('theme-changed'))
    } catch (e) {
      console.error('切换主题失败:', e)
    }
  }

  // 监听系统主题变化
  const handleSystemThemeChange = (e) => {
    try {
      const storedTheme = localStorage.getItem('theme')
      // 如果用户没有手动设置主题，跟随系统变化
      if (!storedTheme) {
        isDarkMode.value = e.matches
        if (e.matches) {
          document.documentElement.classList.add('theme-dark')
        } else {
          document.documentElement.classList.remove('theme-dark')
        }
      }
    } catch (e) {
      console.error('监听系统主题变化失败:', e)
    }
  }

  // 监听全局主题变化事件
  const handleThemeChanged = () => {
    initTheme()
  }

  onMounted(() => {
    initTheme()
    // 监听系统主题变化
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', handleSystemThemeChange)
    // 监听全局主题变化事件
    window.addEventListener('theme-changed', handleThemeChanged)
  })

  onUnmounted(() => {
    window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', handleSystemThemeChange)
    window.removeEventListener('theme-changed', handleThemeChanged)
  })

  return {
    isDarkMode,
    toggleTheme,
    initTheme
  }
}

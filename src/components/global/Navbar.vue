<template>
  <el-header class="navbar">
    <!-- 移除波形装饰以提高性能 -->
    
    <div class="navbar-content">
      <!-- 系统名称 -->
      <div class="navbar-brand">
        <!-- SCNU Logo容器 -->
        <div class="brand-logo-container">
          <img src="/static/logo/SCNU.png" alt="SCNU Logo" class="brand-logo-image" />
        </div>
        <div class="brand-text-block">
          <span class="brand-text gradient-text">WaveTune</span>
          <span class="brand-subtitle">脑疲劳检测与音乐干预系统</span>
        </div>
      </div>
      
      <!-- 导航菜单 -->
      <el-menu
        :default-active="activeIndex"
        class="navbar-menu"
        mode="horizontal"
        @select="handleSelect"
        router
        :collapse-transition="false"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        
        <el-menu-item index="/fatigue-result">
          <el-icon><TrendCharts /></el-icon>
          <span>检测结果</span>
        </el-menu-item>
        
        <el-menu-item index="/music-recommendation">
          <el-icon><Headset /></el-icon>
          <span>音乐推荐</span>
        </el-menu-item>
        
        <el-menu-item index="/signal-monitor">
          <el-icon><Monitor /></el-icon>
          <span>信号监测</span>
        </el-menu-item>
        
        <el-sub-menu index="/federated">
          <template #title>
            <el-icon><Connection /></el-icon>
            <span>联邦学习</span>
          </template>
          <el-menu-item index="/federated/status">参与状态</el-menu-item>
          <el-menu-item index="/federated/progress">训练进度</el-menu-item>
          <el-menu-item index="/federated/devices">设备管理</el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="/user">
          <el-icon><User /></el-icon>
          <span>个人中心</span>
        </el-menu-item>
      </el-menu>
      
      <!-- 用户头像入口 -->
      <div class="navbar-user">
        <!-- Theme toggle -->
        <el-button class="theme-toggle" type="text" @click="toggleTheme" title="切换主题">
          <el-icon><SwitchButton /></el-icon>
        </el-button>
        <el-dropdown v-if="isAuthenticated" @command="handleUserCommand">
          <el-avatar :size="36" class="user-avatar" :src="avatarSrc">
            <el-icon><User /></el-icon>
          </el-avatar>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人资料
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                偏好设置
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <div v-else class="auth-buttons">
          <el-button class="auth-btn login-btn" @click="$router.push('/login')">
            登录
          </el-button>
          <el-button class="auth-btn register-btn" @click="$router.push('/register')">
            注册
          </el-button>
        </div>
      </div>
    </div>
  </el-header>
</template>

<script>
import { 
  Monitor, House, TrendCharts, Headset, 
  Connection, User, Setting, SwitchButton 
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { requestMethod } from '@/utils/request'
import { resolveMedia } from '@/utils/media'

export default {
  name: 'Navbar',
  components: {
    Monitor,
    House,
    TrendCharts,
    Headset,
    Connection,
    User,
    Setting,
    SwitchButton
  },
  data() {
    return {
      activeIndex: '/',
      isAuthenticated: false,
      userInfo: {}
    }
  },
  created() {
    // 在组件创建时根据 localStorage 恢复主题（若在 App 启动前没有恢复）
    const theme = localStorage.getItem('theme')
    if (theme === 'dark') document.documentElement.classList.add('theme-dark')
    else document.documentElement.classList.remove('theme-dark')
  },
  mounted() {
    this.checkAuthStatus()
    this.updateActiveIndex()
    // 监听全局登录状态变化
    window.addEventListener('auth-changed', this.checkAuthStatus)
    // 添加滚动事件监听
    window.addEventListener('scroll', this.handleScroll)
    // 初始化滚动状态
    this.handleScroll()
  },
  beforeUnmount() {
    // 移除事件监听
    try { window.removeEventListener('auth-changed', this.checkAuthStatus) } catch (e) {}
    try { window.removeEventListener('scroll', this.handleScroll) } catch (e) {}
  },
  watch: {
    '$route'() {
      this.updateActiveIndex()
    }
  },
  computed: {
    avatarSrc() {
      if (!this.userInfo || !this.userInfo.avatar) return ''
      // 添加时间戳以避免头像缓存问题（上传后立即刷新能生效）
      return `${this.userInfo.avatar}?t=${Date.now()}`
    }
    ,
    logoSrc() {
      try { return resolveMedia('/static/logo/SCNU.png') } catch (e) { return '/static/logo/SCNU.png' }
    }
  },
  methods: {
    checkAuthStatus() {
      const token = localStorage.getItem('session_token')
      const user = localStorage.getItem('user')
      this.isAuthenticated = !!token
      if (user) {
        try {
          const u = JSON.parse(user)
          if (u && u.avatar) u.avatar = resolveMedia(u.avatar)
          this.userInfo = u
        } catch (e) {
          this.userInfo = JSON.parse(user)
        }
      }
    },
    handleScroll() {
      const navbar = document.querySelector('.navbar')
      if (window.scrollY > 50) {
        navbar.classList.add('navbar-scrolled')
      } else {
        navbar.classList.remove('navbar-scrolled')
      }
    },
    updateActiveIndex() {
      this.activeIndex = this.$route.path
    },
    handleSelect(key) {
      this.activeIndex = key
      this.$router.push(key)
    },
    handleUserCommand(command) {
      switch (command) {
        case 'profile':
          this.$router.push('/user-center')
          break
        case 'settings':
          this.$router.push('/user-center')
          break
        case 'logout':
          this.handleLogout()
          break
      }
    },
    toggleTheme() {
      const root = document.documentElement
      const isDark = root.classList.toggle('theme-dark')
      try { localStorage.setItem('theme', isDark ? 'dark' : 'light') } catch (e) {}
      // 触发全局事件方便其他组件响应（可选）
      try { window.dispatchEvent(new Event('theme-changed')) } catch (e) {}
    },
    async handleLogout() {
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '确认退出', {
          type: 'warning',
          confirmButtonText: '确认',
          cancelButtonText: '取消'
        })
        
        const token = localStorage.getItem('session_token')
        if (token) {
          // 调用登出API
        try {
          await requestMethod.post('/auth/logout', { session_token: token })
        } catch (err) {
          console.error('登出接口调用失败:', err)
        }
        }
        
        // 清除本地存储
        localStorage.removeItem('session_token')
        localStorage.removeItem('user')
        
        ElMessage.success('已退出登录')
        this.isAuthenticated = false
        this.userInfo = {}
        
        // 跳转到登录页
        this.$router.push('/login')
      } catch (error) {
        // Element Plus 会在取消时抛出对象，忽略取消
        // 其它错误显示通用提示
        if (error && error !== 'cancel') {
          console.error('退出登录失败:', error)
          ElMessage.error('退出登录失败')
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
// 导入全局变量
@use '@/assets/styles/_design_tokens.scss' as *;

.navbar {
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid var(--border-light);
  box-shadow: var(--shadow-2);
  padding: 0;
  height: 72px;
  line-height: 72px;
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  overflow: hidden;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  z-index: 100;
  
  // 滚动效果
  &.navbar-scrolled {
    box-shadow: var(--shadow-3);
    background: var(--bg-card);
    height: 64px;
    line-height: 64px;
    border-bottom: 1px solid var(--border-color);
    
    .navbar-brand {
      transform: scale(0.95);
    }
    
    .navbar-menu :deep(.el-menu-item),
    .navbar-menu :deep(.el-sub-menu .el-sub-menu__title) {
      height: 64px;
      line-height: 64px;
    }
  }
}

// 波形装饰
.navbar-wave-decoration {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, var(--wave-purple), var(--wave-blue), var(--wave-pink));
  z-index: 1;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 200%;
    height: 100%;
    background: linear-gradient(90deg, transparent, var(--wave-blue), transparent);
    animation: waveFlow 6s linear infinite;
  }
}

@keyframes waveFlow {
  0% { transform: translateX(-50%); }
  100% { transform: translateX(50%); }
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-component);
  height: 100%;
  position: relative;
  z-index: 2;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: transform 0.2s ease;
  
  &:hover {
    transform: scale(1.02);
  }
  
  .brand-logo-container {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    overflow: hidden;
    background: white;
    border: 2px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    
    &:hover {
      transform: scale(1.05);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
    }
    
    .brand-logo-image {
      width: 100%;
      height: 100%;
      object-fit: contain;
      padding: 4px;
    }
  }
  
  .brand-logo-icon {
    font-size: 24px;
    color: white;
  }
  
  .brand-text-block {
    display: flex;
    flex-direction: column;
    line-height: 1;
  }
  
  .brand-text {
    font-size: 22px;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(90deg, var(--wave-purple), var(--wave-blue), var(--wave-pink));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    letter-spacing: -0.5px;
  }
  
  .brand-subtitle {
    font-size: 12px;
    color: var(--text-secondary);
    margin-left: 2px;
    font-weight: 400;
  }
}

// 渐变文本效果
.gradient-text {
  background: linear-gradient(90deg, var(--wave-blue), var(--wave-purple), var(--wave-pink));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  display: inline-block;
}

.navbar-menu {
  border-bottom: none;
  background: transparent;
  flex: 1;
  max-width: 600px;
  margin: 0 24px;
  
  :deep(.el-menu-item) {
    border-bottom: 3px solid transparent;
    padding: 0 20px;
    height: 72px;
    line-height: 72px;
    font-size: 15px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    
    &:hover {
      color: var(--wave-purple);
      background: transparent;
      transform: translateY(-2px);
      
      .el-icon {
        transform: rotate(15deg) scale(1.1);
      }
    }
    
    &.is-active {
      color: var(--wave-purple);
      font-weight: 600;
      transform: translateY(-1px);
      
      &::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 20%;
        width: 60%;
        height: 3px;
        background: linear-gradient(90deg, var(--wave-purple), var(--wave-blue));
        border-radius: 3px;
        animation: pulseLine 2s infinite;
      }
      
      .el-icon {
        color: var(--wave-purple);
      }
    }
    
    .el-icon {
      margin-right: 6px;
      font-size: 16px;
      transition: all 0.3s ease;
    }
  }
  
  @keyframes pulseLine {
    0%, 100% {
      opacity: 1;
      transform: scaleX(1);
    }
    50% {
      opacity: 0.8;
      transform: scaleX(0.95);
    }
  }
  
  :deep(.el-sub-menu) {
    .el-sub-menu__title {
      border-bottom: 3px solid transparent;
      height: 72px;
      line-height: 72px;
      font-size: 15px;
      transition: all 0.3s ease;
      
      &:hover {
        color: var(--wave-purple);
        background: transparent;
      }
      
      .el-icon {
        margin-right: 6px;
        font-size: 16px;
      }
    }
    
    .el-dropdown-menu {
      border-radius: 12px;
      box-shadow: var(--shadow-3);
      padding: 8px 0;
      margin-top: 8px;
      border: none;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      animation: dropdownFadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      
      .el-dropdown-menu__item {
        padding: 12px 24px;
        font-size: 14px;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
        
        &::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(147, 51, 234, 0.1), transparent);
          transition: left 0.5s ease;
        }
        
        &:hover {
          background: var(--bg-hover);
          color: var(--wave-purple);
          transform: translateX(4px);
          
          &::before {
            left: 100%;
          }
          
          .el-icon {
            transform: translateX(2px);
          }
        }
        
        &.is-disabled {
          color: var(--text-disabled);
        }
        
        .el-icon {
          transition: transform 0.2s ease;
        }
      }
    }
    
    @keyframes dropdownFadeIn {
      from {
        opacity: 0;
        transform: translateY(-10px) scale(0.95);
      }
      to {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
    }
  }
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .user-avatar {
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2px solid rgba(0,0,0,0.06);
    background-color: var(--bg-card);
    padding: 2px;

    &:hover {
      transform: scale(1.05);
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
  }
  
  .auth-buttons {
    display: flex;
    gap: 12px;
    align-items: center;
  }
  
  .auth-btn {
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
    padding: 8px 20px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    background-color: transparent;
    color: var(--brand-primary);
    border: 1px solid transparent;
  }
  
  .login-btn {
    background-color: var(--brand-primary);
    border: none;
    color: white;

    &:hover {
      opacity: 0.95;
      transform: translateY(-1px);
      box-shadow: 0 6px 18px rgba(24,144,255,0.18);
    }
  }
  
  .register-btn {
    background: transparent;
    border: 2px solid var(--brand-primary);
    color: var(--brand-primary);

    &:hover {
      background: var(--brand-primary);
      color: white;
      transform: translateY(-1px);
      box-shadow: 0 6px 18px rgba(24,144,255,0.18);
    }
  }

  .theme-toggle {
    color: var(--text-primary);
    margin-right: 6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background: transparent;
    border: 1px solid transparent;
  }
}

// 响应式适配
@media (max-width: 1024px) {
  .navbar-content {
    padding: 0 16px;
  }
  
  .navbar-menu {
    margin: 0 16px;
    
    :deep(.el-menu-item) {
      padding: 0 16px;
      
      .el-icon {
        margin-right: 4px;
      }
    }
  }
}

@media (max-width: 768px) {
  .navbar {
    height: 64px;
    line-height: 64px;
  }
  
  .navbar-content {
    padding: 0 12px;
  }
  
  .navbar-brand {
    gap: 8px;
    
    .brand-logo-container {
      width: 40px;
      height: 40px;
      
      .brand-logo-icon {
        font-size: 20px;
      }
    }
    
    .brand-text {
      font-size: 18px;
    }
    
    .brand-subtitle {
      display: none;
    }
  }
  
  .navbar-menu {
    margin: 0 8px;
    
    :deep(.el-menu-item) {
      padding: 0 12px;
      height: 64px;
      line-height: 64px;
      font-size: 14px;
      
      span {
        display: none;
      }
      
      .el-icon {
        margin-right: 0;
      }
    }
    
    :deep(.el-sub-menu .el-sub-menu__title) {
      height: 64px;
      line-height: 64px;
      font-size: 14px;
      
      span {
        display: none;
      }
      
      .el-icon {
        margin-right: 0;
      }
    }
  }
  
  .navbar-user {
    .auth-btn {
      padding: 6px 16px;
      font-size: 13px;
    }
  }
}

@media (max-width: 480px) {
  .navbar {
    height: 56px;
    line-height: 56px;
  }
  
  .navbar-brand {
    
    .brand-text {
      font-size: 16px;
    }
  }
  
  .navbar-menu {
    :deep(.el-menu-item) {
      padding: 0 8px;
      height: 56px;
      line-height: 56px;
    }
    
    :deep(.el-sub-menu .el-sub-menu__title) {
      height: 56px;
      line-height: 56px;
    }
  }
  
  .navbar-user {
    gap: 8px;
    
    .user-avatar {
      width: 32px !important;
      height: 32px !important;
    }
    
    .auth-buttons {
      gap: 8px;
    }
    
    .auth-btn {
      padding: 4px 12px;
      font-size: 12px;
    }
  }
}
</style>








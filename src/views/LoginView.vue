<template>
  <div class="login-view">
    <!-- 波形背景装饰 -->
    <div class="wave-background">
      <div class="wave wave-1"></div>
      <div class="wave wave-2"></div>
      <div class="wave wave-3"></div>
    </div>
    
    <div class="login-container">
      <!-- 登录表单卡片 -->
      <el-card class="login-card" shadow="always">
        <div class="login-card-inner">
          <!-- 标题栏 -->
          <div class="login-header">
            <div class="logo-section">
              <div class="logo-container">
                <el-icon class="logo-icon"><Monitor /></el-icon>
              </div>
              <h1 class="system-title gradient-text">WaveTune</h1>
            </div>
            <p class="system-subtitle">智能脑疲劳检测与音乐干预系统</p>
          </div>
          
          <!-- 登录表单 -->
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            label-width="0"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <div class="form-input-group">
              <el-form-item prop="student_id" class="form-item-custom">
                <div class="input-container">
                  <el-icon class="input-icon"><User /></el-icon>
                  <el-input
                    v-model="loginForm.student_id"
                    placeholder="请输入学号"
                    size="large"
                    class="custom-input"
                    clearable
                    :prefix-icon="''"
                  />
                </div>
              </el-form-item>
              
              <el-form-item prop="password" class="form-item-custom">
                <div class="input-container">
                  <el-icon class="input-icon"><Lock /></el-icon>
                  <el-input
                    v-model="loginForm.password"
                    type="password"
                    placeholder="请输入密码"
                    size="large"
                    class="custom-input"
                    show-password
                    clearable
                    @keyup.enter="handleLogin"
                    :prefix-icon="''"
                  />
                </div>
              </el-form-item>
            </div>
            
            <el-form-item class="options-row">
              <el-checkbox v-model="loginForm.remember" class="remember-checkbox">
                <span class="checkbox-label">记住我</span>
              </el-checkbox>
              <el-link type="primary" class="forgot-password" @click="showForgotPassword">
                忘记密码？
              </el-link>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="login-button gradient-button"
                :loading="loginLoading"
                @click="handleLogin"
              >
                <span v-if="!loginLoading">登录</span>
                <el-icon v-else class="loading-icon"><Loading /></el-icon>
              </el-button>
              <p class="demo-account-info" v-if="!loginLoading">
                测试账号: <span class="account-text">20232005118</span> / <span class="password-text">123456</span>
              </p>
            </el-form-item>
            
            <el-form-item class="register-link">
              <span class="register-text">还没有账户？</span>
              <el-link type="primary" class="register-button" @click="$router.push('/register')">
                立即注册
              </el-link>
            </el-form-item>
          </el-form>
        </div>
      </el-card>
      
      <!-- 系统特色介绍 -->
      <div class="system-intro">
        <div class="intro-card">
          <h2 class="intro-title">智能脑疲劳检测系统</h2>
          <p class="intro-description">
            WaveTune 利用多模态生理信号监测技术，结合人工智能算法，
            精准检测脑疲劳状态，并提供个性化音乐干预方案，
            帮助您恢复精力，提高学习和工作效率。
          </p>
          
          <div class="feature-list">
            <div class="feature-item" v-for="(feature, index) in features" :key="index">
              <div class="feature-icon-container">
                <component :is="feature.icon" class="feature-icon" />
              </div>
              <div class="feature-content">
                <h4 class="feature-title">{{ feature.title }}</h4>
                <p class="feature-desc">{{ feature.description }}</p>
              </div>
            </div>
          </div>
          
          <!-- 波形装饰 -->
          <div class="wave-accent">
            <svg viewBox="0 0 1440 120" xmlns="http://www.w3.org/2000/svg">
              <path 
                fill="rgba(255,255,255,0.2)" 
                d="M0,96L48,85.3C96,75,192,53,288,53.3C384,53,480,75,576,80C672,85,768,75,864,64C960,53,1056,43,1152,48C1248,53,1344,75,1392,85.3L1440,96L1440,120L1392,120C1344,120,1248,120,1152,120C1056,120,960,120,864,120C768,120,672,120,576,120C480,120,384,120,288,120C192,120,96,120,48,120L0,120Z"
              ></path>
            </svg>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 忘记密码对话框 -->
    <el-dialog
      v-model="forgotPasswordVisible"
      title="重置密码"
      width="400px"
      :close-on-click-modal="false"
      class="custom-dialog"
    >
      <el-form
        ref="forgotFormRef"
        :model="forgotForm"
        :rules="forgotRules"
        label-width="80px"
      >
        <el-form-item label="学号" prop="student_id">
          <el-input v-model="forgotForm.student_id" placeholder="请输入学号" class="custom-input" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="forgotForm.email" placeholder="请输入注册邮箱" class="custom-input" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="forgotPasswordVisible = false">取消</el-button>
        <el-button type="primary" :loading="forgotLoading" @click="handleForgotPassword">
          发送重置邮件
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { requestMethod } from '@/utils/request'
import { User, Lock, Monitor, TrendCharts, Headset, Connection, DataAnalysis, Loading } from '@element-plus/icons-vue'

export default {
  name: 'LoginView',
  components: {
    User,
    Lock,
    Monitor,
    TrendCharts,
    Headset,
    Connection,
    DataAnalysis,
    Loading
  },
  setup() {
    const router = useRouter()
    const loginFormRef = ref()
    const forgotFormRef = ref()
    
    // 登录表单数据
    const loginForm = reactive({
      student_id: '',
      password: '',
      remember: false
    })
    
    // 忘记密码表单数据
    const forgotForm = reactive({
      student_id: '',
      email: ''
    })
    
    // 状态管理
    const loginLoading = ref(false)
    const forgotPasswordVisible = ref(false)
    const forgotLoading = ref(false)
    
    // 登录表单验证规则
    const loginRules = {
      student_id: [
        { required: true, message: '请输入学号', trigger: 'blur' },
        { min: 1, max: 20, message: '学号长度在 1 到 20 个字符', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
      ]
    }
    
    // 忘记密码表单验证规则
    const forgotRules = {
      student_id: [
        { required: true, message: '请输入学号', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ]
    }
    
    // 系统特色功能列表
    const features = [
      {
        icon: TrendCharts,
        title: '多模态生理信号',
        description: '结合脑电、心率等多维度数据，精准评估疲劳状态'
      },
      {
        icon: Headset,
        title: '个性化音乐干预',
        description: '基于您的脑疲劳状态，智能推荐合适的音乐'
      },
      {
        icon: Connection,
        title: '联邦学习保护',
        description: '采用先进的联邦学习技术，保护您的隐私数据'
      },
      {
        icon: DataAnalysis,
        title: '智能疲劳检测',
        description: 'AI算法实时分析，提供科学的疲劳评估报告'
      }
    ]
    
    // 处理登录
    const handleLogin = async () => {
      if (!loginFormRef.value) return
      
      try {
        const valid = await loginFormRef.value.validate()
        if (!valid) return
        
        loginLoading.value = true
        
        // 使用 axios 封装发起登录请求
        let result
        try {
          result = await requestMethod.post('/auth/login', {
            student_id: loginForm.student_id,
            password: loginForm.password,
            device_info: navigator.userAgent
          })
        } catch (err) {
          console.error('登录错误:', err)
          // 优先展示后端返回的业务错误信息
          const backendMsg = err.response?.data?.msg || err.response?.data?.detail
          ElMessage.error(backendMsg || err.message || '登录失败，请检查网络连接')
          return
        }

        if (result && result.code === 200) {
          // 保存用户信息和会话令牌
          localStorage.setItem('user', JSON.stringify(result.data.user))
          localStorage.setItem('session_token', result.data.session_token)

          ElMessage.success('登录成功！')

          // 通知全局登录状态变化
          try { window.dispatchEvent(new Event('auth-changed')) } catch (e) { /* ignore */ }

          // 跳转到首页
          router.push('/')
        } else {
          ElMessage.error(result?.msg || '登录失败')
        }
      } catch (error) {
        console.error('登录错误:', error)
        ElMessage.error('登录失败，请检查网络连接')
      } finally {
        loginLoading.value = false
      }
    }
    
    // 显示忘记密码对话框
    const showForgotPassword = () => {
      forgotPasswordVisible.value = true
    }
    
    // 处理忘记密码
    const handleForgotPassword = async () => {
      if (!forgotFormRef.value) return
      
      try {
        const valid = await forgotFormRef.value.validate()
        if (!valid) return
        
        forgotLoading.value = true
        
        // 使用 axios 封装发送重置请求
        try {
          const result = await requestMethod.post('/auth/reset-password', forgotForm)
          if (result && result.code === 200) {
            ElMessage.success('重置邮件已发送，请查收邮箱')
            forgotPasswordVisible.value = false
            forgotForm.student_id = ''
            forgotForm.email = ''
          } else {
            ElMessage.error(result?.msg || '发送失败')
          }
        } catch (err) {
          console.error('重置密码错误:', err)
          ElMessage.error('发送失败，请稍后重试')
        }
      } catch (error) {
        console.error('重置密码错误:', error)
        ElMessage.error('发送失败，请稍后重试')
      } finally {
        forgotLoading.value = false
      }
    }
    
    return {
      loginFormRef,
      forgotFormRef,
      loginForm,
      forgotForm,
      loginLoading,
      forgotPasswordVisible,
      forgotLoading,
      loginRules,
      forgotRules,
      features,
      handleLogin,
      showForgotPassword,
      handleForgotPassword,
      // 图标组件
      User,
      Lock,
      Monitor,
      TrendCharts,
      Headset,
      Connection,
      DataAnalysis
    }
  }
}
</script>

<style lang="scss" scoped>
// 修复 el-card 样式穿透
:deep(.el-card) {
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.95);
}

// 修复 el-form 样式穿透
:deep(.el-form) {
  width: 100%;
}

// 修复 el-input 样式穿透
:deep(.el-input__wrapper) {
  padding-left: 44px;
  border-radius: var(--radius-md);
}

// 登录页面容器
.login-view {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--brand-primary) 0%, var(--wave-purple) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
  position: relative;
  overflow: hidden;
}

// 波形背景动画
.wave-background {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: -1;
}

.wave {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 200%;
  height: 120px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50%;
  animation: wave-animation 12s infinite ease-in-out;
}

.wave-1 {
  transform: translate(-50%, 50%);
  animation-delay: 0s;
  animation-duration: 18s;
}

.wave-2 {
  height: 80px;
  transform: translate(-40%, 70%);
  animation-delay: 2s;
  animation-duration: 15s;
}

.wave-3 {
  height: 60px;
  transform: translate(-60%, 80%);
  animation-delay: 4s;
  animation-duration: 12s;
}

@keyframes wave-animation {
  0%, 100% {
    transform: translate(-50%, 50%) scale(1);
  }
  50% {
    transform: translate(-30%, 50%) scale(1.1);
  }
}

// 登录容器
.login-container {
  display: flex;
  gap: var(--spacing-xl);
  max-width: 1100px;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 1;
  backdrop-filter: blur(10px);
}

// 登录卡片
.login-card {
  flex: 0 0 450px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: var(--shadow-elevated);
  transition: var(--transition-fast);
  
  &:hover {
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
    transform: translateY(-5px);
  }
  
  :deep(.el-card__header),
  :deep(.el-card__body) {
    padding: 0;
    background: transparent;
    border: none;
  }
}

.login-card-inner {
  padding: var(--spacing-xl);
}

// 登录头部
.login-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
  
  .logo-section {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-sm);
    
    .logo-container {
      width: 60px;
      height: 60px;
      border-radius: var(--radius-full);
      background: linear-gradient(135deg, var(--wave-blue), var(--wave-purple));
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 20px rgba(106, 90, 205, 0.3);
      transition: var(--transition-base);
      
      &:hover {
        transform: rotate(5deg) scale(1.05);
      }
    }
    
    .logo-icon {
      font-size: 32px;
      color: white;
    }
    
    .system-title {
      margin: 0;
      font-size: var(--font-size-extra-large);
      font-weight: var(--font-weight-bold);
      letter-spacing: -0.5px;
    }
  }
  
  .system-subtitle {
    margin: 0;
    font-size: var(--font-size-medium);
    color: var(--text-secondary);
    font-weight: var(--font-weight-normal);
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

// 登录表单
.login-form {
  .form-item-custom {
    margin-bottom: var(--spacing-md);
  }
  
  .input-container {
    position: relative;
    margin-bottom: var(--spacing-sm);
    
    .input-icon {
      position: absolute;
      left: 16px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 18px;
      z-index: 1;
    }
  }
  
  :deep(.custom-input) {
    padding-left: 44px;
    border-radius: var(--radius-md);
    height: 50px;
    font-size: var(--font-size-base);
    border-color: var(--border-light);
    transition: var(--transition-base);
    
    &:focus {
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px rgba(106, 90, 205, 0.15);
    }
    
    &:hover {
      border-color: var(--color-primary);
    }
  }
  
  .options-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
  }
  
  .checkbox-label {
    font-size: var(--font-size-xs);
    color: var(--text-secondary);
  }
  
  .forgot-password {
    font-size: var(--font-size-xs);
    color: var(--color-primary);
    font-weight: var(--font-weight-medium);
    transition: var(--transition-fast);
    
    &:hover {
      color: var(--color-primary-dark);
      opacity: 0.9;
    }
  }
  
  .login-button {
    width: 100%;
    height: 50px;
    font-size: var(--font-size-medium);
    font-weight: var(--font-weight-semibold);
    border-radius: var(--radius-md);
    border: none;
    position: relative;
    overflow: hidden;
    transition: var(--transition-base);
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(90deg, var(--wave-blue), var(--wave-purple), var(--wave-pink));
      z-index: -1;
      transition: transform 0.5s ease;
    }
    
    &:hover::before {
      transform: scaleX(1.1);
    }
    
    &:active {
      transform: scale(0.98);
    }
  }
  
  .loading-icon {
    animation: rotate 1s linear infinite;
  }
  
  .demo-account-info {
    margin-top: var(--spacing-md);
    text-align: center;
    font-size: var(--font-size-xs);
    color: var(--text-muted);
  }
  
  .account-text,
  .password-text {
    font-weight: var(--font-weight-semibold);
    padding: 2px 8px;
    border-radius: var(--radius-sm);
    background-color: var(--background-color-light);
    color: var(--text-primary);
  }
  
  .register-link {
    text-align: center;
    margin-top: var(--spacing-lg);
    
    .register-text {
      color: var(--text-secondary);
      margin-right: var(--spacing-xs);
      font-size: var(--font-size-xs);
    }
    
    .register-button {
      font-size: var(--font-size-xs);
      font-weight: var(--font-weight-semibold);
      color: var(--color-primary);
      transition: var(--transition-fast);
      
      &:hover {
        color: var(--color-primary-dark);
      }
    }
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 系统介绍部分
.system-intro {
  flex: 1;
  max-width: 500px;
  color: white;
  
  .intro-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  }
  
  .intro-title {
    font-size: var(--font-size-display);
    font-weight: var(--font-weight-bold);
    margin: 0 0 var(--spacing-md) 0;
    line-height: 1.2;
  }
  
  .intro-description {
    font-size: var(--font-size-medium);
    line-height: var(--line-height-relaxed);
    margin-bottom: var(--spacing-xl);
    opacity: 0.9;
  }
  
  .feature-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .feature-item {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--radius-md);
    transition: var(--transition-base);
    
    &:hover {
      background: rgba(255, 255, 255, 0.1);
      transform: translateX(5px);
    }
    
    .feature-icon-container {
      width: 40px;
      height: 40px;
      border-radius: var(--radius-full);
      background: rgba(255, 255, 255, 0.15);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    
    .feature-icon {
      font-size: 20px;
      color: white;
    }
    
    .feature-content {
      flex: 1;
    }
    
    .feature-title {
      font-size: var(--font-size-medium);
      font-weight: var(--font-weight-semibold);
      margin: 0 0 4px 0;
    }
    
    .feature-desc {
      font-size: var(--font-size-xs);
      margin: 0;
      opacity: 0.85;
      line-height: var(--line-height-normal);
    }
  }
  
  .wave-accent {
    margin-top: var(--spacing-xl);
    width: 100%;
    overflow: hidden;
  }
  
  .wave-accent svg {
    width: 100%;
    height: auto;
  }
}

// 自定义对话框
:deep(.custom-dialog) {
  .el-dialog__header {
    background: linear-gradient(90deg, var(--wave-blue), var(--wave-purple));
    padding: var(--spacing-md) var(--spacing-lg);
    margin: 0;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    
    .el-dialog__title {
      color: white;
      font-size: var(--font-size-lg);
    }
  }
  
  .el-dialog__body {
    padding: var(--spacing-lg);
  }
  
  .el-dialog__footer {
    padding: var(--spacing-md) var(--spacing-lg);
    background-color: var(--background-color-light);
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .login-container {
    gap: var(--spacing-lg);
  }
  
  .login-card {
    flex: 0 0 400px;
  }
}

@media (max-width: 768px) {
  .login-view {
    padding: var(--spacing-md);
  }
  
  .login-container {
    flex-direction: column;
    gap: 0;
  }
  
  .login-card {
    flex: 1;
    width: 100%;
    max-width: 420px;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  }
  
  .system-intro {
    max-width: 100%;
    width: 100%;
    
    .intro-card {
      border-radius: 0 0 var(--radius-lg) var(--radius-lg);
      padding: var(--spacing-lg);
    }
    
    .intro-title {
      font-size: var(--font-size-lg);
      text-align: center;
    }
    
    .intro-description {
      font-size: var(--font-size-base);
      text-align: center;
    }
    
    .feature-item {
      padding: var(--spacing-sm);
    }
  }
}

@media (max-width: 480px) {
  .login-card-inner {
    padding: var(--spacing-lg);
  }
  
  .login-header {
    margin-bottom: var(--spacing-lg);
    
    .logo-section {
      .logo-container {
        width: 50px;
        height: 50px;
      }
      
      .logo-icon {
        font-size: 28px;
      }
      
      .system-title {
        font-size: var(--font-size-lg);
      }
    }
  }
  
  .form-input-group {
    gap: var(--spacing-sm);
  }
  
  :deep(.custom-input) {
    height: 44px;
  }
  
  .login-button {
    height: 44px;
  }
}

// 深色模式适配
@media (prefers-color-scheme: dark) {
  .login-card {
    background: rgba(30, 30, 30, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .system-subtitle {
    color: var(--dark-text-secondary);
  }
  
  :deep(.custom-input) {
    background-color: var(--dark-background-color-input);
    border-color: var(--dark-border-light);
    color: var(--dark-text-primary);
    
    &::placeholder {
      color: var(--dark-text-muted);
    }
  }
  
  .checkbox-label {
    color: var(--dark-text-secondary);
  }
  
  .account-text,
  .password-text {
    background-color: var(--dark-background-color-card);
    color: var(--dark-text-primary);
  }
  
  .register-text {
    color: var(--dark-text-secondary);
  }
}
</style>

<style lang="scss">
.login-container {
  display: flex;
  gap: var(--spacing-xl);
  max-width: 1100px;
  width: 100%;
  align-items: center;
  justify-content: center; /* 改为居中，避免空间不足时重叠 */
  position: relative;
  z-index: 1;
  backdrop-filter: blur(10px);
}

.login-card {
  flex: 0 0 450px; /* 固定宽度，避免被压缩 */
}

.system-intro {
  flex: 1;
  max-width: 500px;
  min-width: 300px; /* 最小宽度，避免内容挤压 */
}
</style>
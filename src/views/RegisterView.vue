<template>
  <div class="register-view">
    <!-- 波形背景装饰 -->
    <div class="wave-background">
      <div class="wave wave-1"></div>
      <div class="wave wave-2"></div>
      <div class="wave wave-3"></div>
    </div>
    
    <div class="register-container">
      <!-- 注册表单卡片 -->
      <el-card class="register-card" shadow="always">
        <div class="register-card-inner">
          <!-- 标题栏 -->
          <div class="register-header">
            <div class="logo-section">
              <div class="logo-container">
                <el-icon class="logo-icon"><Monitor /></el-icon>
              </div>
              <h1 class="system-title gradient-text">WaveTune</h1>
            </div>
            <p class="system-subtitle">创建您的账户</p>
          </div>
        
        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          label-width="0"
          class="register-form"
          @submit.prevent="handleRegister"
        >
          <div class="form-input-group">
            <el-form-item prop="username" class="form-item-custom">
              <div class="input-container">
                <el-icon class="input-icon"><User /></el-icon>
                <el-input
                  v-model="registerForm.username"
                  placeholder="请输入用户名"
                  size="large"
                  class="custom-input"
                  clearable
                  :prefix-icon="''"
                />
              </div>
            </el-form-item>
            
            <el-form-item prop="student_id" class="form-item-custom">
              <div class="input-container">
                <el-icon class="input-icon"><CreditCard /></el-icon>
                <el-input
                  v-model="registerForm.student_id"
                  placeholder="请输入学号"
                  size="large"
                  class="custom-input"
                  clearable
                  :prefix-icon="''"
                />
              </div>
            </el-form-item>
            
            <el-form-item prop="email" class="form-item-custom">
              <div class="input-container">
                <el-icon class="input-icon"><Message /></el-icon>
                <el-input
                  v-model="registerForm.email"
                  placeholder="请输入邮箱（可选）"
                  size="large"
                  class="custom-input"
                  clearable
                  :prefix-icon="''"
                />
              </div>
            </el-form-item>
            
            <el-form-item prop="phone" class="form-item-custom">
              <div class="input-container">
                <el-icon class="input-icon"><Phone /></el-icon>
                <el-input
                  v-model="registerForm.phone"
                  placeholder="请输入手机号（可选）"
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
                  v-model="registerForm.password"
                  type="password"
                  placeholder="请输入密码"
                  size="large"
                  class="custom-input"
                  show-password
                  clearable
                  :prefix-icon="''"
                />
              </div>
            </el-form-item>
            
            <el-form-item prop="confirmPassword" class="form-item-custom">
              <div class="input-container">
                <el-icon class="input-icon"><Lock /></el-icon>
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="请确认密码"
                  size="large"
                  class="custom-input"
                  show-password
                  clearable
                  @keyup.enter="handleRegister"
                  :prefix-icon="''"
                />
              </div>
            </el-form-item>
          </div>
          
          <el-form-item prop="agreement" class="options-row">
            <el-checkbox v-model="registerForm.agreement" class="agreement-checkbox">
              <span class="checkbox-label">我已阅读并同意</span>
              <el-link type="primary" @click="showUserAgreement">《用户协议》</el-link>
              <span class="checkbox-label">和</span>
              <el-link type="primary" @click="showPrivacyPolicy">《隐私政策》</el-link>
            </el-checkbox>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="register-button gradient-button"
              :loading="registerLoading"
              @click="handleRegister"
            >
              <span v-if="!registerLoading">立即注册</span>
              <el-icon v-else class="loading-icon"><Loading /></el-icon>
            </el-button>
          </el-form-item>
          
          <el-form-item class="login-link">
            <span class="login-text">已有账户？</span>
            <el-link type="primary" class="login-button-link" @click="$router.push('/login')">
              立即登录
            </el-link>
          </el-form-item>
        </el-form>
        </div>
      </el-card>
      
      <!-- 系统介绍部分 -->
      <div class="system-intro">
        <div class="intro-card">
          <h2 class="intro-title">智能脑疲劳检测与音乐干预系统</h2>
          <p class="intro-description">
            通过EEG、EOG、HRV等多模态生理信号实时监测脑疲劳状态，
            并提供个性化轻音乐干预方案，帮助用户缓解疲劳、提升专注力。
          </p>
          
          <div class="feature-list">
            <div class="feature-item">
              <div class="feature-icon-container">
                <el-icon class="feature-icon"><TrendCharts /></el-icon>
              </div>
              <div class="feature-content">
                <h3 class="feature-title">智能检测</h3>
                <p class="feature-desc">基于多模态生理信号的实时脑疲劳检测</p>
              </div>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon-container">
                <el-icon class="feature-icon"><Headset /></el-icon>
              </div>
              <div class="feature-content">
                <h3 class="feature-title">音乐干预</h3>
                <p class="feature-desc">个性化轻音乐干预方案</p>
              </div>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon-container">
                <el-icon class="feature-icon"><DataAnalysis /></el-icon>
              </div>
              <div class="feature-content">
                <h3 class="feature-title">数据分析</h3>
                <p class="feature-desc">详细的健康数据分析和趋势跟踪</p>
              </div>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon-container">
                <el-icon class="feature-icon"><Connection /></el-icon>
              </div>
              <div class="feature-content">
                <h3 class="feature-title">隐私保护</h3>
                <p class="feature-desc">联邦学习技术确保个人数据安全</p>
              </div>
            </div>
          </div>
          
          <!-- 波形装饰 -->
          <div class="wave-accent">
            <svg viewBox="0 0 1200 120" preserveAspectRatio="none">
              <path d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity="0.25" class="shape-fill"></path>
              <path d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" opacity="0.5" class="shape-fill"></path>
              <path d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" class="shape-fill"></path>
            </svg>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 用户协议对话框 -->
    <el-dialog
      v-model="userAgreementVisible"
      title="用户协议"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="agreement-content">
        <h4>1. 服务条款</h4>
        <p>欢迎使用 WaveTune 脑疲劳检测与音乐干预系统。通过注册和使用本服务，您同意遵守以下条款和条件。</p>
        
        <h4>2. 用户责任</h4>
        <p>用户应确保提供的信息真实、准确、完整，并承担因信息不实导致的一切后果。</p>
        
        <h4>3. 隐私保护</h4>
        <p>我们承诺保护用户隐私，采用联邦学习技术确保数据安全，不会泄露用户个人信息。</p>
        
        <h4>4. 服务限制</h4>
        <p>本服务仅供个人学习和研究使用，不得用于商业用途或非法活动。</p>
        
        <h4>5. 免责声明</h4>
        <p>本系统提供的检测结果仅供参考，不能替代专业医疗诊断。</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="userAgreementVisible = false">我已阅读</el-button>
      </template>
    </el-dialog>
    
    <!-- 隐私政策对话框 -->
    <el-dialog
      v-model="privacyPolicyVisible"
      title="隐私政策"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="agreement-content">
        <h4>1. 信息收集</h4>
        <p>我们仅收集必要的用户信息，包括学号、用户名、邮箱等基本信息。</p>
        
        <h4>2. 信息使用</h4>
        <p>收集的信息仅用于提供服务和改善用户体验，不会用于其他目的。</p>
        
        <h4>3. 数据安全</h4>
        <p>采用加密技术保护用户数据，使用联邦学习技术确保数据隐私。</p>
        
        <h4>4. 信息共享</h4>
        <p>我们不会与第三方共享用户个人信息，除非获得用户明确同意。</p>
        
        <h4>5. 用户权利</h4>
        <p>用户有权查看、修改、删除个人信息，或要求停止使用服务。</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="privacyPolicyVisible = false">我已阅读</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { requestMethod } from '@/utils/request'
import { 
  User, Lock, Monitor, CreditCard, Message, Phone,
  TrendCharts, Headset, DataAnalysis, Connection,
  Loading
} from '@element-plus/icons-vue'

export default {
  name: 'RegisterView',
  components: {
    User,
    Lock,
    Monitor,
    CreditCard,
    Message,
    Phone,
    TrendCharts,
    Headset,
    DataAnalysis,
    Connection,
    Loading
  },
  setup() {
    const router = useRouter()
    const registerFormRef = ref()
    
    // 注册表单数据
    const registerForm = reactive({
      username: '',
      student_id: '',
      email: '',
      phone: '',
      password: '',
      confirmPassword: '',
      agreement: false
    })
    
    // 状态管理
    const registerLoading = ref(false)
    const userAgreementVisible = ref(false)
    const privacyPolicyVisible = ref(false)
    
    // 自定义验证器
    const validateConfirmPassword = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== registerForm.password) {
        callback(new Error('两次输入密码不一致'))
      } else {
        callback()
      }
    }
    
    const validateAgreement = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请阅读并同意用户协议和隐私政策'))
      } else {
        callback()
      }
    }
    
    // 注册表单验证规则
    const registerRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 2, max: 50, message: '用户名长度在 2 到 50 个字符', trigger: 'blur' }
      ],
      student_id: [
        { required: true, message: '请输入学号', trigger: 'blur' },
        { min: 1, max: 20, message: '学号长度在 1 到 20 个字符', trigger: 'blur' }
      ],
      email: [
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      phone: [
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, validator: validateConfirmPassword, trigger: 'blur' }
      ],
      agreement: [
        { required: true, validator: validateAgreement, trigger: 'change' }
      ]
    }
    
    // 处理注册
    const handleRegister = async () => {
      if (!registerFormRef.value) return
      
      try {
        const valid = await registerFormRef.value.validate()
        if (!valid) return
        
        registerLoading.value = true
        
        // 准备注册数据
        const registerData = {
          username: registerForm.username,
          student_id: registerForm.student_id,
          password: registerForm.password
        }
        
        // 添加可选字段
        if (registerForm.email) {
          registerData.email = registerForm.email
        }
        if (registerForm.phone) {
          registerData.phone = registerForm.phone
        }
        
        // 使用 axios 封装发起注册请求
        let result
        try {
          result = await requestMethod.post('/auth/register', registerData)
        } catch (err) {
          console.error('注册错误:', err)
          ElMessage.error(err.message || '注册失败，请检查网络连接')
          return
        }

        if (result && result.code === 200) {
          ElMessage.success('注册成功！请登录')
          router.push('/login')
        } else {
          ElMessage.error(result?.msg || '注册失败')
        }
      } catch (error) {
        console.error('注册错误:', error)
        ElMessage.error('注册失败，请检查网络连接')
      } finally {
        registerLoading.value = false
      }
    }
    
    // 显示用户协议
    const showUserAgreement = () => {
      userAgreementVisible.value = true
    }
    
    // 显示隐私政策
    const showPrivacyPolicy = () => {
      privacyPolicyVisible.value = true
    }
    
    return {
      registerFormRef,
      registerForm,
      registerLoading,
      userAgreementVisible,
      privacyPolicyVisible,
      registerRules,
      handleRegister,
      showUserAgreement,
      showPrivacyPolicy
    }
  }
}
</script>

<style lang="scss" scoped>
// 变量定义
:root {
  // 颜色变量
  --wave-blue: #667eea;
  --wave-purple: #764ba2;
  --wave-pink: #f093fb;
  
  // 字体大小
  --font-size-xs: 13px;
  --font-size-base: 14px;
  --font-size-medium: 16px;
  --font-size-lg: 20px;
  --font-size-xl: 24px;
  --font-size-display: 32px;
  
  // 间距
  --spacing-xs: 8px;
  --spacing-sm: 12px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  // 圆角
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 50%;
  
  // 过渡
  --transition-fast: 0.2s ease;
  --transition-base: 0.3s ease;
  
  // 字体权重
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  // 行高
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.6;
  
  // 文本颜色
  --text-primary: #1d2129;
  --text-secondary: #4e5969;
  --text-muted: #86909c;
  
  // 颜色
  --color-primary: #667eea;
  --color-primary-dark: #5a67d8;
  
  // 背景颜色
  --background-color-light: #f2f3f5;
  --background-color-card: #ffffff;
  --background-color-input: #ffffff;
}

// 深色模式变量
@media (prefers-color-scheme: dark) {
  :root {
    --dark-text-primary: #f7f8fa;
    --dark-text-secondary: #c9cdcf;
    --dark-text-muted: #86909c;
    --dark-background-color-card: #1d1f27;
    --dark-background-color-input: #2c3039;
    --dark-border-light: rgba(255, 255, 255, 0.1);
  }
}

.register-view {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--wave-blue) 0%, var(--wave-purple) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-md);
  position: relative;
  overflow: hidden;
}

// 波形背景装饰
.wave-background {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  
  .wave {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 200%;
    height: 200px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50% 50% 0 0;
    animation: wave-move 15s linear infinite;
    transform-origin: bottom center;
    
    &.wave-1 {
      bottom: -50px;
      height: 300px;
      animation-delay: 0s;
      opacity: 0.3;
    }
    
    &.wave-2 {
      bottom: -80px;
      height: 320px;
      animation-delay: -3s;
      opacity: 0.2;
    }
    
    &.wave-3 {
      bottom: -100px;
      height: 340px;
      animation-delay: -6s;
      opacity: 0.15;
    }
  }
}

@keyframes wave-move {
  0% {
    transform: translateX(-50%) rotate(0deg);
  }
  100% {
    transform: translateX(-50%) rotate(360deg);
  }
}

.register-container {
  display: flex;
  gap: var(--spacing-xl);
  max-width: 1100px;
  width: 100%;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
  backdrop-filter: blur(10px);
}

.register-card {
  flex: 0 0 450px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(15px);
  
  :deep(.el-card__body) {
    padding: 0;
  }
}

.register-card-inner {
  padding: var(--spacing-xl);
}

.register-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
  
  .logo-section {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
    
    .logo-container {
      width: 60px;
      height: 60px;
      border-radius: var(--radius-full);
      background: linear-gradient(135deg, var(--wave-blue), var(--wave-purple));
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .logo-icon {
      font-size: 32px;
      color: white;
    }
    
    .system-title {
      margin: 0;
      font-size: var(--font-size-xl);
      font-weight: var(--font-weight-bold);
      background: linear-gradient(90deg, var(--wave-blue), var(--wave-purple), var(--wave-pink));
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
      background-size: 200% auto;
      animation: gradient-text 3s ease infinite;
    }
  }
  
  .system-subtitle {
    margin: 0;
    font-size: var(--font-size-base);
    color: var(--text-secondary);
  }
}

// 渐变文本动画
@keyframes gradient-text {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.form-input-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.form-item-custom {
  margin-bottom: 0;
}

.input-container {
  display: flex;
  align-items: center;
  background-color: var(--background-color-light);
  border-radius: var(--radius-md);
  padding: 0 var(--spacing-md);
  transition: var(--transition-fast);
  
  &:focus-within {
    background-color: white;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.12);
  }
}

.input-icon {
  color: var(--text-muted);
  margin-right: var(--spacing-sm);
  font-size: 18px;
  transition: var(--transition-fast);
}

.input-container:focus-within .input-icon {
  color: var(--color-primary);
}

:deep(.custom-input) {
  width: 100%;
  height: 48px;
  border: none;
  background: transparent;
  font-size: var(--font-size-base);
  color: var(--text-primary);
  padding: 0;
  
  &:focus {
    box-shadow: none;
    outline: none;
  }
  
  &::placeholder {
    color: var(--text-muted);
  }
}

.options-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: var(--spacing-lg) 0;
}

.agreement-checkbox {
  font-size: var(--font-size-xs);
  line-height: var(--line-height-normal);
  
  :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
    background-color: var(--color-primary);
    border-color: var(--color-primary);
  }
  
  :deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
    color: var(--text-primary);
  }
}

.checkbox-label {
  color: var(--text-secondary);
}

.register-button {
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

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.login-link {
  text-align: center;
  margin-top: var(--spacing-lg);
  
  .login-text {
    color: var(--text-secondary);
    margin-right: var(--spacing-xs);
    font-size: var(--font-size-xs);
  }
  
  .login-button-link {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-primary);
    transition: var(--transition-fast);
    
    &:hover {
      color: var(--color-primary-dark);
    }
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

.agreement-content {
  max-height: 400px;
  overflow-y: auto;
  line-height: 1.6;
  
  h4 {
    color: var(--el-color-primary);
    margin: 20px 0 10px 0;
    font-size: 16px;
    
    &:first-child {
      margin-top: 0;
    }
  }
  
  p {
    margin: 0 0 15px 0;
    color: var(--text-regular);
  }
}

// 响应式适配
@media (max-width: 768px) {
  .register-container {
    flex-direction: column;
    gap: 20px;
  }
  
  .register-card {
    max-width: 100%;
  }
  
  .register-benefits {
    max-width: 100%;
    
    h3 {
      font-size: 20px;
    }
    
    .benefit-list {
      .benefit-item {
        padding: 16px;
        
        .benefit-icon {
          font-size: 20px;
        }
        
        .benefit-content {
          h4 {
            font-size: 16px;
          }
          
          p {
            font-size: 13px;
          }
        }
      }
    }
  }
}

@media (max-width: 480px) {
  .register-view {
    padding: 16px;
  }
  
  .register-card {
    :deep(.el-card__header) {
      padding: 20px;
    }
    
    :deep(.el-card__body) {
      padding: 20px;
    }
  }
  
  .register-header {
    .logo-section {
      .system-title {
        font-size: 24px;
      }
    }
  }
}
</style>

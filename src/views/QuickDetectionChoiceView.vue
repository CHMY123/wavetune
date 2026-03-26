<template>
  <div class="quick-detection-choice">
    <el-card class="choice-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><Aim /></el-icon>
          <span>快速检测</span>
        </div>
      </template>
      
      <div class="choice-container">
        <h2 class="main-title">请选择检测方式</h2>
        <p class="description">
          选择适合您的检测方法，开始脑疲劳检测流程
        </p>
        
        <div class="choice-buttons">
          <!-- 2-Back 实验选项 -->
          <div class="button-wrapper">
            <el-button 
              type="primary" 
              size="large" 
              @click="goToTwoBackExperiment"
              class="choice-button primary-button"
            >
              <div class="button-icon-container">
                <el-icon class="icon"><Histogram /></el-icon>
              </div>
              <div class="button-content">
                <div class="button-title">2-Back 疲劳诱发实验</div>
                <div class="button-subtitle">通过认知任务诱发疲劳，评估疲劳程度</div>
              </div>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </el-button>
          </div>
          
          <!-- 直接检测选项 -->
          <div class="button-wrapper">
            <el-button 
              type="success" 
              size="large" 
              @click="goToDirectDetection"
              class="choice-button success-button"
            >
              <div class="button-icon-container">
                <el-icon class="icon"><DataAnalysis /></el-icon>
              </div>
              <div class="button-content">
                <div class="button-title">直接检测</div>
                <div class="button-subtitle">连接多模态信号采集设备进行实时检测</div>
              </div>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { 
  DataAnalysis, 
  Aim, 
  Histogram, 
  ArrowRight 
} from '@element-plus/icons-vue'

export default {
  name: 'QuickDetectionChoiceView',
  components: {
    DataAnalysis,
    Aim,
    Histogram,
    ArrowRight
  },
  methods: {
    // 跳转到 2-Back 实验页面
    goToTwoBackExperiment() {
      this.$router.push('/quick-detection/two-back')
    },
    
    // 跳转到直接检测页面
    goToDirectDetection() {
      this.$router.push('/signal-monitor')
    }
  }
}
</script>

<style scoped>
.quick-detection-choice {
  min-height: calc(100vh - 60px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background-color: #f5f7fa;
  background-image: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.choice-card {
  width: 100%;
  max-width: 800px;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.choice-card:hover {
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: bold;
  color: #333;
  padding: 20px 24px;
  background-color: #f9f9f9;
  border-bottom: 1px solid #eaeaea;
}

.header-icon {
  font-size: 24px;
  color: #409eff;
}

.choice-container {
  text-align: center;
  padding: 50px 30px;
}

.main-title {
  margin-bottom: 24px;
  color: #333;
  font-size: 28px;
  font-weight: bold;
  animation: fadeInUp 0.6s ease-out;
  position: relative;
  display: inline-block;
}

.main-title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 2px;
  animation: expandWidth 0.8s ease-out 0.3s forwards;
  width: 0;
}

.description {
  margin-bottom: 50px;
  color: #666;
  font-size: 18px;
  line-height: 1.6;
  animation: fadeInUp 0.6s ease-out 0.2s forwards;
  opacity: 0;
}

.choice-buttons {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 600px;
  margin: 0 auto;
}

.button-wrapper {
  animation: fadeInUp 0.6s ease-out;
  animation-fill-mode: both;
}

.button-wrapper:nth-child(1) {
  animation-delay: 0.4s;
}

.button-wrapper:nth-child(2) {
  animation-delay: 0.6s;
}

.choice-button {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 40px 100px;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
  position: relative;
  overflow: hidden;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.choice-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0) 100%);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

.choice-button:hover::before {
  transform: translateX(100%);
}

.choice-button:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.primary-button {
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.primary-button:hover {
  background: linear-gradient(135deg, #3a8ee6, #53a8ff);
}

.success-button {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.success-button:hover {
  background: linear-gradient(135deg, #5cb85c, #71d571);
}

.button-icon-container {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.choice-button:hover .button-icon-container {
  transform: scale(1.1) rotate(5deg);
  background-color: rgba(255, 255, 255, 0.3);
}

.icon {
  font-size: 32px;
  color: rgba(255, 255, 255, 0.9);
}

.button-content {
  flex: 1;
  margin-right: 20px;
}

.button-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.button-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.4;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.arrow-icon {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
}

.choice-button:hover .arrow-icon {
  transform: translateX(8px);
  color: #fff;
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes expandWidth {
  from {
    width: 0;
  }
  to {
    width: 80px;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .quick-detection-choice {
    padding: 16px;
  }
  
  .choice-card {
    max-width: 100%;
  }
  
  .card-header {
    font-size: 18px;
    padding: 16px 20px;
  }
  
  .header-icon {
    font-size: 20px;
  }
  
  .choice-container {
    padding: 40px 20px;
  }
  
  .main-title {
    font-size: 24px;
  }
  
  .description {
    font-size: 16px;
    margin-bottom: 40px;
  }
  
  .choice-buttons {
    gap: 20px;
  }
  
  .choice-button {
    padding: 20px;
  }
  
  .button-icon-container {
    width: 50px;
    height: 50px;
    margin-right: 20px;
  }
  
  .icon {
    font-size: 28px;
  }
  
  .button-title {
    font-size: 18px;
  }
  
  .button-subtitle {
    font-size: 14px;
  }
  
  .arrow-icon {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .choice-container {
    padding: 30px 16px;
  }
  
  .main-title {
    font-size: 20px;
  }
  
  .description {
    font-size: 14px;
    margin-bottom: 30px;
  }
  
  .choice-button {
    padding: 16px;
  }
  
  .button-icon-container {
    width: 40px;
    height: 40px;
    margin-right: 16px;
  }
  
  .icon {
    font-size: 24px;
  }
  
  .button-title {
    font-size: 16px;
  }
  
  .button-subtitle {
    font-size: 12px;
  }
}

/* 暗模式适配 */
.theme-dark .quick-detection-choice {
  background-color: var(--bg-page);
  background-image: none;
}

.theme-dark .choice-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
}

.theme-dark .choice-card:hover {
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
}

.theme-dark .card-header {
  background-color: var(--bg-hover);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.theme-dark .header-icon {
  color: var(--brand-primary);
}

.theme-dark .main-title {
  color: var(--text-primary);
}

.theme-dark .description {
  color: var(--text-secondary);
}

.theme-dark .choice-button:hover {
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
}

.theme-dark .primary-button {
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.theme-dark .primary-button:hover {
  background: linear-gradient(135deg, #3a8ee6, #53a8ff);
}

.theme-dark .success-button {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.theme-dark .success-button:hover {
  background: linear-gradient(135deg, #5cb85c, #71d571);
}

.theme-dark .button-icon-container {
  background-color: rgba(255, 255, 255, 0.15);
}

.theme-dark .choice-button:hover .button-icon-container {
  background-color: rgba(255, 255, 255, 0.25);
}
</style>
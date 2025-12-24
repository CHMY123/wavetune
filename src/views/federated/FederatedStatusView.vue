<template>
  <div class="federated-status-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <el-page-header content="联邦学习参与状态" />
    </div>

    <!-- 联邦学习参与状态展示组件 -->
    <CardContainer class="participation-status-card">
      <el-row :gutter="20">
        <!-- 左侧：参与设备统计 -->
        <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
          <div class="status-item">
            <div class="status-header">
              <h3 class="status-title">参与设备</h3>
              <div class="device-icons">
                <el-icon class="device-icon"><Monitor /></el-icon>
                <el-icon class="device-icon"><Iphone /></el-icon>
              </div>
            </div>
            <div class="status-value">
              <span class="main-number">12</span>
              <span class="main-unit">台</span>
            </div>
            <div class="status-detail">
              <span class="detail-item online">
                <el-icon><CircleCheck /></el-icon>
                在线：10 台
              </span>
              <span class="detail-item offline">
                <el-icon><CircleClose /></el-icon>
                离线：2 台
              </span>
            </div>
          </div>
        </el-col>

        <!-- 中间：训练进度展示 -->
        <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
          <div class="status-item">
            <div class="status-header">
              <h3 class="status-title">当前轮次进度</h3>
            </div>
            <div class="progress-container">
              <el-progress 
                :percentage="68" 
                :stroke-width="12"
                :show-text="false"
                class="progress-bar"
              />
              <div class="progress-text">68%</div>
            </div>
            <div class="round-info">
              第 3/10 轮
            </div>
          </div>
        </el-col>

        <!-- 右侧：剩余时间预估 -->
        <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
          <div class="status-item">
            <div class="status-header">
              <h3 class="status-title">预计剩余时间</h3>
              <el-icon class="time-icon"><Clock /></el-icon>
            </div>
            <div class="status-value">
              <span class="time-display">01:23:45</span>
            </div>
            <div class="time-note">
              基于当前训练速度预估
            </div>
          </div>
        </el-col>
      </el-row>
    </CardContainer>

    <!-- 隐私保护说明 -->
    <CardContainer title="隐私保护说明" class="privacy-card">
      <div class="privacy-content">
        <div class="privacy-section">
          <h4 class="privacy-title">什么是联邦学习？</h4>
          <p class="privacy-text">
            在不泄露您的原始生理数据（如 EEG、EOG 信号）的情况下，仅上传模型参数进行协同训练。
            您的原始数据始终保存在您的设备上，不会被上传到服务器。
          </p>
        </div>
        
        <div class="privacy-section">
          <h4 class="privacy-title">采用的安全技术</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="安全聚合">
              参数加密后传输，聚合过程无法反推原始数据
            </el-descriptions-item>
            <el-descriptions-item label="本地计算">
              所有原始数据仅在您的设备上处理，不上传至服务器
            </el-descriptions-item>
            <el-descriptions-item label="差分隐私">
              在参数中添加随机噪声，进一步保护数据隐私
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="privacy-actions">
          <el-button type="primary" @click="showPrivacyDialog">
            查看详细说明
          </el-button>
          <el-button type="success">
            开始参与联邦学习
          </el-button>
        </div>
      </div>
    </CardContainer>

    <!-- 隐私保护详细说明弹窗 -->
    <el-dialog
      v-model="privacyDialogVisible"
      title="联邦学习隐私保护说明"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="privacy-dialog-content">
        <div class="privacy-flow">
          <h4>联邦学习流程</h4>
          <div class="flow-diagram">
            <div class="flow-step">
              <div class="step-icon step-1">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="step-text">本地设备训练</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-step">
              <div class="step-icon step-2">
                <el-icon><Upload /></el-icon>
              </div>
              <div class="step-text">上传参数</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-step">
              <div class="step-icon step-3">
                <el-icon><Connection /></el-icon>
              </div>
              <div class="step-text">聚合模型</div>
            </div>
          </div>
        </div>
        
        <div class="security-features">
          <h4>安全保障</h4>
          <ul class="security-list">
            <li>原始数据永不离开您的设备</li>
            <li>模型参数经过加密传输</li>
            <li>聚合过程无法还原原始数据</li>
            <li>支持差分隐私技术</li>
          </ul>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="privacyDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="privacyDialogVisible = false">
            我已了解
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import CardContainer from '@/components/global/CardContainer.vue'
import { CircleCheck, CircleClose, Monitor, Upload, Connection } from '@element-plus/icons-vue'

export default {
  name: 'FederatedStatusView',
  components: {
    CardContainer,
    CircleCheck,
    CircleClose,
    Monitor,
    Upload,
    Connection
  },
  data() {
    return {
      privacyDialogVisible: false
    }
  },
  methods: {
    showPrivacyDialog() {
      this.privacyDialogVisible = true
    }
  }
}
</script>

<style lang="scss" scoped>
.federated-status-view {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
  
  :deep(.el-page-header__content) {
    font-size: 24px;
    font-weight: bold;
    color: var(--text-primary);
  }
}

.participation-status-card {
  margin-bottom: 24px;
  
  .status-item {
    text-align: center;
    padding: 20px;
    
    .status-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      
      .status-title {
        margin: 0;
        font-size: 14px;
        color: var(--text-regular);
        font-weight: 500;
      }
      
      .device-icons {
        display: flex;
        gap: 8px;
        
        .device-icon {
          font-size: 16px;
          color: var(--text-secondary);
        }
      }
      
      .time-icon {
        font-size: 16px;
        color: var(--text-secondary);
      }
    }
    
    .status-value {
      margin-bottom: 12px;
      
      .main-number {
        font-size: 28px;
        font-weight: bold;
        color: var(--el-color-primary);
      }
      
      .main-unit {
        font-size: 16px;
        color: var(--text-regular);
        margin-left: 4px;
      }
      
      .time-display {
        font-size: 24px;
        font-weight: bold;
        color: var(--text-primary);
        font-family: 'SF Mono', Monaco, monospace;
      }
    }
    
    .status-detail {
      display: flex;
      flex-direction: column;
      gap: 4px;
      
      .detail-item {
        font-size: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        
        &.online {
          color: var(--el-color-success);
        }
        
        &.offline {
          color: var(--el-color-danger);
        }
      }
    }
    
    .progress-container {
      margin-bottom: 12px;
      position: relative;
      
      .progress-bar {
        :deep(.el-progress-bar__outer) {
          background: #f0f0f0;
        }
        
        :deep(.el-progress-bar__inner) {
          background: var(--el-color-primary);
        }
      }
      
      .progress-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 14px;
        font-weight: bold;
        color: var(--el-color-primary);
      }
    }
    
    .round-info {
      font-size: 14px;
      color: var(--text-regular);
    }
    
    .time-note {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
}

.privacy-card {
  .privacy-content {
    .privacy-section {
      margin-bottom: 24px;
      
      .privacy-title {
        margin: 0 0 12px 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .privacy-text {
        margin: 0;
        font-size: 14px;
        color: var(--text-regular);
        line-height: 1.6;
      }
    }
    
    .privacy-actions {
      display: flex;
      gap: 12px;
      justify-content: center;
      margin-top: 24px;
    }
  }
}

.privacy-dialog-content {
  .privacy-flow {
    margin-bottom: 24px;
    
    h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .flow-diagram {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 16px;
      padding: 20px;
      background: #f8f9fa;
      border-radius: 8px;
      
      .flow-step {
        text-align: center;
        
        .step-icon {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 8px;
          font-size: 18px;
          color: white;
          
          &.step-1 {
            background: #1890ff;
          }
          
          &.step-2 {
            background: #52c41a;
          }
          
          &.step-3 {
            background: #722ed1;
          }
        }
        
        .step-text {
          font-size: 12px;
          color: var(--text-regular);
        }
      }
      
      .flow-arrow {
        font-size: 18px;
        color: var(--text-secondary);
      }
    }
  }
  
  .security-features {
    h4 {
      margin: 0 0 12px 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .security-list {
      margin: 0;
      padding-left: 20px;
      
      li {
        margin-bottom: 8px;
        font-size: 14px;
        color: var(--text-regular);
        line-height: 1.5;
      }
    }
  }
}

// 响应式适配
@media (max-width: 768px) {
  .participation-status-card {
    .status-item {
      padding: 16px;
      margin-bottom: 16px;
      
      .status-header {
        flex-direction: column;
        gap: 8px;
        
        .device-icons {
          order: -1;
        }
      }
      
      .status-value {
        .main-number {
          font-size: 24px;
        }
        
        .time-display {
          font-size: 20px;
        }
      }
      
      .status-detail {
        flex-direction: row;
        justify-content: space-around;
      }
    }
  }
  
  .privacy-card {
    .privacy-content {
      .privacy-actions {
        flex-direction: column;
        
        .el-button {
          width: 100%;
        }
      }
    }
  }
  
  .privacy-dialog-content {
    .flow-diagram {
      flex-direction: column;
      gap: 12px;
      
      .flow-arrow {
        transform: rotate(90deg);
      }
    }
  }
}
</style>








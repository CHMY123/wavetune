<template>
  <div class="federated-progress-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <el-page-header content="联邦学习模型训练进度" />
        <div class="round-info">
          <el-tag type="primary" size="large">当前轮次：3</el-tag>
          <span class="start-time">开始时间：2023-10-10 09:00</span>
        </div>
      </div>
    </div>

    <!-- 主要内容区 -->
    <el-row :gutter="20" class="main-content">
      <!-- 左侧：性能对比图表区 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <CardContainer title="历史轮次模型性能对比">
          <div class="chart-container">
            <div class="chart-placeholder">
              <div class="chart-title">准确率对比趋势图</div>
              <div class="chart-legend">
                <div class="legend-item">
                  <span class="legend-color local"></span>
                  <span class="legend-text">本地模型</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color global"></span>
                  <span class="legend-text">全局模型</span>
                </div>
              </div>
              <div class="chart-note">
                全局模型为联邦学习聚合后模型，本地模型为设备端独立训练模型
              </div>
            </div>
          </div>
        </CardContainer>
      </el-col>

      <!-- 右侧：训练日志区 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <CardContainer title="当前轮次训练日志">
          <el-scrollbar height="300px" class="log-scrollbar">
            <pre class="training-log">{{ trainingLog }}</pre>
          </el-scrollbar>
        </CardContainer>
      </el-col>
    </el-row>

    <!-- 性能指标卡片 -->
    <div class="metrics-section">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
          <CardContainer class="metric-card">
            <div class="metric-content">
              <div class="metric-icon accuracy">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-value">89.2%</div>
                <div class="metric-label">全局准确率</div>
              </div>
            </div>
          </CardContainer>
        </el-col>
        
        <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
          <CardContainer class="metric-card">
            <div class="metric-content">
              <div class="metric-icon loss">
                <el-icon><DataLine /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-value">0.21</div>
                <div class="metric-label">平均损失值</div>
              </div>
            </div>
          </CardContainer>
        </el-col>
        
        <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
          <CardContainer class="metric-card">
            <div class="metric-content">
              <div class="metric-icon devices">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-value">12</div>
                <div class="metric-label">参与设备数</div>
              </div>
            </div>
          </CardContainer>
        </el-col>
        
        <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
          <CardContainer class="metric-card">
            <div class="metric-content">
              <div class="metric-icon rounds">
                <el-icon><Refresh /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-value">3/10</div>
                <div class="metric-label">训练轮次</div>
              </div>
            </div>
          </CardContainer>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import CardContainer from '@/components/global/CardContainer.vue'
import { TrendCharts, DataLine, Monitor, Refresh } from '@element-plus/icons-vue'

export default {
  name: 'FederatedProgressView',
  components: {
    CardContainer,
    TrendCharts,
    DataLine,
    Monitor,
    Refresh
  },
  data() {
    return {
      trainingLog: `09:00:12 开始第 3 轮训练，参与设备 12 台
09:05:30 设备 ID:001 完成本地训练，损失值 0.23
09:10:15 设备 ID:003 完成本地训练，损失值 0.21
09:12:45 设备 ID:005 完成本地训练，损失值 0.19
09:15:40 开始模型参数聚合...
09:16:22 设备 ID:002 完成本地训练，损失值 0.24
09:17:55 设备 ID:004 完成本地训练，损失值 0.22
09:18:22 聚合完成，全局模型准确率提升至 89.2%
09:19:10 设备 ID:006 完成本地训练，损失值 0.20
09:20:35 开始分发更新后的全局模型参数
09:21:15 设备 ID:007 完成本地训练，损失值 0.18
09:22:00 所有设备已接收全局模型参数
09:22:30 设备 ID:008 完成本地训练，损失值 0.25
09:23:45 第 3 轮训练完成，准备开始第 4 轮
09:24:12 设备 ID:009 完成本地训练，损失值 0.17
09:25:00 开始第 4 轮训练，参与设备 12 台
09:26:30 设备 ID:010 完成本地训练，损失值 0.19
09:27:15 设备 ID:011 完成本地训练，损失值 0.16
09:28:00 设备 ID:012 完成本地训练，损失值 0.21
09:29:30 当前轮次训练进行中...`
    }
  }
}
</script>

<style lang="scss" scoped>
.federated-progress-view {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    
    :deep(.el-page-header__content) {
      font-size: 24px;
      font-weight: bold;
      color: var(--text-primary);
    }
    
    .round-info {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .start-time {
        font-size: 14px;
        color: var(--text-regular);
      }
    }
  }
}

.main-content {
  margin-bottom: 24px;
  
  .chart-container {
    height: 400px;
    
    .chart-placeholder {
      height: 100%;
      background: #f8f9fa;
      border: 2px dashed #d9d9d9;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
      
      .chart-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 20px;
      }
      
      .chart-legend {
        display: flex;
        gap: 24px;
        margin-bottom: 20px;
        
        .legend-item {
          display: flex;
          align-items: center;
          gap: 8px;
          
          .legend-color {
            width: 16px;
            height: 3px;
            border-radius: 2px;
            
            &.local {
              background: var(--el-color-warning);
            }
            
            &.global {
              background: var(--el-color-primary);
            }
          }
          
          .legend-text {
            font-size: 14px;
            color: var(--text-regular);
          }
        }
      }
      
      .chart-note {
        font-size: 12px;
        color: var(--text-secondary);
        text-align: center;
        line-height: 1.5;
        max-width: 300px;
      }
    }
  }
  
  .log-scrollbar {
    border: 1px solid #e5e6eb;
    border-radius: 4px;
    
    .training-log {
      margin: 0;
      padding: 16px;
      font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace;
      font-size: 12px;
      line-height: 1.6;
      color: var(--text-regular);
      background: #fafafa;
      white-space: pre-wrap;
      word-wrap: break-word;
      
      // 最新日志行样式
      &::after {
        content: "";
        display: block;
        margin-top: 8px;
        padding: 8px;
        background: #e6f7ff;
        border-left: 3px solid var(--el-color-primary);
        color: var(--el-color-primary);
        font-weight: 500;
      }
    }
  }
}

.metrics-section {
  .metric-card {
    height: 120px;
    
    .metric-content {
      display: flex;
      align-items: center;
      gap: 16px;
      height: 100%;
      
      .metric-icon {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: white;
        
        &.accuracy {
          background: linear-gradient(135deg, #52c41a, #73d13d);
        }
        
        &.loss {
          background: linear-gradient(135deg, #fa8c16, #ffa940);
        }
        
        &.devices {
          background: linear-gradient(135deg, #1890ff, #40a9ff);
        }
        
        &.rounds {
          background: linear-gradient(135deg, #722ed1, #9254de);
        }
      }
      
      .metric-info {
        flex: 1;
        
        .metric-value {
          font-size: 24px;
          font-weight: bold;
          color: var(--text-primary);
          margin-bottom: 4px;
          font-family: 'SF Mono', Monaco, monospace;
        }
        
        .metric-label {
          font-size: 14px;
          color: var(--text-regular);
        }
      }
    }
  }
}

// 响应式适配
@media (max-width: 768px) {
  .page-header {
    .header-content {
      flex-direction: column;
      align-items: flex-start;
      
      .round-info {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
      }
    }
  }
  
  .main-content {
    .chart-container {
      height: 300px;
      margin-bottom: 20px;
      
      .chart-placeholder {
        padding: 16px;
        
        .chart-title {
          font-size: 16px;
          margin-bottom: 16px;
        }
        
        .chart-legend {
          flex-direction: column;
          gap: 12px;
          margin-bottom: 16px;
        }
      }
    }
  }
  
  .metrics-section {
    .metric-card {
      height: 100px;
      margin-bottom: 16px;
      
      .metric-content {
        .metric-icon {
          width: 50px;
          height: 50px;
          font-size: 20px;
        }
        
        .metric-info {
          .metric-value {
            font-size: 20px;
          }
          
          .metric-label {
            font-size: 13px;
          }
        }
      }
    }
  }
}

@media (max-width: 480px) {
  .metrics-section {
    .metric-card {
      .metric-content {
        .metric-icon {
          width: 40px;
          height: 40px;
          font-size: 18px;
        }
        
        .metric-info {
          .metric-value {
            font-size: 18px;
          }
          
          .metric-label {
            font-size: 12px;
          }
        }
      }
    }
  }
}
</style>








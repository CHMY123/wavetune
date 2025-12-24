<template>
  <div class="signal-monitor-view">
    <!-- 顶部区域 -->
    <div class="top-section">
      <div class="header-content">
        <el-page-header content="多模态生理信号实时监测" class="page-title" />
        <div class="status-info">
          <el-tag type="success" size="large">监测中</el-tag>
          <span class="device-status">设备已连接</span>
        </div>
      </div>
      <p class="monitor-info">
        当前监测信号：EEG、EOG、HRV、呼吸频率
      </p>
    </div>

    <!-- 中部主体区：信号监测模块 -->
    <div class="signal-modules">
      <el-row :gutter="16">
        <el-col 
          v-for="signal in signalModules" 
          :key="signal.type"
          :xs="24" 
          :sm="24" 
          :md="12" 
          :lg="12" 
          :xl="12"
        >
          <el-card class="signal-card" :class="signal.status">
            <template #header>
              <div class="card-header">
                <span class="signal-name">{{ signal.name }}</span>
                <el-badge 
                  :type="signal.status === 'normal' ? 'success' : 'danger'" 
                  :value="signal.status === 'normal' ? '正常' : '异常'"
                />
              </div>
            </template>
            
            <!-- 核心数值与状态 -->
            <div class="signal-data">
              <div class="data-value">
                <span class="value-text">{{ signal.value }}</span>
                <span class="value-unit">{{ signal.unit }}</span>
              </div>
              <div class="reference-range">
                {{ signal.range }}
              </div>
            </div>
            
            <!-- 简化波形图 -->
            <div class="waveform-container">
              <svg class="waveform" :viewBox="`0 0 400 120`">
                <!-- 参考线 -->
                <line x1="0" y1="30" x2="400" y2="30" stroke="#ddd" stroke-dasharray="2,2" />
                <line x1="0" y1="60" x2="400" y2="60" stroke="#ddd" stroke-dasharray="2,2" />
                <line x1="0" y1="90" x2="400" y2="90" stroke="#ddd" stroke-dasharray="2,2" />
                
                <!-- 波形路径 -->
                <path 
                  :d="signal.waveform" 
                  :stroke="signal.color" 
                  stroke-width="2" 
                  fill="none"
                  class="waveform-path"
                />
              </svg>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 底部区域 -->
    <div class="bottom-section">
      <div class="timeline-section">
        <div class="timeline-header">
          <span class="timeline-title">监测时间轴</span>
          <span class="current-time">当前时间: 00:03</span>
        </div>
        <div class="timeline">
          <div class="time-marks">
            <span 
              v-for="time in timeMarks" 
              :key="time"
              class="time-mark"
              :class="{ 'current': time === '00:03' }"
            >
              {{ time }}
            </span>
          </div>
          <div class="timeline-progress">
            <div class="progress-line"></div>
            <div class="current-indicator" style="left: 60%"></div>
          </div>
        </div>
      </div>
      
      <div class="action-buttons">
        <el-button type="default" size="large">
          <el-icon><VideoPause /></el-icon>
          暂停监测
        </el-button>
        <el-button type="primary" size="large">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>

        <!-- CSV 上传用于脑疲劳检测 -->
        <input
          ref="csvInput"
          type="file"
          accept=".csv"
          style="display: none"
          @change="onFileChange"
        />

        <el-button
          type="info"
          size="large"
          @click="chooseFile"
          style="margin-left: 12px"
        >
          选择 CSV
        </el-button>

        <el-button
          :disabled="!selectedFile"
          :loading="detecting"
          type="success"
          size="large"
          @click="uploadCsvForDetection"
        >
          上传检测
        </el-button>

        <div class="detection-result" v-if="detectionResult" style="margin-left:12px; display:flex; align-items:center; gap:8px">
          <el-tag :type="detectionResult.type || 'warning'">检测：{{ detectionResult.label_name }}</el-tag>
          <span class="prob">概率: {{ detectionResult.probabilities.map(p => p.toFixed(3)).join(' / ') }}</span>

          <!-- 当检测为中/高疲劳时，显示查看推荐的按钮（占位行为，可跳转或展开推荐面板） -->
          <el-button
            v-if="detectionResult.label_name === 'Medium' || detectionResult.label_name === 'High'"
            type="primary"
            size="small"
            @click="showRecommendations"
          >查看推荐音乐</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { VideoPause, Download } from '@element-plus/icons-vue'
import { requestMethod } from '@/utils/request'
import { ElMessage } from 'element-plus'

export default {
  name: 'SignalMonitorView',
  components: {
    VideoPause,
    Download
  },
  data() {
    return {
      signalModules: [
        {
          type: 'EEG',
          name: 'EEG 脑电信号',
          value: '4.2',
          unit: 'μV²',
          range: '正常范围：5-8 μV²',
          status: 'warning',
          color: '#1890ff',
          waveform: 'M0,60 Q50,20 100,60 T200,60 T300,60 T400,60'
        },
        {
          type: 'EOG',
          name: 'EOG 眼电信号',
          value: '18.5',
          unit: '次/分',
          range: '正常范围：15-20 次/分',
          status: 'normal',
          color: '#722ed1',
          waveform: 'M0,60 Q100,30 200,60 Q300,90 400,60'
        },
        {
          type: 'HRV',
          name: '心率变异性',
          value: '32.4',
          unit: 'ms',
          range: '正常范围：30-50 ms',
          status: 'normal',
          color: '#52c41a',
          waveform: 'M0,60 Q50,40 100,60 Q150,80 200,60 Q250,40 300,60 Q350,80 400,60'
        },
        {
          type: 'RESP',
          name: '呼吸频率',
          value: '16.2',
          unit: '次/分',
          range: '正常范围：12-20 次/分',
          status: 'normal',
          color: '#fa8c16',
          waveform: 'M0,60 Q100,40 200,60 Q300,80 400,60'
        }
      ],
      // CSV 上传与检测相关状态
      selectedFileName: '',
      selectedFile: null,
      detecting: false,
      detectionResult: null,
      timeMarks: ['00:00', '00:01', '00:02', '00:03', '00:04', '00:05']
    }
  },

  methods: {
      chooseFile() {
        // 触发隐藏的 file input
        this.$refs.csvInput && this.$refs.csvInput.click()
      },
      onFileChange(e) {
        const files = e.target.files || e.dataTransfer?.files
        if (!files || !files.length) {
          this.selectedFile = null
          this.selectedFileName = ''
          return
        }
        const f = files[0]
        this.selectedFile = f
        this.selectedFileName = f.name
      },
      async uploadCsvForDetection() {
        if (!this.selectedFile) {
          ElMessage.warning('请先选择一个 CSV 文件')
          return
        }

        const form = new FormData()
        form.append('file', this.selectedFile)

        this.detecting = true
        this.detectionResult = null
        try {
          // 使用 request.js 的 postForm 发送 multipart/form-data
          const res = await requestMethod.postForm('/detection/upload', form)
          // request 的响应拦截器会返回 res（包含 code/msg/data）
          const payload = res.data || {}
          this.detectionResult = {
            label: payload.label,
            label_name: payload.label_name || payload.labelName || 'Unknown',
            probabilities: payload.probabilities || payload.probs || [],
            type: (payload.label_name === 'High' ? 'danger' : (payload.label_name === 'Medium' ? 'warning' : 'success'))
          }
          ElMessage.success(`检测完成：${this.detectionResult.label_name}`)
        } catch (err) {
          // request 已在拦截器中显示错误消息，这里可做额外提示
          console.error('uploadCsvForDetection error', err)
          ElMessage.error('上传或检测失败，请检查文件格式（20×20）并重试')
        } finally {
          this.detecting = false
        }
      },
      showRecommendations() {
        // 占位：根据项目路由结构可跳转到推荐页或展开推荐面板
        // 这里示例跳转到 /music-recommendation（如存在）
        try {
          // 在跳转前将当前检测等级写入 localStorage，供推荐页固定使用
          if (this.detectionResult && this.detectionResult.label_name) {
            try { localStorage.setItem('current_fatigue_level', this.detectionResult.label_name) } catch (e) {}
          }
          this.$router && this.$router.push({ path: '/music-recommendation' })
        } catch (e) {
          // 如果路由不存在则提示
          ElMessage.info('请在推荐页面查看推荐列表')
        }
      }
    }
  }
</script>

<style lang="scss" scoped>
.signal-monitor-view {
  background: #f0f2f5;
  min-height: 100vh;
  padding: var(--spacing-page);
}

.top-section {
  background: var(--bg-card);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    
    .page-title {
      margin: 0;
      
      :deep(.el-page-header__content) {
        font-size: 24px;
        font-weight: bold;
        color: var(--text-primary);
      }
    }
    
    .status-info {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .device-status {
        font-size: 14px;
        color: var(--text-secondary);
      }
    }
  }
  
  .monitor-info {
    margin: 0;
    font-size: 14px;
    color: var(--text-regular);
  }
}

.signal-modules {
  margin-bottom: 20px;
  
  .signal-card {
    height: 240px;
    margin-bottom: 20px;
    border-left: 4px solid;
    transition: box-shadow 0.3s ease;
    
    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }
    
    &.normal {
      border-left-color: var(--el-color-success);
    }
    
    &.warning {
      border-left-color: var(--el-color-warning);
    }
    
    &.danger {
      border-left-color: var(--el-color-danger);
    }
    
    :deep(.el-card__header) {
      padding: 16px 20px;
      background: #fafafa;
      border-bottom: 1px solid #f0f0f0;
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .signal-name {
          font-size: 16px;
          font-weight: 600;
          color: var(--text-primary);
        }
      }
    }
    
    :deep(.el-card__body) {
      padding: 16px 20px;
      height: calc(100% - 57px);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    
    .signal-data {
      .data-value {
        display: flex;
        align-items: baseline;
        gap: 4px;
        margin-bottom: 8px;
        
        .value-text {
          font-size: 24px;
          font-weight: bold;
          color: var(--text-primary);
          font-family: 'SF Mono', Monaco, monospace;
        }
        
        .value-unit {
          font-size: 14px;
          color: var(--text-secondary);
        }
      }
      
      .reference-range {
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
    
    .waveform-container {
      height: 120px;
      background: #fafafa;
      border-radius: 4px;
      padding: 8px;
      
      .waveform {
        width: 100%;
        height: 100%;
        
        .waveform-path {
          filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
        }
      }
    }
  }
}

.bottom-section {
  background: var(--bg-card);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  
  .timeline-section {
    margin-bottom: 20px;
    
    .timeline-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      
      .timeline-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .current-time {
        font-size: 14px;
        color: var(--text-regular);
        font-family: 'SF Mono', Monaco, monospace;
      }
    }
    
    .timeline {
      position: relative;
      height: 30px;
      
      .time-marks {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        
        .time-mark {
          font-size: 12px;
          color: var(--text-secondary);
          font-family: 'SF Mono', Monaco, monospace;
          
          &.current {
            color: var(--el-color-danger);
            font-weight: bold;
          }
        }
      }
      
      .timeline-progress {
        position: relative;
        height: 4px;
        background: #e8e8e8;
        border-radius: 2px;
        
        .progress-line {
          height: 100%;
          background: var(--el-color-primary);
          border-radius: 2px;
          width: 60%;
        }
        
        .current-indicator {
          position: absolute;
          top: -6px;
          width: 2px;
          height: 16px;
          background: var(--el-color-danger);
          border-radius: 1px;
        }
      }
    }
  }
  
  .action-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}

// 响应式适配
@media (max-width: 768px) {
  .signal-monitor-view {
    padding: 16px;
  }
  
  .top-section {
    padding: 16px;
    
    .header-content {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }
  }
  
  .signal-modules {
    .signal-card {
      height: 200px;
      
      .signal-data {
        .data-value {
          .value-text {
            font-size: 20px;
          }
        }
      }
      
      .waveform-container {
        height: 100px;
      }
    }
  }
  
  .bottom-section {
    padding: 16px;
    
    .action-buttons {
      flex-direction: column;
      
      .el-button {
        width: 100%;
      }
    }
  }
}

@media (max-width: 480px) {
  .signal-modules {
    .signal-card {
      height: 180px;
      
      .signal-data {
        .data-value {
          .value-text {
            font-size: 18px;
          }
        }
      }
      
      .waveform-container {
        height: 80px;
      }
    }
  }
}
</style>








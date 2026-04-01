<template>
  <div class="federated-contribute-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <el-page-header content="联邦学习数据贡献" />
      <!-- 训练进度条 -->
        <div v-if="showProgress" class="progress-container">
          <el-progress 
            :percentage="trainingProgress" 
            :status="progressStatus"
            :format="formatProgress"
            :stroke-width="10"
            class="training-progress"
          />
          <div class="progress-info">
            <span class="progress-label">训练进度</span>
            <span class="progress-detail">{{ progressDetail }}</span>
          </div>
          <!-- 训练日志 -->
          <div class="training-logs" v-if="trainingLogs.length > 0">
            <h4 class="logs-title">训练日志</h4>
            <el-scrollbar height="200px" class="logs-container">
              <div v-for="(log, index) in trainingLogs" :key="index" class="log-item">
                <span class="log-time">{{ log.time }}</span>
                <span class="log-content">{{ log.content }}</span>
              </div>
            </el-scrollbar>
          </div>
        </div>
    </div>

    <!-- 数据贡献卡片 -->
    <CardContainer class="contribute-card">
      <div class="contribute-content">
        <!-- 上传区域 -->
        <div class="upload-section">
          <h3 class="section-title">
            <el-icon>
              <component :is="Upload" />
            </el-icon>
            上传CSV数据文件
          </h3>
          <div class="upload-container">
            <el-upload
              class="upload-demo"
              :action="''"
              :auto-upload="false"
              :on-change="handleFileChange"
              :show-file-list="true"
              accept=".csv"
              :limit="1"
            >
              <el-button type="primary" :disabled="loading">
                <el-icon>
                  <component :is="Plus" />
                </el-icon>
                选择CSV文件
              </el-button>
              <template #tip>
                <div class="el-upload__tip">
                  请上传包含生理数据的CSV文件
                </div>
              </template>
            </el-upload>
          </div>
        </div>

        <!-- 训练配置 -->
        <div class="config-section">
          <h3 class="section-title">
            <el-icon>
              <component :is="Setting" />
            </el-icon>
            训练配置
          </h3>
          <div class="config-form">
            <el-form-item label="训练轮次">
              <el-slider
                v-model="trainingRounds"
                :min="1"
                :max="10"
                :step="1"
                show-input
                :disabled="loading"
              />
              <div class="form-hint">建议设置为3-5轮，平衡训练效果和时间</div>
            </el-form-item>
            
            <!-- 疲劳状态选择 -->
            <el-form-item label="疲劳状态">
              <el-select v-model="selectedFatigueStatus" placeholder="请选择疲劳状态" :disabled="loading">
                <el-option label="静息态" value="静息态" />
                <el-option label="正常" value="正常" />
                <el-option label="轻度疲劳" value="轻度疲劳" />
                <el-option label="中度疲劳" value="中度疲劳" />
                <el-option label="重度疲劳" value="重度疲劳" />
                <el-option label="疲劳恢复期" value="疲劳恢复期" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </div>
        </div>

        <!-- 隐私说明 -->
        <div class="privacy-section">
          <h3 class="section-title">
            <el-icon>
              <component :is="Lock" />
            </el-icon>
            隐私保护说明
          </h3>
          <div class="privacy-content">
            <p>您的原始数据将仅在本地设备上处理，不会上传到服务器。</p>
            <p>我们只收集训练后的模型参数，用于联邦学习模型的聚合。</p>
            <p>所有数据传输均采用加密方式，确保您的隐私安全。</p>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-section">
          <el-button 
            type="primary" 
            :loading="loading" 
            @click="submitContribution"
            :disabled="!selectedFile || loading"
          >
            <el-icon>
              <component :is="Upload" />
            </el-icon>
            提交贡献
          </el-button>
          <el-button @click="resetForm" :disabled="loading">
            <el-icon>
              <component :is="Refresh" />
            </el-icon>
            重置
          </el-button>
        </div>
      </div>
    </CardContainer>

    <!-- 贡献记录 -->
    <CardContainer title="最近贡献记录" class="records-card">
      <div v-if="trainingRecords.length > 0" class="records-list">
        <el-table :data="trainingRecords" style="width: 100%">
          <el-table-column prop="client_id" label="客户端ID" width="200" />
          <el-table-column prop="rounds" label="训练轮次" width="100" />
          <el-table-column prop="accuracy" label="准确率" width="100">
            <template #default="scope">
              {{ (scope.row.accuracy * 100).toFixed(2) }}%
            </template>
          </el-table-column>
          <el-table-column prop="loss" label="损失值" width="100">
            <template #default="scope">
              {{ scope.row.loss ? scope.row.loss.toFixed(3) : 0 }}
            </template>
          </el-table-column>
          <el-table-column prop="training_time" label="训练时间" width="180">
            <template #default="scope">
              {{ formatTime(scope.row.training_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getTagType(scope.row.status)">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div v-else class="empty-records">
        <el-icon class="empty-icon">
          <component :is="Document" />
        </el-icon>
        <p>暂无贡献记录</p>
        <p class="empty-hint">上传数据并参与联邦学习后，这里会显示您的贡献记录</p>
      </div>
    </CardContainer>

    <!-- 成功提示 -->
    <el-dialog
      v-model="successDialogVisible"
      title="提交成功"
      width="400px"
    >
      <div class="success-content">
        <el-icon class="success-icon">
          <component :is="SuccessFilled" />
        </el-icon>
        <p>数据上传成功！</p>
        <p>训练时长较长，请耐心等待</p>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="successDialogVisible = false">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import CardContainer from '@/components/global/CardContainer.vue'
import { Upload, Plus, Setting, Lock, Refresh, Document, SuccessFilled } from '@element-plus/icons-vue'
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { requestMethod } from '@/utils/request'

export default {
  name: 'FederatedContributeView',
  components: {
    CardContainer,
    Upload,
    Plus,
    Setting,
    Lock,
    Refresh,
    Document,
    SuccessFilled
  },
  setup() {
    const selectedFile = ref(null)
    const trainingRounds = ref(3)
    const selectedFatigueStatus = ref('')
    const loading = ref(false)
    const successDialogVisible = ref(false)
    const trainingRecords = ref([])
    // 训练进度相关
    const showProgress = ref(false)
    const trainingProgress = ref(0)
    const progressStatus = ref('')
    const progressDetail = ref('')
    const currentTrainingId = ref(localStorage.getItem('currentTrainingId') || null)
    const pollingInterval = ref(null)
    const trainingLogs = ref(JSON.parse(localStorage.getItem('trainingLogs') || '[]'))

    // 处理文件选择
    const handleFileChange = (file) => {
      selectedFile.value = file.raw
    }

    // 提交贡献
    const submitContribution = async () => {
      if (!selectedFile.value) {
        ElMessage.error('请选择CSV文件')
        return
      }
      
      if (!selectedFatigueStatus.value) {
        ElMessage.error('请选择疲劳状态')
        return
      }

      loading.value = true
      try {
        const formData = new FormData()
        formData.append('file', selectedFile.value)
        formData.append('rounds', trainingRounds.value)
        formData.append('fatigue_status', selectedFatigueStatus.value)

        const response = await requestMethod.postForm('/federated/upload-data', formData)

        if (response.code === 200) {
          // 立即显示进度条
          showProgress.value = true
          trainingProgress.value = 0
          progressStatus.value = ''
          progressDetail.value = '准备上传...'
          currentTrainingId.value = response.data.training_id
          // 初始化训练日志
          trainingLogs.value = [{
            time: new Date().toLocaleTimeString(),
            content: '训练任务已启动，正在上传数据到云存储...'
          }, {
            time: new Date().toLocaleTimeString(),
            content: '正在从云存储下载数据到后端...'
          }, {
            time: new Date().toLocaleTimeString(),
            content: '正在准备训练环境...'
          }]
          // 保存到本地存储
          localStorage.setItem('currentTrainingId', response.data.training_id)
          localStorage.setItem('trainingLogs', JSON.stringify(trainingLogs.value))
          localStorage.setItem('showProgress', 'true')
          // 开始轮询训练状态
          pollTrainingStatus(response.data.training_id)
          // 重新加载训练记录
          loadTrainingRecords()
          
          // 严格3秒后显示成功对话框
          setTimeout(() => {
            successDialogVisible.value = true
            // 播放提示音
            playNotificationSound()
          }, 3000)
        } else {
          ElMessage.error(response.msg || '提交失败')
        }
      } catch (error) {
        console.error('提交贡献失败:', error)
        ElMessage.error('提交失败，请重试')
      } finally {
        loading.value = false
      }
    }

    // 重置表单
    const resetForm = () => {
      selectedFile.value = null
      trainingRounds.value = 3
      selectedFatigueStatus.value = ''
    }

    // 加载训练记录
    const loadTrainingRecords = async () => {
      try {
        const response = await requestMethod.get('/federated/training-records')
        if (response.code === 200) {
          trainingRecords.value = response.data.items || []
        }
      } catch (error) {
        console.error('加载训练记录失败:', error)
      }
    }

    // 获取状态标签类型
    const getTagType = (status) => {
      const typeMap = {
        pending: 'info',
        training: 'warning',
        completed: 'success',
        failed: 'danger'
      }
      return typeMap[status] || 'info'
    }

    // 获取状态文本
    const getStatusText = (status) => {
      const textMap = {
        pending: '等待中',
        training: '训练中',
        completed: '完成',
        failed: '失败'
      }
      return textMap[status] || status
    }

    // 格式化时间（直接使用北京时间）
    const formatTime = (timeStr) => {
      if (!timeStr) return ''
      const date = new Date(timeStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      const seconds = String(date.getSeconds()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    }

    // 格式化进度条显示
    const formatProgress = (percentage) => {
      return `${percentage.toFixed(2)}%`
    }

    // 轮询训练状态
    const pollTrainingStatus = (trainingId) => {
      let lastProgress = -1
      let lastMessage = ''
      let notificationShown = false
      
      pollingInterval.value = setInterval(async () => {
        try {
          const response = await requestMethod.get(`/federated/training-status/${trainingId}`)
          if (response.code === 200) {
            const data = response.data
            const currentProgress = data.progress || 0
            const currentMessage = data.message || ''
            
            // 更新进度和详情
            trainingProgress.value = currentProgress
            progressDetail.value = currentMessage
            
            // 添加日志（当进度或消息发生变化时）
            if (currentProgress !== lastProgress || currentMessage !== lastMessage) {
              trainingLogs.value.push({
                time: new Date().toLocaleTimeString(),
                content: `${currentMessage} (${currentProgress}%)`
              })
              // 限制日志数量，保持最新的20条
              if (trainingLogs.value.length > 20) {
                trainingLogs.value = trainingLogs.value.slice(-20)
              }
              // 保存到本地存储
              localStorage.setItem('trainingLogs', JSON.stringify(trainingLogs.value))
              localStorage.setItem('trainingProgress', currentProgress.toString())
              localStorage.setItem('progressDetail', currentMessage)
              lastProgress = currentProgress
              lastMessage = currentMessage
            }
            
            if (data.status === 'completed' && !notificationShown) {
              notificationShown = true
              progressStatus.value = 'success'
              // 添加完成日志
              trainingLogs.value.push({
                time: new Date().toLocaleTimeString(),
                content: '训练完成！模型训练成功。'
              })
              // 保存到本地存储
              localStorage.setItem('trainingLogs', JSON.stringify(trainingLogs.value))
              clearInterval(pollingInterval.value)
              setTimeout(() => {
                showProgress.value = false
                // 清除本地存储
                localStorage.removeItem('currentTrainingId')
                localStorage.removeItem('trainingLogs')
                localStorage.removeItem('showProgress')
                localStorage.removeItem('trainingProgress')
                localStorage.removeItem('progressDetail')
                // 显示全局通知
                showTrainingCompleteNotification()
              }, 1000)
            } else if (data.status === 'failed') {
              progressStatus.value = 'exception'
              // 添加失败日志
              trainingLogs.value.push({
                time: new Date().toLocaleTimeString(),
                content: '训练失败！请检查日志了解详情。'
              })
              // 保存到本地存储
              localStorage.setItem('trainingLogs', JSON.stringify(trainingLogs.value))
              clearInterval(pollingInterval.value)
              setTimeout(() => {
                showProgress.value = false
                // 清除本地存储
                localStorage.removeItem('currentTrainingId')
                localStorage.removeItem('trainingLogs')
                localStorage.removeItem('showProgress')
                localStorage.removeItem('trainingProgress')
                localStorage.removeItem('progressDetail')
              }, 1000)
            }
          }
        } catch (error) {
          console.error('轮询训练状态失败:', error)
          // 添加错误日志
          trainingLogs.value.push({
            time: new Date().toLocaleTimeString(),
            content: `轮询状态失败: ${error.message}`
          })
          if (pollingInterval.value) {
            clearInterval(pollingInterval.value)
          }
        }
      }, 2000)
    }

    // 播放提示音
    const playNotificationSound = () => {
      try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)()
        const oscillator = audioContext.createOscillator()
        const gainNode = audioContext.createGain()
        
        oscillator.connect(gainNode)
        gainNode.connect(audioContext.destination)
        
        oscillator.frequency.value = 600
        oscillator.type = 'sine'
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3)
        
        oscillator.start(audioContext.currentTime)
        oscillator.stop(audioContext.currentTime + 0.3)
      } catch (error) {
        console.warn('播放提示音失败:', error)
      }
    }

    // 显示训练完成通知
    const showTrainingCompleteNotification = () => {
      // 使用Web Audio API播放简单的通知音效
      try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)()
        const oscillator = audioContext.createOscillator()
        const gainNode = audioContext.createGain()
        
        oscillator.connect(gainNode)
        gainNode.connect(audioContext.destination)
        
        oscillator.frequency.value = 800
        oscillator.type = 'sine'
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5)
        
        oscillator.start(audioContext.currentTime)
        oscillator.stop(audioContext.currentTime + 0.5)
      } catch (error) {
        console.warn('播放音效失败:', error)
      }
      
      // 显示全局通知
      ElMessage({
        message: '您的联邦学习贡献已训练完成！点击查看训练结果',
        type: 'success',
        duration: 5000,
        showClose: true,
        onClick: () => {
          // 刷新训练记录
          loadTrainingRecords()
        }
      })
    }

    // 组件挂载时加载训练记录和恢复进度条状态
    onMounted(() => {
      loadTrainingRecords()
      
      // 从本地存储恢复进度条状态
      const savedTrainingId = localStorage.getItem('currentTrainingId')
      const savedShowProgress = localStorage.getItem('showProgress')
      
      if (savedTrainingId && savedShowProgress === 'true') {
        showProgress.value = true
        currentTrainingId.value = savedTrainingId
        trainingProgress.value = parseInt(localStorage.getItem('trainingProgress') || '0')
        progressDetail.value = localStorage.getItem('progressDetail') || '准备上传...'
        trainingLogs.value = JSON.parse(localStorage.getItem('trainingLogs') || '[]')
        // 继续轮询训练状态
        pollTrainingStatus(savedTrainingId)
      }
    })

    // 组件销毁时停止轮询
    onUnmounted(() => {
      if (pollingInterval.value) {
        clearInterval(pollingInterval.value)
      }
      // 隐藏进度条
      showProgress.value = false
    })

    return {
      selectedFile,
      trainingRounds,
      selectedFatigueStatus,
      loading,
      successDialogVisible,
      trainingRecords,
      handleFileChange,
      submitContribution,
      resetForm,
      getTagType,
      getStatusText,
      formatTime,
      formatProgress,
      showProgress,
      trainingProgress,
      progressStatus,
      progressDetail,
      trainingLogs,
      // 图标组件
      Upload,
      Plus,
      Setting,
      Lock,
      Refresh,
      Document,
      SuccessFilled
    }
  }
}
</script>

<style lang="scss" scoped>
.federated-contribute-view {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
  position: relative;
  
  :deep(.el-page-header__content) {
    font-size: 24px;
    font-weight: bold;
    color: var(--text-primary);
  }
  
  .progress-container {
    position: absolute;
    top: 0;
    right: 0;
    width: 300px;
    
    .training-progress {
      margin-bottom: 8px;
    }
    
    .progress-info {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      color: var(--text-secondary);
      
      .progress-label {
        font-weight: 500;
      }
      
      .progress-detail {
        color: var(--text-placeholder);
      }
    }
    
    .training-logs {
      margin-top: 16px;
      border: 1px solid #e8e8e8;
      border-radius: 8px;
      padding: 12px;
      background-color: #fafafa;
      
      .logs-title {
        margin: 0 0 12px 0;
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .logs-container {
        font-size: 12px;
        
        .log-item {
          display: flex;
          margin-bottom: 8px;
          line-height: 1.4;
          
          .log-time {
            width: 80px;
            color: var(--text-secondary);
            margin-right: 12px;
          }
          
          .log-content {
            flex: 1;
            color: var(--text-regular);
          }
        }
      }
    }
  }
}

.contribute-card {
  margin-bottom: 24px;
  
  .contribute-content {
    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .upload-section {
      margin-bottom: 24px;
      
      .upload-container {
        border: 2px dashed #d9d9d9;
        border-radius: 8px;
        padding: 40px;
        text-align: center;
        transition: all 0.3s;
        
        &:hover {
          border-color: var(--el-color-primary);
        }
      }
    }
    
    .config-section {
      margin-bottom: 24px;
      
      .config-form {
        .form-hint {
          margin-top: 8px;
          font-size: 12px;
          color: var(--text-secondary);
        }
      }
    }
    
    .privacy-section {
      margin-bottom: 24px;
      
      .privacy-content {
        background: #f8f9fa;
        padding: 16px;
        border-radius: 8px;
        
        p {
          margin: 0 0 8px 0;
          font-size: 14px;
          color: var(--text-regular);
          line-height: 1.5;
        }
        
        p:last-child {
          margin-bottom: 0;
        }
      }
    }
    
    .action-section {
      display: flex;
      gap: 12px;
      justify-content: center;
    }
  }
}

.records-card {
  .records-list {
    :deep(.el-table) {
      .el-table__row:hover {
        background-color: #f5f7fa;
      }
    }
  }
  
  .empty-records {
    text-align: center;
    padding: 60px 20px;
    color: var(--text-secondary);
    
    .empty-icon {
      font-size: 48px;
      color: var(--text-placeholder);
      margin-bottom: 16px;
    }
    
    p {
      margin: 0 0 8px 0;
      font-size: 16px;
      font-weight: 500;
      color: var(--text-regular);
    }
    
    .empty-hint {
      font-size: 14px;
      color: var(--text-secondary);
      margin-bottom: 0;
    }
  }
}

.success-content {
  text-align: center;
  padding: 20px 0;
  
  .success-icon {
    font-size: 48px;
    color: var(--el-color-success);
    margin-bottom: 16px;
  }
  
  p {
    margin: 0 0 8px 0;
    font-size: 16px;
    color: var(--text-primary);
  }
  
  p:last-child {
    margin-bottom: 0;
    font-size: 14px;
    color: var(--text-regular);
  }
}

// 响应式适配
@media (max-width: 768px) {
  .contribute-card {
    .contribute-content {
      .upload-section {
        .upload-container {
          padding: 20px;
        }
      }
      
      .action-section {
        flex-direction: column;
        
        .el-button {
          width: 100%;
        }
      }
    }
  }
  
  .records-card {
    :deep(.el-table) {
      font-size: 12px;
      
      .el-table__column {
        padding: 8px 0;
      }
    }
  }
}
</style>

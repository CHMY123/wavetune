<template>
  <div class="two-back-experiment">
    <el-card class="experiment-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>2-Back 疲劳诱发实验</span>
          <el-button 
            v-if="experimentState !== 'initial'" 
            type="danger" 
            size="small" 
            @click="exitExperiment"
          >
            退出实验
          </el-button>
        </div>
      </template>
      
      <!-- 错误提示 -->
      <el-alert 
        v-if="errorMessage" 
        :title="errorMessage" 
        type="error" 
        show-icon 
        closable 
        @close="errorMessage = ''" 
        class="error-alert"
      />
      
      <!-- 实验准备界面 -->
      <div v-if="experimentState === 'initial'" class="experiment-prepare">
        <h2>实验准备</h2>
        <p class="description">
          2-Back 实验是一种认知任务，用于评估工作记忆和注意力。在实验过程中，您将看到一系列字母，
          当当前字母与前两个位置的字母相同时，请按下空格键或点击"是"按钮。
        </p>
        
        <el-divider content-position="left">实验参数</el-divider>
        
        <el-form :model="experimentSettings" label-width="120px" class="settings-form">
          <el-form-item label="实验时长">
            <el-slider 
              v-model="experimentSettings.duration" 
              :min="5" 
              :max="30" 
              :step="5"
              show-input
            />
            <span class="unit">分钟</span>
          </el-form-item>
          
          <el-form-item label="每轮试次">
            <el-slider 
              v-model="experimentSettings.trialsPerBlock" 
              :min="10" 
              :max="50" 
              :step="5"
              show-input
            />
            <span class="unit">个</span>
          </el-form-item>
          
          <el-form-item label="实验轮数">
            <el-slider 
              v-model="experimentSettings.blockCount" 
              :min="1" 
              :max="5" 
              :step="1"
              show-input
            />
            <span class="unit">轮</span>
          </el-form-item>
          
          <el-form-item label="刺激时长">
            <el-slider 
              v-model="experimentSettings.stimulusDuration" 
              :min="500" 
              :max="2000" 
              :step="100"
              show-input
            />
            <span class="unit">毫秒</span>
          </el-form-item>
          
          <el-form-item label="间隔时长">
            <el-slider 
              v-model="experimentSettings.intervalDuration" 
              :min="500" 
              :max="2000" 
              :step="100"
              show-input
            />
            <span class="unit">毫秒</span>
          </el-form-item>
          
          <el-form-item label="休息时长">
            <el-slider 
              v-model="experimentSettings.breakDuration" 
              :min="30" 
              :max="300" 
              :step="30"
              show-input
            />
            <span class="unit">秒</span>
          </el-form-item>
          
          <el-form-item label="使用字母">
            <el-select 
              v-model="experimentSettings.letters" 
              multiple 
              placeholder="选择字母" 
              class="letters-select"
            >
              <el-option 
                v-for="letter in availableLetters" 
                :key="letter" 
                :label="letter" 
                :value="letter"
              />
            </el-select>
          </el-form-item>
        </el-form>
        
        <div class="start-button-container">
          <el-button 
            type="primary" 
            size="large" 
            @click="startExperiment"
            :loading="isStarting"
          >
            开始实验
          </el-button>
        </div>
      </div>
      
      <!-- 实验运行界面 -->
      <div v-if="experimentState === 'running'" class="experiment-running">
        <div class="experiment-header">
          <div class="experiment-info">
            <span>轮次: {{ currentRound }} / {{ experimentSettings.blockCount }}</span>
            <span>试次: {{ currentTrial }} / {{ experimentSettings.trialsPerBlock }}</span>
          </div>
          <div class="experiment-timer">
            {{ remainingTime }}s
          </div>
        </div>
        
        <!-- 刺激呈现区域 -->
        <div class="stimulus-container">
          <div v-if="showFeedback" class="feedback" :class="feedbackType">
            {{ feedbackMessage }}
          </div>
          <div v-else class="stimulus">
            {{ currentStimulus }}
          </div>
        </div>
        
        <!-- 响应按钮 -->
        <div class="response-buttons">
          <el-button 
            type="primary" 
            size="large" 
            @click="respond(true)"
            :disabled="showFeedback"
          >
            是
          </el-button>
          <el-button 
            type="info" 
            size="large" 
            @click="respond(false)"
            :disabled="showFeedback"
          >
            否
          </el-button>
        </div>
        
        <p class="response-hint">
          提示：当当前字母与前两个位置的字母相同时，请按下空格键或点击"是"按钮
        </p>
      </div>
      
      <!-- KSS 疲劳量表界面 -->
      <div v-if="experimentState === 'kss'" class="kss-container">
        <h2>KSS 疲劳量表</h2>
        <p class="description">
          请根据您当前的疲劳程度选择相应的评分（1-9分）：
        </p>
        
        <div class="kss-scale">
          <div 
            v-for="score in 9" 
            :key="score" 
            class="kss-item" 
            :class="{ active: selectedKssScore === score }"
            @click="selectKssScore(score)"
          >
            <div class="kss-score">{{ score }}</div>
            <div class="kss-description">{{ kssDescriptions[score - 1] }}</div>
          </div>
        </div>
        
        <div class="kss-button-container">
          <el-button 
            type="primary" 
            size="large" 
            @click="submitKssScore"
            :disabled="!selectedKssScore"
          >
            提交评分
          </el-button>
        </div>
      </div>
      
      <!-- 静息状态界面 -->
      <div v-if="experimentState === 'rest'" class="rest-container">
        <h2>静息状态</h2>
        <p class="description">
          请放松并保持安静，准备下一轮实验
        </p>
        
        <div class="rest-timer">
          <div class="timer-circle">
            <div class="timer-content">
              <div class="timer-number">{{ restRemainingTime }}</div>
              <div class="timer-unit">秒</div>
            </div>
          </div>
          <div class="timer-progress">
            <el-progress 
              :percentage="restTimerProgress" 
              :stroke-width="10" 
              status="success"
            />
          </div>
        </div>
      </div>
      
      <!-- 实验完成界面 -->
      <div v-if="experimentState === 'completed'" class="experiment-completed">
        <h2>实验完成</h2>
        <p class="description">
          您已成功完成 2-Back 疲劳诱发实验，以下是实验结果：
        </p>
        
        <el-divider content-position="left">实验结果</el-divider>
        
        <div class="results-container">
          <div class="result-item">
            <span class="result-label">总试次数：</span>
            <span class="result-value">{{ totalTrials }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">正确次数：</span>
            <span class="result-value">{{ correctTrials }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">错误次数：</span>
            <span class="result-value">{{ errorTrials }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">正确率：</span>
            <span class="result-value">{{ accuracyRate }}%</span>
          </div>
          <div class="result-item">
            <span class="result-label">平均反应时：</span>
            <span class="result-value">{{ averageResponseTime }}ms</span>
          </div>
        </div>
        
        <el-divider content-position="left">KSS 评分</el-divider>
        
        <div class="kss-results">
          <div 
            v-for="(score, index) in kssScores" 
            :key="index" 
            class="kss-result-item"
          >
            <span>轮次 {{ index + 1 }}：</span>
            <span class="kss-score-value">{{ score }}</span>
            <span class="kss-score-description">{{ kssDescriptions[score - 1] }}</span>
          </div>
        </div>
        
        <div class="completed-buttons">
          <el-button 
            type="primary" 
            @click="viewDetailedResults"
          >
            查看详细结果
          </el-button>
          <el-button 
            @click="exitExperiment"
          >
            退出实验
          </el-button>
        </div>
      </div>
      
      <!-- 实验结果界面 -->
      <div v-if="experimentState === 'result'" class="experiment-result">
        <h2>实验详细结果</h2>
        
        <el-divider content-position="left">基本信息</el-divider>
        
        <el-table :data="experimentSummary" style="width: 100%" class="summary-table">
          <el-table-column prop="key" label="项目" width="180" />
          <el-table-column prop="value" label="值" />
        </el-table>
        
        <div class="result-buttons">
          <el-button 
            type="primary" 
            @click="exportResults"
          >
            导出结果
          </el-button>
          <el-button 
            @click="exitExperiment"
          >
            返回主页
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'TwoBackExperimentView',
  data() {
    return {
      // 实验状态：initial, running, kss, rest, completed, result
      experimentState: 'initial',
      // 实验设置
      experimentSettings: {
        duration: 10,
        trialsPerBlock: 20,
        blockCount: 2,
        stimulusDuration: 1000,
        intervalDuration: 1000,
        breakDuration: 60,
        letters: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
      },
      // 可用字母
      availableLetters: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T'],
      // 实验数据
      currentRound: 1,
      currentTrial: 0,
      stimulusSequence: [],
      isTargetSequence: [],
      responses: [],
      responseTimes: [],
      // 当前状态
      currentStimulus: '',
      showFeedback: false,
      feedbackMessage: '',
      feedbackType: '',
      // 计时器
      trialTimer: null,
      restTimer: null,
      experimentTimer: null,
      remainingTime: 0,
      restRemainingTime: 0,
      restTimerProgress: 0,
      // KSS 评分
      selectedKssScore: null,
      kssScores: [],
      kssDescriptions: [
        '非常警觉',
        '警觉',
        '有些警觉',
        '既不警觉也不困倦',
        '有些困倦',
        '困倦',
        '非常困倦',
        '非常非常困倦',
        '即将入睡'
      ],
      // 实验结果
      totalTrials: 0,
      correctTrials: 0,
      errorTrials: 0,
      accuracyRate: 0,
      averageResponseTime: 0,
      experimentSummary: [],
      // 加载状态
      isLoading: false,
      isStarting: false,
      // 错误信息
      errorMessage: '',
      // 会话信息
      sessionId: '',
      participantId: ''
    }
  },
  mounted() {
    // 绑定键盘事件
    window.addEventListener('keydown', this.handleKeydown, { passive: false })
  },
  beforeUnmount() {
    // 解绑键盘事件
    window.removeEventListener('keydown', this.handleKeydown)
    // 清除所有定时器
    this.clearAllTimers()
  },
  methods: {
    // 处理键盘事件
    handleKeydown(event) {
      if (this.experimentState === 'running' && !this.showFeedback) {
        if (event.code === 'Space' || event.key === ' ') {
          event.preventDefault()
          this.respond(true)
        }
      }
    },
    
    // 开始实验
    async startExperiment() {
      this.isStarting = true
      try {
        // 尝试从缓存加载刺激序列
        const cacheKey = `two_back_sequence_${this.experimentSettings.trialsPerBlock}_${this.experimentSettings.blockCount}`
        try {
          const cachedData = localStorage.getItem(cacheKey)
          if (cachedData) {
            const parsedData = JSON.parse(cachedData)
            // 检查缓存是否过期（24小时）
            if (parsedData.timestamp && (Date.now() - parsedData.timestamp) < 24 * 60 * 60 * 1000) {
              this.stimulusSequence = parsedData.sequence
              this.isTargetSequence = parsedData.targets
              console.log('从缓存加载刺激序列')
              
              // 初始化实验会话 - 增加超时时间到30秒
              const initResponse = await this.$axios.post('/api/detection/two-back/init', this.experimentSettings, {
                timeout: 30000
              })
              console.log('初始化实验 - 响应:', initResponse.data)
              if (initResponse.data.code === 200) {
                this.sessionId = initResponse.data.data.session_id
                this.participantId = initResponse.data.data.participant_id
                console.log('初始化实验 - 会话 ID:', this.sessionId)
                
                // 开始实验
                this.experimentState = 'running'
                this.startTrial()
                this.isStarting = false
                return
              } else {
                this.errorMessage = '初始化实验失败'
              }
            }
          }
        } catch (e) {
          console.warn('缓存读取失败:', e)
        }
        
        // 初始化实验会话 - 增加超时时间到30秒
        const initResponse = await this.$axios.post('/api/detection/two-back/init', this.experimentSettings, {
          timeout: 30000
        })
        console.log('初始化实验 - 响应:', initResponse.data)
        if (initResponse.data.code === 200) {
          this.sessionId = initResponse.data.data.session_id
          this.participantId = initResponse.data.data.participant_id
          console.log('初始化实验 - 会话 ID:', this.sessionId)
          
          // 生成刺激序列 - 增加超时时间到30秒
          const sequenceResponse = await this.$axios.post('/api/detection/two-back/generate-sequence', {
            trials: this.experimentSettings.trialsPerBlock * this.experimentSettings.blockCount,
            match_rate: 0.28,
            letters: this.experimentSettings.letters
          }, {
            timeout: 30000
          })
          
          if (sequenceResponse.data.code === 200) {
            this.stimulusSequence = sequenceResponse.data.data.sequence
            this.isTargetSequence = sequenceResponse.data.data.targets
            
            // 缓存刺激序列
            try {
              localStorage.setItem(cacheKey, JSON.stringify({
                sequence: this.stimulusSequence,
                targets: this.isTargetSequence,
                timestamp: Date.now()
              }))
            } catch (e) {
              console.warn('缓存保存失败:', e)
            }
            
            // 开始实验
            this.experimentState = 'running'
            this.startTrial()
          } else {
            this.errorMessage = '生成刺激序列失败'
          }
        } else {
          this.errorMessage = '初始化实验失败'
        }
      } catch (error) {
        console.error('开始实验失败:', error)
        if (error.code === 'ECONNABORTED') {
          this.errorMessage = '连接服务器超时，请检查后端服务是否正常运行'
        } else if (error.response) {
          this.errorMessage = `服务器错误: ${error.response.status} - ${error.response.data?.message || '未知错误'}`
        } else if (error.request) {
          this.errorMessage = '无法连接到服务器，请检查网络连接'
        } else {
          this.errorMessage = '开始实验失败，请稍后重试'
        }
      } finally {
        this.isStarting = false
      }
    },
    
    // 开始试次
    startTrial() {
      if (this.currentTrial >= this.experimentSettings.trialsPerBlock) {
        // 当前轮次完成，进入 KSS 评分
        this.currentTrial = 0
        this.experimentState = 'kss'
        return
      }
      
      // 重置反馈状态
      this.showFeedback = false
      this.feedbackMessage = ''
      this.feedbackType = ''
      
      // 获取当前刺激
      const trialIndex = (this.currentRound - 1) * this.experimentSettings.trialsPerBlock + this.currentTrial
      this.currentStimulus = this.stimulusSequence[trialIndex]
      this.currentTrial++
      
      // 开始计时
      this.remainingTime = (this.experimentSettings.stimulusDuration + this.experimentSettings.intervalDuration) / 1000
      this.updateTimer()
      
      // 设置反馈定时器
      setTimeout(() => {
        if (!this.showFeedback) {
          this.respond(false)
        }
      }, this.experimentSettings.stimulusDuration)
    },
    
    // 更新计时器
    updateTimer() {
      clearInterval(this.trialTimer)
      this.trialTimer = setInterval(() => {
        this.remainingTime--
        if (this.remainingTime <= 0) {
          clearInterval(this.trialTimer)
        }
      }, 1000)
    },
    
    // 响应
    async respond(isMatch) {
      if (this.showFeedback) return
      
      // 计算反应时
      const responseTime = (this.experimentSettings.stimulusDuration - this.remainingTime * 1000) / 1000
      
      // 检查是否正确
      const trialIndex = (this.currentRound - 1) * this.experimentSettings.trialsPerBlock + this.currentTrial - 1
      const isTarget = this.isTargetSequence[trialIndex]
      const isCorrect = isMatch === isTarget
      
      // 记录响应
      this.responses.push(isCorrect)
      this.responseTimes.push(responseTime)
      
      // 显示反馈
      this.showFeedback = true
      this.feedbackMessage = isCorrect ? '正确!' : '错误!'
      this.feedbackType = isCorrect ? 'correct' : 'incorrect'
      
      // 记录试次数据
      try {
        console.log('记录试次 - sessionId:', this.sessionId)
        const trialData = {
          trial_id: `trial_${Date.now()}`,
          trial_index: trialIndex,
          stimulus: this.currentStimulus,
          is_target: isTarget,
          key_pressed: isMatch,
          response_time: responseTime,
          is_hit: isCorrect && isTarget,
          is_false_alarm: !isCorrect && !isTarget,
          is_miss: !isCorrect && isTarget,
          is_correct_reject: isCorrect && !isTarget,
          timestamp: new Date().toISOString(),
          block_num: this.currentRound
        }
        
        console.log('记录试次 - 请求数据:', {
          session_id: this.sessionId,
          trial_data: trialData
        })
        
        const response = await this.$axios.post('/api/detection/two-back/record-trial', {
          session_id: this.sessionId,
          trial_data: trialData
        })
        console.log('记录试次 - 响应:', response.data)
        if (response.data.code !== 200) {
          console.error('记录试次失败:', response.data.msg)
        }
      } catch (error) {
        console.error('记录试次失败:', error)
        if (error.response) {
          console.error('记录试次失败 - 响应:', error.response.data)
        }
      }
      
      // 延迟后进入下一个试次
      setTimeout(() => {
        this.startTrial()
      }, this.experimentSettings.intervalDuration)
    },
    
    // 选择 KSS 评分
    selectKssScore(score) {
      this.selectedKssScore = score
    },
    
    // 提交 KSS 评分
    async submitKssScore() {
      if (this.selectedKssScore) {
        try {
          // 记录 KSS 评分
          const response = await this.$axios.post('/api/detection/two-back/record-kss', {
            session_id: this.sessionId,
            round: this.currentRound - 1,
            score: this.selectedKssScore
          })
          
          if (response.data.code === 200) {
            this.kssScores.push(this.selectedKssScore)
            // 进入静息状态
            this.experimentState = 'rest'
            this.resetRestState()
          }
        } catch (error) {
          console.error('提交 KSS 评分失败:', error)
          // 即使失败也继续实验流程
          this.kssScores.push(this.selectedKssScore)
          this.experimentState = 'rest'
          this.resetRestState()
        }
      }
    },
    
    // 重置静息状态
    resetRestState() {
      this.restRemainingTime = this.experimentSettings.breakDuration
      this.restTimerProgress = 0
      this.startRestTimer()
    },
    
    // 开始静息定时器
    startRestTimer() {
      clearInterval(this.restTimer)
      this.restTimer = setInterval(() => {
        this.restRemainingTime--
        this.restTimerProgress = Math.round(((this.experimentSettings.breakDuration - this.restRemainingTime) / this.experimentSettings.breakDuration) * 100)
        
        if (this.restRemainingTime <= 0) {
          clearInterval(this.restTimer)
          this.currentRound++
          
          if (this.currentRound > this.experimentSettings.blockCount) {
            // 所有轮次完成，进入实验完成状态
            this.completeExperiment()
          } else {
            // 开始下一轮实验
            this.experimentState = 'running'
            this.startTrial()
          }
        }
      }, 1000)
    },
    
    // 完成实验
    async completeExperiment() {
      try {
        // 计算实验结果
        this.calculateResults()
        
        // 完成实验
        const response = await this.$axios.post('/api/detection/two-back/complete', {
          session_id: this.sessionId
        })
        
        if (response.data.code === 200) {
          const analysisResult = response.data.data
          this.processExperimentResults(analysisResult)
        }
      } catch (error) {
        console.error('完成实验失败:', error)
        // 即使失败也显示结果页面
        this.calculateResults()
      } finally {
        this.experimentState = 'result'
      }
    },
    
    // 计算实验结果
    calculateResults() {
      this.totalTrials = this.responses.length
      this.correctTrials = this.responses.filter(r => r).length
      this.errorTrials = this.totalTrials - this.correctTrials
      this.accuracyRate = Math.round((this.correctTrials / this.totalTrials) * 100)
      this.averageResponseTime = Math.round(this.responseTimes.reduce((a, b) => a + b, 0) / this.responseTimes.length * 1000)
      
      // 生成实验摘要
      this.experimentSummary = [
        { key: '总试次数', value: this.totalTrials },
        { key: '正确次数', value: this.correctTrials },
        { key: '错误次数', value: this.errorTrials },
        { key: '正确率', value: `${this.accuracyRate}%` },
        { key: '平均反应时', value: `${this.averageResponseTime}ms` },
        { key: '实验时长', value: `${this.experimentSettings.duration}分钟` },
        { key: '实验轮数', value: this.experimentSettings.blockCount },
        { key: '每轮试次数', value: this.experimentSettings.trialsPerBlock }
      ]
    },
    
    // 处理实验结果
    processExperimentResults(analysisResult) {
      // 这里可以处理后端返回的分析结果
      console.log('分析结果:', analysisResult)
    },
    
    // 查看详细结果
    viewDetailedResults() {
      this.experimentState = 'result'
    },
    
    // 导出结果
    exportResults() {
      // 这里可以实现结果导出功能
      const results = {
        summary: this.experimentSummary,
        responses: this.responses,
        responseTimes: this.responseTimes,
        kssScores: this.kssScores,
        settings: this.experimentSettings
      }
      
      // 转换为 JSON 字符串
      const jsonStr = JSON.stringify(results, null, 2)
      
      // 创建下载链接
      const blob = new Blob([jsonStr], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `two-back-results-${Date.now()}.json`
      a.click()
      
      // 清理
      URL.revokeObjectURL(url)
    },
    
    // 退出实验
    exitExperiment() {
      // 清除所有定时器
      this.clearAllTimers()
      
      // 跳转到选择页面
      this.$router.push('/quick-detection')
    },
    
    // 清除所有定时器
    clearAllTimers() {
      if (this.trialTimer) {
        clearInterval(this.trialTimer)
      }
      if (this.restTimer) {
        clearInterval(this.restTimer)
      }
      if (this.experimentTimer) {
        clearInterval(this.experimentTimer)
      }
    }
  }
}
</script>

<style scoped>
.two-back-experiment {
  min-height: calc(100vh - 60px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background-color: #f5f7fa;
  background-image: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.experiment-card {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.experiment-card:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
  color: #333;
  padding: 20px 24px;
  background-color: #f9f9f9;
  border-bottom: 1px solid #eaeaea;
}

.card-header .el-button {
  transition: all 0.3s ease;
}

.card-header .el-button:hover {
  transform: scale(1.05);
}

/* 错误提示 */
.error-alert {
  margin: 20px;
  animation: slideIn 0.5s ease-out;
}

/* 实验准备界面 */
.experiment-prepare {
  padding: 30px;
  animation: fadeInUp 0.6s ease-out;
}

.experiment-prepare h2 {
  margin-bottom: 24px;
  color: #333;
  font-size: 28px;
  font-weight: bold;
  position: relative;
  display: inline-block;
}

.experiment-prepare h2::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 0;
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 2px;
}

.experiment-prepare .description {
  margin-bottom: 36px;
  color: #666;
  line-height: 1.6;
  font-size: 18px;
}

.settings-form {
  margin-bottom: 48px;
  padding: 28px;
  background: linear-gradient(135deg, #f9f9f9, #f0f0f0);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.settings-form .el-form-item {
  margin-bottom: 24px;
  animation: fadeInUp 0.6s ease-out;
}

.settings-form .el-form-item:nth-child(1) { animation-delay: 0.1s; }
.settings-form .el-form-item:nth-child(2) { animation-delay: 0.2s; }
.settings-form .el-form-item:nth-child(3) { animation-delay: 0.3s; }
.settings-form .el-form-item:nth-child(4) { animation-delay: 0.4s; }
.settings-form .el-form-item:nth-child(5) { animation-delay: 0.5s; }
.settings-form .el-form-item:nth-child(6) { animation-delay: 0.6s; }
.settings-form .el-form-item:nth-child(7) { animation-delay: 0.7s; }

.letters-select {
  width: 100%;
  max-width: 500px;
  transition: all 0.3s ease;
}

.letters-select:hover {
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.start-button-container {
  display: flex;
  justify-content: center;
  margin-top: 48px;
  animation: fadeInUp 0.6s ease-out 0.8s forwards;
  opacity: 0;
}

.start-button-container .el-button {
  padding: 16px 48px;
  font-size: 18px;
  border-radius: 50px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.start-button-container .el-button:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

/* 实验运行界面 */
.experiment-running {
  padding: 30px;
  animation: fadeInUp 0.6s ease-out;
}

.experiment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 48px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #f0f9ff, #e6f7ff);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.experiment-info span {
  margin-right: 24px;
  font-weight: bold;
  color: #333;
  font-size: 16px;
}

.experiment-timer {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
  background-color: rgba(64, 158, 255, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  min-width: 80px;
  text-align: center;
}

.stimulus-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 350px;
  margin: 48px 0;
  background: linear-gradient(135deg, #f9f9f9, #f0f0f0);
  border-radius: 16px;
  position: relative;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.stimulus-container:hover {
  box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stimulus {
  font-size: 140px;
  font-weight: bold;
  color: #333;
  animation: pulse 2s infinite;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.feedback {
  font-size: 48px;
  font-weight: bold;
  padding: 24px 48px;
  border-radius: 12px;
  animation: bounceIn 0.6s ease-out;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.feedback.correct {
  background: linear-gradient(135deg, #f0f9eb, #e6f7ee);
  color: #67c23a;
  border: 2px solid #c2e7b0;
}

.feedback.incorrect {
  background: linear-gradient(135deg, #fef0f0, #fde2e2);
  color: #f56c6c;
  border: 2px solid #fbc4c4;
}

.response-buttons {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin: 48px 0;
  animation: fadeInUp 0.6s ease-out 0.3s forwards;
  opacity: 0;
}

.response-buttons .el-button {
  padding: 16px 48px;
  font-size: 18px;
  border-radius: 50px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 120px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.response-buttons .el-button:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.response-buttons .el-button:first-child {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border: none;
}

.response-buttons .el-button:last-child {
  background: linear-gradient(135deg, #909399, #b3b6bb);
  border: none;
  color: #fff;
}

.response-buttons .el-button:disabled {
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

.response-hint {
  text-align: center;
  color: #666;
  font-size: 16px;
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-top: 24px;
  animation: fadeInUp 0.6s ease-out 0.4s forwards;
  opacity: 0;
}

/* KSS 疲劳量表界面 */
.kss-container {
  padding: 30px;
  animation: fadeInUp 0.6s ease-out;
}

.kss-container h2 {
  margin-bottom: 24px;
  color: #333;
  font-size: 28px;
  font-weight: bold;
  position: relative;
  display: inline-block;
}

.kss-container h2::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 0;
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 2px;
}

.kss-container .description {
  margin-bottom: 36px;
  color: #666;
  line-height: 1.6;
  font-size: 18px;
}

.kss-scale {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin: 48px 0;
}

.kss-item {
  padding: 24px;
  border: 2px solid #eaeaea;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background-color: #f9f9f9;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.kss-item:hover {
  border-color: #409EFF;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
  transform: translateY(-4px);
}

.kss-item.active {
  border-color: #409EFF;
  background: linear-gradient(135deg, #ecf5ff, #e6f7ff);
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
}

.kss-score {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 12px;
  display: inline-block;
  transition: all 0.3s ease;
}

.kss-item:hover .kss-score {
  transform: scale(1.1);
}

.kss-description {
  color: #666;
  line-height: 1.5;
  font-size: 16px;
}

.kss-button-container {
  display: flex;
  justify-content: center;
  margin-top: 48px;
  animation: fadeInUp 0.6s ease-out 0.8s forwards;
  opacity: 0;
}

.kss-button-container .el-button {
  padding: 16px 48px;
  font-size: 18px;
  border-radius: 50px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.kss-button-container .el-button:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

.kss-button-container .el-button:disabled {
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

/* 静息状态界面 */
.rest-container {
  padding: 30px;
  text-align: center;
  animation: fadeInUp 0.6s ease-out;
}

.rest-container h2 {
  margin-bottom: 24px;
  color: #333;
  font-size: 28px;
  font-weight: bold;
  position: relative;
  display: inline-block;
}

.rest-container h2::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, #67c23a, #409eff);
  border-radius: 2px;
}

.rest-container .description {
  margin-bottom: 48px;
  color: #666;
  line-height: 1.6;
  font-size: 18px;
}

.rest-timer {
  max-width: 400px;
  margin: 48px auto;
  animation: fadeInUp 0.6s ease-out 0.3s forwards;
  opacity: 0;
}

.timer-circle {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 240px;
  height: 240px;
  margin: 0 auto 36px;
  background: linear-gradient(135deg, #f0f9ff, #e6f7ff);
  border-radius: 50%;
  position: relative;
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.2);
  transition: all 0.3s ease;
  animation: pulse 3s infinite;
}

.timer-circle::before {
  content: '';
  position: absolute;
  top: 8px;
  left: 8px;
  right: 8px;
  bottom: 8px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
}

.timer-content {
  text-align: center;
  position: relative;
  z-index: 1;
}

.timer-number {
  font-size: 56px;
  font-weight: bold;
  color: #409EFF;
  text-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
  animation: countDown 1s linear infinite;
}

.timer-unit {
  font-size: 20px;
  color: #666;
  margin-top: 8px;
  font-weight: 500;
}

.timer-progress {
  margin-top: 36px;
  animation: fadeInUp 0.6s ease-out 0.5s forwards;
  opacity: 0;
}

.timer-progress .el-progress {
  border-radius: 10px;
  overflow: hidden;
}

.timer-progress .el-progress__bar {
  border-radius: 10px;
  transition: width 1s linear;
}

/* 实验完成界面 */
.experiment-completed {
  padding: 30px;
  animation: fadeInUp 0.6s ease-out;
}

.experiment-completed h2 {
  margin-bottom: 24px;
  color: #333;
  font-size: 28px;
  font-weight: bold;
  position: relative;
  display: inline-block;
}

.experiment-completed h2::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 0;
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, #67c23a, #409eff);
  border-radius: 2px;
}

.experiment-completed .description {
  margin-bottom: 36px;
  color: #666;
  line-height: 1.6;
  font-size: 18px;
}

.results-container {
  margin: 36px 0;
  padding: 28px;
  background: linear-gradient(135deg, #f9f9f9, #f0f0f0);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  animation: fadeInUp 0.6s ease-out 0.3s forwards;
  opacity: 0;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 16px 20px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.result-item:hover {
  transform: translateX(8px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.result-item span:first-child {
  font-weight: bold;
  color: #333;
  font-size: 16px;
}

.result-item span:last-child {
  color: #409EFF;
  font-weight: bold;
  font-size: 18px;
  background-color: rgba(64, 158, 255, 0.1);
  padding: 6px 16px;
  border-radius: 20px;
}

.kss-results {
  margin: 36px 0;
  animation: fadeInUp 0.6s ease-out 0.5s forwards;
  opacity: 0;
}

.kss-result-item {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f0f9ff, #e6f7ff);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
  transition: all 0.3s ease;
}

.kss-result-item:hover {
  transform: translateX(8px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.kss-score-value {
  margin: 0 24px;
  font-weight: bold;
  color: #409EFF;
  font-size: 20px;
  background-color: rgba(64, 158, 255, 0.2);
  padding: 6px 16px;
  border-radius: 20px;
  min-width: 60px;
  text-align: center;
}

.completed-buttons {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 48px;
  animation: fadeInUp 0.6s ease-out 0.8s forwards;
  opacity: 0;
}

.completed-buttons .el-button {
  padding: 14px 32px;
  font-size: 16px;
  border-radius: 50px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.completed-buttons .el-button:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.completed-buttons .el-button:first-child {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border: none;
}

/* 实验结果界面 */
.experiment-result {
  padding: 30px;
  animation: fadeInUp 0.6s ease-out;
}

.experiment-result h2 {
  margin-bottom: 36px;
  color: #333;
  font-size: 32px;
  font-weight: bold;
  text-align: center;
  position: relative;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .two-back-experiment {
    padding: 16px;
  }
  
  .experiment-card {
    max-width: 100%;
  }
  
  .card-header {
    font-size: 18px;
    padding: 16px 20px;
  }
  
  .experiment-prepare,
  .experiment-running,
  .kss-container,
  .rest-container,
  .experiment-completed,
  .experiment-result {
    padding: 20px;
  }
  
  .experiment-prepare h2,
  .kss-container h2,
  .rest-container h2,
  .experiment-completed h2 {
    font-size: 24px;
  }
  
  .experiment-result h2 {
    font-size: 28px;
  }
  
  .experiment-prepare .description,
  .kss-container .description,
  .rest-container .description,
  .experiment-completed .description {
    font-size: 16px;
    margin-bottom: 24px;
  }
  
  .settings-form {
    padding: 20px;
    margin-bottom: 36px;
  }
  
  .settings-form .el-form-item {
    margin-bottom: 20px;
  }
  
  .start-button-container,
  .kss-button-container {
    margin-top: 36px;
  }
  
  .start-button-container .el-button,
  .kss-button-container .el-button {
    padding: 14px 40px;
    font-size: 16px;
  }
  
  .experiment-header {
    flex-direction: column;
    gap: 12px;
    text-align: center;
    padding: 16px 20px;
  }
  
  .experiment-info span {
    margin-right: 16px;
    font-size: 14px;
  }
  
  .stimulus-container {
    height: 250px;
    margin: 32px 0;
  }
  
  .stimulus {
    font-size: 100px;
  }
  
  .feedback {
    font-size: 36px;
    padding: 16px 32px;
  }
  
  .response-buttons {
    gap: 20px;
    margin: 32px 0;
  }
  
  .response-buttons .el-button {
    padding: 14px 32px;
    font-size: 16px;
  }
  
  .response-hint {
    font-size: 14px;
    padding: 12px;
  }
  
  .kss-scale {
    grid-template-columns: 1fr;
    gap: 16px;
    margin: 36px 0;
  }
  
  .kss-item {
    padding: 20px;
  }
  
  .rest-timer {
    max-width: 300px;
    margin: 36px auto;
  }
  
  .timer-circle {
    width: 200px;
    height: 200px;
    margin-bottom: 24px;
  }
  
  .timer-number {
    font-size: 48px;
  }
  
  .timer-unit {
    font-size: 18px;
  }
  
  .results-container {
    padding: 20px;
    margin: 24px 0;
  }
  
  .result-item {
    padding: 12px 16px;
    margin-bottom: 12px;
  }
  
  .result-item span:first-child {
    font-size: 14px;
  }
  
  .result-item span:last-child {
    font-size: 16px;
    padding: 4px 12px;
  }
  
  .kss-results {
    margin: 24px 0;
  }
  
  .kss-result-item {
    padding: 12px 16px;
    margin-bottom: 12px;
  }
  
  .kss-score-value {
    margin: 0 16px;
    font-size: 16px;
    padding: 4px 12px;
    min-width: 50px;
  }
  
  .completed-buttons {
    flex-direction: column;
    align-items: center;
    gap: 16px;
    margin-top: 36px;
  }
  
  .completed-buttons .el-button {
    padding: 12px 28px;
    font-size: 14px;
    width: 100%;
    max-width: 200px;
  }
  
  .chart-container {
    margin: 24px 0;
  }
  
  .chart {
    height: 250px;
  }
  
  .result-buttons {
    flex-direction: column;
    align-items: center;
    gap: 16px;
    margin-top: 36px;
  }
  
  .result-buttons .el-button {
    padding: 12px 28px;
    font-size: 14px;
    width: 100%;
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  .two-back-experiment {
    padding: 12px;
  }
  
  .experiment-prepare,
  .experiment-running,
  .kss-container,
  .rest-container,
  .experiment-completed,
  .experiment-result {
    padding: 16px;
  }
  
  .experiment-prepare h2,
  .kss-container h2,
  .rest-container h2,
  .experiment-completed h2 {
    font-size: 20px;
  }
  
  .experiment-result h2 {
    font-size: 24px;
  }
  
  .experiment-prepare .description,
  .kss-container .description,
  .rest-container .description,
  .experiment-completed .description {
    font-size: 14px;
    margin-bottom: 20px;
  }
  
  .settings-form {
    padding: 16px;
    margin-bottom: 24px;
  }
  
  .settings-form .el-form-item {
    margin-bottom: 16px;
  }
  
  .start-button-container,
  .kss-button-container {
    margin-top: 24px;
  }
  
  .start-button-container .el-button,
  .kss-button-container .el-button {
    padding: 12px 32px;
    font-size: 14px;
  }
  
  .stimulus-container {
    height: 200px;
    margin: 24px 0;
  }
  
  .stimulus {
    font-size: 80px;
  }
  
  .feedback {
    font-size: 28px;
    padding: 12px 24px;
  }
  
  .response-buttons {
    gap: 16px;
    margin: 24px 0;
  }
  
  .response-buttons .el-button {
    padding: 12px 24px;
    font-size: 14px;
  }
  
  .response-hint {
    font-size: 12px;
    padding: 10px;
  }
  
  .kss-scale {
    gap: 12px;
    margin: 24px 0;
  }
  
  .kss-item {
    padding: 16px;
  }
  
  .kss-score {
    font-size: 24px;
  }
  
  .kss-description {
    font-size: 14px;
  }
  
  .rest-timer {
    max-width: 250px;
    margin: 24px auto;
  }
  
  .timer-circle {
    width: 160px;
    height: 160px;
    margin-bottom: 16px;
  }
  
  .timer-number {
    font-size: 36px;
  }
  
  .timer-unit {
    font-size: 16px;
  }
  
  .results-container {
    padding: 16px;
    margin: 20px 0;
  }
  
  .result-item {
    padding: 10px 12px;
    margin-bottom: 10px;
  }
  
  .result-item span:first-child {
    font-size: 12px;
  }
  
  .result-item span:last-child {
    font-size: 14px;
    padding: 3px 10px;
  }
  
  .kss-result-item {
    padding: 10px 12px;
    margin-bottom: 10px;
  }
  
  .kss-score-value {
    margin: 0 12px;
    font-size: 14px;
    padding: 3px 10px;
    min-width: 40px;
  }
  
  .completed-buttons {
    margin-top: 24px;
  }
  
  .completed-buttons .el-button {
    padding: 10px 24px;
    font-size: 12px;
  }
  
  .chart {
    height: 200px;
  }
  
  .result-buttons {
    margin-top: 24px;
  }
  
  .result-buttons .el-button {
    padding: 10px 24px;
    font-size: 12px;
  }
}

/* 暗模式适配 */
.theme-dark .two-back-experiment {
  background-color: var(--bg-page);
  background-image: none;
}

.theme-dark .experiment-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
}

.theme-dark .experiment-card:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
}

.theme-dark .card-header {
  background-color: var(--bg-hover);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.theme-dark .experiment-prepare h2,
.theme-dark .kss-container h2,
.theme-dark .rest-container h2,
.theme-dark .experiment-completed h2,
.theme-dark .experiment-result h2 {
  color: var(--text-primary);
}

.theme-dark .experiment-prepare .description,
.theme-dark .kss-container .description,
.theme-dark .rest-container .description,
.theme-dark .experiment-completed .description {
  color: var(--text-secondary);
}

.theme-dark .settings-form {
  background: linear-gradient(135deg, var(--bg-hover), var(--bg-card));
}

.theme-dark .stimulus-container {
  background: linear-gradient(135deg, var(--bg-hover), var(--bg-card));
}

.theme-dark .stimulus {
  color: var(--text-primary);
}

.theme-dark .feedback.correct {
  background: linear-gradient(135deg, var(--bg-success-light), var(--bg-success));
  color: var(--text-success);
  border: 2px solid var(--border-success);
}

.theme-dark .feedback.incorrect {
  background: linear-gradient(135deg, var(--bg-danger-light), var(--bg-danger));
  color: var(--text-danger);
  border: 2px solid var(--border-danger);
}

.theme-dark .response-hint {
  background-color: var(--bg-hover);
  color: var(--text-secondary);
}

.theme-dark .kss-item {
  background-color: var(--bg-hover);
  border: 2px solid var(--border-color);
}

.theme-dark .kss-item:hover {
  border-color: var(--brand-primary);
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
}

.theme-dark .kss-item.active {
  border-color: var(--brand-primary);
  background: linear-gradient(135deg, var(--bg-primary-light), var(--bg-primary));
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
}

.theme-dark .kss-score {
  color: var(--brand-primary);
}

.theme-dark .kss-description {
  color: var(--text-secondary);
}

.theme-dark .timer-circle {
  background: linear-gradient(135deg, var(--bg-primary-light), var(--bg-primary));
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.2);
}

.theme-dark .timer-circle::before {
  background-color: rgba(255, 255, 255, 0.05);
}

.theme-dark .timer-number {
  color: var(--brand-primary);
  text-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
}

.theme-dark .timer-unit {
  color: var(--text-secondary);
}

.theme-dark .results-container {
  background: linear-gradient(135deg, var(--bg-hover), var(--bg-card));
}

.theme-dark .result-item {
  background-color: var(--bg-card);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.theme-dark .result-item span:first-child {
  color: var(--text-primary);
}

.theme-dark .result-item span:last-child {
  color: var(--brand-primary);
  background-color: rgba(64, 158, 255, 0.1);
}

.theme-dark .kss-result-item {
  background: linear-gradient(135deg, var(--bg-primary-light), var(--bg-primary));
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.theme-dark .kss-score-value {
  color: var(--brand-primary);
  background-color: rgba(64, 158, 255, 0.2);
}

.theme-dark .kss-result-item:hover {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.theme-dark .summary-table {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
}

.theme-dark .summary-table th,
.theme-dark .summary-table td {
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
}

.theme-dark .chart-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
}

.theme-dark .chart-header {
  color: var(--text-primary);
}

.experiment-result h2::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 2px;
}

.summary-table {
  margin: 36px 0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  animation: fadeInUp 0.6s ease-out 0.3s forwards;
  opacity: 0;
}

.summary-table .el-table {
  border-radius: 12px;
  overflow: hidden;
}

.summary-table .el-table__header {
  background: linear-gradient(135deg, #f9f9f9, #f0f0f0);
}

.summary-table .el-table__header th {
  font-weight: bold;
  color: #333;
  font-size: 16px;
}

.summary-table .el-table__body tr:hover {
  background-color: #f0f9ff;
}

.chart-container {
  margin: 36px 0;
}

.chart-card {
  margin-bottom: 36px;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.chart-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  transform: translateY(-4px);
}

.chart-header {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  padding: 16px 24px;
  background: linear-gradient(135deg, #f9f9f9, #f0f0f0);
  border-bottom: 1px solid #eaeaea;
}

.chart {
  width: 100% !important;
  height: 300px !important;
  min-height: 300px;
  padding: 0;
  background-color: #fff;
  position: relative;
}

.result-buttons {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 48px;
  animation: fadeInUp 0.6s ease-out 0.8s forwards;
  opacity: 0;
}

.result-buttons .el-button {
  padding: 14px 32px;
  font-size: 16px;
  border-radius: 50px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.result-buttons .el-button:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.result-buttons .el-button:first-child {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  border: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .two-back-experiment {
    padding: 16px;
    min-height: calc(100vh - 40px);
  }
  
  .experiment-card {
    max-width: 100%;
  }
  
  .card-header {
    font-size: 18px;
    padding: 16px 20px;
  }
  
  .experiment-prepare,
  .experiment-running,
  .kss-container,
  .rest-container,
  .experiment-completed,
  .experiment-result {
    padding: 20px;
  }
  
  .experiment-prepare h2,
  .kss-container h2,
  .rest-container h2,
  .experiment-completed h2,
  .experiment-result h2 {
    font-size: 24px;
  }
  
  .experiment-prepare .description,
  .kss-container .description,
  .rest-container .description,
  .experiment-completed .description {
    font-size: 16px;
    margin-bottom: 30px;
  }
  
  .settings-form {
    padding: 20px;
  }
  
  .stimulus {
    font-size: 100px;
  }
  
  .feedback {
    font-size: 36px;
    padding: 16px 32px;
  }
  
  .stimulus-container {
    height: 280px;
    margin: 30px 0;
  }
  
  .response-buttons {
    gap: 20px;
    margin: 30px 0;
  }
  
  .response-buttons .el-button {
    padding: 12px 32px;
    font-size: 16px;
  }
  
  .kss-scale {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .kss-item {
    padding: 20px;
  }
  
  .kss-score {
    font-size: 28px;
  }
  
  .timer-circle {
    width: 180px;
    height: 180px;
  }
  
  .timer-number {
    font-size: 48px;
  }
  
  .results-container {
    padding: 20px;
  }
  
  .result-item {
    padding: 12px 16px;
  }
  
  .chart {
    width: 100% !important;
    height: 250px !important;
    min-height: 250px;
    padding: 0;
  }
  
  .start-button-container .el-button,
  .kss-button-container .el-button,
  .completed-buttons .el-button,
  .result-buttons .el-button {
    padding: 12px 32px;
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .experiment-prepare h2,
  .kss-container h2,
  .rest-container h2,
  .experiment-completed h2,
  .experiment-result h2 {
    font-size: 20px;
  }
  
  .stimulus {
    font-size: 80px;
  }
  
  .feedback {
    font-size: 28px;
    padding: 12px 24px;
  }
  
  .response-buttons {
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }
  
  .response-buttons .el-button {
    width: 100%;
    max-width: 200px;
  }
  
  .experiment-info span {
    display: block;
    margin-bottom: 8px;
  }
  
  .experiment-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .completed-buttons,
  .result-buttons {
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }
  
  .completed-buttons .el-button,
  .result-buttons .el-button {
    width: 100%;
    max-width: 200px;
  }
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

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

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes countDown {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes expandWidth {
  from {
    width: 0;
  }
  to {
    width: 60px;
  }
}
</style>
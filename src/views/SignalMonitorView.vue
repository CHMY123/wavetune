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
        当前监测信号：EEG、fNIRS
      </p>
    </div>

    <!-- 中部主体区：数据可视化图表模块 -->
    <div class="signal-modules">
      <el-row :gutter="16">
        <el-col :xs="24" :md="12">
          <el-card class="signal-card">
            <template #header>
              <div class="card-header">
                <span class="signal-name">EEG 脑电信号</span>
              </div>
            </template>
            <div ref="eegChart" class="chart"></div>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-card class="signal-card">
            <template #header>
              <div class="card-header">
                <span class="signal-name">fNIRS 近红外信号</span>
              </div>
            </template>
            <div ref="fnirsChart" class="chart"></div>
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

        <div class="detection-result" v-if="detectionResult" style="margin-left:12px; display:flex; align-items:center; gap:8px; flex-wrap:wrap">
          <el-tag :type="detectionResult.type || 'warning'">检测：{{ detectionResult.label_name }}</el-tag>
          
          <!-- 概率分布显示 -->
          <div class="probability-distribution" style="margin-top:8px; width:100%;">
            <h4 style="margin:0 0 8px 0;">概率分布：</h4>
            <div v-for="(prob, label) in detectionResult.probabilities" :key="label" style="margin-bottom:4px; display:flex; align-items:center;">
              <span style="width:100px; font-size:14px;">{{ label }}:</span>
              <div style="flex:1; height:12px; background-color:#f0f0f0; border-radius:6px; overflow:hidden; margin:0 8px;">
                <div 
                  :style="{
                    width: `${prob}%`, 
                    height: '100%', 
                    backgroundColor: getProbabilityColor(label),
                    transition: 'width 0.3s ease'
                  }"
                ></div>
              </div>
              <span style="width:60px; text-align:right; font-size:14px;">{{ prob.toFixed(2) }}%</span>
            </div>
          </div>

          <!-- 跳转按钮：根据检测结果跳转到对应疲劳等级的音乐推荐 -->
          <div class="recommendation-section" style="margin-top:12px; width:100%; display:flex; flex-direction:column; gap:12px;">
            <div v-if="detectionResult.label !== '其他'" class="scene-selection" style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:14px; font-weight:500;">选择场景：</span>
              <el-radio-group v-model="selectedScene" size="small" style="flex:1;">
                <el-radio-button label="">不限</el-radio-button>
                <el-radio-button label="work">工作</el-radio-button>
                <el-radio-button label="study">学习</el-radio-button>
                <el-radio-button label="drive">驾驶</el-radio-button>
              </el-radio-group>
            </div>
            <el-button
              v-if="detectionResult.label !== '其他'"
              type="primary"
              size="small"
              @click="navigateToRecommendation"
            >
              {{ getRecommendationButtonText() }}
            </el-button>
            <el-tag v-if="detectionResult.label === '其他'" type="info">建议再试一次</el-tag>
          </div>
        </div>
        
        <!-- 清空按钮：用于清空暂存在页面的数据可视化 -->
        <el-button
          v-if="csvData"
          type="danger"
          size="large"
          @click="clearData"
          style="margin-left:12px"
        >
          <el-icon><Delete /></el-icon>
          清空数据
        </el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { VideoPause, Download, Delete } from '@element-plus/icons-vue'
import { requestMethod } from '@/utils/request'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

export default {
  name: 'SignalMonitorView',
  components: {
    VideoPause,
    Download,
    Delete
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
      detectionResult: localStorage.getItem('detectionResult') ? JSON.parse(localStorage.getItem('detectionResult')) : null,
      timeMarks: ['00:00', '00:01', '00:02', '00:03', '00:04', '00:05'],
      // 数据可视化相关状态
      csvData: localStorage.getItem('chartData') ? JSON.parse(localStorage.getItem('chartData')) : null,
      eegChart: null,
      fnirsChart: null,
      // 场景选择
      selectedScene: ''
    }
  },
  created() {
    // 日志：组件创建完成，初始化信号监测数据
    console.log('%c [SignalMonitorView] 组件创建完成', 'color: #1890ff; font-weight: bold;')
    console.log('%c [SignalMonitorView] 初始化信号监测模块数据：', 'color: #722ed1;', this.signalModules)
    
    // 从localStorage中读取图表数据
    if (localStorage.getItem('chartData')) {
      this.csvData = JSON.parse(localStorage.getItem('chartData'))
      console.log('%c [SignalMonitorView] 从localStorage读取图表数据：', 'color: #1890ff;', this.csvData)
      
      // 延迟初始化图表，确保DOM已经更新
      setTimeout(() => {
        this.initCharts()
      }, 100)
    }
  },
  methods: {
      chooseFile() {
        console.log('%c [SignalMonitorView] 触发选择CSV文件操作', 'color: #52c41a;')
        // 触发隐藏的 file input
        if (this.$refs.csvInput) {
          this.$refs.csvInput.click()
        } else {
          console.warn('%c [SignalMonitorView] 未找到csvInput引用，无法触发文件选择', 'color: #fa8c16;')
        }
      },
      onFileChange(e) {
        console.log('%c [SignalMonitorView] 触发文件选择变更事件', 'color: #52c41a;')
        const files = e.target.files || e.dataTransfer?.files
        if (!files || !files.length) {
          console.log('%c [SignalMonitorView] 未选择任何文件，清空当前文件状态', 'color: #fa8c16;')
          this.selectedFile = null
          this.selectedFileName = ''
          return
        }
        const f = files[0]
        this.selectedFile = f
        this.selectedFileName = f.name
        // 日志：记录选择的文件信息
        console.log('%c [SignalMonitorView] 成功选择CSV文件：', 'color: #1890ff;', {
          文件名: f.name,
          文件大小: `${(f.size / 1024).toFixed(2)} KB`,
          文件类型: f.type
        })
      },
      async uploadCsvForDetection() {
        // 校验是否选择文件
        if (!this.selectedFile) {
          console.warn('%c [SignalMonitorView] 未选择CSV文件，无法执行上传检测', 'color: #faad14;')
          ElMessage.warning('请先选择一个 CSV 文件')
          return
        }

        // 先解析CSV文件数据用于可视化
        await this.parseCsvFile()

        // 构建FormData
        const form = new FormData()
        form.append('file', this.selectedFile)
        console.log('%c [SignalMonitorView] 构建FormData完成，准备上传文件', 'color: #1890ff;')

        this.detecting = true
        this.detectionResult = null
        try {
          console.log('%c [SignalMonitorView] 开始上传CSV文件并执行检测，请求地址：/detection/upload', 'color: #1890ff;')
          // 使用 request.js 的 postForm 发送 multipart/form-data
          const res = await requestMethod.postForm('/detection/upload', form, {
            onUploadProgress: (progressEvent) => {
              // 可选：添加上传进度显示
              if (progressEvent.total) {
                this.uploadProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              }
            },
            timeout: 120000 // 关键：延长超时时间，解决60秒超时问题
          });
          console.log('%c [SignalMonitorView] 上传检测请求响应成功：', 'color: #52c41a;', res)
          
          // request 的响应拦截器会返回 res（包含 code/msg/data）
          const payload = res.data || {}
          this.detectionResult = {
            label: payload.label,
            label_name: payload.label || 'Unknown',
            probabilities: payload.probabilities || payload.probs || {},
            type: (payload.label === '重度疲劳' ? 'danger' : (payload.label === '中度疲劳' || payload.label === '轻度疲劳' ? 'warning' : 'success'))
          }
          
          // 存储到localStorage
          localStorage.setItem('detectionResult', JSON.stringify(this.detectionResult))
          
          // 日志：记录检测结果
          console.log('%c [SignalMonitorView] 脑疲劳检测结果解析完成并存储：', 'color: #722ed1;', this.detectionResult)
          ElMessage.success(`检测完成：${this.detectionResult.label_name}`)
        } catch (err) {
          // 日志：记录上传检测异常
          console.error('%c [SignalMonitorView] 上传CSV文件或检测失败：', 'color: #f5222d;', err)
          // request 已在拦截器中显示错误消息，这里可做额外提示
          ElMessage.error('上传或检测失败，请检查文件格式（20×20）并重试')
        } finally {
          this.detecting = false
          console.log('%c [SignalMonitorView] 上传检测流程结束，重置detecting状态', 'color: #fa8c16;')
        }
      },
      async parseCsvFile() {
        if (!this.selectedFile) return
        
        try {
          console.log('%c [SignalMonitorView] 开始解析CSV文件数据', 'color: #1890ff;')
          console.log('%c [SignalMonitorView] 文件信息：', 'color: #1890ff;', {
            name: this.selectedFile.name,
            size: this.selectedFile.size,
            type: this.selectedFile.type
          })
          
          // 构建FormData
          const form = new FormData()
          form.append('file', this.selectedFile)
          
          // 发送请求到后端，获取处理后的数据
          console.log('%c [SignalMonitorView] 发送请求到后端处理CSV文件', 'color: #1890ff;')
          const res = await requestMethod.postForm('/detection/process_csv', form, {
            timeout: 300000 // 延长超时时间，处理大型文件
          })
          
          console.log('%c [SignalMonitorView] 后端处理CSV文件响应成功：', 'color: #52c41a;', res)
          
          // 提取数据
          let extractedData = {
            eeg: [],
            fnirs_raw: [],
            hbo: [],
            hbr: [],
            marker: [],
            label: [],
            shape: [0, 0]
          }
          
          // 检查响应数据
          if (res && res.eeg) {
            // 直接使用响应数据
            extractedData = res
          } else if (res && res.data) {
            // 使用响应中的data字段
            extractedData = res.data
          }
          
          console.log('%c [SignalMonitorView] 提取的数据：', 'color: #1890ff;', extractedData)
          
          // 赋值给csvData
          this.csvData = extractedData
          
          // 存储图表数据到localStorage（只存储前500个点，避免超出存储限制）
          try {
            const chartData = {
              eeg: extractedData.eeg ? extractedData.eeg.map(channel => channel.slice(0, 500)) : [],
              fnirs_raw: extractedData.fnirs_raw ? extractedData.fnirs_raw.map(channel => channel.slice(0, 500)) : [],
              shape: extractedData.shape || [0, 0]
            }
            localStorage.setItem('chartData', JSON.stringify(chartData))
            console.log('%c [SignalMonitorView] 图表数据存储完成：', 'color: #52c41a;', chartData)
          } catch (err) {
            console.error('%c [SignalMonitorView] 存储图表数据失败：', 'color: #f5222d;', err)
          }
          
          console.log('%c [SignalMonitorView] CSV数据赋值完成：', 'color: #52c41a;', this.csvData)
          
          // 延迟初始化图表，确保DOM已经更新
          setTimeout(() => {
            console.log('%c [SignalMonitorView] 延迟初始化图表', 'color: #1890ff;')
            this.initCharts()
          }, 100)
        } catch (err) {
          console.error('%c [SignalMonitorView] 解析CSV文件失败：', 'color: #f5222d;', err)
          ElMessage.error('解析CSV文件失败')
        }
      },
      transpose(matrix) {
        // 转置二维数组
        if (!matrix || matrix.length === 0 || !matrix[0]) {
          console.error('%c [SignalMonitorView] 转置失败：输入矩阵为空或格式错误', 'color: #f5222d;')
          return { shape: [0, 0] }
        }
        
        const rows = matrix.length
        const cols = matrix[0].length
        const result = new Array(cols)
        
        for (let i = 0; i < cols; i++) {
          result[i] = new Array(rows)
          for (let j = 0; j < rows; j++) {
            result[i][j] = matrix[j][i]
          }
        }
        
        // 添加shape属性，模拟numpy数组
        result.shape = [cols, rows]
        return result
      },
      extractData(rawData) {
        // 检查数据是否有效
        if (!rawData || rawData.length === 0) {
          console.error('%c [SignalMonitorView] 提取数据失败：输入数据为空或格式错误', 'color: #f5222d;')
          return {
            eeg: [],
            fnirs_raw: [],
            hbo: [],
            hbr: [],
            marker: [],
            label: [],
            shape: [0, 0]
          }
        }
        
        // 提取EEG数据（1-32通道）
        const eegData = rawData.slice ? rawData.slice(1, 33) : []
        
        // 提取fNIRS原始数据（33-56通道）
        const fnirsRaw = rawData.slice ? rawData.slice(33, 57) : []
        
        // 提取标记数据（第57列）
        const markerData = rawData[56] || []
        
        // 提取标签数据（最后一列）
        const labelData = rawData.length > 0 ? rawData[rawData.length - 1] : []
        
        // 这里简化处理，实际项目中可以调用后端API获取处理后的数据
        // 或者在前端实现类似processing_fNIRS_new.py的功能
        
        return {
          eeg: eegData,
          fnirs_raw: fnirsRaw,
          hbo: [], // 简化处理，实际项目中需要计算
          hbr: [], // 简化处理，实际项目中需要计算
          marker: markerData,
          label: labelData,
          shape: rawData.shape || [0, 0]
        }
      },
      initCharts() {
        console.log('%c [SignalMonitorView] 开始初始化图表', 'color: #1890ff;')
        console.log('%c [SignalMonitorView] EEG图表容器：', 'color: #1890ff;', this.$refs.eegChart)
        console.log('%c [SignalMonitorView] fNIRS图表容器：', 'color: #1890ff;', this.$refs.fnirsChart)
        console.log('%c [SignalMonitorView] CSV数据：', 'color: #1890ff;', this.csvData)
        
        // 初始化EEG图表
        if (this.$refs.eegChart) {
          // 先销毁旧图表，避免内存泄漏
          if (this.eegChart) {
            this.eegChart.dispose()
          }
          this.eegChart = echarts.init(this.$refs.eegChart)
          console.log('%c [SignalMonitorView] EEG图表初始化成功', 'color: #52c41a;')
          this.updateEegChart()
        }
        
        // 初始化fNIRS图表
        if (this.$refs.fnirsChart) {
          // 先销毁旧图表，避免内存泄漏
          if (this.fnirsChart) {
            this.fnirsChart.dispose()
          }
          this.fnirsChart = echarts.init(this.$refs.fnirsChart)
          console.log('%c [SignalMonitorView] fNIRS图表初始化成功', 'color: #52c41a;')
          this.updateFnirsChart()
        }
      },
      updateEegChart() {
        console.log('%c [SignalMonitorView] 开始更新EEG图表', 'color: #1890ff;')
        if (!this.eegChart || !this.csvData) {
          console.log('%c [SignalMonitorView] EEG图表或CSV数据不存在', 'color: #f5222d;')
          return
        }
        
        const eegData = this.csvData.eeg
        if (!eegData || eegData.length === 0) {
          console.log('%c [SignalMonitorView] EEG数据不存在或为空', 'color: #f5222d;')
          return
        }
        
        console.log('%c [SignalMonitorView] EEG数据形状：', 'color: #1890ff;', {
          channels: eegData.length,
          points: eegData[0] ? eegData[0].length : 0
        })
        
        // 选择前4个EEG通道进行显示
        const channels = [0, 1, 2, 3]
        const sampleRate = 1000
        const maxPoints = 500 // 最多显示500个点
        const endSample = Math.min(eegData[0].length, maxPoints)
        
        console.log('%c [SignalMonitorView] 显示点数：', 'color: #1890ff;', endSample)
        
        // 生成时间轴数据
        const timeData = []
        for (let i = 0; i < endSample; i++) {
          timeData.push((i / sampleRate).toFixed(2))
        }
        
        // 准备系列数据
        const series = channels.map((ch, index) => {
          const color = this.getColor(index)
          const channelData = eegData[ch].slice(0, endSample)
          console.log('%c [SignalMonitorView] EEG通道' + (ch + 1) + '数据长度：', 'color: #1890ff;', channelData.length)
          
          return {
            name: `Channel ${ch + 1}`,
            type: 'line',
            data: channelData,
            smooth: true,
            lineStyle: {
              width: 2,
              color
            },
            showSymbol: false
          }
        })
        
        const option = {
          title: {
            text: `EEG 信号波形（前${endSample}个点）`,
            left: 'center'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross'
            }
          },
          legend: {
            data: channels.map(ch => `Channel ${ch + 1}`),
            orient: 'vertical',
            right: 10,
            top: 'center'
          },
          grid: {
            left: '3%',
            right: '15%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: timeData,
            axisLabel: {
              formatter: '{value}s'
            }
          },
          yAxis: {
            type: 'value',
            axisLabel: {
              formatter: '{value}'
            }
          },
          series
        }
        
        console.log('%c [SignalMonitorView] EEG图表选项：', 'color: #1890ff;', option)
        this.eegChart.setOption(option)
        console.log('%c [SignalMonitorView] EEG图表更新完成', 'color: #52c41a;')
      },
      updateFnirsChart() {
        console.log('%c [SignalMonitorView] 开始更新fNIRS图表', 'color: #1890ff;')
        if (!this.fnirsChart || !this.csvData) {
          console.log('%c [SignalMonitorView] fNIRS图表或CSV数据不存在', 'color: #f5222d;')
          return
        }
        
        const fnirsRaw = this.csvData.fnirs_raw
        if (!fnirsRaw || fnirsRaw.length === 0) {
          console.log('%c [SignalMonitorView] fNIRS数据不存在或为空', 'color: #f5222d;')
          return
        }
        
        console.log('%c [SignalMonitorView] fNIRS数据形状：', 'color: #1890ff;', {
          channels: fnirsRaw.length,
          points: fnirsRaw[0] ? fnirsRaw[0].length : 0
        })
        
        // 选择前4个fNIRS通道进行显示
        const channels = [0, 1, 2, 3]
        const sampleRate = 5 // fNIRS采样率
        const maxPoints = 500 // 最多显示500个点
        const endSample = Math.min(fnirsRaw[0].length, maxPoints)
        
        console.log('%c [SignalMonitorView] 显示点数：', 'color: #1890ff;', endSample)
        
        // 生成时间轴数据
        const timeData = []
        for (let i = 0; i < endSample; i++) {
          timeData.push((i / sampleRate).toFixed(2))
        }
        
        // 准备系列数据
        const series = channels.map((ch, index) => {
          const color = this.getColor(index + 10) // 使用不同的颜色
          const channelData = fnirsRaw[ch].slice(0, endSample)
          console.log('%c [SignalMonitorView] fNIRS通道' + (ch + 1) + '数据长度：', 'color: #1890ff;', channelData.length)
          
          return {
            name: `Channel ${ch + 1}`,
            type: 'line',
            data: channelData,
            smooth: true,
            lineStyle: {
              width: 2,
              color
            },
            showSymbol: false
          }
        })
        
        const option = {
          title: {
            text: `fNIRS 信号波形（前${endSample}个点）`,
            left: 'center'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross'
            }
          },
          legend: {
            data: channels.map(ch => `Channel ${ch + 1}`),
            orient: 'vertical',
            right: 10,
            top: 'center'
          },
          grid: {
            left: '3%',
            right: '15%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: timeData,
            axisLabel: {
              formatter: '{value}s'
            }
          },
          yAxis: {
            type: 'value',
            axisLabel: {
              formatter: '{value}'
            }
          },
          series
        }
        
        console.log('%c [SignalMonitorView] fNIRS图表选项：', 'color: #1890ff;', option)
        this.fnirsChart.setOption(option)
        console.log('%c [SignalMonitorView] fNIRS图表更新完成', 'color: #52c41a;')
      },
      updateSignalModules() {
        if (!this.csvData) return
        
        // 计算EEG数据的平均值
        const eegColumns = this.csvData.headers.filter(header => 
          header.toLowerCase().includes('eeg') || header.toLowerCase().includes('脑电')
        )
        
        if (eegColumns.length > 0) {
          const eegData = this.csvData.data.map(row => {
            return eegColumns.reduce((sum, column) => sum + row[column], 0) / eegColumns.length
          })
          const eegAvg = eegData.reduce((sum, val) => sum + val, 0) / eegData.length
          
          // 更新EEG模块数据
          this.signalModules[0].value = eegAvg.toFixed(1)
          this.signalModules[0].status = eegAvg >= 5 && eegAvg <= 8 ? 'normal' : 'warning'
        }
        
        // 这里可以根据CSV数据更新其他模块的数据
        // 例如EOG、HRV、呼吸频率等
      },
      getColor(index) {
        const colors = [
          '#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1',
          '#13c2c2', '#fa8c16', '#eb2f96', '#a0d911', '#2f54eb'
        ]
        return colors[index % colors.length]
      },
      showRecommendations() {
        console.log('%c [SignalMonitorView] 触发查看推荐音乐操作，当前疲劳等级：', 'color: #722ed1;', this.detectionResult.label_name)
        // 占位：根据项目路由结构可跳转到推荐页或展开推荐面板
        try {
          // 在跳转前将当前检测等级写入 localStorage，供推荐页固定使用
          if (this.detectionResult && this.detectionResult.label_name) {
            localStorage.setItem('current_fatigue_level', this.detectionResult.label_name)
            console.log('%c [SignalMonitorView] 已将当前疲劳等级写入localStorage：', 'color: #1890ff;', this.detectionResult.label_name)
          }
          if (this.$router) {
            this.$router.push({ path: '/music-recommendation' })
            console.log('%c [SignalMonitorView] 成功跳转至音乐推荐页面', 'color: #52c41a;')
          } else {
            console.warn('%c [SignalMonitorView] 未找到$router实例，无法跳转', 'color: #faad14;')
          }
        } catch (e) {
          // 如果路由不存在则提示
          console.error('%c [SignalMonitorView] 跳转音乐推荐页面失败：', 'color: #f5222d;', e)
          ElMessage.info('请在推荐页面查看推荐列表')
        }
      },

      // 根据标签获取概率条颜色
      getProbabilityColor(label) {
        const colorMap = {
          '静息态': '#409EFF',  // 蓝色
          '正常': '#67C23A',     // 绿色
          '轻度疲劳': '#E6A23C', // 黄色
          '中度疲劳': '#F56C6C',  // 橙色
          '重度疲劳': '#F56C6C',  // 红色
          '疲劳恢复期': '#909399', // 灰色
          '其他': '#909399'       // 灰色
        };
        return colorMap[label] || '#909399';
      },
      
      // 获取推荐按钮文本
      getRecommendationButtonText() {
        const label = this.detectionResult?.label;
        if (!label) return '推荐音乐';
        
        // 依据结果跳转到对应疲劳等级的音乐推荐
        if (label === '静息态' || label === '正常' || label === '疲劳恢复期' || label === '轻度疲劳') {
          return '跳转至轻度疲劳推荐音乐';
        } else if (label === '中度疲劳') {
          return '跳转至中度疲劳推荐音乐';
        } else if (label === '重度疲劳') {
          return '跳转至重度疲劳推荐音乐';
        }
        return '推荐音乐';
      },
      
      // 跳转到对应疲劳等级的音乐推荐
      navigateToRecommendation() {
        const label = this.detectionResult?.label;
        if (!label) return;
        
        // 依据结果跳转到对应疲劳等级的音乐推荐
        let fatigueLevel = label;
        if (label === '静息态' || label === '正常' || label === '疲劳恢复期') {
          fatigueLevel = '轻度疲劳';
        }
        
        // 将中文疲劳等级转换为英文对应值，以便后端API使用
        const fatigueLevelMap = {
          '轻度疲劳': 'Light',
          '中度疲劳': 'Medium',
          '重度疲劳': 'Heavy'
        };
        
        const englishFatigueLevel = fatigueLevelMap[fatigueLevel] || 'light';
        
        console.log('%c [SignalMonitorView] 跳转到音乐推荐，疲劳等级：', 'color: #722ed1;', fatigueLevel);
        console.log('%c [SignalMonitorView] 转换为英文疲劳等级：', 'color: #1890ff;', englishFatigueLevel);
        console.log('%c [SignalMonitorView] 选择的场景：', 'color: #1890ff;', this.selectedScene);
        
        // 在跳转前将当前检测等级和场景写入 localStorage，供推荐页使用
        localStorage.setItem('current_fatigue_level', englishFatigueLevel);
        localStorage.setItem('current_scene', this.selectedScene);
        console.log('%c [SignalMonitorView] 已将当前疲劳等级和场景写入localStorage：', 'color: #1890ff;', {
          fatigueLevel: englishFatigueLevel,
          scene: this.selectedScene
        });
        
        try {
          if (this.$router) {
            this.$router.push({ 
              path: '/music-recommendation',
              query: {
                fatigue_level: englishFatigueLevel,
                scene: this.selectedScene
              }
            });
            console.log('%c [SignalMonitorView] 成功跳转至音乐推荐页面', 'color: #52c41a;');
          } else {
            console.warn('%c [SignalMonitorView] 未找到$router实例，无法跳转', 'color: #faad14;');
          }
        } catch (e) {
          // 如果路由不存在则提示
          console.error('%c [SignalMonitorView] 跳转音乐推荐页面失败：', 'color: #f5222d;', e);
          ElMessage.info('请在推荐页面查看推荐列表');
        }
      },
      
      // 清空暂存在页面的数据可视化
      clearData() {
        console.log('%c [SignalMonitorView] 开始清空数据', 'color: #f5222d;');
        
        // 清空本地存储的数据
        localStorage.removeItem('chartData');
        localStorage.removeItem('detectionResult');
        localStorage.removeItem('current_fatigue_level');
        localStorage.removeItem('current_scene');
        
        // 清空组件状态
        this.csvData = null;
        this.detectionResult = null;
        this.selectedFile = null;
        this.selectedFileName = '';
        this.selectedScene = '';
        
        // 销毁图表实例
        if (this.eegChart) {
          this.eegChart.dispose();
          this.eegChart = null;
        }
        if (this.fnirsChart) {
          this.fnirsChart.dispose();
          this.fnirsChart = null;
        }
        
        console.log('%c [SignalMonitorView] 数据清空完成', 'color: #52c41a;');
        ElMessage.success('数据已清空');
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
          height: 300px;
          margin-bottom: 20px;
          border-left: 4px solid var(--el-color-primary);
          transition: box-shadow 0.3s ease;
          
          &:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
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
            padding: 0;
            height: calc(100% - 57px);
            display: flex;
            flex-direction: column;
            justify-content: center;
          }
          
          .chart {
            width: 100%;
            height: 100%;
            border-radius: 0;
            min-height: 200px;
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

/* 数据可视化区域样式 */
.data-visualization {
  margin-bottom: 20px;
  
  .visualization-card {
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    
    :deep(.el-card__body) {
      padding: 20px;
    }
    
    .chart-container {
      margin-bottom: 20px;
      
      h3 {
        margin: 0 0 16px 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .chart {
        width: 100%;
        height: 400px;
        border-radius: 4px;
        min-height: 400px;
      }
    }
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
      height: 250px;
    }
  }
  
  .data-visualization {
    .visualization-card {
      :deep(.el-card__body) {
        padding: 16px;
      }
      
      .chart-container {
        .chart {
          height: 300px;
          min-height: 300px;
        }
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
      height: 200px;
    }
  }
}

/* 暗模式适配 */
.theme-dark {
  .signal-monitor-view {
    background: var(--bg-page);
  }
  
  .top-section {
    background: var(--bg-card);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    
    .header-content {
      .page-title {
        :deep(.el-page-header__content) {
          color: var(--text-primary);
        }
      }
      
      .status-info {
        .device-status {
          color: var(--text-secondary);
        }
      }
    }
    
    .monitor-info {
      color: var(--text-regular);
    }
  }
  
  .signal-modules {
    .signal-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      
      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
      }
      
      :deep(.el-card__header) {
        background: rgba(30, 41, 59, 0.8);
        border-bottom: 1px solid var(--border-color);
        
        .card-header {
          .signal-name {
            color: var(--text-primary);
          }
        }
      }
    }
  }
  
  .bottom-section {
    background: var(--bg-card);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    
    .timeline-section {
      .timeline-header {
        .timeline-title {
          color: var(--text-primary);
        }
        
        .current-time {
          color: var(--text-regular);
        }
      }
      
      .timeline {
        .time-marks {
          .time-mark {
            color: var(--text-secondary);
            
            &.current {
              color: var(--el-color-danger);
            }
          }
        }
        
        .timeline-progress {
          background: rgba(255, 255, 255, 0.1);
          
          .progress-line {
            background: var(--el-color-primary);
          }
        }
      }
    }
  }
}
</style>
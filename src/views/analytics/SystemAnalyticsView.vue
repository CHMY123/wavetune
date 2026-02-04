<template>
  <div class="system-analytics-view">
    <div class="view-header">
      <h1>系统分析</h1>
      <div class="filter-controls">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="handleDateChange"
          style="width: 280px; margin-right: 16px;"
        />
        <el-button type="primary" @click="loadSystemAnalytics">
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 关键指标卡片 -->
    <div class="metrics-grid">
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ systemStats.totalOperations || 0 }}</div>
          <div class="metric-label">操作总次数</div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ systemStats.errorCount || 0 }}</div>
          <div class="metric-label">错误次数</div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ systemStats.errorRate || 0 }}%</div>
          <div class="metric-label">错误率</div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ systemStats.averageResponseTime || 0 }}ms</div>
          <div class="metric-label">平均响应时间</div>
        </div>
      </el-card>
    </div>

    <!-- 操作类型分布 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <h2>操作类型分布</h2>
        </div>
      </template>
      <div class="chart-container">
        <div ref="operationTypeChartRef" class="chart" style="height: 400px;"></div>
      </div>
    </el-card>

    <!-- API响应时间趋势 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <h2>API响应时间趋势</h2>
        </div>
      </template>
      <div class="chart-container">
        <div ref="responseTimeChartRef" class="chart" style="height: 400px;"></div>
      </div>
    </el-card>

    <!-- 系统错误率趋势 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <h2>系统错误率趋势</h2>
        </div>
      </template>
      <div class="chart-container">
        <div ref="errorRateChartRef" class="chart" style="height: 400px;"></div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { useAnalyticsStore } from '@/stores/analyticsStore'

const analyticsStore = useAnalyticsStore()

// 数据状态
const systemStats = ref({})
const dateRange = ref([])

// 图表引用
const operationTypeChartRef = ref(null)
const responseTimeChartRef = ref(null)
const errorRateChartRef = ref(null)

// 图表实例
let operationTypeChart = null
let responseTimeChart = null
let errorRateChart = null

// 加载系统分析数据
const loadSystemAnalytics = async () => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const data = await analyticsStore.getSystemStats(params)
    systemStats.value = data
    updateCharts(data)
  } catch (error) {
    console.error('加载系统分析数据失败:', error)
  }
}

// 处理日期范围变化
const handleDateChange = () => {
  loadSystemAnalytics()
}

// 更新图表
const updateCharts = (data) => {
  updateOperationTypeChart(data.operationTypeDistribution || {})
  updateResponseTimeChart(data.responseTimeTrend || [])
  updateErrorRateChart(data.errorRateTrend || [])
}

// 更新操作类型分布图
const updateOperationTypeChart = (typeData) => {
  if (!operationTypeChartRef.value) return

  if (!operationTypeChart) {
    operationTypeChart = echarts.init(operationTypeChartRef.value)
  }

  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '操作类型',
        type: 'pie',
        radius: '50%',
        data: Object.entries(typeData).map(([type, count]) => ({ name: type, value: count })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  operationTypeChart.setOption(option)
}

// 更新API响应时间趋势图
const updateResponseTimeChart = (responseData) => {
  if (!responseTimeChartRef.value) return

  if (!responseTimeChart) {
    responseTimeChart = echarts.init(responseTimeChartRef.value)
  }

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['响应时间']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: responseData.map(item => item.date)
    },
    yAxis: {
      type: 'value',
      name: '响应时间 (ms)'
    },
    series: [
      {
        name: '响应时间',
        type: 'line',
        data: responseData.map(item => item.response_time || 0),
        smooth: true,
        itemStyle: {
          color: '#3b82f6'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59, 130, 246, 0.5)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0.1)' }
          ])
        }
      }
    ]
  }

  responseTimeChart.setOption(option)
}

// 更新系统错误率趋势图
const updateErrorRateChart = (errorRateData) => {
  if (!errorRateChartRef.value) return

  if (!errorRateChart) {
    errorRateChart = echarts.init(errorRateChartRef.value)
  }

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['错误率']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: errorRateData.map(item => item.date)
    },
    yAxis: {
      type: 'value',
      name: '错误率 (%)'
    },
    series: [
      {
        name: '错误率',
        type: 'line',
        data: errorRateData.map(item => item.error_rate || 0),
        smooth: true,
        itemStyle: {
          color: '#ef4444'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(239, 68, 68, 0.5)' },
            { offset: 1, color: 'rgba(239, 68, 68, 0.1)' }
          ])
        }
      }
    ]
  }

  errorRateChart.setOption(option)
}

// 响应式调整图表大小
const handleResize = () => {
  operationTypeChart?.resize()
  responseTimeChart?.resize()
  errorRateChart?.resize()
}

// 组件挂载时加载数据
onMounted(() => {
  // 设置默认日期范围为最近30天
  const endDate = new Date()
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 30)
  dateRange.value = [
    startDate.toISOString().split('T')[0],
    endDate.toISOString().split('T')[0]
  ]
  
  loadSystemAnalytics()
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  operationTypeChart?.dispose()
  responseTimeChart?.dispose()
  errorRateChart?.dispose()
})
</script>

<style lang="scss" scoped>
.system-analytics-view {
  .view-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    h1 {
      font-size: 24px;
      font-weight: 600;
      margin: 0;
      color: #1f2937;
    }

    .filter-controls {
      display: flex;
      align-items: center;
    }
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }

  .metric-card {
    border-radius: 8px;
    overflow: hidden;

    .metric-content {
      padding: 20px;
      text-align: center;

      .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 8px;
      }

      .metric-label {
        font-size: 14px;
        color: #6b7280;
      }
    }
  }

  .chart-card {
    margin-bottom: 24px;
    border-radius: 8px;
    overflow: hidden;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      h2 {
        font-size: 18px;
        font-weight: 600;
        margin: 0;
        color: #1f2937;
      }
    }

    .chart-container {
      padding: 20px;
    }

    .chart {
      width: 100%;
    }
  }
}
</style>

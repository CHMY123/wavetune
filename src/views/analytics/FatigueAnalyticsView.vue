<template>
  <div class="fatigue-analytics-view">
    <div class="view-header">
      <h1>疲劳检测分析</h1>
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
        <el-button type="primary" @click="loadFatigueAnalytics">
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 关键指标卡片 -->
    <div class="metrics-grid">
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ fatigueStats.totalTests || 0 }}</div>
          <div class="metric-label">检测总次数</div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ fatigueStats.averageFatigueLevel || 0 }}</div>
          <div class="metric-label">平均疲劳等级</div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ fatigueStats.heavyFatigueCount || 0 }}</div>
          <div class="metric-label">重度疲劳次数</div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ fatigueStats.interventionCount || 0 }}</div>
          <div class="metric-label">干预次数</div>
        </div>
      </el-card>
    </div>

    <!-- 疲劳等级分布 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <h2>疲劳等级分布</h2>
        </div>
      </template>
      <div class="chart-container">
        <div ref="fatigueLevelChartRef" class="chart" style="height: 400px;"></div>
      </div>
    </el-card>

    <!-- 疲劳检测趋势 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <h2>疲劳检测趋势</h2>
        </div>
      </template>
      <div class="chart-container">
        <div ref="fatigueTrendChartRef" class="chart" style="height: 400px;"></div>
      </div>
    </el-card>

    <!-- 不同人群疲劳对比 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <h2>不同人群疲劳对比</h2>
        </div>
      </template>
      <div class="chart-container">
        <div ref="fatigueComparisonChartRef" class="chart" style="height: 400px;"></div>
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
const fatigueStats = ref({})
const dateRange = ref([])

// 图表引用
const fatigueLevelChartRef = ref(null)
const fatigueTrendChartRef = ref(null)
const fatigueComparisonChartRef = ref(null)

// 图表实例
let fatigueLevelChart = null
let fatigueTrendChart = null
let fatigueComparisonChart = null

// 加载疲劳分析数据
const loadFatigueAnalytics = async () => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const data = await analyticsStore.getFatigueStats(params)
    fatigueStats.value = data
    updateCharts(data)
  } catch (error) {
    console.error('加载疲劳分析数据失败:', error)
  }
}

// 处理日期范围变化
const handleDateChange = () => {
  loadFatigueAnalytics()
}

// 更新图表
const updateCharts = (data) => {
  updateFatigueLevelChart(data.fatigueLevelDistribution || {})
  updateFatigueTrendChart(data.fatigueTrend || [])
  updateFatigueComparisonChart(data.fatigueComparison || {})
}

// 更新疲劳等级分布图
const updateFatigueLevelChart = (levelData) => {
  if (!fatigueLevelChartRef.value) return

  if (!fatigueLevelChart) {
    fatigueLevelChart = echarts.init(fatigueLevelChartRef.value)
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
        name: '疲劳等级',
        type: 'pie',
        radius: '50%',
        data: [
          { name: '轻度疲劳', value: levelData.light || 0, itemStyle: { color: '#10b981' } },
          { name: '中度疲劳', value: levelData.medium || 0, itemStyle: { color: '#f59e0b' } },
          { name: '重度疲劳', value: levelData.heavy || 0, itemStyle: { color: '#ef4444' } }
        ],
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

  fatigueLevelChart.setOption(option)
}

// 更新疲劳检测趋势图
const updateFatigueTrendChart = (trendData) => {
  if (!fatigueTrendChartRef.value) return

  if (!fatigueTrendChart) {
    fatigueTrendChart = echarts.init(fatigueTrendChartRef.value)
  }

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['轻度疲劳', '中度疲劳', '重度疲劳']
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
      data: trendData.map(item => item.date)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '轻度疲劳',
        type: 'line',
        data: trendData.map(item => item.light || 0),
        smooth: true,
        itemStyle: {
          color: '#10b981'
        }
      },
      {
        name: '中度疲劳',
        type: 'line',
        data: trendData.map(item => item.medium || 0),
        smooth: true,
        itemStyle: {
          color: '#f59e0b'
        }
      },
      {
        name: '重度疲劳',
        type: 'line',
        data: trendData.map(item => item.heavy || 0),
        smooth: true,
        itemStyle: {
          color: '#ef4444'
        }
      }
    ]
  }

  fatigueTrendChart.setOption(option)
}

// 更新不同人群疲劳对比图
const updateFatigueComparisonChart = (comparisonData) => {
  if (!fatigueComparisonChartRef.value) return

  if (!fatigueComparisonChart) {
    fatigueComparisonChart = echarts.init(fatigueComparisonChartRef.value)
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['轻度疲劳', '中度疲劳', '重度疲劳']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: Object.keys(comparisonData)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '轻度疲劳',
        type: 'bar',
        stack: 'total',
        data: Object.values(comparisonData).map(item => item.light || 0),
        itemStyle: { color: '#10b981' }
      },
      {
        name: '中度疲劳',
        type: 'bar',
        stack: 'total',
        data: Object.values(comparisonData).map(item => item.medium || 0),
        itemStyle: { color: '#f59e0b' }
      },
      {
        name: '重度疲劳',
        type: 'bar',
        stack: 'total',
        data: Object.values(comparisonData).map(item => item.heavy || 0),
        itemStyle: { color: '#ef4444' }
      }
    ]
  }

  fatigueComparisonChart.setOption(option)
}

// 响应式调整图表大小
const handleResize = () => {
  fatigueLevelChart?.resize()
  fatigueTrendChart?.resize()
  fatigueComparisonChart?.resize()
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
  
  loadFatigueAnalytics()
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  fatigueLevelChart?.dispose()
  fatigueTrendChart?.dispose()
  fatigueComparisonChart?.dispose()
})
</script>

<style lang="scss" scoped>
.fatigue-analytics-view {
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

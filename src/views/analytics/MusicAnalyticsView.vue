<template>
  <div class="music-analytics-view">
    <div class="view-header">
      <h1>音乐分析</h1>
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
        <el-button type="primary" @click="loadMusicAnalytics">
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 关键指标卡片 -->
    <div class="metrics-grid">
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ musicStats.totalMusic || 0 }}</div>
          <div class="metric-label">音乐总数</div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ musicStats.totalPlays || 0 }}</div>
          <div class="metric-label">总播放量</div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ musicStats.averagePlays || 0 }}</div>
          <div class="metric-label">平均播放量</div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ musicStats.topPlayCount || 0 }}</div>
          <div class="metric-label">最高播放量</div>
        </div>
      </el-card>
    </div>

    <!-- 播放量排行榜 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <h2>播放量排行榜</h2>
        </div>
      </template>
      <div class="chart-container">
        <div ref="playRankingChartRef" class="chart" style="height: 400px;"></div>
      </div>
    </el-card>

    <!-- 音乐类别分布 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <h2>音乐类别分布</h2>
        </div>
      </template>
      <div class="chart-container">
        <div ref="categoryDistributionChartRef" class="chart" style="height: 400px;"></div>
      </div>
    </el-card>

    <!-- 播放时长趋势 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <h2>播放时长趋势</h2>
        </div>
      </template>
      <div class="chart-container">
        <div ref="playDurationChartRef" class="chart" style="height: 400px;"></div>
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
const musicStats = ref({})
const dateRange = ref([])

// 图表引用
const playRankingChartRef = ref(null)
const categoryDistributionChartRef = ref(null)
const playDurationChartRef = ref(null)

// 图表实例
let playRankingChart = null
let categoryDistributionChart = null
let playDurationChart = null

// 加载音乐分析数据
const loadMusicAnalytics = async () => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const data = await analyticsStore.getMusicStats(params)
    musicStats.value = data
    updateCharts(data)
  } catch (error) {
    console.error('加载音乐分析数据失败:', error)
  }
}

// 处理日期范围变化
const handleDateChange = () => {
  loadMusicAnalytics()
}

// 更新图表
const updateCharts = (data) => {
  updatePlayRankingChart(data.playRanking || [])
  updateCategoryDistributionChart(data.categoryDistribution || {})
  updatePlayDurationChart(data.playDurationTrend || [])
}

// 更新播放量排行榜
const updatePlayRankingChart = (rankingData) => {
  if (!playRankingChartRef.value) return

  if (!playRankingChart) {
    playRankingChart = echarts.init(playRankingChartRef.value)
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: rankingData.slice(0, 10).map(item => item.title || '未知歌曲')
    },
    series: [
      {
        name: '播放量',
        type: 'bar',
        data: rankingData.slice(0, 10).map(item => item.play_count || 0),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#3b82f6' },
            { offset: 1, color: '#93c5fd' }
          ])
        }
      }
    ]
  }

  playRankingChart.setOption(option)
}

// 更新音乐类别分布图
const updateCategoryDistributionChart = (categoryData) => {
  if (!categoryDistributionChartRef.value) return

  if (!categoryDistributionChart) {
    categoryDistributionChart = echarts.init(categoryDistributionChartRef.value)
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
        name: '音乐类别',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: Object.entries(categoryData).map(([category, count]) => ({ name: category, value: count }))
      }
    ]
  }

  categoryDistributionChart.setOption(option)
}

// 更新播放时长趋势图
const updatePlayDurationChart = (durationData) => {
  if (!playDurationChartRef.value) return

  if (!playDurationChart) {
    playDurationChart = echarts.init(playDurationChartRef.value)
  }

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['播放时长']
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
      data: durationData.map(item => item.date)
    },
    yAxis: {
      type: 'value',
      name: '时长（分钟）'
    },
    series: [
      {
        name: '播放时长',
        type: 'line',
        data: durationData.map(item => item.duration || 0),
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59, 130, 246, 0.5)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0.1)' }
          ])
        },
        itemStyle: {
          color: '#3b82f6'
        }
      }
    ]
  }

  playDurationChart.setOption(option)
}

// 响应式调整图表大小
const handleResize = () => {
  playRankingChart?.resize()
  categoryDistributionChart?.resize()
  playDurationChart?.resize()
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
  
  loadMusicAnalytics()
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  playRankingChart?.dispose()
  categoryDistributionChart?.dispose()
  playDurationChart?.dispose()
})
</script>

<style lang="scss" scoped>
.music-analytics-view {
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

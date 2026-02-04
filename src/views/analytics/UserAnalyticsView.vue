<template>
  <div class="user-analytics-view">
    <div class="view-header">
      <h1>用户分析</h1>
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
        <el-button type="primary" @click="loadUserAnalytics">
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 关键指标卡片 -->
    <div class="metrics-grid">
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ userStats.totalUsers || 0 }}</div>
          <div class="metric-label">总用户数</div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ userStats.activeUsers || 0 }}</div>
          <div class="metric-label">活跃用户数</div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ userStats.newUsers || 0 }}</div>
          <div class="metric-label">新增用户数</div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-value">{{ userStats.adminUsers || 0 }}</div>
          <div class="metric-label">管理员用户</div>
        </div>
      </el-card>
    </div>

    <!-- 用户增长趋势图 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <h2>用户增长趋势</h2>
        </div>
      </template>
      <div class="chart-container">
        <div ref="userGrowthChartRef" class="chart" style="height: 400px;"></div>
      </div>
    </el-card>

    <!-- 用户角色分布 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <h2>用户角色分布</h2>
        </div>
      </template>
      <div class="chart-container">
        <div ref="roleDistributionChartRef" class="chart" style="height: 400px;"></div>
      </div>
    </el-card>

    <!-- 用户活跃度热力图 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <h2>用户活跃度热力图</h2>
        </div>
      </template>
      <div class="chart-container">
        <div ref="activityHeatmapChartRef" class="chart" style="height: 400px;"></div>
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
const userStats = ref({})
const dateRange = ref([])

// 图表引用
const userGrowthChartRef = ref(null)
const roleDistributionChartRef = ref(null)
const activityHeatmapChartRef = ref(null)

// 图表实例
let userGrowthChart = null
let roleDistributionChart = null
let activityHeatmapChart = null

// 加载用户分析数据
const loadUserAnalytics = async () => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const data = await analyticsStore.getUserStats(params)
    userStats.value = data
    updateCharts(data)
  } catch (error) {
    console.error('加载用户分析数据失败:', error)
  }
}

// 处理日期范围变化
const handleDateChange = () => {
  loadUserAnalytics()
}

// 更新图表
const updateCharts = (data) => {
  updateUserGrowthChart(data.userGrowth || [])
  updateRoleDistributionChart(data.roleDistribution || {})
  updateActivityHeatmapChart(data.activityHeatmap || [])
}

// 更新用户增长趋势图
const updateUserGrowthChart = (growthData) => {
  if (!userGrowthChartRef.value) return

  if (!userGrowthChart) {
    userGrowthChart = echarts.init(userGrowthChartRef.value)
  }

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['新增用户', '活跃用户']
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
      data: growthData.map(item => item.date)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '新增用户',
        type: 'line',
        data: growthData.map(item => item.newUsers || 0),
        smooth: true,
        itemStyle: {
          color: '#3b82f6'
        }
      },
      {
        name: '活跃用户',
        type: 'line',
        data: growthData.map(item => item.activeUsers || 0),
        smooth: true,
        itemStyle: {
          color: '#10b981'
        }
      }
    ]
  }

  userGrowthChart.setOption(option)
}

// 更新用户角色分布图
const updateRoleDistributionChart = (roleData) => {
  if (!roleDistributionChartRef.value) return

  if (!roleDistributionChart) {
    roleDistributionChart = echarts.init(roleDistributionChartRef.value)
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
        name: '用户角色',
        type: 'pie',
        radius: '50%',
        data: Object.entries(roleData).map(([role, count]) => ({ name: role, value: count })),
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

  roleDistributionChart.setOption(option)
}

// 更新用户活跃度热力图
const updateActivityHeatmapChart = (heatmapData) => {
  if (!activityHeatmapChartRef.value) return

  if (!activityHeatmapChart) {
    activityHeatmapChart = echarts.init(activityHeatmapChartRef.value)
  }

  const option = {
    tooltip: {
      position: 'top'
    },
    grid: {
      height: '50%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      splitArea: {
        show: true
      }
    },
    yAxis: {
      type: 'category',
      data: ['0时', '4时', '8时', '12时', '16时', '20时'],
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: 0,
      max: 100,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '15%'
    },
    series: [
      {
        name: '活跃度',
        type: 'heatmap',
        data: heatmapData.map(item => [item.dayIndex, item.hourIndex, item.value]),
        label: {
          show: true
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  activityHeatmapChart.setOption(option)
}

// 响应式调整图表大小
const handleResize = () => {
  userGrowthChart?.resize()
  roleDistributionChart?.resize()
  activityHeatmapChart?.resize()
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
  
  loadUserAnalytics()
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  userGrowthChart?.dispose()
  roleDistributionChart?.dispose()
  activityHeatmapChart?.dispose()
})
</script>

<style lang="scss" scoped>
.user-analytics-view {
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

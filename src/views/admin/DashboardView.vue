<template>
  <div class="dashboard-view">
    <h1>仪表盘概览</h1>
    
    <!-- 关键指标卡片 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-card-content">
          <div class="stat-info">
            <h3>总用户数</h3>
            <p class="stat-number">{{ dashboardData.user_stats?.total_users || 0 }}</p>
            <p class="stat-desc">今日新增: {{ dashboardData.user_stats?.new_users_today || 0 }}</p>
          </div>
          <div class="stat-icon">
            <el-icon class="icon-large"><User /></el-icon>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-card-content">
          <div class="stat-info">
            <h3>总音乐数</h3>
            <p class="stat-number">{{ dashboardData.music_stats?.total_music || 0 }}</p>
            <p class="stat-desc">总播放量: {{ dashboardData.music_stats?.total_plays || 0 }}</p>
          </div>
          <div class="stat-icon">
            <el-icon class="icon-large"><Headset /></el-icon>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-card-content">
          <div class="stat-info">
            <h3>疲劳检测</h3>
            <p class="stat-number">{{ dashboardData.fatigue_stats?.total_detections || 0 }}</p>
            <p class="stat-desc">平均等级: {{ dashboardData.fatigue_stats?.avg_fatigue_level?.toFixed(1) || 0 }}</p>
          </div>
          <div class="stat-icon">
            <el-icon class="icon-large"><Warning /></el-icon>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-card-content">
          <div class="stat-info">
            <h3>系统操作</h3>
            <p class="stat-number">{{ dashboardData.system_stats?.total_operations || 0 }}</p>
            <p class="stat-desc">错误率: {{ dashboardData.system_stats?.error_rate?.toFixed(1) || 0 }}%</p>
          </div>
          <div class="stat-icon">
            <el-icon class="icon-large"><Operation /></el-icon>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 图表区域 -->
    <div class="charts-section">
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>用户增长趋势</span>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="handleDateChange"
              size="small"
            />
          </div>
        </template>
        <div class="chart-container">
          <el-skeleton :rows="5" animated v-if="loading" />
          <div v-else ref="userGrowthChart" class="chart"></div>
        </div>
      </el-card>
      
      <div class="chart-row">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>用户角色分布</span>
            </div>
          </template>
          <div class="chart-container">
            <el-skeleton :rows="3" animated v-if="loading" />
            <div v-else ref="roleDistributionChart" class="chart"></div>
          </div>
        </el-card>
        
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>疲劳等级分布</span>
            </div>
          </template>
          <div class="chart-container">
            <el-skeleton :rows="3" animated v-if="loading" />
            <div v-else ref="fatigueDistributionChart" class="chart"></div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { User, Headset, Warning, Operation } from '@element-plus/icons-vue';
import * as echarts from 'echarts';
import { useAdminStore } from '@/stores/adminStore';

const router = useRouter();
const adminStore = useAdminStore();

const loading = ref(true);
const dashboardData = ref({});
const dateRange = ref([]);

// 图表实例
const userGrowthChart = ref(null);
const roleDistributionChart = ref(null);
const fatigueDistributionChart = ref(null);
let userGrowthChartInstance = null;
let roleDistributionChartInstance = null;
let fatigueDistributionChartInstance = null;

// 加载仪表盘数据
const loadDashboardData = async () => {
  try {
    loading.value = true;
    const data = await adminStore.getDashboardData();
    dashboardData.value = data;
    updateCharts();
  } catch (error) {
    console.error('加载仪表盘数据失败:', error);
  } finally {
    loading.value = false;
  }
};

// 更新图表
const updateCharts = () => {
  updateUserGrowthChart();
  updateRoleDistributionChart();
  updateFatigueDistributionChart();
};

// 更新用户增长趋势图
const updateUserGrowthChart = () => {
  if (!userGrowthChart.value) return;
  
  if (userGrowthChartInstance) {
    userGrowthChartInstance.dispose();
  }
  
  userGrowthChartInstance = echarts.init(userGrowthChart.value);
  
  const growthTrend = dashboardData.value.user_stats?.growth_trend || [];
  const xAxisData = growthTrend.map(item => item.date);
  const seriesData = growthTrend.map(item => item.count);
  
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
      type: 'category',
      data: xAxisData,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '新增用户数'
    },
    series: [
      {
        name: '新增用户',
        type: 'line',
        data: seriesData,
        smooth: true,
        itemStyle: {
          color: '#3b82f6'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgba(59, 130, 246, 0.5)'
            },
            {
              offset: 1,
              color: 'rgba(59, 130, 246, 0.1)'
            }
          ])
        }
      }
    ]
  };
  
  userGrowthChartInstance.setOption(option);
};

// 更新角色分布图
const updateRoleDistributionChart = () => {
  if (!roleDistributionChart.value) return;
  
  if (roleDistributionChartInstance) {
    roleDistributionChartInstance.dispose();
  }
  
  roleDistributionChartInstance = echarts.init(roleDistributionChart.value);
  
  const roleDistribution = dashboardData.value.user_stats?.role_distribution || {};
  const seriesData = Object.entries(roleDistribution).map(([name, value]) => ({
    name,
    value
  }));
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: Object.keys(roleDistribution)
    },
    series: [
      {
        name: '用户角色',
        type: 'pie',
        radius: '60%',
        data: seriesData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };
  
  roleDistributionChartInstance.setOption(option);
};

// 更新疲劳等级分布图
const updateFatigueDistributionChart = () => {
  if (!fatigueDistributionChart.value) return;
  
  if (fatigueDistributionChartInstance) {
    fatigueDistributionChartInstance.dispose();
  }
  
  fatigueDistributionChartInstance = echarts.init(fatigueDistributionChart.value);
  
  const levelDistribution = dashboardData.value.fatigue_stats?.level_distribution || {};
  const seriesData = Object.entries(levelDistribution).map(([name, value]) => ({
    name: `等级 ${name}`,
    value
  }));
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: seriesData.map(item => item.name)
    },
    series: [
      {
        name: '疲劳等级',
        type: 'pie',
        radius: '60%',
        data: seriesData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };
  
  fatigueDistributionChartInstance.setOption(option);
};

// 处理日期范围变化
const handleDateChange = (val) => {
  if (val && val.length === 2) {
    // 这里可以根据选择的日期范围重新加载数据
    console.log('日期范围变化:', val);
  }
};

// 窗口大小变化时重新调整图表大小
const handleResize = () => {
  userGrowthChartInstance?.resize();
  roleDistributionChartInstance?.resize();
  fatigueDistributionChartInstance?.resize();
};

onMounted(() => {
  loadDashboardData();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  userGrowthChartInstance?.dispose();
  roleDistributionChartInstance?.dispose();
  fatigueDistributionChartInstance?.dispose();
});
</script>

<style lang="scss" scoped>
.dashboard-view {
  h1 {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 24px;
    color: #1f2937;
  }
  
  .stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
    
    .stat-card {
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
      }
      
      .stat-card-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .stat-info {
          h3 {
            font-size: 14px;
            font-weight: 500;
            color: #6b7280;
            margin: 0 0 8px 0;
          }
          
          .stat-number {
            font-size: 28px;
            font-weight: 700;
            color: #1f2937;
            margin: 0 0 4px 0;
          }
          
          .stat-desc {
            font-size: 12px;
            color: #9ca3af;
            margin: 0;
          }
        }
        
        .stat-icon {
          .icon-large {
            font-size: 36px;
            color: #3b82f6;
          }
        }
      }
    }
  }
  
  .charts-section {
    .chart-card {
      margin-bottom: 24px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 16px;
        font-weight: 600;
      }
      
      .chart-container {
        height: 300px;
        
        .chart {
          width: 100%;
          height: 100%;
        }
      }
    }
    
    .chart-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      
      @media (max-width: 768px) {
        grid-template-columns: 1fr;
      }
    }
  }
}
</style>

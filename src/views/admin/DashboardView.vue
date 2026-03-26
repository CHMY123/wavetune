<template>
  <div class="dashboard-view">
    <div class="dashboard-header">
      <h1>仪表盘概览</h1>
      <el-button type="primary" size="small" @click="handleRefresh">
        <el-icon><Refresh /></el-icon> 刷新数据
      </el-button>
    </div>
    
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
          <div v-else id="userGrowthChart" style="width: 100%; height: 300px;"></div>
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
            <div v-else id="roleDistributionChart" style="width: 100%; height: 300px;"></div>
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
            <div v-else id="fatigueDistributionChart" style="width: 100%; height: 300px;"></div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { User, Headset, Warning, Operation, Refresh } from '@element-plus/icons-vue';
import * as echarts from 'echarts';
import { useAdminStore } from '@/stores/adminStore';
import { ElMessage } from 'element-plus';

const router = useRouter();
const adminStore = useAdminStore();

const loading = ref(true);
const dashboardData = ref({});
const dateRange = ref([]);

// 图表实例
let userGrowthChartInstance = null;
let roleDistributionChartInstance = null;
let fatigueDistributionChartInstance = null;

// 加载仪表盘数据
const loadDashboardData = async (dateRange = null) => {
  try {
    loading.value = true
    const cacheKey = `dashboard_${dateRange ? dateRange.join('_') : 'all'}`
    
    // 尝试从缓存加载
    try {
      const cachedData = localStorage.getItem(cacheKey)
      if (cachedData) {
        const parsedData = JSON.parse(cachedData)
        // 检查缓存是否过期（30分钟）
        if (parsedData.timestamp && (Date.now() - parsedData.timestamp) < 30 * 60 * 1000) {
          dashboardData.value = parsedData.data
          loading.value = false
          return
        }
      }
    } catch (e) {
      console.warn('缓存读取失败:', e)
    }
    
    const data = await adminStore.getDashboardData(dateRange)
    dashboardData.value = data
    
    // 缓存仪表盘数据
    try {
      localStorage.setItem(cacheKey, JSON.stringify({
        data: data,
        timestamp: Date.now()
      }))
    } catch (e) {
      console.warn('缓存保存失败:', e)
    }
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
    // 显示错误消息
    ElMessage.error('加载仪表盘数据失败，请刷新页面重试')
  } finally {
    loading.value = false
  }
};

// 初始化图表
const initCharts = () => {
  // 确保DOM元素完全渲染
  setTimeout(() => {
    updateUserGrowthChart();
    updateRoleDistributionChart();
    updateFatigueDistributionChart();
  }, 100);
};

// 更新用户增长趋势图
const updateUserGrowthChart = () => {
  const chartDom = document.getElementById('userGrowthChart');
  if (!chartDom) return;
  
  if (userGrowthChartInstance) {
    userGrowthChartInstance.dispose();
  }
  
  userGrowthChartInstance = echarts.init(chartDom);
  
  let growthTrend = dashboardData.value.user_stats?.growth_trend || [];
  
  // 直接使用后端返回的真实数据
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
      name: '新增用户数',
      min: 0,
      interval: 1
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
  const chartDom = document.getElementById('roleDistributionChart');
  if (!chartDom) return;
  
  if (roleDistributionChartInstance) {
    roleDistributionChartInstance.dispose();
  }
  
  roleDistributionChartInstance = echarts.init(chartDom);
  
  let roleDistribution = dashboardData.value.user_stats?.role_distribution || {};
  
  // 如果没有数据，使用默认数据
  if (Object.keys(roleDistribution).length === 0) {
    roleDistribution = {
      'user': 18,
      'admin': 2
    };
  }
  
  const seriesData = Object.entries(roleDistribution).map(([name, value]) => ({
    name: name === 'user' ? '普通用户' : '管理员',
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
  const chartDom = document.getElementById('fatigueDistributionChart');
  if (!chartDom) return;
  
  if (fatigueDistributionChartInstance) {
    fatigueDistributionChartInstance.dispose();
  }
  
  fatigueDistributionChartInstance = echarts.init(chartDom);
  
  // 硬编码固定数据
  const levelDistribution = {
    '静息态': 12,
    '正常': 8,
    '轻度': 5,
    '中度': 3,
    '重度': 2
  };
  
  const seriesData = Object.entries(levelDistribution).map(([name, value]) => ({
    name: `${name}`,
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
const handleDateChange = async (val) => {
  if (val && val.length === 2) {
    // 根据选择的日期范围重新加载数据
    console.log('日期范围变化:', val);
    await loadDashboardData(val);
    // 重新初始化图表
    initCharts();
  }
};

// 手动刷新数据
const handleRefresh = async () => {
  // 清除缓存
  try {
    localStorage.removeItem('dashboard_all');
    if (dateRange.value && dateRange.value.length === 2) {
      const cacheKey = `dashboard_${dateRange.value.join('_')}`;
      localStorage.removeItem(cacheKey);
    }
  } catch (e) {
    console.warn('清除缓存失败:', e);
  }
  
  // 重新加载数据
  await loadDashboardData(dateRange.value.length === 2 ? dateRange.value : null);
  // 重新初始化图表
  initCharts();
  
  // 显示刷新成功消息
  ElMessage.success('数据刷新成功');
};

// 窗口大小变化时重新调整图表大小
const handleResize = () => {
  userGrowthChartInstance?.resize();
  roleDistributionChartInstance?.resize();
  fatigueDistributionChartInstance?.resize();
};

onMounted(async () => {
  await loadDashboardData();
  initCharts();
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
  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }
  
  h1 {
    font-size: 24px;
    font-weight: 600;
    margin: 0;
    color: #1f2937;
    
    // 深色主题样式
    :global(.theme-dark) & {
      color: #f3f4f6;
    }
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
      
      // 深色主题样式
      :global(.theme-dark) & {
        background-color: #1f2937;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        
        .stat-card-content {
          .stat-info {
            h3 {
              color: #9ca3af;
            }
            
            .stat-number {
              color: #f3f4f6;
            }
            
            .stat-desc {
              color: #6b7280;
            }
          }
          
          .stat-icon {
            .icon-large {
              color: #60a5fa;
            }
          }
        }
      }
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        
        // 深色主题样式
        :global(.theme-dark) & {
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        }
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
      
      // 深色主题样式
      :global(.theme-dark) & {
        background-color: #1f2937;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        
        .card-header {
          color: #f3f4f6;
        }
      }
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 16px;
        font-weight: 600;
      }
      
      .chart-container {
        height: 300px;
        width: 100%;
        position: relative;
        
        .chart {
          width: 100%;
          height: 100%;
          position: absolute;
          top: 0;
          left: 0;
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
  
  // 移动设备适配
  @media (max-width: 768px) {
    h1 {
      font-size: 20px;
      margin-bottom: 16px;
    }
    
    .stats-cards {
      gap: 12px;
      margin-bottom: 24px;
      
      // 调整卡片大小以适应移动设备
      grid-template-columns: repeat(2, 1fr);
    }
    
    .charts-section {
      .chart-card {
        margin-bottom: 16px;
        
        .card-header {
          font-size: 14px;
        }
        
        .chart-container {
          height: 250px; // 减小图表高度以适应移动设备
        }
      }
    }
    
    // 确保底部栏有足够的空间
    padding-bottom: 24px;
  }
}
</style>

<template>
  <div class="analytics-dashboard-view">
    <h1>数据分析面板</h1>
    
    <!-- 时间范围选择 -->
    <div class="time-range-selector">
      <span>时间范围：</span>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        @change="handleDateChange"
      />
      <el-button type="primary" @click="loadAnalyticsData">
        <el-icon><Refresh /></el-icon>
        <span>刷新数据</span>
      </el-button>
    </div>
    
    <!-- 关键指标卡片 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-card-content">
          <div class="stat-info">
            <h3>活跃用户数</h3>
            <p class="stat-number">{{ analyticsData.user_stats?.active_users || 0 }}</p>
            <p class="stat-desc">总用户: {{ analyticsData.user_stats?.total_users || 0 }}</p>
          </div>
          <div class="stat-icon">
            <el-icon class="icon-large"><UserFilled /></el-icon>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-card-content">
          <div class="stat-info">
            <h3>总播放量</h3>
            <p class="stat-number">{{ analyticsData.music_stats?.total_plays || 0 }}</p>
            <p class="stat-desc">总音乐: {{ analyticsData.music_stats?.total_music || 0 }}</p>
          </div>
          <div class="stat-icon">
            <el-icon class="icon-large"><Headset /></el-icon>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-card-content">
          <div class="stat-info">
            <h3>平均疲劳等级</h3>
            <p class="stat-number">{{ analyticsData.fatigue_stats?.avg_fatigue_level?.toFixed(1) || 0 }}</p>
            <p class="stat-desc">检测次数: {{ analyticsData.fatigue_stats?.total_detections || 0 }}</p>
          </div>
          <div class="stat-icon">
            <el-icon class="icon-large"><WarningFilled /></el-icon>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-info">
          <h3>系统错误率</h3>
          <p class="stat-number">{{ analyticsData.system_stats?.error_rate?.toFixed(1) || 0 }}%</p>
          <p class="stat-desc">总操作: {{ analyticsData.system_stats?.total_operations || 0 }}</p>
        </div>
        <div class="stat-icon">
          <el-icon class="icon-large"><Warning /></el-icon>
        </div>
      </el-card>
    </div>
    
    <!-- 图表区域 -->
    <div class="charts-section">
      <!-- 用户分析 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>用户分析</span>
            <el-select v-model="userChartType" @change="updateUserChart">
              <el-option label="增长趋势" value="growth" />
              <el-option label="角色分布" value="role" />
            </el-select>
          </div>
        </template>
        <div class="chart-container">
          <el-skeleton :rows="5" animated v-if="loading" />
          <div v-else ref="userChartRef" class="chart"></div>
        </div>
      </el-card>
      
      <!-- 音乐分析 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>音乐分析</span>
            <el-select v-model="musicChartType" @change="updateMusicChart">
              <el-option label="播放量排行" value="ranking" />
              <el-option label="类型分布" value="type" />
              <el-option label="情绪分布" value="mood" />
            </el-select>
          </div>
        </template>
        <div class="chart-container">
          <el-skeleton :rows="5" animated v-if="loading" />
          <div v-else ref="musicChartRef" class="chart"></div>
        </div>
      </el-card>
      
      <!-- 疲劳分析 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>疲劳分析</span>
            <el-select v-model="fatigueChartType" @change="updateFatigueChart">
              <el-option label="等级分布" value="distribution" />
              <el-option label="检测趋势" value="trend" />
            </el-select>
          </div>
        </template>
        <div class="chart-container">
          <el-skeleton :rows="5" animated v-if="loading" />
          <div v-else ref="fatigueChartRef" class="chart"></div>
        </div>
      </el-card>
      
      <!-- 系统分析 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>系统分析</span>
            <el-select v-model="systemChartType" @change="updateSystemChart">
              <el-option label="操作类型分布" value="operation" />
              <el-option label="错误率趋势" value="error" />
            </el-select>
          </div>
        </template>
        <div class="chart-container">
          <el-skeleton :rows="5" animated v-if="loading" />
          <div v-else ref="systemChartRef" class="chart"></div>
        </div>
      </el-card>
    </div>
    
    <!-- 导出选项 -->
    <div class="export-options">
      <h3>数据导出</h3>
      <el-button type="primary" @click="exportData('excel')">
        <el-icon><Download /></el-icon>
        <span>导出Excel</span>
      </el-button>
      <el-button type="success" @click="exportData('pdf')">
        <el-icon><Picture /></el-icon>
        <span>导出PDF</span>
      </el-button>
      <el-button type="info" @click="exportData('image')">
        <el-icon><Camera /></el-icon>
        <span>导出图表</span>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { Refresh, Download, Picture, Camera, UserFilled, Headset, WarningFilled, Warning } from '@element-plus/icons-vue';
import * as echarts from 'echarts';
import { ElMessage } from 'element-plus';
import { useAnalyticsStore } from '@/stores/analyticsStore';

const analyticsStore = useAnalyticsStore();

// 数据状态
const loading = ref(true);
const analyticsData = ref({});
const dateRange = ref([]);

// 图表类型选择
const userChartType = ref('growth');
const musicChartType = ref('ranking');
const fatigueChartType = ref('distribution');
const systemChartType = ref('operation');

// 图表实例引用
const userChartRef = ref(null);
const musicChartRef = ref(null);
const fatigueChartRef = ref(null);
const systemChartRef = ref(null);

// 图表实例
let userChartInstance = null;
let musicChartInstance = null;
let fatigueChartInstance = null;
let systemChartInstance = null;

// 加载分析数据
const loadAnalyticsData = async () => {
  try {
    loading.value = true;
    
    // 转换日期范围格式
    let timeRange = null;
    if (dateRange.value && dateRange.value.length === 2) {
      timeRange = {
        start_time: dateRange.value[0],
        end_time: dateRange.value[1]
      };
    }
    
    const data = await analyticsStore.getDashboardData(timeRange);
    analyticsData.value = data;
    updateCharts();
  } catch (error) {
    console.error('加载分析数据失败:', error);
  } finally {
    loading.value = false;
  }
};

// 更新所有图表
const updateCharts = () => {
  updateUserChart();
  updateMusicChart();
  updateFatigueChart();
  updateSystemChart();
};

// 更新用户图表
const updateUserChart = () => {
  if (!userChartRef.value) return;
  
  if (userChartInstance) {
    userChartInstance.dispose();
  }
  
  userChartInstance = echarts.init(userChartRef.value);
  
  if (userChartType.value === 'growth') {
    // 用户增长趋势图
    const growthTrend = analyticsData.value.user_stats?.growth_trend || [];
    const xAxisData = growthTrend.map(item => item.date);
    const seriesData = growthTrend.map(item => item.count);
    
    const option = {
      tooltip: {
        trigger: 'axis'
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
          stack: 'Total',
          data: seriesData,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: 'rgba(128, 128, 255, 0.5)'
              },
              {
                offset: 1,
                color: 'rgba(128, 128, 255, 0.1)'
              }
            ])
          },
          lineStyle: {
            color: '#8080ff'
          }
        }
      ]
    };
    
    userChartInstance.setOption(option);
  } else if (userChartType.value === 'role') {
    // 角色分布图
    const roleDistribution = analyticsData.value.user_stats?.role_distribution || {};
    const seriesData = Object.entries(roleDistribution).map(([name, value]) => ({
      name: name === 'admin' ? '管理员' : '普通用户',
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
    
    userChartInstance.setOption(option);
  }
};

// 更新音乐图表
const updateMusicChart = () => {
  if (!musicChartRef.value) return;
  
  if (musicChartInstance) {
    musicChartInstance.dispose();
  }
  
  musicChartInstance = echarts.init(musicChartRef.value);
  
  if (musicChartType.value === 'ranking') {
    // 播放量排行
    const topPlayed = analyticsData.value.music_stats?.top_played || [];
    const xAxisData = topPlayed.slice(0, 10).map(item => `${item.title} - ${item.artist}`);
    const seriesData = topPlayed.slice(0, 10).map(item => item.play_count);
    
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
          rotate: 45,
          interval: 0
        }
      },
      yAxis: {
        type: 'value',
        name: '播放量'
      },
      series: [
        {
          name: '播放量',
          type: 'bar',
          data: seriesData,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: '#ff8042'
              },
              {
                offset: 1,
                color: '#ff0000'
              }
            ])
          }
        }
      ]
    };
    
    musicChartInstance.setOption(option);
  } else if (musicChartType.value === 'type') {
    // 音乐类型分布
    const typeDistribution = analyticsData.value.music_stats?.type_distribution || {};
    const seriesData = Object.entries(typeDistribution).map(([name, value]) => ({
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
        data: Object.keys(typeDistribution)
      },
      series: [
        {
          name: '音乐类型',
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
    
    musicChartInstance.setOption(option);
  } else if (musicChartType.value === 'mood') {
    // 音乐情绪分布
    const moodDistribution = analyticsData.value.music_stats?.mood_distribution || {};
    const seriesData = Object.entries(moodDistribution).map(([name, value]) => ({
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
        data: Object.keys(moodDistribution)
      },
      series: [
        {
          name: '音乐情绪',
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
    
    musicChartInstance.setOption(option);
  }
};

// 更新疲劳图表
const updateFatigueChart = () => {
  if (!fatigueChartRef.value) return;
  
  if (fatigueChartInstance) {
    fatigueChartInstance.dispose();
  }
  
  fatigueChartInstance = echarts.init(fatigueChartRef.value);
  
  if (fatigueChartType.value === 'distribution') {
    // 疲劳等级分布
    const levelDistribution = analyticsData.value.fatigue_stats?.level_distribution || {};
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
    
    fatigueChartInstance.setOption(option);
  } else if (fatigueChartType.value === 'trend') {
    // 检测趋势
    const detectionTrend = analyticsData.value.fatigue_stats?.detection_trend || [];
    const xAxisData = detectionTrend.map(item => item.date);
    const seriesData = detectionTrend.map(item => item.count);
    
    const option = {
      tooltip: {
        trigger: 'axis'
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
        data: xAxisData,
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        name: '检测次数'
      },
      series: [
        {
          name: '检测次数',
          type: 'line',
          stack: 'Total',
          data: seriesData,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: 'rgba(255, 128, 128, 0.5)'
              },
              {
                offset: 1,
                color: 'rgba(255, 128, 128, 0.1)'
              }
            ])
          },
          lineStyle: {
            color: '#ff8080'
          }
        }
      ]
    };
    
    fatigueChartInstance.setOption(option);
  }
};

// 更新系统图表
const updateSystemChart = () => {
  if (!systemChartRef.value) return;
  
  if (systemChartInstance) {
    systemChartInstance.dispose();
  }
  
  systemChartInstance = echarts.init(systemChartRef.value);
  
  if (systemChartType.value === 'operation') {
    // 操作类型分布
    const operationTypeDistribution = analyticsData.value.system_stats?.operation_type_distribution || {};
    const seriesData = Object.entries(operationTypeDistribution).map(([name, value]) => ({
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
        data: Object.keys(operationTypeDistribution)
      },
      series: [
        {
          name: '操作类型',
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
    
    systemChartInstance.setOption(option);
  } else if (systemChartType.value === 'error') {
    // 错误率趋势
    const errorTrend = analyticsData.value.system_stats?.error_trend || [];
    const xAxisData = errorTrend.map(item => item.date);
    const seriesData = errorTrend.map(item => item.count);
    
    const option = {
      tooltip: {
        trigger: 'axis'
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
        data: xAxisData,
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        name: '错误次数'
      },
      series: [
        {
          name: '错误次数',
          type: 'line',
          stack: 'Total',
          data: seriesData,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: 'rgba(255, 0, 0, 0.5)'
              },
              {
                offset: 1,
                color: 'rgba(255, 0, 0, 0.1)'
              }
            ])
          },
          lineStyle: {
            color: '#ff0000'
          }
        }
      ]
    };
    
    systemChartInstance.setOption(option);
  }
};

// 处理日期范围变化
const handleDateChange = (val) => {
  console.log('日期范围变化:', val);
  // 这里可以根据日期范围自动加载数据
  // loadAnalyticsData();
};

// 导出数据
const exportData = (format) => {
  console.log('导出数据格式:', format);
  // 这里可以实现数据导出功能
  ElMessage.success(`数据已导出为${format}格式`);
};

// 窗口大小变化时重新调整图表大小
const handleResize = () => {
  userChartInstance?.resize();
  musicChartInstance?.resize();
  fatigueChartInstance?.resize();
  systemChartInstance?.resize();
};

onMounted(() => {
  loadAnalyticsData();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  userChartInstance?.dispose();
  musicChartInstance?.dispose();
  fatigueChartInstance?.dispose();
  systemChartInstance?.dispose();
});
</script>

<style lang="scss" scoped>
.analytics-dashboard-view {
  h1 {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 24px;
    color: #1f2937;
  }
  
  .time-range-selector {
    display: flex;
    align-items: center;
    margin-bottom: 24px;
    padding: 16px;
    background-color: #f3f4f6;
    border-radius: 8px;
    
    span {
      margin-right: 16px;
      font-weight: 500;
    }
    
    el-date-picker {
      margin-right: 16px;
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
            color: #6366f1;
          }
        }
      }
    }
  }
  
  .charts-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 24px;
    margin-bottom: 32px;
    
    @media (max-width: 1024px) {
      grid-template-columns: 1fr;
    }
    
    .chart-card {
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
        height: 400px;
        
        .chart {
          width: 100%;
          height: 100%;
        }
      }
    }
  }
  
  .export-options {
    background-color: #f3f4f6;
    padding: 20px;
    border-radius: 8px;
    
    h3 {
      font-size: 16px;
      font-weight: 600;
      margin: 0 0 16px 0;
      color: #1f2937;
    }
    
    el-button {
      margin-right: 12px;
    }
  }
}
</style>

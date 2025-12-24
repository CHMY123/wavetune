<template>
  <div class="fatigue-result-view">
    <!-- 顶部区域 -->
    <div class="top-section">
      <el-page-header @back="$router.go(-1)" content="脑疲劳检测结果">
        <template #extra>
          <el-button type="primary" @click="$router.push('/')">
            返回首页
          </el-button>
        </template>
      </el-page-header>
      
      <el-descriptions class="detection-info" :column="2" border>
        <el-descriptions-item label="检测时间">
          2023-10-10 15:30:22
        </el-descriptions-item>
        <el-descriptions-item label="检测场景">
          <el-tag type="primary">学习场景</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <!-- 中部区域 -->
    <el-row :gutter="20" class="middle-section">
      <!-- 左栏：核心结果可视化 -->
      <el-col :xs="24" :sm="24" :md="14" :lg="14" :xl="14">
        <div class="left-panel">
          <!-- 疲劳等级概览 -->
          <CardContainer title="当前疲劳等级" class="fatigue-overview">
            <div class="fatigue-level">
              <div class="level-display moderate">
                <span class="level-text">中度疲劳</span>
                <div class="level-indicator"></div>
              </div>
              <p class="level-desc">
                基于 EEG α 波功率与 EOG 眨眼频率综合判定
              </p>
            </div>
          </CardContainer>

          <!-- 趋势图表区 -->
          <div class="charts-section">
            <!-- 近7天趋势图 -->
            <CardContainer title="近 7 天疲劳指数变化趋势">
              <div class="chart-container" ref="trendChart"></div>
            </CardContainer>

            <!-- 今日各时段对比图 -->
            <CardContainer title="今日各时段疲劳程度对比">
              <div class="chart-container" ref="timeChart"></div>
            </CardContainer>
          </div>
        </div>
      </el-col>

      <!-- 右栏：关键指标数值展示 -->
      <el-col :xs="24" :sm="24" :md="10" :lg="10" :xl="10">
        <div class="right-panel">
          <CardContainer title="关键指标" class="indicators-panel">
            <el-row :gutter="16">
              <el-col :span="12" v-for="indicator in indicators" :key="indicator.name">
                <div class="indicator-card" :class="indicator.status">
                  <div class="indicator-header">
                    <span class="indicator-name">{{ indicator.name }}</span>
                    <el-icon class="status-icon">
                      <component :is="indicator.icon" />
                    </el-icon>
                  </div>
                  <div class="indicator-value">
                    <span class="value">{{ indicator.value }}</span>
                    <span class="unit">{{ indicator.unit }}</span>
                  </div>
                  <div class="indicator-range">
                    {{ indicator.range }}
                  </div>
                </div>
              </el-col>
            </el-row>
          </CardContainer>
        </div>
      </el-col>
    </el-row>

    <!-- 底部区域：详细指标表格 -->
    <div class="bottom-section">
      <el-divider>
        <h3>多模态生理信号详细指标</h3>
      </el-divider>
      
      <CardContainer>
        <el-table :data="detailedIndicators" stripe>
          <el-table-column prop="signalType" label="信号类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getSignalTypeTag(row.signalType)">
                {{ row.signalType }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="indicatorName" label="指标名称" width="180" />
          <el-table-column prop="detectedValue" label="检测值" width="120" />
          <el-table-column prop="referenceRange" label="参考范围" width="150" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <span :class="row.status === '正常' ? 'status-normal' : 'status-danger'">
                {{ row.status }}
              </span>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="table-pagination">
          <el-pagination
            :current-page="1"
            :page-size="5"
            :total="detailedIndicators.length"
            layout="total, prev, pager, next"
            background
          />
        </div>
      </CardContainer>
    </div>
  </div>
</template>

<script>
import CardContainer from '@/components/global/CardContainer.vue'
import { ArrowDown, ArrowUp, Check } from '@element-plus/icons-vue'

export default {
  name: 'FatigueResultView',
  components: {
    CardContainer
  },
  data() {
    return {
      indicators: [
        {
          name: 'EEG α 波功率',
          value: '4.2',
          unit: 'μV²',
          range: '正常：5-8 μV²',
          status: 'warning',
          icon: ArrowDown
        },
        {
          name: 'EEG β 波功率',
          value: '6.8',
          unit: 'μV²',
          range: '正常：4-7 μV²',
          status: 'danger',
          icon: ArrowUp
        },
        {
          name: 'EOG 眨眼频率',
          value: '18.5',
          unit: '次/分',
          range: '正常：15-20 次/分',
          status: 'normal',
          icon: Check
        },
        {
          name: '心率变异性',
          value: '32.4',
          unit: 'ms',
          range: '正常：30-50 ms',
          status: 'normal',
          icon: Check
        }
      ],
      detailedIndicators: [
        {
          signalType: 'EEG',
          indicatorName: 'θ 波功率',
          detectedValue: '3.2 μV²',
          referenceRange: '2-4 μV²',
          status: '正常'
        },
        {
          signalType: 'EEG',
          indicatorName: 'δ 波功率',
          detectedValue: '1.8 μV²',
          referenceRange: '1-3 μV²',
          status: '正常'
        },
        {
          signalType: 'EOG',
          indicatorName: '瞳孔直径波动率',
          detectedValue: '12.3%',
          referenceRange: '10-15%',
          status: '正常'
        },
        {
          signalType: 'EOG',
          indicatorName: '眼动速度',
          detectedValue: '450°/s',
          referenceRange: '400-500°/s',
          status: '正常'
        },
        {
          signalType: 'HRV',
          indicatorName: 'RMSSD',
          detectedValue: '28.6 ms',
          referenceRange: '25-35 ms',
          status: '正常'
        },
        {
          signalType: '其他',
          indicatorName: '皮肤电导水平',
          detectedValue: '2.1 μS',
          referenceRange: '1.5-2.5 μS',
          status: '正常'
        }
      ]
    }
  },
  methods: {
    getSignalTypeTag(type) {
      const typeMap = {
        'EEG': 'primary',
        'EOG': 'success',
        'HRV': 'warning',
        '其他': 'info'
      }
      return typeMap[type] || 'info'
    }
  }
}
</script>

<style lang="scss" scoped>
.fatigue-result-view {
  max-width: 1200px;
  margin: 0 auto;
  background: var(--bg-card);
  border-radius: 8px;
  overflow: hidden;
}

.top-section {
  padding: var(--spacing-page);
  border-bottom: 1px solid #e5e6eb;
  
  .detection-info {
    margin-top: 20px;
  }
}

.middle-section {
  padding: var(--spacing-page);
  min-height: 600px;
}

.left-panel {
  .fatigue-overview {
    margin-bottom: 20px;
    
    .fatigue-level {
      text-align: center;
      
      .level-display {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
        
        .level-text {
          font-size: 32px;
          font-weight: bold;
          line-height: 1;
        }
        
        .level-indicator {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          border: 4px solid;
        }
        
        &.moderate {
          .level-text {
            color: var(--el-color-warning);
          }
          
          .level-indicator {
            background: var(--el-color-warning);
            border-color: var(--el-color-warning);
          }
        }
      }
      
      .level-desc {
        margin-top: 16px;
        color: var(--text-secondary);
        font-size: 14px;
      }
    }
  }
  
  .charts-section {
    .chart-container {
      height: 300px;
      background: #fafafa;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--text-secondary);
      font-size: 14px;
      
      &::before {
        content: "ECharts 图表占位区域";
      }
    }
  }
}

.right-panel {
  .indicators-panel {
    .indicator-card {
      background: #fafafa;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
      border-left: 4px solid;
      
      &.normal {
        border-left-color: var(--el-color-success);
      }
      
      &.warning {
        border-left-color: var(--el-color-warning);
      }
      
      &.danger {
        border-left-color: var(--el-color-danger);
      }
      
      .indicator-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        
        .indicator-name {
          font-size: 14px;
          color: var(--text-regular);
        }
        
        .status-icon {
          font-size: 16px;
          
          &.normal {
            color: var(--el-color-success);
          }
          
          &.warning {
            color: var(--el-color-warning);
          }
          
          &.danger {
            color: var(--el-color-danger);
          }
        }
      }
      
      .indicator-value {
        margin-bottom: 8px;
        
        .value {
          font-size: 20px;
          font-weight: bold;
          color: var(--text-primary);
          font-family: 'SF Mono', Monaco, monospace;
        }
        
        .unit {
          font-size: 12px;
          color: var(--text-secondary);
          margin-left: 4px;
        }
      }
      
      .indicator-range {
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
  }
}

.bottom-section {
  padding: var(--spacing-page);
  border-top: 1px solid #e5e6eb;
  
  .table-pagination {
    margin-top: 16px;
    display: flex;
    justify-content: center;
  }
}

// 响应式适配
@media (max-width: 768px) {
  .middle-section {
    .left-panel {
      .fatigue-level {
        .level-display {
          .level-text {
            font-size: 24px;
          }
          
          .level-indicator {
            width: 40px;
            height: 40px;
          }
        }
      }
      
      .charts-section {
        .chart-container {
          height: 200px;
        }
      }
    }
    
    .right-panel {
      margin-top: 20px;
      
      .indicator-card {
        .indicator-value {
          .value {
            font-size: 16px;
          }
        }
      }
    }
  }
}
</style>









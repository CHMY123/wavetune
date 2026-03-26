<template>
  <div class="federated-management-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <el-page-header content="联邦学习管理" />
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card class="stats-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><DataAnalysis /></el-icon>
            <span>总参与人次</span>
          </div>
        </template>
        <div class="stats-value">{{ stats.total_participants || 0 }}</div>
      </el-card>
      
      <el-card class="stats-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Monitor /></el-icon>
            <span>总设备数</span>
          </div>
        </template>
        <div class="stats-value">{{ stats.total_devices || 0 }}</div>
      </el-card>
      
      <el-card class="stats-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Refresh /></el-icon>
            <span>总训练轮次</span>
          </div>
        </template>
        <div class="stats-value">{{ stats.total_rounds || 0 }}</div>
      </el-card>
      
      <el-card class="stats-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Check /></el-icon>
            <span>平均准确率</span>
          </div>
        </template>
        <div class="stats-value">{{ ((stats.average_accuracy || 0) * 100).toFixed(2) }}%</div>
      </el-card>
    </div>

    <!-- 数据图表 -->
    <div class="charts-section">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Check /></el-icon>
            <span>训练状态分布</span>
          </div>
        </template>
        <div class="chart-container">
          <div ref="statusChartRef" style="width: 100%; height: 300px;"></div>
        </div>
      </el-card>
      
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Refresh /></el-icon>
            <span>训练趋势</span>
          </div>
        </template>
        <div class="chart-container">
          <div ref="trendChartRef" style="width: 100%; height: 300px;"></div>
        </div>
      </el-card>
    </div>

    <!-- 训练记录表格 -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>训练记录管理</span>
          <el-button type="primary" size="small" @click="refreshRecords">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <div class="table-container">
        <el-table :data="trainingRecords" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="user_id" label="用户ID" width="100" />
          <el-table-column prop="client_id" label="客户端ID" width="200" />
          <el-table-column prop="rounds" label="训练轮次" width="100" />
          <el-table-column prop="accuracy" label="准确率" width="100">
            <template #default="scope">
              {{ (scope.row.accuracy * 100).toFixed(2) }}%
            </template>
          </el-table-column>
          <el-table-column prop="loss" label="损失值" width="100" />
          <el-table-column prop="training_time" label="训练时间" width="180">
            <template #default="scope">
              {{ formatTime(scope.row.training_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="scope">
              <el-button type="primary" size="small" @click="viewRecordDetail(scope.row)">
                查看
              </el-button>
              <el-button type="danger" size="small" @click="deleteRecord(scope.row.id)" style="margin-left: 5px;">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-if="pagination.total > 0"
          :current-page="pagination.page"
          :page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="pagination"
        />
      </div>
    </el-card>

    <!-- 设备管理表格 -->
    <el-card class="table-card" shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <el-icon><Monitor /></el-icon>
          <span>设备管理</span>
        </div>
      </template>
      <div class="table-container">
        <el-table :data="devices" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="user_id" label="用户ID" width="100" />
          <el-table-column prop="device_id" label="设备ID" width="200" />
          <el-table-column prop="device_type" label="设备类型" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="training_count" label="训练次数" width="100" />
          <el-table-column prop="contribution" label="贡献值" width="100">
            <template #default="scope">
              {{ scope.row.contribution.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="last_participate" label="最后参与时间" width="180">
            <template #default="scope">
              {{ formatTime(scope.row.last_participate) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 记录详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="训练记录详情"
      width="600px"
    >
      <div v-if="selectedRecord" class="record-detail">
        <el-descriptions :column="2">
          <el-descriptions-item label="训练ID">{{ selectedRecord.id }}</el-descriptions-item>
          <el-descriptions-item label="用户ID">{{ selectedRecord.user_id }}</el-descriptions-item>
          <el-descriptions-item label="客户端ID">{{ selectedRecord.client_id }}</el-descriptions-item>
          <el-descriptions-item label="训练轮次">{{ selectedRecord.rounds }}</el-descriptions-item>
          <el-descriptions-item label="准确率">{{ (selectedRecord.accuracy * 100).toFixed(2) }}%</el-descriptions-item>
          <el-descriptions-item label="损失值">{{ selectedRecord.loss.toFixed(4) }}</el-descriptions-item>
          <el-descriptions-item label="训练时间">{{ formatTime(selectedRecord.training_time) }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ getStatusText(selectedRecord.status) }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { DataAnalysis, Monitor, Refresh, Check, Document } from '@element-plus/icons-vue'
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { requestMethod } from '@/utils/request'
import * as echarts from 'echarts'

export default {
  name: 'FederatedManagementView',
  components: {
    DataAnalysis,
    Monitor,
    Refresh,
    Check,
    Document
  },
  setup() {
    const stats = ref({})
    const trainingRecords = ref([])
    const devices = ref([])
    const detailDialogVisible = ref(false)
    const selectedRecord = ref(null)
    const statusChartRef = ref(null)
    const trendChartRef = ref(null)
    let statusChart = null
    let trendChart = null
    const pagination = reactive({
      page: 1,
      pageSize: 10,
      total: 0
    })

    // 加载统计数据
    const loadStats = async () => {
      try {
        const response = await requestMethod.get('/federated/stats')
        if (response.code === 200) {
          stats.value = response.data
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }

    // 加载训练记录
    const loadTrainingRecords = async () => {
      try {
        const response = await requestMethod.get('/federated/training-records', {
          params: {
            page: pagination.page,
            page_size: pagination.pageSize
          }
        })
        if (response.code === 200) {
          trainingRecords.value = response.data.items
          pagination.total = response.data.pagination.total
          // 更新图表数据
          updateChartData()
        }
      } catch (error) {
        console.error('加载训练记录失败:', error)
      }
    }

    // 更新图表数据
    const updateChartData = () => {
      // 更新状态分布饼图
      if (statusChartRef.value) {
        if (!statusChart) {
          statusChart = echarts.init(statusChartRef.value)
        }
        
        const statusCount = {
          pending: 0,
          training: 0,
          completed: 0,
          failed: 0
        }
        trainingRecords.value.forEach(record => {
          if (statusCount[record.status] !== undefined) {
            statusCount[record.status]++
          }
        })
        
        const statusData = Object.keys(statusCount)
          .filter(status => statusCount[status] > 0)
          .map(status => ({
            name: getStatusText(status),
            value: statusCount[status]
          }))
        
        statusChart.setOption({
          tooltip: {
            trigger: 'item'
          },
          legend: {
            orient: 'vertical',
            left: 'left'
          },
          series: [
            {
              name: '训练状态',
              type: 'pie',
              radius: '50%',
              data: statusData,
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              }
            }
          ]
        })
      }
      
      // 更新趋势折线图
      if (trendChartRef.value) {
        if (!trendChart) {
          trendChart = echarts.init(trendChartRef.value)
        }
        
        const trendRecords = [...trainingRecords.value]
          .sort((a, b) => new Date(a.training_time) - new Date(b.training_time))
          .slice(-20)
        
        const times = trendRecords.map(record => formatTime(record.training_time))
        const accuracies = trendRecords.map(record => (record.accuracy * 100).toFixed(2))
        const losses = trendRecords.map(record => record.loss.toFixed(4))
        
        trendChart.setOption({
          tooltip: {
            trigger: 'axis'
          },
          legend: {
            data: ['准确率', '损失值']
          },
          xAxis: {
            type: 'category',
            data: times
          },
          yAxis: [
            {
              type: 'value',
              name: '准确率 (%)',
              position: 'left'
            },
            {
              type: 'value',
              name: '损失值',
              position: 'right'
            }
          ],
          series: [
            {
              name: '准确率',
              type: 'line',
              data: accuracies,
              yAxisIndex: 0,
              smooth: true
            },
            {
              name: '损失值',
              type: 'line',
              data: losses,
              yAxisIndex: 1,
              smooth: true
            }
          ]
        })
      }
    }

    // 加载设备列表
    const loadDevices = async () => {
      try {
        const response = await requestMethod.get('/federated/devices')
        if (response.code === 200) {
          devices.value = response.data
        }
      } catch (error) {
        console.error('加载设备列表失败:', error)
      }
    }

    // 刷新数据
    const refreshRecords = () => {
      loadTrainingRecords()
      loadStats()
      loadDevices()
    }

    // 查看记录详情
    const viewRecordDetail = (record) => {
      selectedRecord.value = record
      detailDialogVisible.value = true
    }

    // 格式化时间
    const formatTime = (timeStr) => {
      if (!timeStr) return ''
      const date = new Date(timeStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      const seconds = String(date.getSeconds()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    }

    // 获取状态类型
    const getStatusType = (status) => {
      const typeMap = {
        pending: 'info',
        training: 'warning',
        completed: 'success',
        failed: 'danger',
        online: 'success',
        offline: 'danger'
      }
      return typeMap[status] || 'info'
    }

    // 获取状态文本
    const getStatusText = (status) => {
      const textMap = {
        pending: '等待中',
        training: '训练中',
        completed: '完成',
        failed: '失败'
      }
      return textMap[status] || status
    }

    // 分页处理
    const handleSizeChange = (size) => {
      pagination.pageSize = size
      loadTrainingRecords()
    }

    const handleCurrentChange = (current) => {
      pagination.page = current
      loadTrainingRecords()
    }

    // 删除训练记录
    const deleteRecord = async (recordId) => {
      try {
        const response = await requestMethod.delete(`/federated/training-records/${recordId}`)
        if (response.code === 200) {
          ElMessage.success('删除训练记录成功')
          // 刷新训练记录列表
          loadTrainingRecords()
        }
      } catch (error) {
        console.error('删除训练记录失败:', error)
        ElMessage.error('删除训练记录失败，请重试')
      }
    }

    // 组件挂载时加载数据
    onMounted(() => {
      loadStats()
      loadTrainingRecords()
      loadDevices()
    })

    return {
      stats,
      trainingRecords,
      devices,
      detailDialogVisible,
      selectedRecord,
      statusChartRef,
      trendChartRef,
      pagination,
      refreshRecords,
      viewRecordDetail,
      deleteRecord,
      formatTime,
      getStatusType,
      getStatusText,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script>

<style lang="scss" scoped>
.federated-management-view {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
  
  :deep(.el-page-header__content) {
    font-size: 24px;
    font-weight: bold;
    color: var(--text-primary);
  }
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
  
  .stats-card {
    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
    }
    
    .stats-value {
      font-size: 32px;
      font-weight: bold;
      color: var(--el-color-primary);
      margin-top: 16px;
    }
  }
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
  
  .chart-card {
    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
    }
    
    .chart-container {
      height: 300px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}

.table-card {
  margin-bottom: 24px;
  
  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    justify-content: space-between;
  }
  
  .table-container {
    margin-top: 16px;
  }
  
  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}

.record-detail {
  padding: 16px 0;
}

// 响应式适配
@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
    
    .chart-card {
      .chart-container {
        height: 250px;
      }
    }
  }
}
</style>
<template>
  <div class="federated-devices-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <el-page-header content="联邦学习设备管理" />
    </div>

    <!-- 筛选区 -->
    <CardContainer class="filter-section">
      <el-row :gutter="16" align="middle">
        <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="8">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索设备 ID / 类型"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="8">
          <el-select v-model="filterStatus" placeholder="筛选设备状态">
            <el-option label="全部设备" value="all" />
            <el-option label="在线设备" value="online" />
            <el-option label="离线设备" value="offline" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
          <div class="device-stats">
            <span class="stat-item">
              <span class="stat-label">总计：</span>
              <span class="stat-value">{{ deviceList.length }}</span>
            </span>
            <span class="stat-item">
              <span class="stat-label">在线：</span>
              <span class="stat-value online">{{ onlineDevices }}</span>
            </span>
            <span class="stat-item">
              <span class="stat-label">离线：</span>
              <span class="stat-value offline">{{ offlineDevices }}</span>
            </span>
          </div>
        </el-col>
      </el-row>
    </CardContainer>

    <!-- 设备卡片列表 -->
    <div class="devices-grid">
      <el-row :gutter="16">
        <el-col 
          v-for="device in filteredDevices" 
          :key="device.id"
          :xs="24" 
          :sm="12" 
          :md="8" 
          :lg="8" 
          :xl="8"
        >
          <el-card class="device-card" :class="device.status">
            <div class="device-header">
              <div class="device-id">{{ device.id }}</div>
              <el-badge 
                :type="device.status === 'online' ? 'success' : 'danger'" 
                :value="device.status === 'online' ? '在线' : '离线'"
                class="status-badge"
              />
            </div>
            
            <div class="device-info">
              <div class="device-type">
                <el-icon class="device-icon">
                  <component :is="device.type === 'mobile' ? 'Iphone' : 'Monitor'" />
                </el-icon>
                <span class="type-text">{{ device.typeName }}</span>
              </div>
              
              <div class="device-meta">
                <div class="meta-item">
                  <span class="meta-label">最后参与：</span>
                  <span class="meta-value">{{ device.lastParticipate }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">训练次数：</span>
                  <span class="meta-value">{{ device.trainingCount }} 次</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">贡献度：</span>
                  <span class="meta-value">{{ device.contribution }}%</span>
                </div>
              </div>
            </div>
            
            <div class="device-actions">
              <el-button 
                type="text" 
                size="small"
                :class="device.status === 'online' ? 'disable-btn' : 'enable-btn'"
              >
                {{ device.status === 'online' ? '禁用参与' : '启用参与' }}
              </el-button>
              <el-button type="text" size="small" class="detail-btn">
                查看详情
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredDevices.length === 0" class="empty-state">
      <el-icon class="empty-icon">
        <Monitor />
      </el-icon>
      <p class="empty-text">暂无符合条件的设备</p>
      <p class="empty-subtext">请调整筛选条件或等待设备连接</p>
    </div>

    <!-- 分页 -->
    <div v-if="filteredDevices.length > 0" class="pagination-section">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="filteredDevices.length"
        layout="total, prev, pager, next, jumper"
        background
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script>
import CardContainer from '@/components/global/CardContainer.vue'
import { Search, Monitor, Iphone } from '@element-plus/icons-vue'

export default {
  name: 'FederatedDevicesView',
  components: {
    CardContainer,
    Search,
    Monitor,
    Iphone
  },
  data() {
    return {
      searchKeyword: '',
      filterStatus: 'all',
      currentPage: 1,
      pageSize: 9,
      deviceList: [
        {
          id: '设备 ID: 001',
          type: 'mobile',
          typeName: '可穿戴设备',
          status: 'online',
          lastParticipate: '2023-10-09 16:30',
          trainingCount: 15,
          contribution: 12.5
        },
        {
          id: '设备 ID: 002',
          type: 'desktop',
          typeName: '桌面设备',
          status: 'online',
          lastParticipate: '2023-10-10 09:15',
          trainingCount: 22,
          contribution: 18.3
        },
        {
          id: '设备 ID: 003',
          type: 'mobile',
          typeName: '移动设备',
          status: 'offline',
          lastParticipate: '2023-10-08 14:20',
          trainingCount: 8,
          contribution: 6.7
        },
        {
          id: '设备 ID: 004',
          type: 'mobile',
          typeName: '智能手表',
          status: 'online',
          lastParticipate: '2023-10-10 10:45',
          trainingCount: 31,
          contribution: 25.8
        },
        {
          id: '设备 ID: 005',
          type: 'desktop',
          typeName: '工作站',
          status: 'online',
          lastParticipate: '2023-10-10 11:20',
          trainingCount: 19,
          contribution: 15.9
        },
        {
          id: '设备 ID: 006',
          type: 'mobile',
          typeName: '平板电脑',
          status: 'offline',
          lastParticipate: '2023-10-07 18:10',
          trainingCount: 5,
          contribution: 4.2
        },
        {
          id: '设备 ID: 007',
          type: 'mobile',
          typeName: '智能眼镜',
          status: 'online',
          lastParticipate: '2023-10-10 12:30',
          trainingCount: 27,
          contribution: 22.5
        },
        {
          id: '设备 ID: 008',
          type: 'desktop',
          typeName: '服务器',
          status: 'online',
          lastParticipate: '2023-10-10 13:15',
          trainingCount: 35,
          contribution: 29.2
        },
        {
          id: '设备 ID: 009',
          type: 'mobile',
          typeName: 'VR 设备',
          status: 'online',
          lastParticipate: '2023-10-10 14:00',
          trainingCount: 13,
          contribution: 10.8
        }
      ]
    }
  },
  computed: {
    onlineDevices() {
      return this.deviceList.filter(device => device.status === 'online').length
    },
    offlineDevices() {
      return this.deviceList.filter(device => device.status === 'offline').length
    },
    filteredDevices() {
      let devices = this.deviceList
      
      // 搜索过滤
      if (this.searchKeyword) {
        devices = devices.filter(device => 
          device.id.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
          device.typeName.toLowerCase().includes(this.searchKeyword.toLowerCase())
        )
      }
      
      // 状态过滤
      if (this.filterStatus !== 'all') {
        devices = devices.filter(device => device.status === this.filterStatus)
      }
      
      return devices
    }
  },
  methods: {
    handlePageChange(page) {
      this.currentPage = page
    }
  }
}
</script>

<style lang="scss" scoped>
.federated-devices-view {
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

.filter-section {
  margin-bottom: 24px;
  
  .device-stats {
    display: flex;
    gap: 16px;
    justify-content: flex-end;
    
    .stat-item {
      display: flex;
      align-items: center;
      gap: 4px;
      
      .stat-label {
        font-size: 14px;
        color: var(--text-regular);
      }
      
      .stat-value {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
        
        &.online {
          color: var(--el-color-success);
        }
        
        &.offline {
          color: var(--el-color-danger);
        }
      }
    }
  }
}

.devices-grid {
  margin-bottom: 24px;
  
  .device-card {
    height: 240px;
    margin-bottom: 16px;
    border-left: 4px solid;
    transition: box-shadow 0.3s ease;
    
    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }
    
    &.online {
      border-left-color: var(--el-color-success);
    }
    
    &.offline {
      border-left-color: var(--el-color-danger);
    }
    
    :deep(.el-card__body) {
      height: 100%;
      padding: 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    
    .device-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      
      .device-id {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .status-badge {
        :deep(.el-badge__content) {
          font-size: 12px;
        }
      }
    }
    
    .device-info {
      flex: 1;
      
      .device-type {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        
        .device-icon {
          font-size: 16px;
          color: var(--text-secondary);
        }
        
        .type-text {
          font-size: 14px;
          color: var(--text-regular);
        }
      }
      
      .device-meta {
        .meta-item {
          display: flex;
          justify-content: space-between;
          margin-bottom: 6px;
          
          .meta-label {
            font-size: 12px;
            color: var(--text-secondary);
          }
          
          .meta-value {
            font-size: 12px;
            color: var(--text-primary);
            font-family: 'SF Mono', Monaco, monospace;
          }
        }
      }
    }
    
    .device-actions {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      margin-top: 16px;
      
      .disable-btn {
        color: var(--el-color-danger);
        
        &:hover {
          background: rgba(245, 108, 108, 0.1);
        }
      }
      
      .enable-btn {
        color: var(--el-color-success);
        
        &:hover {
          background: rgba(82, 196, 26, 0.1);
        }
      }
      
      .detail-btn {
        color: var(--el-color-primary);
        
        &:hover {
          background: rgba(24, 144, 255, 0.1);
        }
      }
    }
  }
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-secondary);
  
  .empty-icon {
    font-size: 64px;
    color: var(--text-placeholder);
    margin-bottom: 16px;
  }
  
  .empty-text {
    font-size: 18px;
    font-weight: 500;
    margin: 0 0 8px 0;
    color: var(--text-regular);
  }
  
  .empty-subtext {
    font-size: 14px;
    margin: 0;
    color: var(--text-secondary);
  }
}

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

// 响应式适配
@media (max-width: 768px) {
  .filter-section {
    .device-stats {
      justify-content: flex-start;
      margin-top: 16px;
    }
  }
  
  .devices-grid {
    .device-card {
      height: 200px;
      margin-bottom: 12px;
      
      .device-header {
        .device-id {
          font-size: 14px;
        }
      }
      
      .device-info {
        .device-meta {
          .meta-item {
            .meta-label,
            .meta-value {
              font-size: 11px;
            }
          }
        }
      }
      
      .device-actions {
        flex-direction: column;
        
        .el-button {
          width: 100%;
          text-align: center;
        }
      }
    }
  }
}

@media (max-width: 480px) {
  .devices-grid {
    .device-card {
      height: 180px;
      
      :deep(.el-card__body) {
        padding: 12px;
      }
    }
  }
}
</style>








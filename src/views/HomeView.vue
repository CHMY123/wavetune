<template>
  <div class="home-view">
    <div class="container">
      <!-- 系统介绍区域 -->
      <div class="hero-section">
        <div class="hero-content">
          <div class="hero-text">
            <h1 class="system-title gradient-text">WaveTune</h1>
            <p class="system-subtitle">基于多模态生理信号的脑疲劳检测和轻音乐个性化干预系统</p>
            <p class="system-desc">
              采用联邦学习技术保护用户隐私，通过EEG、fNIRS等多模态生理信号实时监测脑疲劳状态，
              并提供个性化轻音乐干预方案，帮助用户缓解疲劳、提升专注力。
            </p>
            <div class="hero-actions">
              <el-button class="primary-btn" size="large" @click="$router.push('/signal-monitor')">
                <img src="/static/icon/detection.png" class="btn-icon" alt="开始监测" 
                style="width: 20px; height: 20px; object-fit: contain; margin-right: 10px;" />
                开始监测
              </el-button>
              <el-button class="secondary-btn" size="large" @click="$router.push('/music-recommendation')">
                <img src="/static/icon/music.png" class="btn-icon" alt="音乐推荐" 
                style="width: 30px; height: 30px; object-fit: contain; margin-right: 5px;" />
                音乐推荐
              </el-button>
            </div>
          </div>
          <div class="hero-image">
            <div class="system-icon">
              <img src="/static/logo/logo.png" class="hero-main-icon" alt="WaveTune" 
              style="width: 140px; height: 140px; object-fit: contain; object-position: 90% 5px" />
            </div>
          </div>
        </div>
      </div>

      <!-- 功能模块卡片 -->
      <div class="features-section">
        <h2 class="section-title">核心功能模块</h2>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6" v-for="feature in features" :key="feature.id">
            <CardContainer 
              class="feature-card" 
              @click="navigateTo(feature.route)"
              waveStyle 
              gradientBorder
            >
              <div class="feature-icon" :class="feature.iconClass">
                <img :src="feature.iconSrc" class="feature-inner-icon" :alt="feature.title" />
              </div>
              <h3 class="feature-title">{{ feature.title }}</h3>
              <p class="feature-desc">{{ feature.description }}</p>
              <div class="feature-actions">
                <el-button class="feature-btn" size="small">
                  {{ feature.buttonText }}
                  <el-icon class="btn-icon">
                    <ArrowRight />
                  </el-icon>
                </el-button>
              </div>
            </CardContainer>
          </el-col>
        </el-row>
      </div>

      <!-- 系统运行统计 -->
      <div class="stats-section">
        <CardContainer title="系统运行统计" waveStyle gradientBorder>
          <el-row :gutter="20">
            <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6" v-for="stat in stats" :key="stat.id">
              <div class="stat-item">
                <div class="stat-icon">
                  <img :src="stat.iconSrc" class="stat-inner-icon" :alt="stat.label" />
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ stat.value }}</div>
                  <div class="stat-label">{{ stat.label }}</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </CardContainer>
      </div>

      <!-- 快速操作 -->
      <div class="quick-actions">
        <h3 class="section-title">快速操作</h3>
        <div class="action-buttons">
          <el-button class="action-btn primary-btn" size="large" @click="$router.push('/quick-detection')">
            <img src="/static/icon/result.png" class="btn-icon-large" alt="检测结果" />
            <span>查看检测结果</span>
          </el-button>
          <el-button class="action-btn success-btn" size="large" @click="$router.push('/music-recommendation')">
            <img src="/static/icon/music.png" class="btn-icon-large" alt="音乐推荐" />
            <span>音乐推荐</span>
          </el-button>
          <el-button class="action-btn warning-btn" size="large" @click="$router.push('/signal-monitor')">
            <img src="/static/icon/detection.png" class="btn-icon-large" alt="信号监测" />
            <span>信号监测</span>
          </el-button>
          <el-button class="action-btn info-btn" size="large" @click="$router.push('/user')">
            <img src="/static/icon/user.png" class="btn-icon-large" alt="个人中心" />
            <span>个人中心</span>
          </el-button>
        </div>
      </div>

      <!-- 贡献者名单 -->
      <div class="contributors-section">
        <CardContainer title="团队成员" waveStyle gradientBorder>
          <div class="team-members-list">
            <div class="team-member-card" v-for="(member, index) in teamMembers" :key="index">
              <div class="member-avatar">
                <img :src="member.avatar" :alt="member.name" v-if="member.avatar" />
                <div class="avatar-placeholder" v-else>{{ member.name.charAt(0) }}</div>
              </div>
              <div class="member-info">
                <h4 class="member-name">{{ member.name }}</h4>
                <p class="member-position">职位：{{ member.position }}</p>
                <p class="member-wechat">微信号：{{ member.wechat }}</p>
              </div>
            </div>
          </div>
        </CardContainer>
      </div>
    </div>
  </div>
</template>

<script>
import CardContainer from '@/components/global/CardContainer.vue'
import { ArrowRight, User } from '@element-plus/icons-vue'
import { ref, onMounted } from 'vue'
import { requestMethod } from '@/utils/request'

export default {
  name: 'HomeView',
  components: {
    CardContainer,
    ArrowRight,
    User
  },
  setup() {
    const features = ref([
      {
        id: 1,
        title: '脑疲劳检测',
        description: '实时监测脑疲劳状态，提供准确的疲劳等级评估',
        iconSrc: '/static/icon/result.png',
        iconClass: 'detection',
        route: '/quick-detection',
        buttonText: '查看结果'
      },
      {
        id: 2,
        title: '音乐干预',
        description: '根据疲劳等级和个人偏好，智能推荐个性化轻音乐进行干预',
        iconSrc: '/static/icon/music.png',
        iconClass: 'music',
        route: '/music-recommendation',
        buttonText: '开始推荐'
      },
      {
        id: 3,
        title: '信号监测',
        description: '实时监测EEG、fNIRS等多模态生理信号，可视化展示数据',
        iconSrc: '/static/icon/detection.png',
        iconClass: 'monitor',
        route: '/signal-monitor',
        buttonText: '开始监测'
      },
      {
        id: 4,
        title: '联邦学习',
        description: '采用联邦学习技术保护隐私，协同优化模型性能，增强用户参与',
        iconSrc: '/static/icon/federation.png',
        iconClass: 'federated',
        route: '/federated/contribute',
        buttonText: '参与学习'
      }
    ])
    
    const stats = ref([
      {
        id: 1,
        value: '0',
        label: '检测次数',
        iconSrc: '/static/icon/result.png',
        iconClass: 'detection'
      },
      {
        id: 2,
        value: '0',
        label: '干预次数',
        iconSrc: '/static/icon/intervene.png',
        iconClass: 'music'
      },
      {
        id: 3,
        value: '0',
        label: '参与设备',
        iconSrc: '/static/icon/federation.png',
        iconClass: 'devices'
      },
      {
        id: 4,
        value: '0%',
        label: '模型准确率',
        iconSrc: '/static/icon/model.png',
        iconClass: 'accuracy'
      }
    ])
    
    const teamMembers = ref([
      {
        name: '钟红红',
        position: '项目负责人',
        wechat: 'red9267426426',
        avatar: 'static/avatar/zhh.jpg'
      },
      {
        name: '赖文韬',
        position: '全栈开发工程师',
        wechat: 'laiwentao0618',
        avatar: 'static/avatar/default.jpg'
      },
      {
        name: '李洋',
        position: '模型开发工程师',
        wechat: 'ymyxcyntz2004',
        avatar: 'static/avatar/ly.jpg'
      },
      {
        name: '梁炜琳',
        position: '架构工程师',
        wechat: 'ForestJacqueline14',
        avatar: 'static/avatar/lwl.jpg'
      }
    ])
    
    const navigateTo = (route) => {
      window.location.href = route
    }
    
    // 获取系统运行统计数据 - 并行请求优化
    const fetchSystemStats = async () => {
      try {
        // 并行发送所有请求
        const [detectionResponse, federatedResponse, dashboardResponse] = await Promise.allSettled([
          requestMethod.get('/federated/signal-detection/count'),
          requestMethod.get('/federated/stats'),
          requestMethod.get('/admin/dashboard').catch(() => null) // 单独捕获错误
        ])
        
        // 处理检测次数
        if (detectionResponse.status === 'fulfilled' && detectionResponse.value?.code === 200) {
          const detectionCount = detectionResponse.value.data?.detection_count || 0
          const detectionStat = stats.value.find(stat => stat.label === '检测次数')
          if (detectionStat) {
            detectionStat.value = detectionCount.toString()
          }
        }
        
        // 处理联邦学习统计数据
        if (federatedResponse.status === 'fulfilled' && federatedResponse.value?.code === 200) {
          const federatedData = federatedResponse.value.data || {}
          
          // 更新参与设备
          const deviceStat = stats.value.find(stat => stat.label === '参与设备')
          if (deviceStat) {
            deviceStat.value = federatedData.total_devices?.toString() || '0'
          }
          
          // 更新模型准确率
          const accuracyStat = stats.value.find(stat => stat.label === '模型准确率')
          if (accuracyStat) {
            const accuracy = federatedData.average_accuracy || 0
            accuracyStat.value = `${(accuracy * 100).toFixed(1)}%`
          }
        }
        
        // 处理音乐总播放量（干预次数）
        if (dashboardResponse.status === 'fulfilled' && dashboardResponse.value?.code === 200) {
          const totalPlays = dashboardResponse.value.data?.music_stats?.total_plays || 0
          const musicStat = stats.value.find(stat => stat.label === '干预次数')
          if (musicStat) {
            musicStat.value = totalPlays.toString()
          }
        } else {
          const musicStat = stats.value.find(stat => stat.label === '干预次数')
          if (musicStat) {
            musicStat.value = '0'
          }
        }
      } catch (error) {
        console.error('获取系统统计数据失败:', error)
      }
    }
    
    // 页面加载时获取数据
    onMounted(() => {
      fetchSystemStats()
    })
    
    return {
      features,
      stats,
      teamMembers,
      navigateTo
    }
  }
}
</script>

<style lang="scss" scoped>
@use '@/assets/styles/_design_tokens.scss' as *;

.home-view {
  position: relative;
  padding: 0;
  background: var(--bg-page);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-section {
  background: linear-gradient(135deg, var(--wave-purple) 0%, var(--wave-blue) 100%);
  border-radius: 20px;
  padding: 60px 50px;
  margin: 30px 0 40px 0;
  color: white;
  box-shadow: 0 12px 32px rgba(106, 90, 205, 0.15);
  position: relative;
  overflow: hidden;
  
  .hero-content {
    display: flex;
    align-items: center;
    gap: 50px;
    
    .hero-text {
      flex: 1;
      
      .system-title {
        font-size: 56px;
        font-weight: 800;
        margin: 0 0 16px 0;
        background: linear-gradient(45deg, #fff, #e6f7ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1px;
        line-height: 1.1;
      }
      
      .system-subtitle {
        font-size: 20px;
        margin: 0 0 16px 0;
        opacity: 0.95;
        font-weight: 500;
      }
      
      .system-desc {
        font-size: 15px;
        line-height: 1.7;
        margin: 0 0 28px 0;
        opacity: 0.9;
        max-width: 480px;
      }
      
      .hero-actions {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
      }
    }
    
    .hero-image {
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;

      .system-icon {
        width: 140px;
        height: 140px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
      }
    }
  }
}

.gradient-text {
  background: linear-gradient(90deg, var(--wave-blue), var(--wave-purple), var(--wave-pink));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  display: inline-block;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 32px;
  text-align: center;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, var(--wave-purple), var(--wave-blue));
    border-radius: 2px;
  }
}

.features-section,
.stats-section,
.federated-section {
  margin-bottom: 40px;
}

.quick-actions {
  margin-bottom: 20px;
}

.contributors-section {
  margin-bottom: 40px;
}

.features-section {
    .feature-card {
      height: 300px;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s ease;
      border: none;
      
      &:hover {
        transform: translateY(-6px);
        box-shadow: 0 8px 24px rgba(106, 90, 205, 0.12);
      }
      
      :deep(.el-card__body) {
        height: 100%;
        padding: 24px 20px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background: var(--bg-card);
        border-radius: 16px;
      }
      
      .feature-icon {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 16px;
        font-size: 24px;
        color: white;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        transition: all 0.3s ease;
        
        &.detection,
        &.music,
        &.monitor,
        &.federated {
          background: linear-gradient(135deg, #6b46c1, #9f7aea);
        }
        
        .feature-inner-icon {
          font-size: 28px;
          width: 28px;
          height: 28px;
          object-fit: contain;
        }
      }
      
      .feature-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 12px 0;
        transition: color 0.3s ease;
      }
      
      &:hover .feature-title {
        color: #6b46c1;
      }
      
      .feature-desc {
        font-size: 13px;
        color: var(--text-regular);
        line-height: 1.6;
        margin: 0 0 16px 0;
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .feature-actions {
        margin-top: 8px;
        
        .feature-btn {
          width: 100%;
          background: transparent;
          border: 2px solid #6b46c1;
          color: #6b46c1;
          border-radius: 20px;
          padding: 8px 20px;
          font-weight: 500;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          
          &:hover {
            background: #6b46c1;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(107, 70, 193, 0.25);
          }
          
          .btn-icon {
            font-size: 14px;
            transition: transform 0.3s ease;
          }
          
          &:hover .btn-icon {
            transform: translateX(4px);
          }
        }
      }
    }
  }

.stats-section {
  .stat-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    background: var(--bg-card);
    border-radius: 12px;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
    }
    
    .stat-icon {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      color: white;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
      background: linear-gradient(135deg, var(--wave-blue), var(--wave-purple));
      
      .stat-inner-icon {
        font-size: 28px;
        width: 28px;
        height: 28px;
      }
      
      :deep(.stat-inner-icon) svg {
        width: 28px;
        height: 28px;
      }
    }
    
    .stat-content {
      .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 4px;
        font-family: 'SF Mono', Monaco, monospace;
        line-height: 1;
      }
      
      .stat-label {
        font-size: 13px;
        color: var(--text-regular);
        font-weight: 500;
      }
    }
  }
}

.federated-section {
  .federated-status {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 24px;
    
    .status-info {
      display: flex;
      gap: 32px;
      
      .status-item {
        text-align: center;
        padding: 16px 20px;
        background: var(--bg-hover);
        border-radius: 10px;
        
        .status-label {
          display: block;
          font-size: 13px;
          color: var(--text-regular);
          margin-bottom: 8px;
          font-weight: 500;
        }
        
        .status-value {
          font-size: 20px;
          font-weight: 700;
          font-family: 'SF Mono', Monaco, monospace;
          
          &.primary {
            color: var(--wave-purple);
          }
          
          &.success {
            color: var(--wave-green);
          }
          
          &.warning {
            color: var(--wave-orange);
          }
        }
      }
    }
    
    .status-actions {
      .primary-btn {
        min-width: 120px;
        background-color: var(--brand-primary);
        border: none;
        color: white;
        border-radius: 20px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 6px;
        
        &:hover {
          background-color: var(--brand-primary-hover);
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
        }
        
        .btn-icon {
          font-size: 14px;
          transition: transform 0.3s ease;
        }
        
        &:hover .btn-icon {
          transform: translateX(4px);
        }
      }
    }
  }
}

.quick-actions {
    .action-buttons {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
    }
    
    .action-btn {
      height: 90px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 8px;
      border-radius: 12px;
      border: none;
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
      }
      
      .btn-icon-large {
        width: 32px;
        height: 32px;
        object-fit: contain;
      }
      
      span {
        font-size: 14px;
        font-weight: 500;
      }
    }
    
    .primary-btn {
      background: linear-gradient(135deg, #6b46c1, #9f7aea);
      color: white;
      
      &:hover {
        box-shadow: 0 6px 16px rgba(107, 70, 193, 0.25);
      }
    }
    
    .success-btn {
      background: linear-gradient(135deg, #38a169, #48bb78);
      color: white;
      
      &:hover {
        box-shadow: 0 6px 16px rgba(56, 161, 105, 0.25);
      }
    }
    
    .warning-btn {
      background: linear-gradient(135deg, #ed8936, #f6ad55);
      color: white;
      
      &:hover {
        box-shadow: 0 6px 16px rgba(237, 137, 54, 0.25);
      }
    }
    
    .info-btn {
      background: linear-gradient(135deg, #3182ce, #4299e1);
      color: white;
      
      &:hover {
        box-shadow: 0 6px 16px rgba(49, 130, 206, 0.25);
      }
    }
  }
  
  .contributors-section {
    margin-top: 16px;
    
    .team-members-list {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      padding: 12px 0;
    }
    
    .team-member-card {
      background: var(--bg-card);
      border-radius: 16px;
      padding: 24px;
      text-align: center;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
      }
      
      .member-avatar {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        margin: 0 auto 16px;
        overflow: hidden;
        background: linear-gradient(135deg, #6b46c1, #9f7aea);
        
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        
        .avatar-placeholder {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 32px;
          font-weight: 700;
        }
      }
      
      .member-info {
        .member-name {
          font-size: 18px;
          font-weight: 700;
          color: var(--text-primary);
          margin: 0 0 8px 0;
        }
        
        .member-position {
          font-size: 14px;
          color: var(--text-secondary);
          margin: 0 0 8px 0;
        }
        
        .member-wechat {
          font-size: 14px;
          color: var(--text-tertiary);
          margin: 0;
        }
      }
    }
  }

.primary-btn {
  background: linear-gradient(135deg, var(--wave-blue), var(--wave-purple));
  border: none;
  color: white;
  border-radius: 20px;
  padding: 12px 28px;
  font-weight: 500;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(106, 90, 205, 0.3);
  }
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.15);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  border-radius: 20px;
  padding: 12px 28px;
  font-weight: 500;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  }
}

.btn-icon {
  font-size: 16px;
  transition: transform 0.3s ease;
}

.primary-btn:hover .btn-icon,
.secondary-btn:hover .btn-icon {
  transform: translateX(4px);
}

.theme-dark {
  .hero-section {
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
  }
  
  .feature-card,
  .stat-item,
  .status-item,
  .contributor-item {
    background: var(--bg-card);
  }
  
  .status-item {
    background: var(--bg-hover);
  }
  
  .contributor-item {
    background: var(--bg-hover);
    
    &:hover {
      background: var(--bg-active);
    }
  }
}

@media (max-width: 1024px) {
  .hero-section {
    padding: 50px 40px;
    
    .hero-content {
      gap: 40px;
      
      .hero-text {
        .system-title {
          font-size: 48px;
        }
        
        .system-subtitle {
          font-size: 18px;
        }
        
        .system-desc {
          font-size: 14px;
        }
      }
    }
  }
  
  .features-section {
    .feature-card {
      height: 260px;
    }
  }
  
  .quick-actions {
    .action-buttons {
      grid-template-columns: repeat(2, 1fr);
    }
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 40px 30px;
    
    .hero-content {
      flex-direction: column;
      text-align: center;
      gap: 30px;
      
      .hero-text {
        .system-title {
          font-size: 40px;
        }
        
        .system-subtitle {
          font-size: 16px;
        }
        
        .system-desc {
          font-size: 13px;
          max-width: 100%;
        }
        
        .hero-actions {
          justify-content: center;
        }
      }
    }
  }
  
  .features-section {
    .feature-card {
      height: 240px;
      margin-bottom: 16px;
    }
  }
  
  .federated-section {
    .federated-status {
      flex-direction: column;
      gap: 20px;
      
      .status-info {
        flex-direction: column;
        gap: 16px;
        width: 100%;
      }
      
      .status-actions {
        width: 100%;
        
        .primary-btn {
          width: 100%;
        }
      }
    }
  }
  
  .quick-actions {
    .action-buttons {
      grid-template-columns: 1fr;
    }
    
    .action-btn {
      height: 70px;
    }
  }
  
  .contributors-section {
    .contributors-list {
      gap: 12px;
      justify-content: space-around;
    }
    
    .contributor-item {
      padding: 8px 12px;
      
      .contributor-avatar {
        width: 28px;
        height: 28px;
        font-size: 14px;
      }
      
      .contributor-name {
        font-size: 12px;
      }
    }
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 16px;
  }
  
  .hero-section {
    padding: 30px 20px;
    margin: 20px 0 30px 0;
    
    .hero-content {
      .hero-text {
        .system-title {
          font-size: 32px;
        }
        
        .system-subtitle {
          font-size: 14px;
        }
        
        .system-desc {
          font-size: 12px;
        }
        
        .hero-actions {
          flex-direction: column;
          gap: 12px;
        }
      }
      
      .hero-image {
        .system-icon {
          width: 120px;
          height: 120px;
        }
      }
    }
  }
  
  .section-title {
    font-size: 24px;
    margin-bottom: 24px;
  }
  
  .features-section,
  .stats-section,
  .federated-section {
    margin-bottom: 30px;
  }
  
  .quick-actions {
    margin-bottom: 16px;
  }
  
  .contributors-section {
    margin-bottom: 30px;
  }
  
  .features-section {
    .feature-card {
      height: 220px;
      margin-bottom: 16px;
    }
  }
  
  .quick-actions {
    .action-btn {
      height: 64px;
      
      .btn-icon-large {
        width: 24px;
        height: 24px;
      }
      
      span {
        font-size: 11px;
      }
    }
  }
  
  .contributors-section {
    .contributors-list {
      gap: 10px;
      flex-wrap: wrap;
    }
    
    .contributor-item {
      padding: 6px 10px;
      
      .contributor-avatar {
        width: 24px;
        height: 24px;
        font-size: 12px;
      }
      
      .contributor-name {
        font-size: 11px;
      }
    }
  }
}

/* 确保底部内容完全显示 */
.home-view {
  padding-bottom: 20px;
  min-height: 100vh;
  box-sizing: border-box;
}
</style>

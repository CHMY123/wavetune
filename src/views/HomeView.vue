<template>
  <div class="home-view">
    <!-- 波形背景装饰 -->
    <div class="home-wave-decoration"></div>
    
    <div class="container">
    <!-- 系统介绍区域 -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="system-title gradient-text">WaveTune</h1>
          <p class="system-subtitle">基于多模态生理信号的脑疲劳检测和轻音乐个性化干预系统</p>
          <p class="system-desc">
            采用联邦学习技术保护用户隐私，通过EEG、EOG、HRV等多模态生理信号实时监测脑疲劳状态，
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
            <img src="/static/logo/SCNU.png" class="hero-main-icon" alt="WaveTune" 
            style="width: 140px; height: 140px; object-fit: contain; 
            object-position: 90% 5px" />
          </div>
          <!-- 波形装饰 -->
          <div class="hero-wave-decoration">
            <div class="wave"></div>
            <div class="wave wave-2"></div>
            <div class="wave wave-3"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能模块卡片 -->
    <div class="features-section animate-in">
      <h2 class="section-title">核心功能模块</h2>
      <el-row :gutter="24">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6" v-for="feature in features" :key="feature.id">
          <CardContainer 
            class="feature-card" 
            @click="navigateTo(feature.route)"
            waveStyle 
            gradientBorder
            glowEffect
          >
            <div class="feature-icon" :class="feature.iconClass">
              <img :src="feature.iconSrc" class="feature-inner-icon" :alt="feature.title" />
            </div>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-desc">{{ feature.description }}</p>
            <div class="feature-actions">
              <el-button class="feature-btn" size="small">
                {{ feature.buttonText }}
                <el-icon :component="ArrowRight" class="btn-icon" />
              </el-button>
            </div>
          </CardContainer>
        </el-col>
      </el-row>
    </div>

    <!-- 系统统计信息 -->
    <div class="stats-section">
      <CardContainer title="系统运行统计" waveStyle gradientBorder>
        <el-row :gutter="24">
          <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6" v-for="stat in stats" :key="stat.id">
            <div class="stat-item hover-scale">
              <div class="stat-icon" :class="stat.iconClass">
                <img :src="stat.iconSrc" class="stat-inner-icon" :alt="stat.label" />
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
              <!-- 装饰光晕 -->
              <div class="stat-glow" :class="stat.iconClass"></div>
            </div>
          </el-col>
        </el-row>
      </CardContainer>
    </div>

    <!-- 联邦学习状态 -->
    <div class="federated-section">
      <CardContainer title="联邦学习状态" waveStyle gradientBorder glowEffect>
        <div class="federated-status">
          <div class="status-info">
            <div class="status-item hover-scale">
              <span class="status-label">参与设备：</span>
              <span class="status-value primary">12 台</span>
            </div>
            <div class="status-item hover-scale">
              <span class="status-label">训练轮次：</span>
              <span class="status-value success">第 3/10 轮</span>
            </div>
            <div class="status-item hover-scale">
              <span class="status-label">模型准确率：</span>
              <span class="status-value warning">89.2%</span>
            </div>
          </div>
          <div class="status-actions">
            <el-button class="primary-btn" @click="$router.push('/federated/status')">
              查看详情
              <el-icon :component="ArrowRight" class="btn-icon" />
            </el-button>
          </div>
        </div>
        <!-- 联邦学习装饰图表 -->
        <div class="federated-chart">
          <div class="chart-node" v-for="i in 6" :key="i">
            <div class="node"></div>
            <div class="node-connection" v-if="i < 6"></div>
          </div>
        </div>
      </CardContainer>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h3 class="section-title">快速操作</h3>
      <div class="action-buttons">
        <el-button class="action-btn primary-btn" size="large" @click="$router.push('/fatigue-result')">
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
    </div>
  </div>
</template>

<script>
import CardContainer from '@/components/global/CardContainer.vue'
import { ArrowRight } from '@element-plus/icons-vue'

export default {
  name: 'HomeView',
  components: {
    CardContainer,
    ArrowRight
  },
  data() {
    return {
      features: [
        {
          id: 1,
          title: '脑疲劳检测',
          description: '基于多模态生理信号实时监测脑疲劳状态，提供准确的疲劳等级评估',
          iconSrc: '/static/icon/result.png',
          iconClass: 'detection',
          route: '/fatigue-result',
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
          description: '实时监测EEG、EOG、HRV等多模态生理信号，可视化展示数据',
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
          route: '/federated/status',
          buttonText: '参与学习'
        }
      ],
      stats: [
        {
          id: 1,
          value: '256',
          label: '检测次数',
          iconSrc: '/static/icon/result.png',
          iconClass: 'detection'
        },
        {
          id: 2,
          value: '85',
          label: '干预次数',
          iconSrc: '/static/icon/intervene.png',
          iconClass: 'music'
        },
        {
          id: 3,
          value: '12',
          label: '参与设备',
          iconSrc: '/static/icon/federation.png',
          iconClass: 'devices'
        },
        {
          id: 4,
          value: '89.2%',
          label: '模型准确率',
          iconSrc: '/static/icon/model.png',
          iconClass: 'accuracy'
        }
      ]
    }
  },
  mounted() {
    // 页面加载时的初始化操作
    // 添加动画效果
    setTimeout(() => {
      const sections = document.querySelectorAll('.features-section, .stats-section, .federated-section, .quick-actions');
      sections.forEach(section => {
        section.classList.add('animate-in');
      });
    }, 100);
  },
  methods: {
    navigateTo(route) {
      this.$router.push(route)
    },
    resolveMedia(val) {
      try { return resolveMedia(val) } catch (e) { return val }
    }
  }
}
</script>

<style lang="scss" scoped>
// 导入全局变量
@use '@/assets/styles/_design_tokens.scss' as *;

.home-view {
  position: relative;
  padding: 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  position: relative;
}

// 全局波形背景装饰
.home-wave-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, rgba(106, 90, 205, 0.05) 0%, transparent 50%);
  z-index: -1;
  pointer-events: none;
}

.hero-section {
  background: linear-gradient(135deg, var(--wave-purple) 0%, var(--wave-blue) 100%);
  border-radius: 24px;
  padding: 80px 60px;
  margin: 40px 0 64px 0;
  color: white;
  box-shadow: 0 20px 40px rgba(106, 90, 205, 0.2);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  }
  
  .hero-content {
    display: flex;
    align-items: center;
    gap: 60px;
    position: relative;
    z-index: 1;
    
    .hero-text {
      flex: 1;
      
      .system-title {
        font-size: 64px;
        font-weight: 800;
        margin: 0 0 20px 0;
        background: linear-gradient(45deg, #fff, #e6f7ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -2px;
        line-height: 1.1;
      }
      
      .system-subtitle {
        font-size: 24px;
        margin: 0 0 24px 0;
        opacity: 0.95;
        font-weight: 500;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }
      
      .system-desc {
        font-size: 16px;
        line-height: 1.8;
        margin: 0 0 32px 0;
        opacity: 0.9;
        max-width: 500px;
      }
      
      .hero-actions {
        display: flex;
        gap: 20px;
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
        background: rgba(255, 255, 255, 0.10);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        /* remove font-size to avoid affecting inline SVGs */
        font-size: initial;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.08);
      }
      
      .hero-wave-decoration {
          position: absolute;
          bottom: -60px;
          width: 100%;
          height: 100px;
          
          .wave {
            position: absolute;
            left: 0;
            bottom: 0;
            width: 200%;
            height: 4px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            
            &.wave-2 {
              bottom: 8px;
              height: 3px;
              opacity: 0.6;
            }
            
            &.wave-3 {
              bottom: 16px;
              height: 2px;
              opacity: 0.4;
            }
          }
        }
    }
  }
}

// 简化动画效果，移除持续动画以优化性能
// 仅保留必要的过渡效果

// 渐变文本效果
.gradient-text {
  background: linear-gradient(90deg, var(--wave-blue), var(--wave-purple), var(--wave-pink));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  display: inline-block;
}

.section-title {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 48px;
  text-align: center;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -12px;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 4px;
    background: linear-gradient(90deg, var(--wave-purple), var(--wave-blue));
    border-radius: 2px;
  }
}

// 简化区块进入动画，减少过渡时间和复杂度
.features-section,
.stats-section,
.federated-section,
.quick-actions {
  margin-bottom: 100px;
  opacity: 1; /* 修改为默认显示 */
  transition: opacity 0.3s ease;
  
  &.animate-in {
    opacity: 1;
  }
}

.features-section {
  margin-bottom: 80px;
  
  .feature-card {
    height: 320px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    border: none;
    
    &:hover {
      transform: translateY(-8px);
      box-shadow: 0 12px 36px rgba(106, 90, 205, 0.15);
    }
    
    :deep(.el-card__body) {
      height: 100%;
      padding: 32px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      background: var(--bg-card);
      border-radius: 16px;
    }
    
    .feature-icon {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 24px;
      font-size: 32px;
      color: white;
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
      transition: all 0.3s ease;
      position: relative;
      
      &::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: inherit;
        filter: blur(20px);
        opacity: 0.5;
        z-index: -1;
        transition: all 0.3s ease;
      }
      
      &:hover::before {
        filter: blur(25px);
        opacity: 0.7;
      }
      
      &.detection {
        background-color: var(--wave-blue);
      }

      &.music {
        background-color: var(--wave-blue);
      }

      &.monitor {
        background-color: var(--wave-blue);
      }

      &.federated {
        background-color: var(--wave-blue);
      }
      .feature-inner-icon {
        font-size: 36px; /* 控制图标大小 */
        width: 36px;
        height: 36px;
      }
      :deep(.feature-inner-icon) svg {
        width: 36px;
        height: 36px;
      }
    }
    
    .feature-title {
      font-size: 20px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 16px 0;
      transition: color 0.3s ease;
    }
    
    &:hover .feature-title {
      color: var(--wave-purple);
    }
    
    .feature-desc {
      font-size: 14px;
      color: var(--text-regular);
      line-height: 1.6;
      margin: 0 0 24px 0;
      flex: 1;
    }
    
    .feature-actions {
      .feature-btn {
        width: 100%;
        background: transparent;
        border: 2px solid var(--wave-purple);
        color: var(--wave-purple);
        border-radius: 24px;
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        
        &:hover {
          background: var(--wave-purple);
          color: white;
          transform: translateY(-2px);
          box-shadow: 0 4px 16px rgba(106, 90, 205, 0.3);
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
  margin-bottom: 80px;
  
  .stat-item {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 24px;
    background: var(--bg-card);
    border-radius: 16px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    
    .stat-glow {
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      border-radius: 50%;
      filter: blur(40px);
      opacity: 0;
      transition: opacity 0.3s ease;
      pointer-events: none;

      &.detection { background-color: rgba(59,130,246,0.12); }
      &.music { background-color: rgba(59,130,246,0.12); }
      &.devices { background-color: rgba(59,130,246,0.12); }
      &.accuracy { background-color: rgba(59,130,246,0.12); }
    }
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
      
      .stat-glow {
        opacity: 0.2;
      }
    }
    
    .stat-icon {
      width: 64px;
      height: 64px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      color: white;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
      
      &.detection {
        background-color: var(--wave-blue);
      }

      &.music {
        background-color: var(--wave-blue);
      }

      &.devices {
        background-color: var(--wave-blue);
      }

      &.accuracy {
        background-color: var(--wave-blue);
      }
      .stat-inner-icon {
        font-size: 36px;
        width: 36px;
        height: 36px;
      }
      :deep(.stat-inner-icon) svg {
        width: 36px;
        height: 36px;
      }
    }
    
    .stat-content {
      .stat-value {
        font-size: 32px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 6px;
        font-family: 'SF Mono', Monaco, monospace;
        line-height: 1;
      }
      
      .stat-label {
        font-size: 14px;
        color: var(--text-regular);
        font-weight: 500;
      }
    }
  }
}

.federated-section {
  margin-bottom: 80px;
  
  .federated-status {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 32px;
    margin-bottom: 24px;
    
    .status-info {
      display: flex;
      gap: 40px;
      
      .status-item {
        text-align: center;
        padding: 16px 24px;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 12px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        
        .status-label {
          display: block;
          font-size: 14px;
          color: var(--text-regular);
          margin-bottom: 12px;
          font-weight: 500;
        }
        
        .status-value {
          font-size: 24px;
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
        min-width: 140px;
        background-color: var(--brand-primary);
        border: none;
        color: white;
        border-radius: 24px;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(24,144,255,0.18);
          opacity: 0.95;
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
  
  .federated-chart {
    display: flex;
    justify-content: space-around;
    align-items: center;
    padding: 20px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    
    .chart-node {
      display: flex;
      align-items: center;
      
      .node {
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background-color: var(--brand-primary);
      box-shadow: 0 0 12px rgba(24,144,255,0.18);
      animation: pulse 2s ease-in-out infinite;
      }
      
        .node-connection {
        width: 60px;
        height: 2px;
        background-color: rgba(24,144,255,0.18);
        margin-left: 8px;
      }
    }
  }
}

.quick-actions {
  .action-buttons {
    display: flex;
    gap: 24px;
    justify-content: center;
    flex-wrap: wrap;
    
    .action-btn {
      min-width: 200px;
      padding: 16px 24px;
      border-radius: 28px;
      font-weight: 600;
      font-size: 16px;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      position: relative;
      overflow: hidden;
      border: none;
      
      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s ease;
      }
      
      &:hover::before {
        left: 100%;
      }
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
      }
      
      .btn-icon-large {
        font-size: 20px;
      }
      
      &.primary-btn {
        background-color: var(--brand-primary);
        color: white;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
      }

      &.success-btn {
        background-color: var(--brand-primary);
        color: white;
      }

      &.warning-btn {
        background-color: var(--brand-primary);
        color: white;
      }

      &.info-btn {
        background-color: var(--brand-primary);
        color: white;
      }

      &.primary-btn:hover {
        opacity: 0.95;
        box-shadow: 0 6px 16px rgba(24,144,255,0.18);
      }
      &.success-btn:hover {
        opacity: 0.95;
        box-shadow: 0 6px 16px rgba(24,144,255,0.18);
      }
      &.warning-btn:hover {
        opacity: 0.95;
        box-shadow: 0 6px 16px rgba(24,144,255,0.18);
      }
      &.info-btn:hover {
        opacity: 0.95;
        box-shadow: 0 6px 16px rgba(24,144,255,0.18);
      }
    }
  }

  /* 确保 el-icon 内部 svg 能被限定大小显示（Scoped 样式下需用深度选择器） */
  :deep(.btn-icon) svg { width: 16px; height: 16px; }
  :deep(.btn-icon-large) svg { width: 20px; height: 20px; }
  /* 统一图片图标的尺寸与对齐 */
  .btn-icon { width: 20px; height: 20px; display: inline-flex; align-items:center; justify-content:center; vertical-align: middle; margin-right: 8px; }
  .btn-icon img { width: 100%; height: 100%; object-fit: contain; display: block }
  .btn-icon-large { width: 32px; height: 32px; display: inline-flex; align-items:center; justify-content:center; vertical-align: middle; margin-right: 8px; }
  .btn-icon-large img { width: 100%; height: 100%; object-fit: contain; display: block }
  .feature-inner-icon { width: 48px; height: 48px; display: inline-flex; align-items:center; justify-content:center; }
  .feature-inner-icon img { width: 100%; height: 100%; object-fit: contain; display:block }
  .stat-inner-icon { width: 48px; height: 48px; display: inline-flex; align-items:center; justify-content:center; }
  .stat-inner-icon img { width: 100%; height: 100%; object-fit: contain; display:block }
  .hero-main-icon { width: 120px; height: 120px; display: block; }
  .hero-main-icon img { width: 100%; height: 100%; object-fit: contain; display:block }
}

// 通用按钮样式
.primary-btn {
  background: linear-gradient(135deg, #7b61ff, #4593ff);
  border: none;
  color: white;
  border-radius: 28px;
  padding: 12px 32px;
  font-weight: 600;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(123, 97, 255, 0.3);
  }
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid white;
  color: white;
  border-radius: 28px;
  padding: 12px 32px;
  font-weight: 600;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  }
}

// 通用悬停缩放效果
.hover-scale {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  
  &:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  }
}

// 响应式适配
@media (max-width: 1024px) {
  .hero-section {
    padding: 48px 32px;
    
    .hero-content {
      gap: 40px;
      
      .hero-text {
        .system-title {
          font-size: 48px;
        }
        
        .system-subtitle {
          font-size: 20px;
        }
      }
      
      .hero-image {
        .system-icon {
          width: 120px;
          height: 120px;
          font-size: 48px;
        }
      }
    }
  }
  
  .federated-section {
    .federated-status {
      .status-info {
        gap: 24px;
      }
    }
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 36px 24px;
    border-radius: 16px;
    
    .hero-content {
      flex-direction: column;
      text-align: center;
      gap: 32px;
      
      .hero-text {
        .system-title {
          font-size: 40px;
          letter-spacing: -1px;
        }
        
        .system-subtitle {
          font-size: 18px;
        }
        
        .system-desc {
          font-size: 14px;
          max-width: 100%;
        }
        
        .hero-actions {
          justify-content: center;
          
          .primary-btn,
          .secondary-btn {
            padding: 10px 24px;
            font-size: 14px;
          }
        }
      }
      
      .hero-image {
        .system-icon {
          width: 100px;
          height: 100px;
          font-size: 40px;
        }
      }
    }
  }
  
  .section-title {
    font-size: 28px;
    margin-bottom: 24px;
    
    &::after {
      width: 60px;
      height: 3px;
      bottom: -8px;
    }
  }
  
  .features-section {
    .feature-card {
      height: 280px;
      margin-bottom: 24px;
      
      :deep(.el-card__body) {
        padding: 24px;
      }
      
      .feature-icon {
        width: 64px;
        height: 64px;
        font-size: 28px;
        margin-bottom: 20px;
      }
      
      .feature-title {
        font-size: 18px;
      }
      
      .feature-desc {
        font-size: 13px;
      }
    }
  }
  
  .stats-section {
    .stat-item {
      padding: 20px;
      margin-bottom: 16px;
      
      .stat-icon {
        width: 56px;
        height: 56px;
        font-size: 22px;
      }
      
      .stat-content {
        .stat-value {
          font-size: 28px;
        }
        
        .stat-label {
          font-size: 13px;
        }
      }
    }
  }
  
  .federated-section {
    .federated-status {
      flex-direction: column;
      gap: 24px;
      
      .status-info {
        flex-direction: column;
        gap: 16px;
        width: 100%;
        
        .status-item {
          padding: 16px;
        }
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
      flex-direction: column;
      gap: 16px;
      
      .action-btn {
        width: 100%;
        min-width: auto;
        padding: 14px 24px;
        font-size: 15px;
      }
    }
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 24px 16px;
    
    .hero-content {
      .hero-text {
        .system-title {
          font-size: 32px;
        }
        
        .system-subtitle {
          font-size: 16px;
        }
      }
    }
  }
  
  .section-title {
    font-size: 24px;
  }
  
  .features-section {
    .feature-card {
      height: 260px;
      
      :deep(.el-card__body) {
        padding: 20px;
      }
      
      .feature-icon {
        width: 56px;
        height: 56px;
        font-size: 24px;
      }
    }
  }
  
  .stats-section {
    .stat-item {
      padding: 16px;
      
      .stat-icon {
        width: 48px;
        height: 48px;
        font-size: 20px;
      }
      
      .stat-content {
        .stat-value {
          font-size: 24px;
        }
      }
    }
  }
  
  .federated-section {
    .federated-chart {
      .chart-node {
        .node {
          width: 12px;
          height: 12px;
        }
        
        .node-connection {
          width: 40px;
        }
      }
    }
  }
}
</style>

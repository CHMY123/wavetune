<template>
  <el-card 
    :class="[
      'modern-card',
      {
        'wave-card': waveStyle,
        'gradient-border': gradientBorder,
        'glow-effect': glowEffect,
        'compact': compact
      },
      customClass
    ]"
    :shadow="shadowLevel"
  >
    <!-- 头部装饰条 -->
    <div 
      v-if="showHeaderBar || waveStyle" 
      class="card-header-bar"
      :style="headerBarStyle"
    ></div>
    
    <!-- 标题栏 -->
    <template #header v-if="title || $slots.header">
      <div class="card-header">
        <slot name="header">
          <h3 
            class="card-title" 
            :class="{
              'title-gradient': gradientTitle,
              'title-large': titleSize === 'large',
              'title-medium': titleSize === 'medium',
              'title-small': titleSize === 'small'
            }"
          >
            {{ title }}
          </h3>
        </slot>
        <div class="card-actions" v-if="$slots.actions">
          <slot name="actions"></slot>
        </div>
      </div>
    </template>
    
    <!-- 内容区 -->
    <div class="card-content" :style="{ padding: contentPadding }">
      <slot></slot>
    </div>
    
    <!-- 操作按钮区 -->
    <div class="card-footer" v-if="$slots.footer">
      <slot name="footer"></slot>
    </div>
    
    <!-- 波形装饰（仅在waveStyle时显示） -->
    <div v-if="waveStyle" class="wave-decoration">
      <svg viewBox="0 0 1440 320" xmlns="http://www.w3.org/2000/svg">
        <path 
          fill="currentColor" 
          fill-opacity="0.08" 
          d="M0,160L60,170.7C120,181,240,203,360,186.7C480,171,600,117,720,112C840,107,960,149,1080,176C1200,203,1320,213,1380,218.7L1440,224L1440,320L1380,320C1320,320,1200,320,1080,320C960,320,840,320,720,320C600,320,480,320,360,320C240,320,120,320,60,320L0,320Z"
        ></path>
      </svg>
    </div>
  </el-card>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'CardContainer',
  props: {
    // 基础属性
    title: {
      type: String,
      default: ''
    },
    shadow: {
      type: String,
      default: 'hover'
    },
    customClass: {
      type: String,
      default: ''
    },
    
    // 新增视觉属性
    waveStyle: {
      type: Boolean,
      default: false
    },
    gradientBorder: {
      type: Boolean,
      default: false
    },
    glowEffect: {
      type: Boolean,
      default: false
    },
    compact: {
      type: Boolean,
      default: false
    },
    showHeaderBar: {
      type: Boolean,
      default: true
    },
    gradientTitle: {
      type: Boolean,
      default: false
    },
    
    // 内容控制
    titleSize: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },
    contentPadding: {
      type: String,
      default: '24px'
    },
    
    // 主题控制
    headerBarColor: {
      type: String,
      default: ''
    }
  },
  
  setup(props) {
    // 计算阴影级别
    const shadowLevel = computed(() => {
      switch(props.shadow) {
        case 'none': return 'none'
        case 'always': return 'always'
        case 'hover':
        default: return 'hover'
      }
    })
    
    // 计算头部栏样式
    const headerBarStyle = computed(() => {
      if (props.headerBarColor) {
        return {
          backgroundColor: props.headerBarColor
        }
      }
      return {}
    })
    
    return {
      shadowLevel,
      headerBarStyle
    }
  }
}
</script>

<style lang="scss" scoped>
// 导入全局 CSS 变量（如果需要）
// @import '../../assets/styles/_variables.css';

.modern-card {
    margin-bottom: var(--spacing-lg);
    border: none;
    border-radius: var(--radius-card);
    transition: var(--transition-base);
    position: relative;
    overflow: hidden;
  
  :deep(.el-card__header) {
    padding: var(--spacing-md) var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
    background: transparent;
  }
  
  :deep(.el-card__body) {
    padding: var(--spacing-lg);
  }
  
  &:hover {
    box-shadow: var(--shadow-hover);
  }
  
  // 紧凑模式
  &.compact {
    :deep(.el-card__header) {
      padding: var(--spacing-sm) var(--spacing-md);
    }
    
    :deep(.el-card__body) {
      padding: var(--spacing-md);
    }
  }
  
  // 渐变边框
  &.gradient-border {
    border: 1px solid transparent;
    background-image: linear-gradient(var(--background-color-light), var(--background-color-light)),
                     linear-gradient(90deg, var(--wave-blue), var(--wave-purple), var(--wave-pink));
    background-origin: border-box;
    background-clip: padding-box, border-box;
  }
  
  // 发光效果
  &.glow-effect {
    &:hover {
      box-shadow: 0 0 20px rgba(106, 90, 205, 0.2); // 使用品牌主色的 RGB 值
    }
  }
  
  // 波形卡片
  &.wave-card {
    background-color: var(--background-color-light);
    position: relative;
    overflow: hidden;
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 100%;
      background-image: radial-gradient(circle at 10% 20%, rgba(var(--wave-blue-rgb), 0.05) 0%, transparent 20%),
                        radial-gradient(circle at 80% 70%, rgba(var(--wave-purple-rgb), 0.05) 0%, transparent 30%);
      pointer-events: none;
    }
  }
}

.card-header-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--wave-blue), var(--wave-purple), var(--wave-pink));
  transform: scaleX(0);
  transform-origin: left;
  transition: var(--transition-base);
  z-index: 1;
}

.modern-card:hover .card-header-bar {
  transform: scaleX(1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 2;
  
  .card-title {
    margin: 0;
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    transition: var(--transition-base);
    line-height: var(--line-height-display);
    
    &.title-small {
      font-size: var(--font-size-medium);
    }
    
    &.title-medium {
      font-size: var(--font-size-lg);
    }
    
    &.title-large {
      font-size: var(--font-size-extra-large);
    }
    
    &.title-gradient {
      background: linear-gradient(90deg, var(--wave-blue), var(--wave-purple), var(--wave-pink));
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
      display: inline-block;
    }
  }
  
  .card-actions {
    display: flex;
    gap: var(--spacing-sm);
  }
}

.card-content {
  min-height: 80px;
  position: relative;
  z-index: 2;
}

.card-footer {
  border-top: 1px solid var(--border-light);
  padding: var(--spacing-md) var(--spacing-lg) 0;
  margin-top: var(--spacing-md);
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  position: relative;
  z-index: 2;
}

.wave-decoration {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  color: var(--color-primary);
  opacity: 0.8;
  z-index: 0;
}

.wave-decoration svg {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modern-card {
    :deep(.el-card__header) {
      padding: var(--spacing-sm) var(--spacing-md);
    }
    
    :deep(.el-card__body) {
      padding: var(--spacing-md);
    }
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
    
    .card-actions {
      width: 100%;
      justify-content: flex-end;
    }
  }
  
  .card-footer {
    flex-direction: column;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md) 0;
  }
  
  .card-title {
    font-size: var(--font-size-base) !important;
  }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .modern-card {
    background-color: var(--dark-background-color-light);
    
    :deep(.el-card__header),
    :deep(.el-card__body) {
      background-color: transparent;
    }
    
    &.gradient-border {
      background-image: linear-gradient(var(--dark-background-color-light), var(--dark-background-color-light)),
                       linear-gradient(90deg, var(--wave-blue), var(--wave-purple), var(--wave-pink));
    }
    
    &.wave-card {
      background-color: var(--dark-background-color-light);
      
      &::before {
        background-image: radial-gradient(circle at 10% 20%, rgba(59, 130, 246, 0.03) 0%, transparent 20%),
                          radial-gradient(circle at 80% 70%, rgba(106, 90, 205, 0.03) 0%, transparent 30%);
      }
    }
  }
  
  .card-title {
    color: var(--dark-text-primary);
  }
}
</style>
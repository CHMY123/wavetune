<template>
  <el-footer class="footer">
    <div class="footer-content">
      <div class="footer-info">
        <div class="footer-brand">
          <el-icon class="footer-icon">
            <Monitor />
          </el-icon>
          <span class="footer-title">WaveTune</span>
        </div>
        <p class="footer-desc">
          基于多模态生理信号的脑疲劳检测和轻音乐个性化干预系统
        </p>
        <p class="footer-tech">
          技术栈：Vue 3 + Element Plus + ECharts + 联邦学习
        </p>
      </div>
      
      <div class="footer-links">
        <div class="link-group">
          <h4 class="link-title">功能模块</h4>
          <ul class="link-list">
            <li><router-link to="/fatigue-result">检测结果</router-link></li>
            <li><router-link to="/music-recommendation">音乐推荐</router-link></li>
            <li><router-link to="/signal-monitor">信号监测</router-link></li>
            <li><router-link to="/federated/status">联邦学习</router-link></li>
          </ul>
        </div>
        
        <div class="link-group">
          <h4 class="link-title">技术支持</h4>
          <ul class="link-list">
            <li><a href="#" @click.prevent>使用指南</a></li>
            <li><a href="#" @click.prevent>隐私保护</a></li>
            <li><a href="#" @click.prevent>联系我们</a></li>
            <li><a href="#" @click.prevent>反馈建议</a></li>
          </ul>
        </div>
      </div>
    </div>
    
    <div class="footer-bottom">
      <div class="footer-copyright">
        <p>&copy; 2023 WaveTune System. 基于联邦学习的隐私保护脑疲劳检测系统</p>
        <p class="footer-privacy">
          我们采用联邦学习技术保护您的生理数据隐私，所有数据仅在本地处理
        </p>
      </div>
    </div>
  </el-footer>
</template>

<script>
import { Monitor } from '@element-plus/icons-vue'

export default {
  name: 'Footer',
  components: {
    Monitor
  }
}
</script>

<style lang="scss" scoped>
.footer {
  background: #2c3e50;
  color: #ecf0f1;
  padding: 0;
  margin-top: auto; 
  width: 100%; 
  z-index: 9999;
  flex-shrink: 0; 
  box-sizing: border-box;
  position: relative; // 确保层级，防止被遮挡
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px 20px;
  display: flex;
  justify-content: space-between;
  gap: 40px;
  box-sizing: border-box;
  width: 100%;
  overflow: visible; // 防止内容溢出
}

.footer-info {
  flex: 1;
  
  .footer-brand {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    
    .footer-icon {
      font-size: 24px;
      color: var(--el-color-primary);
    }
    
    .footer-title {
      font-size: 20px;
      font-weight: bold;
    }
  }
  
  .footer-desc {
    font-size: 14px;
    line-height: 1.6;
    color: #bdc3c7;
    margin-bottom: 12px;
  }
  
  .footer-tech {
    font-size: 12px;
    color: #95a5a6;
    margin: 0;
  }
}

.footer-links {
  display: flex;
  gap: 40px;
  flex-wrap: wrap; // 小屏自动换行，避免横向溢出
}

.link-group {
  .link-title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 16px;
    color: #ecf0f1;
  }
  
  .link-list {
    list-style: none;
    padding: 0;
    margin: 0;
    
    li {
      margin-bottom: 8px;
      
      a {
        color: #bdc3c7;
        text-decoration: none;
        font-size: 14px;
        transition: color 0.3s ease;
        
        &:hover {
          color: var(--el-color-primary);
        }
      }
    }
  }
}

.footer-bottom {
  border-top: 1px solid #34495e;
  padding: 20px 24px; // 移除未定义变量，避免padding失效
  text-align: center;
  box-sizing: border-box;
}

.footer-copyright {
  max-width: 1200px;
  margin: 0 auto;
  
  p {
    margin: 4px 0;
    font-size: 14px;
    color: #95a5a6;
    word-wrap: break-word; // 防止文字换行溢出
  }
  
  .footer-privacy {
    font-size: 12px;
    color: #7f8c8d;
  }
}

// 响应式适配优化
@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    gap: 24px;
    padding: 24px 16px 16px;
  }
  
  .footer-links {
    flex-direction: column;
    gap: 24px;
  }
  
  .footer-bottom {
    padding: 16px 16px;
  }
}

@media (max-width: 480px) {
  .footer-info {
    .footer-brand {
      .footer-title {
        font-size: 18px;
      }
    }
    
    .footer-desc {
      font-size: 13px;
      line-height: 1.5; // 优化行高，避免文字重叠
    }
  }
  
  .link-group {
    .link-title {
      font-size: 15px;
    }
    .link-list li a {
      font-size: 13px;
    }
  }
}
</style>
<template>
  <div id="app">
    <Navbar />
    <!-- 去掉 el-container，使用纯 div 布局 -->
    <div class="app-content">
      <main class="app-main">
        <router-view />
      </main>
    </div>
    <Footer />
    <!-- 全局播放器 -->
    <MusicPlayer />
    <!-- AI助手侧边栏 -->
    <AIAssistantSidebar v-model:isOpen="isAISidebarOpen" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Navbar from './components/global/Navbar.vue'
import Footer from './components/global/Footer.vue'
import MusicPlayer from './components/global/MusicPlayer.vue'
import AIAssistantSidebar from './components/global/AIAssistantSidebar.vue'
import { useTheme } from './composables/useTheme'

// 使用主题管理
const { initTheme } = useTheme()

// AI侧边栏状态
const isAISidebarOpen = ref(false)

onMounted(() => {
  // 初始化主题
  initTheme()
})
</script>

<style lang="scss">
@use './assets/styles/global.scss' as *;

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-page);
  width: 100%;
  margin: 0;
  padding: 0;
  position: relative;
}

// 关键：使用简单的 div 容器替代 el-container
.app-content {
  flex: 1; // 占据剩余空间
  display: flex;
  flex-direction: column;
  width: 100%;
  position: relative;
}

.app-main {
  flex: 1;
  padding: var(--spacing-page, 24px);
  width: 100%;
  overflow-y: auto; // 允许内容滚动
  overflow-x: hidden;
  position: relative;
  box-sizing: border-box;
}

// 全局元素过渡动画
.btn-hover {
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-2);
  }
  
  &:active {
    transform: translateY(0);
  }
}

.card-hover {
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-3);
  }
}

// 平滑滚动
html {
  scroll-behavior: smooth;
  height: 100%; // 确保html占满视口高度
  box-sizing: border-box;
}

body {
  height: 100%; // 确保body占满视口高度
  margin: 0; // 移除body默认margin
  padding: 0; // 移除body默认padding
  box-sizing: border-box;
}

// 响应式布局优化
@media (max-width: 768px) {
  .app-main {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .app-main {
    padding: 12px;
  }
}

// 自定义滚动条
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
  transition: background 0.3s ease;
  
  &:hover {
    background: var(--text-light);
  }
}
</style>
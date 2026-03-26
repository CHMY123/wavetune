<template>
  <div class="admin-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- 侧边导航 -->
    <aside class="admin-sidebar" :class="{ 'collapsed': sidebarCollapsed }">
      <div class="admin-sidebar-header">
        <h2 v-if="!sidebarCollapsed">WaveTune CMS</h2>
        <el-icon v-else class="sidebar-logo"><House /></el-icon>
      </div>
      <nav class="admin-nav">
        <ul>
          <li>
            <router-link to="/admin/dashboard" class="nav-item">
              <el-icon><House /></el-icon>
              <span v-if="!sidebarCollapsed">仪表盘</span>
            </router-link>
          </li>
          <li>
            <router-link to="/admin/music" class="nav-item">
              <el-icon><Headset /></el-icon>
              <span v-if="!sidebarCollapsed">音乐管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/admin/users" class="nav-item">
              <el-icon><User /></el-icon>
              <span v-if="!sidebarCollapsed">用户管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/admin/feedback" class="nav-item">
              <el-icon><ChatDotRound /></el-icon>
              <span v-if="!sidebarCollapsed">反馈管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/admin/federated" class="nav-item">
              <el-icon><DataAnalysis /></el-icon>
              <span v-if="!sidebarCollapsed">联邦学习管理</span>
            </router-link>
          </li>
          <li>
            <router-link to="/admin/config" class="nav-item">
              <el-icon><Setting /></el-icon>
              <span v-if="!sidebarCollapsed">系统配置</span>
            </router-link>
          </li>
        </ul>
      </nav>
    </aside>
    
    <!-- 主内容区 -->
    <main class="admin-content">
      <!-- 顶部栏 -->
      <header class="admin-header">
        <div class="admin-header-left">
          <el-button type="text" @click="toggleSidebar" class="sidebar-toggle" :icon="sidebarCollapsed ? Menu : Close" />
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-for="(item, index) in breadcrumb" :key="index">
              {{ item }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="admin-header-right">
          <el-dropdown>
            <span class="admin-user">
              <el-avatar :size="32" :src="userInfo.avatar || '/static/avatar/default.jpg'">
                {{ userInfo.username?.charAt(0) || 'U' }}
              </el-avatar>
              <span v-if="!isMobile">{{ userInfo.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      
      <!-- 内容区域 -->
      <div class="admin-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { House, Headset, User, ChatDotRound, Setting, ArrowDown, SwitchButton, Menu, Close, DataAnalysis } from '@element-plus/icons-vue';

const router = useRouter();
const route = useRoute();

const userInfo = ref({});
const breadcrumb = ref([]);
const sidebarCollapsed = ref(false);
const isMobile = ref(false);

// 计算当前激活的菜单
const activeMenu = computed(() => {
  const path = route.path;
  return path;
});

// 检查是否为移动设备
const checkIsMobile = () => {
  isMobile.value = window.innerWidth < 768;
  if (isMobile.value) {
    sidebarCollapsed.value = true;
  }
};

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
};

// 计算面包屑
const updateBreadcrumb = () => {
  const path = route.path;
  const breadcrumbMap = {
    '/admin/dashboard': ['仪表盘'],
    '/admin/music': ['音乐管理'],
    '/admin/users': ['用户管理'],
    '/admin/feedback': ['反馈管理'],
    '/admin/config': ['系统配置'],
    '/admin/federated': ['联邦学习管理']
  };
  
  breadcrumb.value = breadcrumbMap[path] || ['仪表盘'];
};

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('session_token');
  localStorage.removeItem('user');
  router.push('/login');
};

// 从localStorage获取用户信息
const getUserInfoFromLocalStorage = () => {
  try {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      return JSON.parse(userStr);
    }
    return {};
  } catch (error) {
    console.error('获取用户信息失败:', error);
    return {};
  }
};

// 检查用户是否登录且具有管理员权限
const checkAdminPermission = () => {
  const token = localStorage.getItem('session_token');
  if (!token) {
    router.push('/login');
    return false;
  }
  
  const user = getUserInfoFromLocalStorage();
  if (!user.role || user.role !== 'admin') {
    router.push('/user-center');
    return false;
  }
  
  return true;
};

// 监听窗口大小变化
const handleResize = () => {
  checkIsMobile();
};

// 初始化
onMounted(() => {
  if (checkAdminPermission()) {
    userInfo.value = getUserInfoFromLocalStorage();
    updateBreadcrumb();
    checkIsMobile();
    window.addEventListener('resize', handleResize);
  }
});

// 监听路由变化
watch(() => route.path, () => {
  updateBreadcrumb();
  // 在移动设备上，切换路由后自动收起侧边栏
  if (isMobile.value) {
    sidebarCollapsed.value = true;
  }
});

// 清理事件监听
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style lang="scss" scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background-color: #f5f7fa;
  transition: all 0.3s ease;
  position: relative;
  
  // 深色主题样式
  :global(.theme-dark) & {
    background-color: #111827;
  }
  
  .admin-sidebar {
    width: 240px;
    background-color: #1f2937;
    color: #f3f4f6;
    display: flex;
    flex-direction: column;
    transition: all 0.3s ease;
    
    &.collapsed {
      width: 64px;
      
      .admin-sidebar-header {
        padding: 16px;
        display: flex;
        justify-content: center;
        
        h2 {
          display: none;
        }
        
        .sidebar-logo {
          display: block;
          font-size: 24px;
          color: #ffffff;
        }
      }
      
      .admin-nav {
        ul {
          li {
            .nav-item {
              padding: 12px 8px;
              justify-content: center;
              
              el-icon {
                margin-right: 0;
              }
              
              span {
                display: none;
              }
            }
          }
        }
      }
    }
    
    .admin-sidebar-header {
      padding: 20px;
      border-bottom: 1px solid #374151;
      
      h2 {
        font-size: 18px;
        font-weight: 600;
        margin: 0;
      }
      
      .sidebar-logo {
        display: none;
      }
    }
    
    .admin-nav {
      flex: 1;
      padding: 20px 0;
      
      ul {
        list-style: none;
        padding: 0;
        margin: 0;
        
        li {
          margin: 0;
          
          .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            color: #d1d5db;
            text-decoration: none;
            transition: all 0.3s ease;
            
            el-icon {
              margin-right: 10px;
              font-size: 18px;
            }
            
            &:hover {
              background-color: #374151;
              color: #ffffff;
            }
            
            &.router-link-active {
              background-color: #3b82f6;
              color: #ffffff;
            }
          }
        }
      }
    }
  }
  
  .admin-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    
    .admin-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 20px;
      height: 60px;
      background-color: #ffffff;
      border-bottom: 1px solid #e5e7eb;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      
      // 深色主题样式
      :global(.theme-dark) & {
        background-color: #1f2937;
        border-bottom: 1px solid #374151;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        
        .admin-header-left {
          el-breadcrumb {
            color: #d1d5db;
          }
        }
        
        .admin-header-right {
          .admin-user {
            color: #d1d5db;
            
            &:hover {
              background-color: #374151;
            }
          }
        }
      }
      
      .admin-header-left {
        display: flex;
        align-items: center;
        gap: 12px;
        
        .sidebar-toggle {
          display: none;
        }
        
        el-breadcrumb {
          font-size: 14px;
        }
      }
      
      .admin-header-right {
        .admin-user {
          display: flex;
          align-items: center;
          cursor: pointer;
          padding: 8px 12px;
          border-radius: 6px;
          transition: all 0.3s ease;
          
          &:hover {
            background-color: #f3f4f6;
          }
          
          el-avatar {
            margin-right: 10px;
          }
          
          span {
            margin-right: 5px;
          }
        }
      }
    }
    
    .admin-main {
      flex: 1;
      padding: 20px;
      overflow-y: auto;
      -webkit-overflow-scrolling: touch;
      
      // 深色主题样式
      :global(.theme-dark) & {
        background-color: #111827;
        color: #f3f4f6;
      }
    }
  }
  
  // 移动设备适配
  @media (max-width: 768px) {
    height: 100vh;
    overflow: hidden;
    
    .admin-sidebar {
      position: fixed;
      left: 0;
      top: 0;
      height: 100vh;
      z-index: 1000;
      transform: translateX(-100%);
      
      &.collapsed {
        transform: translateX(0);
      }
    }
    
    .admin-content {
      width: 100%;
      height: 100vh;
      
      .admin-header {
        padding: 0 16px;
        
        .admin-header-left {
          .sidebar-toggle {
            display: block;
          }
          
          el-breadcrumb {
            font-size: 12px;
          }
        }
      }
      
      .admin-main {
        padding: 16px;
        height: calc(100vh - 60px);
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
      }
    }
  }
  
  // 平板设备适配
  @media (min-width: 769px) and (max-width: 1024px) {
    .admin-sidebar {
      width: 200px;
      
      .admin-sidebar-header {
        padding: 16px;
        
        h2 {
          font-size: 16px;
        }
      }
      
      .admin-nav {
        ul {
          li {
            .nav-item {
              padding: 10px 16px;
              
              el-icon {
                font-size: 16px;
              }
            }
          }
        }
      }
    }
  }
}

// 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

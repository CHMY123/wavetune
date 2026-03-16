<template>
  <div class="ai-assistant-sidebar" :class="{ 'sidebar-open': isOpen }">
    <div class="sidebar-header">
      <div class="header-content">
        <div class="ai-avatar">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 16v-4"></path>
            <path d="M12 8h.01"></path>
          </svg>
        </div>
        <div class="header-info">
          <h3>AI 助手</h3>
          <p class="status">在线</p>
        </div>
      </div>
      <button class="close-btn" @click="toggleSidebar">
        <span class="close-icon">×</span>
      </button>
    </div>
    <div class="chat-container">
      <div class="message-list" ref="messageList">
        <div 
          v-for="(message, index) in messages" 
          :key="index"
          class="message" 
          :class="{ 'user-message': message.role === 'user', 'ai-message': message.role === 'assistant' }"
        >
          <div v-if="message.role === 'assistant'" class="message-avatar">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M12 16v-4"></path>
              <path d="M12 8h.01"></path>
            </svg>
          </div>
          <div class="message-content">
            <span v-if="message.role === 'user'">{{ message.content }}</span>
            <div v-else v-html="parseMarkdown(message.content)"></div>
          </div>
          <div v-if="message.role === 'user'" class="message-avatar user-avatar">
            <img :src="userAvatarUrl" alt="用户头像" class="avatar-image">
          </div>
        </div>
      </div>
      <div class="input-container">
        <input 
          v-model="userInput" 
          type="text" 
          placeholder="输入您的问题..."
          @keyup.enter="sendMessage"
          class="message-input"
          :disabled="isLoading"
        />
        <button @click="sendMessage" class="send-btn" :disabled="isLoading">
          <span v-if="!isLoading" class="send-icon">→</span>
          <div v-else class="loading-spinner"></div>
        </button>
      </div>
    </div>
  </div>
  <button class="toggle-btn" @click="toggleSidebar" :class="{ 'toggle-btn-open': isOpen }">
    <svg v-if="!isOpen" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <line x1="3" y1="12" x2="21" y2="12"></line>
      <line x1="3" y1="6" x2="21" y2="6"></line>
      <line x1="3" y1="18" x2="21" y2="18"></line>
    </svg>
    <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <line x1="21" y1="12" x2="3" y2="12"></line>
      <line x1="21" y1="6" x2="3" y2="6"></line>
      <line x1="21" y1="18" x2="3" y2="18"></line>
    </svg>
  </button>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import { usePlayerStore } from '../../stores/playerStore'
import { requestMethod } from '../../utils/request'
import axios from 'axios'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:isOpen'])

const messages = ref([
  {
    role: 'assistant',
    content: '您好！我是您的AI助手，有什么可以帮助您的吗？'
  }
])
const userInput = ref('')
const messageList = ref(null)
const playerStore = usePlayerStore()
const isLoading = ref(false)

// 获取用户信息和头像
const userInfo = computed(() => {
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      return JSON.parse(userStr)
    }
    return null
  } catch (error) {
    console.error('获取用户信息失败:', error)
    return null
  }
})

// 用户头像URL
const userAvatarUrl = computed(() => {
  return userInfo.value?.avatar || '/static/avatar/default.jpg'
})

const toggleSidebar = () => {
  emit('update:isOpen', !props.isOpen)
}

// 解析markdown格式
const parseMarkdown = (text) => {
  // 解析粗体
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // 解析斜体
  text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
  // 解析无序列表
  text = text.replace(/^\s*\-\s+(.*?)$/gm, '<li>$1</li>');
  text = text.replace(/(<li>.*?<\/li>)/s, '<ul>$1</ul>');
  // 解析有序列表
  text = text.replace(/^\s*\d+\.\s+(.*?)$/gm, '<li>$1</li>');
  text = text.replace(/(<li>.*?<\/li>)/s, '<ol>$1</ol>');
  // 解析段落
  text = text.replace(/^(?!<ul>|<ol>|<li>)(.*?)$/gm, '<p>$1</p>');
  // 移除多余的空行
  text = text.replace(/\n{3,}/g, '\n\n');
  return text;
};

const sendMessage = async () => {
  if (!userInput.value.trim()) return
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userInput.value
  })
  
  const input = userInput.value
  userInput.value = ''
  isLoading.value = true
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  // 调用后端API
  try {
    const response = await requestMethod.post('/ai/chat', {
      message: input
    })
    
    // 添加AI回复
    messages.value.push({
      role: 'assistant',
      content: response.response
    })
    
    // 滚动到底部
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('AI API 调用失败:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，系统出现错误，请稍后再试。'
    })
    
    // 滚动到底部
    await nextTick()
    scrollToBottom()
  } finally {
    isLoading.value = false
  }
}

const scrollToBottom = () => {
  if (messageList.value) {
    messageList.value.scrollTop = messageList.value.scrollHeight
  }
}

// 监听消息变化，自动滚动到底部
watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })
</script>

<style lang="scss" scoped>
.ai-assistant-sidebar {
  position: fixed;
  right: -400px;
  top: 0;
  width: 400px;
  height: 100vh;
  background-color: var(--bg-card);
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
  transition: right 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  
  &.sidebar-open {
    right: 0;
  }
  
  .sidebar-header {
    padding: 20px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .header-content {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .ai-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
      }
      
      .header-info {
        h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        .status {
          margin: 4px 0 0 0;
          font-size: 12px;
          color: var(--text-light);
          display: flex;
          align-items: center;
          gap: 4px;
          
          &::before {
            content: '';
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #4CAF50;
          }
        }
      }
    }
    
    .close-btn {
      background: none;
      border: none;
      font-size: 24px;
      color: var(--text-secondary);
      cursor: pointer;
      padding: 0;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 4px;
      transition: all 0.2s ease;
      
      &:hover {
        background-color: var(--bg-secondary);
        color: var(--text-primary);
      }
    }
  }
  
  .chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 20px;
    
    .message-list {
      flex: 1;
      overflow-y: auto;
      margin-bottom: 20px;
      
      .message {
        margin-bottom: 16px;
        max-width: 80%;
        display: flex;
        align-items: flex-start;
        gap: 8px;
        
        &.user-message {
          align-self: flex-end;
          margin-left: auto;
          flex-direction: row-reverse;
          
          .message-content {
            background-color: var(--color-primary);
            color: white;
            border-radius: 18px 18px 4px 18px;
          }
        }
        
        &.ai-message {
          align-self: flex-start;
          
          .message-content {
            background-color: var(--bg-secondary);
            color: var(--text-primary);
            border-radius: 18px 18px 18px 4px;
          }
        }
        
        .message-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          margin-top: 2px;
          
          &.user-avatar {
            background-color: var(--bg-secondary);
            color: var(--text-secondary);
          }
          
          .avatar-image {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            object-fit: cover;
          }
          
          &:not(.user-avatar) {
            background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
            color: white;
          }
        }
        
        .message-content {
          padding: 12px 16px;
          font-size: 14px;
          line-height: 1.5;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }
      }
    }
    
    .input-container {
      display: flex;
      gap: 10px;
      
      .message-input {
        flex: 1;
        padding: 12px 16px;
        border: 1px solid var(--border-color);
        border-radius: 24px;
        font-size: 14px;
        background-color: var(--bg-secondary);
        color: var(--text-primary);
        transition: all 0.2s ease;
        
        &:focus {
          outline: none;
          border-color: var(--color-primary);
          box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
        }
        
        &::placeholder {
          color: var(--text-light);
        }
      }
      
      .send-btn {
        width: 48px;
        height: 48px;
        border: none;
        border-radius: 50%;
        background-color: var(--color-primary);
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        
        &:hover:not(:disabled) {
          background-color: var(--color-primary-light);
          transform: scale(1.05);
        }
        
        &:active:not(:disabled) {
          transform: scale(0.95);
        }
        
        &:disabled {
          background-color: var(--text-muted);
          cursor: not-allowed;
        }
      }
      
      .loading-spinner {
        width: 20px;
        height: 20px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s ease-in-out infinite;
      }
      
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    }
  }
}

.toggle-btn {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 56px;
  height: 56px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
  transition: all 0.3s ease;
  z-index: 999;
  backdrop-filter: blur(10px);
  
  &:hover {
    transform: translateY(-50%) scale(1.1);
    box-shadow: 0 8px 24px rgba(64, 158, 255, 0.5);
  }
  
  &:active {
    transform: translateY(-50%) scale(0.95);
  }
  
  &.toggle-btn-open {
    right: 420px;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .ai-assistant-sidebar {
    width: 300px;
    right: -300px;
    
    &.sidebar-open {
      right: 0;
    }
  }
  
  .toggle-btn {
    width: 48px;
    height: 48px;
  }
  
  .toggle-btn.toggle-btn-open {
    right: 320px;
  }
}

@media (max-width: 480px) {
  .ai-assistant-sidebar {
    width: 100%;
    right: -100%;
  }
  
  .toggle-btn {
    width: 48px;
    height: 48px;
    right: 16px;
  }
  
  .toggle-btn.toggle-btn-open {
    right: 16px;
  }
  
  .message-list {
    .message {
      max-width: 85%;
    }
  }
}

// 自定义滚动条
.message-list {
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--bg-secondary);
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 3px;
    
    &:hover {
      background: var(--text-light);
    }
  }
}
</style>
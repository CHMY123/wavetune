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
import { ref, watch, nextTick, computed, onMounted } from 'vue'
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

// 初始化消息列表，从本地存储加载
const initMessages = () => {
  try {
    const savedMessages = localStorage.getItem('ai_assistant_messages')
    if (savedMessages) {
      const parsedMessages = JSON.parse(savedMessages)
      return parsedMessages.length > 0 ? parsedMessages : [
        {
          role: 'assistant',
          content: '您好！我是您的AI助手，有什么可以帮助您的吗？'
        }
      ]
    }
  } catch (error) {
    console.error('加载消息历史失败:', error)
  }
  return [
    {
      role: 'assistant',
      content: '您好！我是您的AI助手，有什么可以帮助您的吗？'
    }
  ]
}

const messages = ref(initMessages())
const userInput = ref('')
const messageList = ref(null)
const playerStore = usePlayerStore()
const isLoading = ref(false)
const showGuide = ref(false)

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
  // 解析标题
  text = text.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
  text = text.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
  text = text.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
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
  // 解析段落（排除标题）
  text = text.replace(/^(?!<h[1-3]>|<ul>|<ol>|<li>)(.*?)$/gm, '<p>$1</p>');
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
  
  // 添加AI消息占位符
  const aiMessageIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: ''
  })
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  // 调用后端API
  try {
    const response = await requestMethod.post('/ai/chat', {
      message: input
    })
    
    // 逐字显示AI回复
    const aiResponse = response.response
    let currentText = ''
    let index = 0
    
    const typingInterval = setInterval(() => {
      if (index < aiResponse.length) {
        currentText += aiResponse.charAt(index)
        messages.value[aiMessageIndex].content = currentText
        index++
        // 滚动到底部
        nextTick(() => {
          scrollToBottom()
        })
      } else {
        clearInterval(typingInterval)
        isLoading.value = false
      }
    }, 30) // 控制打字速度
  } catch (error) {
    console.error('AI API 调用失败:', error)
    // 逐字显示错误消息
    const errorMessage = '抱歉，系统出现错误，请稍后再试。'
    let currentText = ''
    let index = 0
    
    const typingInterval = setInterval(() => {
      if (index < errorMessage.length) {
        currentText += errorMessage.charAt(index)
        messages.value[aiMessageIndex].content = currentText
        index++
        // 滚动到底部
        nextTick(() => {
          scrollToBottom()
        })
      } else {
        clearInterval(typingInterval)
        isLoading.value = false
      }
    }, 50)
  }
}

const scrollToBottom = () => {
  if (messageList.value) {
    messageList.value.scrollTop = messageList.value.scrollHeight
  }
}

// 保存消息历史到本地存储
const saveMessagesToStorage = () => {
  try {
    // 只保存最近3条对话（6条消息，因为每条对话包含用户和AI的消息）
    const recentMessages = messages.value.slice(-6)
    localStorage.setItem('ai_assistant_messages', JSON.stringify(recentMessages))
  } catch (error) {
    console.error('保存消息历史失败:', error)
  }
}

// 监听消息变化，自动滚动到底部并保存到本地存储
watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
    saveMessagesToStorage()
  })
}, { deep: true })

// 组件挂载时检查是否是新用户，并确保初始化消息被保存
onMounted(() => {
  checkNewUser()
  // 确保初始化消息被保存到本地存储
  saveMessagesToStorage()
})

// 检查是否是新用户并显示引导
const checkNewUser = () => {
  try {
    const user = localStorage.getItem('user')
    const hasSeenGuide = localStorage.getItem('has_seen_ai_guide')
    
    if (user && !hasSeenGuide) {
      // 显示新用户引导
      showGuide.value = true
      // 标记用户已看过引导
      localStorage.setItem('has_seen_ai_guide', 'true')
      
      // 添加引导消息
      setTimeout(() => {
        messages.value.push({
          role: 'assistant',
          content: '欢迎使用WaveTune智能脑疲劳检测系统！\n\n我是您的AI助手，为您提供以下服务：\n\n- 脑疲劳检测结果解读\n- 音乐推荐与干预方案\n- 系统功能使用指导\n- 常见问题解答\n\n您可以随时向我咨询任何问题，我会尽力为您提供帮助！'
        })
      }, 1000)
    }
  } catch (error) {
    console.error('检查新用户状态失败:', error)
  }
}
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
  z-index: 2100;
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
    min-height: 0; /* 确保flex子元素能够正确收缩 */
    
    .message-list {
      flex: 1;
      overflow-y: auto;
      margin-bottom: 20px;
      max-height: calc(100vh - 200px); /* 限制最大高度，确保输入框有空间 */
      
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
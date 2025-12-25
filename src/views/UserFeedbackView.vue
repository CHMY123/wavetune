<template>
  <div class="user-feedback-view">
    <!-- 波形背景装饰 -->
    <div class="wave-background">
      <div class="wave wave-1"></div>
      <div class="wave wave-2"></div>
      <div class="wave wave-3"></div>
    </div>
    <!-- 顶部导航区域 -->
    <div class="top-section">

      <el-page-header content="用户信息与反馈" class="page-header">
        <template #extra>
          <div class="header-divider"></div>
        </template>
      </el-page-header>
    </div>

    <!-- 主要内容区域 -->
    <el-row :gutter="20" class="main-section">
      <!-- 个人信息卡片 -->
      <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
        <CardContainer title="个人信息" class="user-info-card">
          <div class="avatar-section">
            <el-avatar 
              :size="100" 
              :src="user.avatar || resolveMedia('/static/avatar/default.jpg')" 
              class="user-avatar" 
            />
            <div style="margin-top: 12px">{{ user.name || '未登录' }}</div>
            <el-button 
              type="text" 
              class="change-avatar-btn" 
              @click="$router.push('/user-center')"
            >
              更换头像
            </el-button>
          </div>

          <el-descriptions :column="1" class="user-descriptions">
            <el-descriptions-item label="姓名">
              <span class="user-name">{{ user.name || '—' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="学号">{{ user.student_id || '—' }}</el-descriptions-item>
            <el-descriptions-item label="注册">{{ user.create_time ? formatDate(user.create_time) : '—' }}</el-descriptions-item>
            <el-descriptions-item label="检测">
              <span class="status-normal">{{ user.detection_count || 0 }} 次</span>
            </el-descriptions-item>
            <el-descriptions-item label="干预">
              <span class="status-primary">{{ user.intervention_count || 0 }} 次</span>
            </el-descriptions-item>
          </el-descriptions>

          <div class="info-notice">
            以上信息仅用于系统数据关联，不会对外泄露
          </div>
        </CardContainer>
      </el-col>

      <!-- 反馈表单卡片 -->
      <el-col :xs="24" :sm="24" :md="16" :lg="16" :xl="16">
        <CardContainer title="系统使用反馈" class="feedback-form-card">
          <el-form 
            ref="feedbackFormRef" 
            :model="feedbackForm" 
            :rules="formRules" 
            label-width="100px" 
            class="feedback-form"
          >
            <el-form-item label="反馈类型" prop="type">
              <el-radio-group v-model="feedbackForm.type">
                <el-radio label="accuracy">脑疲劳检测准确性</el-radio>
                <el-radio label="music">轻音乐推荐效果</el-radio>
                <el-radio label="function">系统功能建议</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="反馈内容" prop="content">
              <el-input 
                v-model="feedbackForm.content" 
                type="textarea" 
                :rows="5" 
                placeholder="请详细描述您的体验或建议（最多 500 字）" 
                maxlength="500" 
                show-word-limit 
              />
            </el-form-item>

            <el-form-item label="满意度评分" prop="rating">
              <div class="rating-section">
                <p class="rating-title">对系统的满意度</p>
                <!-- 仅显示星星，不显示数值 -->
                <el-rate v-model="feedbackForm.rating" :max="5" />
              </div>
            </el-form-item>

            <el-form-item class="form-actions">
              <div class="action-buttons">
                <el-button @click="cancelFeedback">取消</el-button>
                <el-button type="primary" @click="submitFeedback">提交反馈</el-button>
              </div>
            </el-form-item>
          </el-form>

          <!-- 历史反馈记录 -->
          <div class="history-section" v-if="feedbackList.length">
          <h4>历史反馈</h4>
          <el-timeline>
              <el-timeline-item
                v-for="item in feedbackList"
                :key="item.id"
                :timestamp="item.submit_time"
              >
                <div class="history-item" style="padding: 12px; border-radius: 8px; background: #f9f9f9;">
                  <!-- 操作栏：名称+类型 + 评分+删除 -->
                  <div class="history-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div style="display:flex;align-items:center;gap:12px">
                      <strong>{{ user.name || '匿名' }}</strong>
                      <el-tag size="small">{{ item.feedback_type_name || '其他' }}</el-tag>
                    </div>
                    <div style="display: flex; align-items: center; gap: 16px;">
                      <el-rate :model-value="item.score" :max="5" disabled />
                      <el-button type="danger" size="mini" @click="deleteFeedback(item.id)">删除</el-button>
                    </div>
                  </div>
                  <!-- 反馈内容：单独区块，与操作栏分隔 -->
                  <div class="history-content" style="padding: 8px; background: #fff; border-radius: 4px;">
                    {{ item.content }}
                  </div>
                </div>
              </el-timeline-item>
          </el-timeline>
        </div>
          <div v-else class="history-empty" style="margin-top:24px;padding:24px;">
            <el-empty description="还没有历史反馈">
              <template #footer>
                <el-button type="primary" @click="$refs.feedbackFormRef?.scrollIntoView?.() || window.scrollTo({top:0,behavior:'smooth'})">去提交第一个反馈</el-button>
              </template>
            </el-empty>
          </div>
        </CardContainer>
      </el-col>
    </el-row>

    <!-- 底部提示区域 -->
    <div class="bottom-section">
      <div class="feedback-notice">
        <p>反馈提交后，我们将在 3 个工作日内评估并回复；若需紧急支持，请通过以下方式联系我们：</p>
        <p>邮箱：<a href="mailto:help@wavetune.example">help@wavetune.com</a> ｜ QQ 群：12345678</p>
        <p>常见问题：<a href="/help/faq" target="_blank">查看 FAQ</a></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import CardContainer from '@/components/global/CardContainer.vue'
import { resolveMedia } from '@/utils/media'
import { requestMethod } from '@/utils/request'
import { ElMessage } from 'element-plus'
import { ElMessageBox } from 'element-plus'

// 路由实例
const router = useRouter()

// 表单引用
const feedbackFormRef = ref(null)

// 表单数据
const feedbackForm = reactive({
  type: 'accuracy',
  content: '',
  rating: 3
})

// 表单验证规则
const formRules = {
  type: [
    { required: true, message: '请选择反馈类型', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入反馈内容', trigger: 'blur' },
    { min: 10, message: '反馈内容至少10个字符', trigger: 'blur' }
  ]
}

// 用户信息（补充完整字段）
const user = reactive({
  avatar: null,
  name: '',
  student_id: '',       // 学号
  create_time: '',      // 注册时间
  detection_count: 0,   // 检测次数
  intervention_count: 0 // 干预次数
})

// 反馈列表
const feedbackList = ref([])

// 加载用户信息（补充完整字段读取）
const loadUser = () => {
  try {
    const u = JSON.parse(window.localStorage.getItem('user') || 'null')
    if (u) {
      user.avatar = resolveMedia(u.avatar || '/static/avatar/default.jpg')
      user.name = u.username || u.name || ''
      // 补充其他个人信息字段
      user.student_id = u.student_id || ''
      user.create_time = u.create_time || ''
      user.detection_count = u.detection_count || 0
      user.intervention_count = u.intervention_count || 0
    }
  } catch (e) {
    console.error('加载用户信息失败:', e)
  }
}

// 日期格式化工具
const formatDate = (dateString) => {
  if (!dateString) return '—'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return dateString // 格式化失败时显示原始字符串
  }
}

// 获取历史反馈
const fetchFeedbackList = async () => {
  try {
    // 尝试从 localStorage 获取用户ID
    let userId = null
    try {
      const u = JSON.parse(window.localStorage.getItem('user') || 'null')
      if (u && u.id) userId = u.id
    } catch (e) {
      console.error('获取用户ID失败:', e)
    }

    if (!userId) {
      feedbackList.value = []
      return
    }

    const res = await requestMethod.get('/feedback/history', {
      user_id: userId,
      page: 1,
      page_size: 20
    })

    // 后端返回结构: { code, msg, data: { list: [...] } }
    feedbackList.value = res.data?.list || []
  } catch (e) {
    console.error('获取历史反馈失败:', e)
  }
}

// 提交反馈
const submitFeedback = async () => {
  // 表单验证
  try {
    await feedbackFormRef.value.validate()
  } catch (err) {
    return
  }

  // 构建提交数据（按后端 Pydantic 模型字段命名）
  let userId = null
  try {
    const u = JSON.parse(window.localStorage.getItem('user') || 'null')
    if (u && u.id) userId = u.id
  } catch (e) {
    console.error('获取用户ID失败:', e)
  }

  if (!userId) {
    ElMessage.error('请先登录后再提交反馈')
    return
  }

  const payload = {
    user_id: userId,
    feedback_type: feedbackForm.type,
    content: feedbackForm.content.trim(),
    score: feedbackForm.rating
  }

  // 发送请求
  try {
    await requestMethod.post('/feedback/submit', payload)
    ElMessage.success('反馈已提交，感谢您的建议')
    // 重新拉取历史反馈，确保格式一致
    await fetchFeedbackList()
    // 重置表单
    feedbackForm.content = ''
    feedbackForm.rating = 3
    feedbackForm.type = 'accuracy'
    // 触发反馈更新事件
    try {
      window.dispatchEvent(new Event('feedback-changed'))
    } catch (e) {}
  } catch (e) {
    console.error('提交反馈失败:', e)
  }
}

// 删除反馈
const deleteFeedback = async (feedbackId) => {
  try {
    const u = JSON.parse(window.localStorage.getItem('user') || 'null')
    if (!u || !u.id) {
      ElMessage.error('请先登录')
      return
    }

    await ElMessageBox.confirm('确认删除这条反馈吗？此操作不可恢复', '删除反馈', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

      const res = await requestMethod.delete(`/feedback/${feedbackId}`, { user_id: u.id })
    if (res && res.code === 200) {
      ElMessage.success('删除成功')
      // 从本地列表移除
      feedbackList.value = feedbackList.value.filter(i => i.id !== feedbackId)
      try { window.dispatchEvent(new Event('feedback-changed')) } catch (e) {}
    } else {
      ElMessage.error(res?.msg || '删除失败')
    }
  } catch (e) {
    // 取消确认会抛错，不必提示
    if (e && e.message && e.message.includes('取消')) return
    console.error('删除反馈失败:', e)
    ElMessage.error('删除失败')
  }
}

// 取消反馈
const cancelFeedback = () => {
  feedbackForm.content = ''
  feedbackForm.rating = 3
  feedbackForm.type = 'accuracy'
  // 重置表单验证状态
  if (feedbackFormRef.value) {
    feedbackFormRef.value.clearValidate()
  }
}

// 组件挂载时
onMounted(() => {
  loadUser()
  window.addEventListener('auth-changed', loadUser)
  fetchFeedbackList()
})

// 组件卸载前
onBeforeUnmount(() => {
  window.removeEventListener('auth-changed', loadUser)
})
</script>

<style lang="scss" scoped>
// 设计令牌
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --color-primary: #3b82f6;
  --color-primary-light: #93c5fd;
  --color-primary-dark: #2563eb;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05);
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
}

.user-feedback-view {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  overflow: visible;
  box-shadow: var(--shadow-md);
  min-height: calc(100vh - 100px);
}

.wave-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
}

.wave {
  position: absolute;
  width: 200%;
  height: 100px;
  background: linear-gradient(90deg, var(--color-primary-light) 0%, transparent 100%);
  opacity: 0.1;
  border-radius: 50%;
  animation: wave-animation 15s linear infinite;
}

.wave-1 {
  top: 10%;
  left: -50%;
  animation-duration: 20s;
  animation-delay: 0s;
}

.wave-2 {
  top: 30%;
  left: -70%;
  animation-duration: 25s;
  animation-delay: -5s;
  height: 150px;
  background: linear-gradient(90deg, var(--color-primary) 0%, transparent 100%);
}

.wave-3 {
  top: 50%;
  left: -60%;
  animation-duration: 18s;
  animation-delay: -2s;
  height: 80px;
  background: linear-gradient(90deg, var(--color-primary-dark) 0%, transparent 100%);
}

@keyframes wave-animation {
  0% {
    transform: translateX(0) translateY(0);
  }
  50% {
    transform: translateX(-25%) translateY(10px);
  }
  100% {
    transform: translateX(-50%) translateY(0);
  }
}

.top-section {
  position: relative;
  z-index: 1;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(255, 255, 255, 0.8) 100%);
}

.main-section {
  position: relative;
  z-index: 1;
  padding: var(--spacing-lg);
  min-height: 600px;

.user-info-card {
  height: fit-content;
  background: rgba(255, 255, 255, 0.95);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }

  .avatar-section {
    text-align: center;
    margin-bottom: var(--spacing-lg);
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(255, 255, 255, 0.5) 100%);
    border-radius: var(--radius-md);
    padding: var(--spacing-md);
    border: 1px solid var(--border-color);
    
    .user-avatar {
      margin-bottom: var(--spacing-md);
      border: 4px solid rgba(59, 130, 246, 0.2);
      transition: transform 0.3s ease, border-color 0.3s ease;
      
      &:hover {
        transform: scale(1.05);
        border-color: var(--color-primary);
      }
    }

    .change-avatar-btn {
      font-size: 14px;
      transition: all 0.2s ease;
      color: var(--color-primary);
      
      &:hover {
        transform: translateY(-1px);
        text-decoration: underline;
      }
    }
  }

  .user-descriptions {
    margin-bottom: var(--spacing-md);
    
    :deep(.el-descriptions-item__label) {
      font-weight: 500;
      color: var(--text-secondary);
    }
    
    .user-name {
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .status-normal {
      color: #10b981;
      font-weight: 500;
    }
    
    .status-primary {
      color: var(--color-primary);
      font-weight: 500;
    }
  }

  .info-notice {
    margin-top: var(--spacing-md);
    font-size: 12px;
    color: var(--text-secondary);
    text-align: center;
    padding: var(--spacing-sm);
    background: rgba(248, 250, 252, 0.8);
    border-radius: var(--radius-sm);
  }
}

.feedback-form-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }

  .feedback-form {
    .el-form-item {
      margin-bottom: var(--spacing-lg);
      
      :deep(.el-form-item__label) {
        font-weight: 500;
        color: var(--text-primary);
      }
      
      :deep(.el-input__wrapper) {
        border-radius: var(--radius-md);
        transition: all 0.3s ease;
        
        &:focus-within {
          box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
          border-color: var(--color-primary);
        }  
  } 
      :deep(.el-radio__label) {
        color: var(--text-primary);
      }
      
      :deep(.el-radio__input.is-checked .el-radio__inner) {
        border-color: var(--color-primary);
        background-color: var(--color-primary);
      }
    }
    
    .rating-section {
      margin-bottom: var(--spacing-md);

      .rating-title {
        margin-bottom: var(--spacing-sm);
        font-size: 14px;
        color: var(--text-primary);
        font-weight: 500;
      }
      
      :deep(.el-rate__icon) {
        font-size: 22px;
        
        &.is-active {
          color: #f59e0b;
        }
      }
    }

    .form-actions {
      margin-bottom: 0;
      padding-top: var(--spacing-md);

      .action-buttons {
        display: flex;
        gap: var(--spacing-md);
      }
    }  

  .history-section {
    margin-top: var(--spacing-xl);
    padding-top: var(--spacing-lg);
    border-top: 1px dashed var(--border-color);

    h4 {
      margin-bottom: var(--spacing-md);
      font-size: 16px;
      color: var(--text-primary);
      font-weight: 600;
      position: relative;
      padding-left: var(--spacing-md);
      
      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 16px;
        background-color: var(--color-primary);
        border-radius: 2px;
      }
    }

    .history-item {
      padding: var(--spacing-md);
      background: rgba(255, 255, 255, 0.95);
      border-radius: var(--radius-md);
      border: 1px solid var(--border-color);
      margin-bottom: calc(var(--spacing-md) * 1.2);
      transition: all 0.24s ease;
      backdrop-filter: blur(6px);
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
      word-break: break-word;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        border-color: var(--color-primary-light);
      }

      .history-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 12px;
          flex-wrap: wrap;
          margin-bottom: var(--spacing-sm);
          font-size: 14px;

          .left {
            display: flex;
            align-items: center;
            gap: 12px;
          }

          .date {
            font-weight: 500;
            color: var(--text-secondary);
            font-size: 13px;
          }

          .feedback-type {
            color: var(--color-primary);
            font-weight: 600;
            font-size: 13px;
          }

          .rating {
            color: #f59e0b;
            font-weight: 500;
          }
        }

        .history-content {
          font-size: 14px;
          color: var(--text-primary);
          line-height: 1.7;
          padding: 12px;
          background: rgba(248, 250, 252, 0.95);
          border-radius: var(--radius-sm);
          border-left: 3px solid var(--color-primary);
          max-width: 100%;
          white-space: pre-wrap;
          word-break: break-word;
        }
      
      .history-actions {
        margin-top: var(--spacing-sm);
        display: flex;
        gap: var(--spacing-sm);
      }
    }
    /* 确保 Element Plus 时间线的内容区域不被固定宽度或 padding 限制 */
    :deep(.el-timeline) {
      padding-left: 0;
    }
    :deep(.el-timeline-item__wrapper) {
      display: block;
      padding: 0 0 16px 0;
    }
    :deep(.el-timeline-item__content) {
      width: 100% !important;
      padding: 0 !important;
    }
  }
}

.bottom-section {
  position: relative;
  z-index: 1;
  padding: calc(var(--spacing-lg) * 1.5);
  border-top: 1px solid var(--border-color);
  text-align: left;
  background: linear-gradient(180deg, rgba(250,250,250,0.6), transparent);
  backdrop-filter: blur(8px);

  .feedback-notice {
    margin: 0 0 var(--spacing-sm) 0;
    font-size: 14px;
    color: var(--text-primary);
    line-height: 1.6;
    font-weight: 500;
  }

  a {
    color: var(--color-primary);
    text-decoration: none;
    transition: all 0.2s ease;
    font-weight: 500;
    
    &:hover {
      text-decoration: underline;
      color: var(--color-primary-dark);
      transform: translateY(-1px);
    }
  }

  .contact-row {
    margin-top: var(--spacing-sm);
    display:flex;
    gap: var(--spacing-md);
    flex-wrap:wrap;
    align-items: center;
    
    p {
      margin:0;
      color: var(--text-secondary);
    }
  }

  .footer-divider {
    height: 1px;
    background: var(--border-color);
    margin: var(--spacing-md) 0;
  }
}

// 应用响应式工具
@import '@/assets/styles/breakpoints.scss';

// 响应式适配 - 使用断点混入
@include mobile-layout {
  :root {
    --spacing-page: 16px;
    --spacing-lg: 16px;
    --spacing-md: 12px;
    --spacing-sm: 8px;
  }
  
  .top-section {
    padding: var(--spacing-page);
    min-height: 200px;
  }
  
  .main-section {
    padding: var(--spacing-page);
    gap: var(--spacing-md);
  }
  
  .user-info-card {
    @include card(16px, 12px);
    margin-bottom: var(--spacing-md);
    
    .avatar-section {
      width: 100%;
      margin-bottom: var(--spacing-md);
      
      .avatar-container {
        width: 70px;
        height: 70px;
      }
      
      .user-details {
        text-align: center;
      }
    }
    
    .user-details {
      .user-name {
        @include responsive-font(18px, null, 16px);
      }
      
      .user-status {
        @include responsive-font(13px, null, 12px);
      }
    }
    
    .action-button {
      width: 100%;
      font-size: 14px;
      padding: 10px;
    }
  }
  
  .feedback-form-card {
    @include card(16px, 12px);
    margin-top: 0;
    
    .card-title {
      font-size: 18px;
      margin-bottom: var(--spacing-md);
    }
    
    .form-group {
      margin-bottom: var(--spacing-md);
    }
    
    .form-label {
      font-size: 14px;
      margin-bottom: 8px;
    }
    
    :deep(.el-input__wrapper),
    :deep(.el-textarea__wrapper) {
      padding: 6px 12px;
    }
    
    .rating-container {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--spacing-xs);
    }
    
    .submit-button {
      width: 100%;
      padding: 12px;
      font-size: 16px;
    }
  }
  
  .history-card {
    @include card(16px, 12px);
    
    .card-title {
      font-size: 18px;
      margin-bottom: var(--spacing-md);
    }
    
    .history-item {
      padding: 16px;
      
      .history-header {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--spacing-xs);
        margin-bottom: var(--spacing-xs);
      }
      
      .history-date {
        font-size: 12px;
      }
      
      .history-content {
        font-size: 13px;
        line-height: 1.5;
      }
    }
  }
  
  .bottom-section {
    padding: var(--spacing-md);
    
    .feedback-notice {
      font-size: 13px;
      line-height: 1.5;
    }
    
    .contact-row {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--spacing-sm);
      
      p {
        font-size: 12px;
      }
    }
  }
}

// 平板设备适配
@include respond-to(sm) {
  .content-wrapper {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }
  
  .user-info-card,
  .feedback-form-card,
  .history-card {
    @include card(18px);
  }
  
  .user-info-card {
    .avatar-section {
      width: 100%;
      margin-bottom: var(--spacing-md);
    }
  }
  
  .history-item {
    padding: 20px;
  }
}

// 大屏设备优化
@include large-desktop-layout {
  .user-feedback-view {
    min-height: 100vh;
  }
  
  .main-section {
    @include container(false);
    max-width: 1400px;
    display: grid;
    grid-template-columns: 300px 1fr;
    gap: 32px;
  }
  
  .user-info-card {
    @include card(24px);
    position: sticky;
    top: 100px;
  }
  
  .form-history-container {
    display: flex;
    flex-direction: column;
    gap: 32px;
  }
  
  .feedback-form-card,
  .history-card {
    @include card(24px);
  }
}

// 超大屏设备优化
@include extra-large-desktop-layout {
  .main-section {
    max-width: 1600px;
    grid-template-columns: 350px 1fr;
    gap: 40px;
  }
}

// 高对比度模式支持
@include high-contrast {
  .user-info-card,
  .feedback-form-card,
  .history-card {
    border: 2px solid #000;
    box-shadow: none;
  }
  
  .history-item {
    border: 1px solid #000;
  }
  
  :deep(.el-button) {
    border-width: 2px;
  }
  
  :deep(.el-input__wrapper),
  :deep(.el-textarea__wrapper) {
    border-width: 2px;
  }
}

// 减少动画模式支持
@media (prefers-reduced-motion: reduce) {
  * {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
  }
  
  .wave {
    animation: none !important;
  }
}
  .footer-divider {
    height: 1px;
    background: var(--border-color);
    margin: var(--spacing-lg) 0;
  }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .user-feedback-view {
    margin: 0;
    border-radius: 0;
    min-height: 100vh;
  }

  .top-section,
  .main-section,
  .bottom-section {
    padding: var(--spacing-md);
  }

  .main-section {
    flex-direction: column;
  }

  .history-item .history-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }
}
}
</style>
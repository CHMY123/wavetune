<template>
  <div class="user-center">
    <!-- 波形背景装饰 -->
    <div class="wave-background">
      <div class="wave wave-1"></div>
      <div class="wave wave-2"></div>
      <div class="wave wave-3"></div>
    </div>
    
    <div class="user-center-container">
      <!-- 用户信息卡片 -->
      <el-card class="user-info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <h2>个人信息</h2>
            <el-button type="primary" @click="editMode = !editMode">
              {{ editMode ? '取消编辑' : '编辑资料' }}
            </el-button>
          </div>
        </template>
        
        <div class="user-info-content">
          <!-- 头像区域 -->
          <div class="avatar-section">
            <el-avatar
              :size="120"
              :src="userInfo.avatar || '/static/avatar/default.jpg'"
              class="user-avatar"
            >
              <el-icon><User /></el-icon>
            </el-avatar>
            <el-upload
              v-if="editMode"
              class="avatar-uploader"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              :http-request="uploadAvatar"
            >
              <el-button type="primary" size="small" class="upload-btn">
                <el-icon><Upload /></el-icon>
                更换头像
              </el-button>
            </el-upload>
          </div>
          
          <!-- 用户信息表单 -->
          <el-form
            ref="userFormRef"
            :model="userForm"
            :rules="userRules"
            label-width="100px"
            class="user-form"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名" prop="username">
                  <el-input
                    v-model="userForm.username"
                    :disabled="!editMode"
                    placeholder="请输入用户名"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="学号" prop="student_id">
                  <el-input
                    v-model="userForm.student_id"
                    :disabled="!editMode"
                    placeholder="请输入学号"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input
                    v-model="userForm.email"
                    :disabled="!editMode"
                    placeholder="请输入邮箱"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="手机号" prop="phone">
                  <el-input
                    v-model="userForm.phone"
                    :disabled="!editMode"
                    placeholder="请输入手机号"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="检测次数">
                  <el-input :value="userInfo.detection_count" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="干预次数">
                  <el-input :value="userInfo.intervention_count" disabled />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="注册时间">
                  <el-input :value="formatDate(userInfo.create_time)" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="最后登录">
                  <el-input :value="formatDate(userInfo.last_login_time)" disabled />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item v-if="editMode">
              <el-button type="primary" :loading="updateLoading" @click="handleUpdateProfile">
                保存修改
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-card>
      
      <!-- 偏好设置卡片 -->
      <el-card class="preferences-card" shadow="hover">
        <template #header>
          <h2>偏好设置</h2>
        </template>
        
        <el-form
          ref="preferencesFormRef"
          :model="preferencesForm"
          label-width="120px"
          class="preferences-form"
        >
          <el-form-item label="默认疲劳等级">
            <el-select v-model="preferencesForm.default_fatigue_level" @change="updatePreference('default_fatigue_level', $event)">
              <el-option label="轻度疲劳" value="light" />
              <el-option label="中度疲劳" value="medium" />
              <el-option label="重度疲劳" value="heavy" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="偏好音乐类型">
            <el-select v-model="preferencesForm.preferred_music_type" @change="updatePreference('preferred_music_type', $event)">
              <el-option label="自然音效" value="natural" />
              <el-option label="钢琴音乐" value="piano" />
              <el-option label="白噪音" value="whitenoise" />
              <el-option label="混合音乐" value="mix" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="通知设置">
            <el-switch
              v-model="preferencesForm.notification_enabled"
              active-text="开启"
              inactive-text="关闭"
              @change="updatePreference('notification_enabled', $event ? 'true' : 'false')"
            />
          </el-form-item>
          
          <el-form-item label="自动播放">
            <el-switch
              v-model="preferencesForm.auto_play"
              active-text="开启"
              inactive-text="关闭"
              @change="updatePreference('auto_play', $event ? 'true' : 'false')"
            />
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- 会话管理卡片 -->
      <el-card class="sessions-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <h2>会话管理</h2>
            <el-button type="danger" @click="handleLogoutAll">
              退出所有设备
            </el-button>
          </div>
        </template>
        
        <el-table :data="sessions" style="width: 100%">
          <el-table-column prop="device_display" label="设备信息" />
          <el-table-column prop="ip_address" label="IP地址" />
          <el-table-column prop="create_time" label="登录时间">
            <template #default="{ row }">
              {{ formatDate(row.create_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="last_activity" label="最后活动">
            <template #default="{ row }">
              {{ formatDate(row.last_activity) }}
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button
                v-if="row.id !== currentSessionId"
                type="danger"
                size="small"
                @click="handleRevokeSession(row.id)"
              >
                撤销
              </el-button>
              <el-tag v-else type="success" size="small">当前会话</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
      
      <!-- 历史反馈卡片 -->
      <el-card class="feedback-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <h2>历史反馈</h2>
            <el-button type="primary" size="small" @click="showFeedbackForm = !showFeedbackForm">
              提交新反馈
            </el-button>
          </div>
        </template>
        
        <!-- 新反馈表单 -->
        <div v-if="showFeedbackForm" class="feedback-form-container">
          <el-form ref="feedbackFormRef" :model="feedbackForm" label-width="100px" class="feedback-form">
            <el-form-item label="反馈类型">
              <el-select v-model="feedbackForm.type">
                <el-option label="功能建议" value="suggestion" />
                <el-option label="问题反馈" value="bug" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
            <el-form-item label="反馈内容">
              <el-input v-model="feedbackForm.content" type="textarea" rows="4" placeholder="请输入您的反馈内容" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSubmitFeedback">提交</el-button>
              <el-button @click="showFeedbackForm = false">取消</el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 历史反馈列表 -->
        <el-table :data="feedbackList" style="width: 100%" class="feedback-table">
          <el-table-column prop="feedback_type" label="反馈类型">
            <template #default="{ row }">
              <el-tag :type="getFeedbackTypeTag(row.feedback_type)">
                {{ getFeedbackTypeText(row.feedback_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="content" label="反馈内容">
            <template #default="{ row }">
              <div class="feedback-content">{{ row.content }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="submit_time" label="提交时间">
            <template #default="{ row }">
              {{ formatDate(row.submit_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="处理状态">
            <template #default="{ row }">
              <el-tag :type="row.status === 'processed' ? 'success' : 'info'">
                {{ row.status === 'processed' ? '已处理' : '待处理' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
      
      <!-- 密码修改卡片 -->
      <el-card class="password-card" shadow="hover">
        <template #header>
          <h2>修改密码</h2>
        </template>
        
        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          label-width="100px"
          class="password-form"
        >
          <el-form-item label="原密码" prop="old_password">
            <el-input
              v-model="passwordForm.old_password"
              type="password"
              placeholder="请输入原密码"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="新密码" prop="new_password">
            <el-input
              v-model="passwordForm.new_password"
              type="password"
              placeholder="请输入新密码"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirm_password">
            <el-input
              v-model="passwordForm.confirm_password"
              type="password"
              placeholder="请再次输入新密码"
              show-password
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" :loading="passwordLoading" @click="handleChangePassword">
              修改密码
            </el-button>
            <el-button @click="resetPasswordForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { requestMethod } from '@/utils/request'
import { User, Upload } from '@element-plus/icons-vue'

export default {
  name: 'UserCenterView',
  components: {
    User,
    Upload
  },
  setup() {
    const router = useRouter()
    const userFormRef = ref()
    const preferencesFormRef = ref()
    const passwordFormRef = ref()
    
    // 用户信息
    const userInfo = ref({})
    const editMode = ref(false)
    const updateLoading = ref(false)
    const passwordLoading = ref(false)
    
    // 用户表单数据
    const userForm = reactive({
      username: '',
      student_id: '',
      email: '',
      phone: ''
    })
    
    // 偏好设置表单数据
    const preferencesForm = reactive({
      default_fatigue_level: 'medium',
      preferred_music_type: 'natural',
      notification_enabled: true,
      auto_play: false
    })
    
    // 密码修改表单数据
    const passwordForm = reactive({
      old_password: '',
      new_password: '',
      confirm_password: ''
    })
    
    // 会话数据
    const sessions = ref([])
    const currentSessionId = ref(null)
    
    // 表单验证规则
    const userRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 2, max: 50, message: '用户名长度在 2 到 50 个字符', trigger: 'blur' }
      ],
      student_id: [
        { required: true, message: '请输入学号', trigger: 'blur' },
        { min: 1, max: 20, message: '学号长度在 1 到 20 个字符', trigger: 'blur' }
      ],
      email: [
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      phone: [
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
      ]
    }
    
    const passwordRules = {
      old_password: [
        { required: true, message: '请输入原密码', trigger: 'blur' }
      ],
      new_password: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
      ],
      confirm_password: [
        { required: true, message: '请确认新密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== passwordForm.new_password) {
              callback(new Error('两次输入密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }
    
    // 获取当前用户 ID（优先使用本地存储的 user）
    const getCurrentUserId = () => {
      const u = localStorage.getItem('user')
      if (u) {
        try { return JSON.parse(u).id } catch { return 1 }
      }
      return 1
    }

    // 获取用户信息
    const fetchUserInfo = async () => {
      try {
        const uid = getCurrentUserId()
        const result = await requestMethod.get('/auth/profile', { user_id: uid })
        if (result && result.code === 200) {
          userInfo.value = result.data
          // 同步表单数据
          Object.assign(userForm, {
            username: result.data.username,
            student_id: result.data.student_id,
            email: result.data.email || '',
            phone: result.data.phone || ''
          })

          // 同步偏好设置
          if (result.data.preferences) {
            Object.assign(preferencesForm, {
              default_fatigue_level: result.data.preferences.default_fatigue_level || 'medium',
              preferred_music_type: result.data.preferences.preferred_music_type || 'natural',
              notification_enabled: result.data.preferences.notification_enabled === 'true',
              auto_play: result.data.preferences.auto_play === 'true'
            })
          }
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        ElMessage.error('获取用户信息失败')
      }
    }
    
    // 获取会话列表
    const fetchSessions = async () => {
      try {
        const uid = getCurrentUserId()
        const result = await requestMethod.get('/auth/sessions', { user_id: uid })
        if (result && result.code === 200) {
          sessions.value = result.data.sessions
          // 找到当前会话
          const currentToken = localStorage.getItem('session_token')
          const currentSession = sessions.value.find(s => s.session_token === currentToken)
          if (currentSession) {
            currentSessionId.value = currentSession.id
          }
        }
      } catch (error) {
        console.error('获取会话列表失败:', error)
      }
    }
    
    // 更新用户资料
    const handleUpdateProfile = async () => {
      if (!userFormRef.value) return

      try {
        // Element Plus validate 在校验失败时会抛出错误，成功时不返回值
        try {
          await userFormRef.value.validate()
        } catch (e) {
          // 校验未通过，直接返回
          return
        }

        updateLoading.value = true

        const uid = getCurrentUserId()

        // 构建干净的 payload：只包含后端期望的字段，且过滤掉空字符串
        const payload = {}
        if (userForm.username !== undefined && String(userForm.username).trim() !== '') {
          payload.username = String(userForm.username).trim()
        }
        if (userForm.email !== undefined && String(userForm.email).trim() !== '') {
          payload.email = String(userForm.email).trim()
        }
        if (userForm.phone !== undefined && String(userForm.phone).trim() !== '') {
          payload.phone = String(userForm.phone).trim()
        }

        // 发送请求（user_id 作为 query 参数）
        let result
        try {
          result = await requestMethod.put('/auth/profile', payload, { user_id: uid })
        } catch (err) {
          // 如果是后端的验证错误（FastAPI 返回 422），尽可能展示详细信息
          const detail = err.response?.data || err.response?.data?.detail
          console.error('更新用户资料失败 (后端):', err, detail)
          if (detail && detail.detail) {
            // FastAPI 验证错误通常在 detail 字段里
            const msgs = Array.isArray(detail.detail) ? detail.detail.map(d => d.msg).join('; ') : String(detail.detail)
            ElMessage.error(msgs || '更新失败，数据校验未通过')
          } else if (err.response?.data?.msg) {
            ElMessage.error(err.response.data.msg)
          } else {
            ElMessage.error(err.message || '更新失败，请稍后重试')
          }
          return
        }

        if (result && result.code === 200) {
          ElMessage.success('资料更新成功')
          // 更新本地存储中的 user，保证 Navbar 等组件显示最新资料
          try { localStorage.setItem('user', JSON.stringify(result.data)) } catch (e) {}
          // 通知全局 auth 变化，以便 Navbar 刷新用户信息
          try { window.dispatchEvent(new Event('auth-changed')) } catch (e) {}
          editMode.value = false
          await fetchUserInfo()
        } else {
          ElMessage.error(result?.msg || '更新失败')
        }
      } catch (error) {
        console.error('更新用户资料失败:', error)
        ElMessage.error('更新失败，请稍后重试')
      } finally {
        updateLoading.value = false
      }
    }
    
    // 更新偏好设置
    const updatePreference = async (key, value) => {
      try {
        const uid = getCurrentUserId()
        const result = await requestMethod.put('/auth/preference', {
          preference_key: key,
          preference_value: value
        }, { user_id: uid })
        if (result && result.code === 200) {
          ElMessage.success('偏好设置已更新')
        } else {
          ElMessage.error(result?.msg || '更新失败')
        }
      } catch (error) {
        console.error('更新偏好设置失败:', error)
        ElMessage.error('更新失败，请稍后重试')
      }
    }
    
    // 修改密码
    const handleChangePassword = async () => {
      if (!passwordFormRef.value) return
      
      try {
        const valid = await passwordFormRef.value.validate()
        if (!valid) return
        
        passwordLoading.value = true
        
        const uid = getCurrentUserId()
        const result = await requestMethod.post('/auth/change-password', {
          old_password: passwordForm.old_password,
          new_password: passwordForm.new_password
        }, { user_id: uid })
        if (result && result.code === 200) {
          ElMessage.success('密码修改成功')
          resetPasswordForm()
        } else {
          ElMessage.error(result?.msg || '修改失败')
        }
      } catch (error) {
        console.error('修改密码失败:', error)
        ElMessage.error('修改失败，请稍后重试')
      } finally {
        passwordLoading.value = false
      }
    }
    
    // 撤销会话
    const handleRevokeSession = async (sessionId) => {
      try {
        await ElMessageBox.confirm('确定要撤销此会话吗？', '确认撤销', {
          type: 'warning',
          confirmButtonText: '确认',
          cancelButtonText: '取消'
        })
        
        const uid = getCurrentUserId()
        const result = await requestMethod.delete(`/auth/session/${sessionId}`, { user_id: uid })
        if (result && result.code === 200) {
          ElMessage.success('会话已撤销')
          await fetchSessions()
        } else {
          ElMessage.error(result?.msg || '撤销失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('撤销会话失败:', error)
          ElMessage.error('撤销失败，请稍后重试')
        }
      }
    }
    
    // 退出所有设备
    const handleLogoutAll = async () => {
      try {
        await ElMessageBox.confirm('确定要退出所有设备吗？', '确认退出', {
          type: 'warning',
          confirmButtonText: '确认',
          cancelButtonText: '取消'
        })
        
  // 这里应该调用退出所有设备的API
  ElMessage.success('已退出所有设备')
  localStorage.removeItem('session_token')
  localStorage.removeItem('user')
  try { window.dispatchEvent(new Event('auth-changed')) } catch (e) {}
  router.push('/login')
      } catch (error) {
        if (error !== 'cancel') {
          console.error('退出所有设备失败:', error)
        }
      }
    }
    
    // 头像上传
    const beforeAvatarUpload = (file) => {
      const isImage = file.type.startsWith('image/')
      const isLt2M = file.size / 1024 / 1024 < 2
      
      if (!isImage) {
        ElMessage.error('只能上传图片文件!')
        return false
      }
      if (!isLt2M) {
        ElMessage.error('图片大小不能超过 2MB!')
        return false
      }
      return true
    }
    
    const uploadAvatar = async (options) => {
      try {
        const formData = new FormData()
        formData.append('avatar', options.file)
  formData.append('user_id', String(getCurrentUserId()))

        const result = await requestMethod.postForm('/user/avatar/upload', formData)
        if (result && result.code === 200) {
          ElMessage.success('头像上传成功')
          userInfo.value.avatar = result.data.avatar_url
          // 更新本地存储并通知全局（使 Navbar 等组件实时刷新）
          try { localStorage.setItem('user', JSON.stringify(Object.assign({}, JSON.parse(localStorage.getItem('user')||'{}'), { avatar: result.data.avatar_url }))) } catch (e) {}
          try { window.dispatchEvent(new Event('auth-changed')) } catch (e) {}
        } else {
          ElMessage.error(result?.msg || '上传失败')
        }
      } catch (error) {
        console.error('头像上传失败:', error)
        ElMessage.error('上传失败，请稍后重试')
      }
    }
    
    // 重置表单
    const resetForm = () => {
      Object.assign(userForm, {
        username: userInfo.value.username,
        student_id: userInfo.value.student_id,
        email: userInfo.value.email || '',
        phone: userInfo.value.phone || ''
      })
    }
    
    const resetPasswordForm = () => {
      Object.assign(passwordForm, {
        old_password: '',
        new_password: '',
        confirm_password: ''
      })
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleString('zh-CN')
    }
    
    // 反馈相关数据
    const feedbackFormRef = ref()
    const showFeedbackForm = ref(false)
    const feedbackForm = reactive({
      type: 'suggestion',
      content: ''
    })
    // 从后端拉取的历史反馈
    const feedbackList = ref([])

    // 分页参数（简单实现）
    const feedbackPage = ref(1)
    const feedbackPageSize = ref(20)

    const fetchFeedbacks = async (page = 1) => {
      try {
        const uid = getCurrentUserId()
        const res = await requestMethod.get('/feedback/history', { user_id: uid, page: page, page_size: feedbackPageSize.value })
        if (res && res.code === 200) {
          feedbackList.value = res.data.list || []
          feedbackPage.value = res.data.page || page
        }
      } catch (error) {
        console.error('获取历史反馈失败:', error)
        ElMessage.error('获取历史反馈失败')
      }
    }
    
    // 获取反馈类型标签样式（兼容后端 feedback_type 值）
    const getFeedbackTypeTag = (type) => {
      const tagMap = {
        accuracy: 'primary',
        music: 'success',
        function: 'warning',
        suggestion: 'primary',
        bug: 'danger',
        other: 'warning'
      }
      return tagMap[type] || 'info'
    }

    // 获取反馈类型文本（中文友好名）
    const getFeedbackTypeText = (type) => {
      const textMap = {
        accuracy: '检测准确性',
        music: '音乐推荐',
        function: '系统建议',
        suggestion: '功能建议',
        bug: '问题反馈',
        other: '其他'
      }
      return textMap[type] || (type || '未知类型')
    }
    
    // 提交反馈（调用后端）
    const handleSubmitFeedback = async () => {
      try {
        const uid = getCurrentUserId()
        const payload = {
          user_id: uid,
          feedback_type: feedbackForm.type,
          content: feedbackForm.content,
          score: 0
        }
        const res = await requestMethod.post('/feedback/submit', payload)
        if (res && res.code === 200) {
          ElMessage.success('反馈提交成功')
          showFeedbackForm.value = false
          feedbackForm.type = 'suggestion'
          feedbackForm.content = ''
          // 重新拉取第一页数据
          await fetchFeedbacks(1)
        } else {
          ElMessage.error(res?.msg || '提交失败')
        }
      } catch (error) {
        console.error('提交反馈失败:', error)
        ElMessage.error('提交反馈失败')
      }
    }
    
    // 组件挂载时获取数据
    onMounted(() => {
      fetchUserInfo()
      fetchSessions()
      fetchFeedbacks()
    })
    
    return {
      userFormRef,
      preferencesFormRef,
      passwordFormRef,
      feedbackFormRef,
      userInfo,
      editMode,
      updateLoading,
      passwordLoading,
      userForm,
      preferencesForm,
      passwordForm,
      sessions,
      currentSessionId,
      showFeedbackForm,
      feedbackForm,
      feedbackList,
      userRules,
      passwordRules,
      handleUpdateProfile,
      updatePreference,
      handleChangePassword,
      handleRevokeSession,
      handleLogoutAll,
      beforeAvatarUpload,
      uploadAvatar,
      resetForm,
      resetPasswordForm,
      formatDate,
      getFeedbackTypeTag,
      getFeedbackTypeText,
      handleSubmitFeedback
    }
  }
}
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

.user-center {
  position: relative;
  padding: 20px;
  background-color: var(--bg-secondary);
  min-height: 100vh;
  overflow-x: hidden;
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

.user-center-container {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.user-info-card,
.preferences-card,
.sessions-card,
.password-card,
.feedback-card {
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
  
  :deep(.el-card__header) {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(255, 255, 255, 0.8) 100%);
    border-bottom: 1px solid var(--border-color);
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    padding: var(--spacing-md) var(--spacing-lg);
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      h2 {
        margin: 0;
        color: var(--text-primary);
        font-size: 18px;
        font-weight: 600;
      }
    }
  }
  
  :deep(.el-card__body) {
    padding: var(--spacing-lg);
  }
}

.user-info-content {
  display: flex;
  gap: var(--spacing-xl);
  align-items: flex-start;
  padding: var(--spacing-md);
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(255, 255, 255, 0.5) 100%);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  
  .user-avatar {
    border: 4px solid rgba(59, 130, 246, 0.2);
    transition: transform 0.3s ease, border-color 0.3s ease;
    
    &:hover {
      transform: scale(1.05);
      border-color: var(--color-primary);
    }
  }
  
  .avatar-uploader {
    .upload-btn {
      display: flex;
      align-items: center;
      gap: 4px;
      transition: all 0.2s ease;
      
      &:hover {
        transform: translateY(-1px);
      }
    }
  }
}

.user-form {
  flex: 1;
  
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
    
    :deep(.el-input.is-disabled .el-input__wrapper) {
      background-color: rgba(248, 250, 252, 0.8);
    }
  }
}

.preferences-form {
  .el-form-item {
    margin-bottom: var(--spacing-lg);
    
    :deep(.el-form-item__label) {
      font-weight: 500;
      color: var(--text-primary);
    }
    
    :deep(.el-select__wrapper) {
      border-radius: var(--radius-md);
      transition: all 0.3s ease;
      
      &:focus-within {
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        border-color: var(--color-primary);
      }
    }
    
    :deep(.el-switch) {
      --el-switch-on-color: var(--color-primary);
    }
  }
}

.password-form {
  max-width: 500px;
  
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
  }
}

/* 会话管理表格样式优化 */
.sessions-card :deep(.el-table),
.feedback-card :deep(.el-table) {
  width: 100%;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.sessions-card :deep(.el-table__header-wrapper),
.feedback-card :deep(.el-table__header-wrapper) {
  background-color: rgba(59, 130, 246, 0.05);
}

.sessions-card :deep(.el-table th),
.feedback-card :deep(.el-table th) {
  font-weight: 600;
  color: var(--text-primary);
  background-color: transparent;
  border-bottom: 1px solid var(--border-color);
  padding: 12px 16px;
}

.sessions-card :deep(.el-table td),
.feedback-card :deep(.el-table td) {
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.2s ease;
  padding: 12px 16px;
}

.sessions-card :deep(.el-table__row:hover td),
.feedback-card :deep(.el-table__row:hover td) {
  background-color: rgba(59, 130, 246, 0.05);
}

.sessions-card :deep(.el-tag),
.feedback-card :deep(.el-tag) {
  border-radius: 16px;
  font-size: 12px;
  padding: 2px 8px;
}

.sessions-card :deep(.el-button--danger) {
  transition: all 0.2s ease;
}

.sessions-card :deep(.el-button--danger:hover) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

/* 反馈表单样式 */
.feedback-form-container {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(255, 255, 255, 0.8) 100%);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  border: 1px solid var(--border-color);
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
  }
}

.feedback-content {
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

/* 反馈卡片样式优化 */
.feedback-card {
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
  
  :deep(.el-card__header) {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(255, 255, 255, 0.8) 100%);
    border-bottom: 1px solid var(--border-color);
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    padding: var(--spacing-md) var(--spacing-lg);
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      h2 {
        margin: 0;
        color: var(--text-primary);
        font-size: 18px;
        font-weight: 600;
      }
    }
  }
  
  :deep(.el-card__body) {
    padding: var(--spacing-lg);
  }
}

/* 按钮样式优化 */
:deep(.el-button) {
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
  font-weight: 500;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
  }
  
  &:active {
    transform: translateY(0);
  }
}

:deep(.el-button--primary) {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  
  &:hover {
    background-color: var(--color-primary-dark);
    border-color: var(--color-primary-dark);
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
  
  .user-center-container {
    padding: var(--spacing-page);
  }
  
  .user-info-card {
    @include card(16px, 12px);
    margin-bottom: var(--spacing-md);
    
    .avatar-section {
      width: 100%;
      margin-bottom: var(--spacing-md);
      
      .avatar-container {
        width: 80px;
        height: 80px;
      }
      
      .user-details {
        text-align: center;
      }
    }
    
    .user-details {
      .user-name {
        @include responsive-font(20px, null, 18px);
      }
      
      .user-id {
        @include responsive-font(14px, null, 13px);
      }
    }
    
    .profile-form {
      :deep(.el-form-item__label) {
        font-size: 13px;
      }
      
      :deep(.el-input__wrapper) {
        padding: 6px 12px;
      }
    }
  }
  
  .sessions-card {
    margin-top: var(--spacing-md);
    @include card(16px, 12px);
    
    .card-header {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--spacing-sm);
    }
    
    .sessions-table :deep(.el-table__header th) {
      padding: 10px 6px;
      font-size: 12px;
      
      // 隐藏某些不重要的表头
      &:nth-child(3), // IP地址
      &:nth-child(4) { // 设备信息
        display: none;
      }
    }
    
    .sessions-table :deep(.el-table__body td) {
      padding: 10px 6px;
      font-size: 12px;
      
      // 隐藏对应的表格内容
      &:nth-child(3),
      &:nth-child(4) {
        display: none;
      }
    }
    
    // 自定义移动端操作按钮
    .action-buttons {
      .el-button {
        padding: 6px 12px;
        font-size: 12px;
        min-width: auto;
      }
    }
  }
}

// 平板设备适配
@include respond-to(sm) {
  .user-info-card {
    @include card(18px);
    
    .avatar-section {
      width: 100%;
      margin-bottom: var(--spacing-md);
    }
  }
  
  .sessions-table :deep(.el-table__header th) {
    padding: 14px 10px;
    font-size: 13px;
  }
  
  .sessions-table :deep(.el-table__body td) {
    padding: 14px 10px;
    font-size: 13px;
  }
}

// 大屏设备优化
@include large-desktop-layout {
  .user-center-container {
    @include container(false);
    max-width: 1400px;
  }
  
  .content-wrapper {
    display: grid;
    grid-template-columns: 350px 1fr;
    gap: 32px;
  }
  
  .user-info-card {
    @include card(24px);
  }
}

// 超大屏设备优化
@include extra-large-desktop-layout {
  .user-center-container {
    max-width: 1600px;
  }
}

// 高对比度模式支持
@include high-contrast {
  .user-info-card,
  .sessions-card {
    border: 2px solid #000;
    box-shadow: none;
  }
  
  :deep(.el-button) {
    border-width: 2px;
  }
}

// 减少动画模式支持
@media (prefers-reduced-motion: reduce) {
  * {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
  }
}
</style>

import { defineStore } from 'pinia'
import { requestMethod } from '@/utils/request'

export const useAdminStore = defineStore('admin', {
  state: () => ({
    musicList: [],
    userList: [],
    feedbackList: [],
    systemConfig: {},
    loading: false
  }),

  actions: {
    // 音乐管理
    async getMusicList(params = {}) {
      try {
        this.loading = true
        const result = await requestMethod.get('/admin/music', params)
        if (result && result.code === 200) {
          this.musicList = result.data.items || []
          return { items: this.musicList, pagination: result.data.pagination }
        }
        return { items: [], pagination: { total: 0 } }
      } catch (error) {
        console.error('获取音乐列表失败:', error)
        return { items: [], pagination: { total: 0 } }
      } finally {
        this.loading = false
      }
    },

    async createMusic(data) {
      try {
        const result = await requestMethod.post('/admin/music', data)
        if (result && result.code === 200) {
          return result.data
        }
        throw new Error(result?.msg || '创建失败')
      } catch (error) {
        console.error('创建音乐失败:', error)
        throw error
      }
    },

    async updateMusic(musicId, data) {
      try {
        const result = await requestMethod.put(`/admin/music/${musicId}`, data)
        if (result && result.code === 200) {
          return result.data
        }
        throw new Error(result?.msg || '更新失败')
      } catch (error) {
        console.error('更新音乐失败:', error)
        throw error
      }
    },

    async deleteMusic(musicId) {
      try {
        const result = await requestMethod.delete(`/admin/music/${musicId}`)
        if (result && result.code === 200) {
          return true
        }
        throw new Error(result?.msg || '删除失败')
      } catch (error) {
        console.error('删除音乐失败:', error)
        throw error
      }
    },

    async batchDeleteMusic(musicIds) {
      try {
        const result = await requestMethod.post('/admin/music/batch-delete', { ids: musicIds })
        if (result && result.code === 200) {
          return true
        }
        throw new Error(result?.msg || '批量删除失败')
      } catch (error) {
        console.error('批量删除音乐失败:', error)
        throw error
      }
    },

    // 用户管理
    async getUserList(params = {}) {
      try {
        this.loading = true
        const result = await requestMethod.get('/admin/users', params)
        if (result && result.code === 200) {
          this.userList = result.data.items || []
          return { items: this.userList, pagination: result.data.pagination }
        }
        return { items: [], pagination: { total: 0 } }
      } catch (error) {
        console.error('获取用户列表失败:', error)
        return { items: [], pagination: { total: 0 } }
      } finally {
        this.loading = false
      }
    },

    async updateUser(userId, data) {
      try {
        const result = await requestMethod.put(`/admin/users/${userId}`, data)
        if (result && result.code === 200) {
          return result.data
        }
        throw new Error(result?.msg || '更新失败')
      } catch (error) {
        console.error('更新用户失败:', error)
        throw error
      }
    },

    // 反馈管理
    async getFeedbackList(params = {}) {
      try {
        this.loading = true
        const result = await requestMethod.get('/admin/feedback', params)
        if (result && result.code === 200) {
          this.feedbackList = result.data.items || []
          return { items: this.feedbackList, pagination: result.data.pagination }
        }
        return { items: [], pagination: { total: 0 } }
      } catch (error) {
        console.error('获取反馈列表失败:', error)
        return { items: [], pagination: { total: 0 } }
      } finally {
        this.loading = false
      }
    },

    async updateFeedback(feedbackId, data) {
      try {
        const result = await requestMethod.put(`/admin/feedback/${feedbackId}`, data)
        if (result && result.code === 200) {
          return result.data
        }
        throw new Error(result?.msg || '更新失败')
      } catch (error) {
        console.error('更新反馈失败:', error)
        throw error
      }
    },

    // 系统配置
    async getSystemConfig() {
      try {
        this.loading = true
        const result = await requestMethod.get('/admin/config')
        if (result && result.code === 200) {
          this.systemConfig = result.data
          return this.systemConfig
        }
        return {}
      } catch (error) {
        console.error('获取系统配置失败:', error)
        return {}
      } finally {
        this.loading = false
      }
    },

    async updateSystemConfig(data) {
      try {
        const result = await requestMethod.put('/admin/config', data)
        if (result && result.code === 200) {
          this.systemConfig = result.data
          return this.systemConfig
        }
        throw new Error(result?.msg || '更新失败')
      } catch (error) {
        console.error('更新系统配置失败:', error)
        throw error
      }
    },

    // 获取仪表盘数据
    async getDashboardData() {
      try {
        this.loading = true
        const result = await requestMethod.get('/admin/dashboard')
        if (result && result.code === 200) {
          return result.data
        }
        return {}
      } catch (error) {
        console.error('获取仪表盘数据失败:', error)
        return {}
      } finally {
        this.loading = false
      }
    }
  }
})

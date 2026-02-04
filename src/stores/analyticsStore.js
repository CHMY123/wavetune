import { defineStore } from 'pinia'
import { requestMethod } from '@/utils/request'

export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    userStats: {},
    musicStats: {},
    fatigueStats: {},
    systemStats: {},
    dashboardOverview: {},
    loading: false
  }),

  actions: {
    // 获取仪表盘概览数据
    async getDashboardOverview(params = {}) {
      try {
        this.loading = true
        const result = await requestMethod.get('/analytics/dashboard', params)
        if (result && result.code === 200) {
          this.dashboardOverview = result.data
          return this.dashboardOverview
        }
        return {}
      } catch (error) {
        console.error('获取仪表盘概览失败:', error)
        return {}
      } finally {
        this.loading = false
      }
    },

    // 获取仪表盘数据（兼容前端调用）
    async getDashboardData(params = {}) {
      try {
        this.loading = true
        console.log('开始获取仪表盘数据，参数:', params)
        const result = await requestMethod.get('/analytics/dashboard', params)
        console.log('获取仪表盘数据成功，结果:', result)
        if (result && result.code === 200) {
          return result.data
        }
        console.log('获取仪表盘数据失败，结果:', result)
        return {}
      } catch (error) {
        console.error('获取仪表盘数据异常:', error)
        return {}
      } finally {
        this.loading = false
      }
    },

    // 用户数据分析
    async getUserStats(params = {}) {
      try {
        this.loading = true
        const result = await requestMethod.get('/analytics/users', params)
        if (result && result.code === 200) {
          this.userStats = result.data
          return this.userStats
        }
        return {}
      } catch (error) {
        console.error('获取用户数据失败:', error)
        return {}
      } finally {
        this.loading = false
      }
    },

    // 音乐数据分析
    async getMusicStats(params = {}) {
      try {
        this.loading = true
        const result = await requestMethod.get('/analytics/music', params)
        if (result && result.code === 200) {
          this.musicStats = result.data
          return this.musicStats
        }
        return {}
      } catch (error) {
        console.error('获取音乐数据失败:', error)
        return {}
      } finally {
        this.loading = false
      }
    },

    // 疲劳检测数据分析
    async getFatigueStats(params = {}) {
      try {
        this.loading = true
        const result = await requestMethod.get('/analytics/fatigue', params)
        if (result && result.code === 200) {
          this.fatigueStats = result.data
          return this.fatigueStats
        }
        return {}
      } catch (error) {
        console.error('获取疲劳数据失败:', error)
        return {}
      } finally {
        this.loading = false
      }
    },

    // 系统操作数据分析
    async getSystemStats(params = {}) {
      try {
        this.loading = true
        const result = await requestMethod.get('/analytics/system', params)
        if (result && result.code === 200) {
          this.systemStats = result.data
          return this.systemStats
        }
        return {}
      } catch (error) {
        console.error('获取系统数据失败:', error)
        return {}
      } finally {
        this.loading = false
      }
    },

    // 通用数据获取方法
    async getAnalyticsData(endpoint, params = {}) {
      try {
        this.loading = true
        const result = await requestMethod.get(`/analytics${endpoint}`, params)
        if (result && result.code === 200) {
          return result.data
        }
        return {}
      } catch (error) {
        console.error(`获取分析数据失败 (${endpoint}):`, error)
        return {}
      } finally {
        this.loading = false
      }
    }
  }
})

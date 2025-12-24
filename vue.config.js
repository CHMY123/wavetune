const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    client: {
      overlay: {
        warnings: false,
        errors: false, // 关闭错误覆盖层
        runtimeErrors: (error) => {
          // 忽略 ResizeObserver 错误
          if (error.message && error.message.includes('ResizeObserver loop completed with undelivered notifications')) {
            return false
          }
          return true
        }
      }
    },
    // 本地开发时将 API 和静态文件请求转发到后端 FastAPI 服务
    proxy: {
      // API 接口代理（已存在）
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        pathRewrite: { '^/api': '/api' }
      },
      // 新增：静态文件（头像等）代理
      '/static': {
        target: 'http://localhost:8000', // 转发到后端服务器
        changeOrigin: true,
        secure: false
        // 不需要 pathRewrite，因为前端请求 /static/... 和后端路径一致
      }
    }
  },
  configureWebpack: {
    resolve: {
      alias: {
        // 别名配置（保持不变）
      }
    }
  }
})
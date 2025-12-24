const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack') // 引入 webpack 核心模块

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    client: {
      overlay: {
        warnings: false,
        errors: false,
        runtimeErrors: (error) => {
          if (error.message && error.message.includes('ResizeObserver loop completed with undelivered notifications')) {
            return false
          }
          return true
        }
      }
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        pathRewrite: { '^/api': '/api' }
      },
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  configureWebpack: {
    resolve: {
      alias: {} // 保持你的别名配置
    },
    // 关键：注入 process 到 window，彻底解决未定义问题
    plugins: [
      new webpack.DefinePlugin({
        'window.process': JSON.stringify({
          env: {
            // 注入你的环境变量（和 .env 文件一致）
            VUE_APP_API_BASE_URL: process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000/api',
            NODE_ENV: process.env.NODE_ENV || 'development'
          }
        })
      })
    ]
  }
})
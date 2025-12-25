const { defineConfig } = require('@vue/cli-service')
const path = require('path')

module.exports = defineConfig({
  publicPath: '/',
  outputDir: 'dist',
  
  devServer: {
    port: 8080,
    
    // 仅保留默认的 public 目录作为静态资源根目录（无需额外配置）
    // 删掉多余的 static 数组配置，使用 Vue CLI 默认的 public 目录映射
    static: {
      directory: path.resolve(__dirname, 'public'),
      publicPath: '/',
      watch: true
    },
    
    proxy: {
      // 仅保留 API 代理（删除 /static 代理规则，避免拦截本地静态资源）
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        pathRewrite: { '^/api': '/api' }
      }
    },
    
    historyApiFallback: true,
    
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
    }
  },
  
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    }
  }
})
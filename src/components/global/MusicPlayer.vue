<template>
  <div class="music-player" v-if="playerStore.showPlayer && playerStore.currentTrack" :class="{ 'dark-mode': isDarkMode }">
    <!-- 背景渐变层 -->
    <div class="bg-overlay" :style="{ backgroundImage: `linear-gradient(to top, ${getAccentColor}20, transparent)` }"></div>
    
    <!-- 顶部装饰条 -->
    <div class="player-accent" :style="{ background: getAccentGradient }"></div>
    
    <div class="player-main">
      <!-- 唱片封面区域 -->
      <div class="record-container">
        <!-- 唱片旋转容器 -->
        <div class="record-wrapper" :class="{ 'playing': isPlaying }">
          <!-- 唱片主体 -->
          <div class="record">
            <img 
              :src="currentTrack.cover" 
              alt="专辑封面" 
              class="record-cover" 
              loading="lazy"
            />
            <!-- 唱片纹理 -->
            <div class="record-texture"></div>
            <!-- 唱片中心 -->
            <div class="record-center">
              <div class="spindle"></div>
            </div>
          </div>
        </div>
        
        <!-- 唱臂装饰 -->
        <div class="tonearm" :class="{ 'playing': isPlaying }"></div>
      </div>
      
      <!-- 信息与控制区域 -->
      <div class="meta-controls">
        <div class="meta">
          <h2 class="title" :title="currentTrack.title">
            <span class="text" :data-text="currentTrack.title">{{ currentTrack.title }}</span>
          </h2>
          <p class="artist" :title="currentTrack.artist">{{ currentTrack.artist }}</p>
          <p class="reason" v-if="currentTrack.reason" :title="currentTrack.reason">
            <span class="reason-icon">♪</span>
            {{ currentTrack.reason }}
          </p>
        </div>
        
        <!-- 进度条区域 -->
        <div class="progress-container">
          <div class="progress-bar-wrapper">
            <div 
              class="progress-indicator" 
              :style="{ width: `${(duration > 0 ? (currentTime / duration) * 100 : 0)}%` }"
            ></div>
            <input 
              ref="progressSlider"
              type="range" 
              min="0" 
              :max="duration || 100" 
              step="0.1" 
              :value="currentTime"
              @input="handleProgressInput"
              @change="handleProgressChange"
              class="progress-slider"
              aria-label="播放进度"
            />
          </div>
          <div class="time-display">
            <span class="current-time">{{ formatTime(currentTime) }}</span>
            <span class="total-time">{{ formatTime(duration) }}</span>
          </div>
        </div>
        
        <!-- 控制按钮区域 -->
        <div class="controls">
          <div class="control-group">
            <!-- 上一首按钮 -->
            <button 
              class="control-btn prev-btn" 
              @click="playPrevious" 
              :aria-label="'上一首'"
              :disabled="!hasPrevTrack"
            >
              <el-icon class="control-icon"><ArrowLeft /></el-icon>
            </button>
            
            <!-- 播放/暂停按钮 -->
            <button 
              class="play-btn" 
              @click="togglePlay" 
              :aria-label="isPlaying ? '暂停' : '播放'"
              :style="{ background: getAccentGradient }"
            >
              <el-icon v-if="!isPlaying" class="play-icon"><VideoPlay /></el-icon>
              <el-icon v-else class="pause-icon"><VideoPause /></el-icon>
            </button>
            
            <!-- 下一首按钮 -->
            <button 
              class="control-btn next-btn" 
              @click="playNext" 
              :aria-label="'下一首'"
              :disabled="!hasNextTrack"
            >
              <el-icon class="control-icon"><ArrowRight /></el-icon>
            </button>
            
            <!-- 循环模式按钮 -->
            <button 
              class="control-btn repeat-btn" 
              @click="toggleRepeatMode" 
              :aria-label="getRepeatModeLabel"
              :class="{ 'active': repeatMode !== 'list' }"
            >
              <el-icon v-if="repeatMode === 'list'" class="repeat-icon"><Refresh /></el-icon>
              <el-icon v-else-if="repeatMode === 'single'" class="repeat-icon"><RefreshLeft /></el-icon>
              <el-icon v-else class="repeat-icon"><Rank /></el-icon>
            </button>
          </div>
          
          <!-- 音量控制 -->
          <div class="volume-controls">
            <button 
              class="mute-btn" 
              @click="toggleMute" 
              :aria-pressed="isMuted"
              :title="isMuted ? '取消静音' : '静音'"
            >
              <span v-if="isMuted">🔇</span>
              <span v-else-if="volume >= 0.66">🔊</span>
              <span v-else-if="volume >= 0.33">🔉</span>
              <span v-else>🔈</span>
            </button>
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.01" 
              v-model.number="volume" 
              @input="setVolume" 
              class="volume-slider"
              aria-label="音量调节"
            />
          </div>
        </div>
      </div>
      
      <!-- 关闭按钮 -->
      <button class="close-btn" @click="handleClose" aria-label="关闭播放器">
        <el-icon><Close /></el-icon>
      </button>
    </div>
    
    <!-- 音频元素 -->
  <audio 
    ref="audioEl" 
    :src="currentTrack?.src || ''" 
    @timeupdate="onTimeUpdate" 
    @loadedmetadata="onLoaded" 
    @ended="onEnded"
    @error="handleAudioError"
    @pause="handleUnexpectedPause"
    class="audio-element"
    preload="auto"
  >
    您的浏览器不支持HTML5音频播放
  </audio>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { VideoPlay, VideoPause, Close, ArrowLeft, ArrowRight, Refresh, RefreshLeft, Rank } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { usePlayerStore } from '../../stores/playerStore'

// 使用 Pinia store
const playerStore = usePlayerStore()

// 音频元素引用
const audioEl = ref(null)
const progressSlider = ref(null)
const isSeeking = ref(false)
const isClosing = ref(false)
const viewportWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1200)
const isManualPause = ref(false)

// 直接使用playerStore状态，不再需要computed包装
const currentTrack = computed(() => playerStore.currentTrack)
const isPlaying = computed(() => playerStore.isPlaying)
const duration = computed(() => playerStore.duration)
const currentTime = computed(() => playerStore.currentTime)
const volume = computed({
  get: () => playerStore.volume,
  set: (value) => playerStore.setVolume(value)
})
const isMuted = computed({
  get: () => playerStore.isMuted,
  set: (value) => playerStore.setIsMuted(value)
})
const repeatMode = computed(() => playerStore.repeatMode)
const hasNextTrack = computed(() => playerStore.hasNextTrack)
const hasPrevTrack = computed(() => playerStore.hasPrevTrack)

// 检测系统暗色模式
const isDarkMode = computed(() => {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
})

// 获取主题色
const getAccentColor = computed(() => {
  return isDarkMode.value ? '#34d399' : '#10b981'
})

const getAccentGradient = computed(() => {
  const color = getAccentColor.value
  return `linear-gradient(135deg, ${color}, ${color.replace('1)', '9)').replace('399', '81')})`
})

// 获取循环模式标签
const getRepeatModeLabel = computed(() => {
  switch (repeatMode.value) {
    case 'list': return '列表循环'
    case 'single': return '单曲循环'
    case 'random': return '随机播放'
    default: return '循环模式'
  }
})

// 播放函数
const play = async () => {
  if (!audioEl.value || !currentTrack.value) {
    console.error('播放失败: 缺少音频元素或曲目信息')
    return
  }
  
  try {
    // 确保src有效
    if (!audioEl.value.src || audioEl.value.src === '') {
      console.error('播放失败: 音频URL无效')
      ElMessage.error('音频URL无效')
      return
    }
    
    // 先重置播放状态
    playerStore.setIsPlaying(false)
    isManualPause.value = false
    
    // 确保音频已加载
    if (audioEl.value.readyState < 2) {
      try {
        await audioEl.value.load()
      } catch (loadError) {
        console.error('音频加载失败:', loadError)
        ElMessage.error('音频加载失败')
        return
      }
    }
    
    // 尝试播放
    const playPromise = audioEl.value.play()
    
    // 处理异步播放请求
    if (playPromise && typeof playPromise.then === 'function') {
      await playPromise
      playerStore.setIsPlaying(true)
      console.debug('音频播放成功', { title: currentTrack.value.title, url: audioEl.value.src })
    } else {
      // 旧浏览器兼容性处理
      playerStore.setIsPlaying(true)
    }
  } catch (e) {
    console.error('播放时发生错误:', e)
    playerStore.setIsPlaying(false)
    
    // 检测是否是用户交互问题导致的播放错误
    if (e.name === 'NotAllowedError' || e.message && e.message.includes('user gesture')) {
      ElMessage.warning('请点击播放按钮以开始播放音频')
    } else {
      ElMessage.error('播放失败，请重试')
    }
  }
}

const pause = () => {
  if (!audioEl.value) return
  try {
    console.debug('[MusicPlayer] pause() called')
    audioEl.value.pause()
    playerStore.setIsPlaying(false)
    isManualPause.value = true
    console.info('[MusicPlayer] paused, isPlaying=', playerStore.isPlaying)
  } catch (e) {
    console.warn('暂停音频时发生警告:', e)
  }
}

const togglePlay = () => {
  isPlaying.value ? pause() : play()
}

// 播放下一首
const playNext = () => {
  const nextTrack = playerStore.playNext()
  if (nextTrack) {
    // 延迟加载新歌曲
    setTimeout(() => {
      play().catch(err => {
        console.warn('播放下一首失败:', err)
      })
    }, 100)
  }
}

// 播放上一首
const playPrevious = () => {
  const prevTrack = playerStore.playPrevious()
  if (prevTrack) {
    // 延迟加载新歌曲
    setTimeout(() => {
      play().catch(err => {
        console.warn('播放上一首失败:', err)
      })
    }, 100)
  }
}

// 切换循环模式
const toggleRepeatMode = () => {
  playerStore.toggleRepeatMode()
}

// 处理意外暂停
const handleUnexpectedPause = () => {
  // 如果不是手动暂停、不是正在关闭、不是正在拖动进度条，且应该处于播放状态
  if (!isManualPause.value && !isClosing.value && !isSeeking.value && isPlaying.value) {
    console.debug('[MusicPlayer] 检测到意外暂停，尝试恢复播放')
    // 延迟恢复，避免浏览器策略拦截
    setTimeout(() => {
      play().catch(err => {
        console.warn('恢复播放失败:', err)
      })
    }, 100)
  }
}

// 时间更新处理
const onTimeUpdate = () => {
  if (!audioEl.value || isSeeking.value) return
  playerStore.setCurrentTime(audioEl.value.currentTime)
}

// 音频加载完成
const onLoaded = () => {
  if (!audioEl.value) return
  
  try {
    // 优先使用 audio 元数据
    const metaDur = Number(audioEl.value.duration)
    console.debug('[MusicPlayer] onLoaded: audio.duration=', metaDur)
    if (!isNaN(metaDur) && metaDur > 0) {
      playerStore.setDuration(metaDur)
    }
    audioEl.value.volume = volume.value
    audioEl.value.muted = isMuted.value
    
    // 自动播放
    if (isPlaying.value) {
      setTimeout(() => play(), 300)
    }
  } catch (e) {
    console.warn('音频加载完成处理时发生警告:', e)
  }
}

// 音频错误处理
const handleAudioError = (e) => {
  // 在组件正在关闭或资源已被清理时，忽略错误
  if (isClosing.value) return
  if (!audioEl.value || audioEl.value.src === '') return

  console.error('音频错误:', e, '音频URL:', audioEl.value.src)
  playerStore.setIsPlaying(false)
  
  // 提供用户友好的错误提示
  let errorMessage = '音频播放失败'
  if (e && e.type === 'error') {
    // 根据不同的错误码提供更具体的错误信息
    switch (e.target.error.code) {
      case e.target.error.MEDIA_ERR_ABORTED:
        errorMessage = '播放已被取消'
        break
      case e.target.error.MEDIA_ERR_NETWORK:
        errorMessage = '网络错误导致播放失败'
        break
      case e.target.error.MEDIA_ERR_DECODE:
        errorMessage = '音频格式不支持或已损坏'
        break
      case e.target.error.MEDIA_ERR_SRC_NOT_SUPPORTED:
        errorMessage = '无法加载音频文件'
        break
      default:
        errorMessage = '音频播放失败，请尝试其他音乐'
    }
  }
  ElMessage.error(errorMessage)
}

// 进度条输入处理
const handleProgressInput = (event) => {
  if (!audioEl.value) return
  
  const newTime = parseFloat(event.target.value)
  isSeeking.value = true
  playerStore.setCurrentTime(newTime)
  console.debug('[MusicPlayer] handleProgressInput newTime=', newTime, 'isSeeking=', isSeeking.value)
}

const handleProgressChange = async (event) => {
  if (!audioEl.value) return
  
  const newTime = parseFloat(event.target.value)
  const validTime = Math.max(0, Math.min(newTime, duration.value))
  playerStore.setCurrentTime(validTime)
  console.debug('[MusicPlayer] handleProgressChange -> applying time=', validTime)
  try {
    audioEl.value.currentTime = validTime
  } catch (e) {
    console.warn('设置音频时间时发生警告:', e)
  }
  
  await nextTick()
  isSeeking.value = false
  
  if (isPlaying.value) {
    try {
      await audioEl.value.play()
      console.debug('[MusicPlayer] resumed play after change')
    } catch (e) {
      console.error('恢复播放失败:', e)
      playerStore.setIsPlaying(false)
    }
  }
}

// 音量控制
const setVolume = () => {
  if (!audioEl.value) return
  
  try {
    audioEl.value.volume = volume.value
    if (volume.value > 0) playerStore.setIsMuted(false)
    audioEl.value.muted = isMuted.value
  } catch (e) {
    console.warn('设置音量时发生警告:', e)
  }
}

const toggleMute = () => {
  playerStore.setIsMuted(!isMuted.value)
  if (audioEl.value) {
    try {
      audioEl.value.muted = !isMuted.value
    } catch (e) {
      console.warn('切换静音时发生警告:', e)
    }
  }
}

// 播放结束处理
const onEnded = () => {
  // 根据循环模式处理
  if (repeatMode.value === 'single') {
    // 单曲循环，重新播放
    audioEl.value.currentTime = 0
    play().catch(err => {
      console.warn('单曲循环播放失败:', err)
    })
  } else {
    // 其他模式，播放下一首
    playNext()
  }
}

// 页面可见性变化监听
const handleVisibilityChange = () => {
  // 页面从不可见变为可见
  if (!document.hidden && isPlaying.value && !isManualPause.value && !isClosing.value) {
    console.debug('[MusicPlayer] 页面切回，恢复播放')
    play().catch(err => {
      console.warn('页面切回恢复播放失败:', err)
    })
  }
}

// 监听音量变化
watch([volume, isMuted], () => {
  if (audioEl.value) {
    try {
      audioEl.value.volume = volume.value
      audioEl.value.muted = isMuted.value
    } catch (e) {
      console.warn('监听音量变化时发生警告:', e)
    }
  }
})

// 监听当前歌曲变化
watch(currentTrack, (newTrack) => {
  if (newTrack) {
    // 重置进度
    playerStore.setCurrentTime(0)
    playerStore.setDuration(0)
    
    // 延迟设置音频源
    setTimeout(() => {
      if (audioEl.value) {
        try {
          audioEl.value.volume = volume.value
          audioEl.value.muted = isMuted.value
        } catch (e) {
          console.warn('切换轨道时设置音量和静音状态发生警告:', e)
        }
      }
    }, 100)
  }
}, { deep: true })

// 安全清理音频资源
const safelyCleanupAudio = () => {
  if (!audioEl.value) return
  
  try {
    // 先暂停播放
    audioEl.value.pause()
    // 移除事件监听器
    audioEl.value.onerror = null
    audioEl.value.ontimeupdate = null
    audioEl.value.onloadedmetadata = null
    audioEl.value.onended = null
    audioEl.value.onpause = null
    // 清空音频源
    audioEl.value.src = ''
    // 加载空源以释放资源
    audioEl.value.load()
  } catch (e) {
    console.warn('清理音频资源时发生警告:', e)
  }
}

// 关闭播放器
const handleClose = () => {
  // 标记正在关闭
  isClosing.value = true
  // 先停止播放
  pause()
  // 安全清理音频资源
  safelyCleanupAudio()
  // 关闭播放器
  playerStore.closePlayer()
  // 延迟清除标志
  setTimeout(() => {
    isClosing.value = false
  }, 50)
}

// 窗口大小处理
const handleResize = () => {
  try { viewportWidth.value = window.innerWidth } catch(e) {}
}

// 时间格式化工具函数
const formatTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '00:00'
  
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

// 组件挂载
onMounted(() => {
  // 监听窗口大小变化
  try { window.addEventListener('resize', handleResize) } catch(e) {}
  // 监听页面可见性变化
  try { document.addEventListener('visibilitychange', handleVisibilityChange) } catch(e) {}
  // 初始化时设置音频元素的 pause 事件监听
  if (audioEl.value) {
    audioEl.value.onpause = handleUnexpectedPause
  }
})

// 组件卸载时清理
onBeforeUnmount(() => {
  safelyCleanupAudio()
  // 移除窗口大小监听
  try { window.removeEventListener('resize', handleResize) } catch(e) {}
  // 移除页面可见性监听
  try { document.removeEventListener('visibilitychange', handleVisibilityChange) } catch(e) {}
})
</script>

<style scoped>
/* 基础变量定义 */
:root {
  --player-width: 620px;
  --player-radius: 20px;
  --transition-normal: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-fast: all 0.15s ease;
  --shadow-light: 0 8px 30px rgba(0, 0, 0, 0.1);
  --shadow-dark: 0 8px 30px rgba(0, 0, 0, 0.3);
}

/* 播放器容器 */
.music-player {
  position: fixed;
  right: 32px;
  bottom: 32px;
  width: var(--player-width);
  background: var(--bg-light, #ffffff);
  border-radius: var(--player-radius);
  box-shadow: var(--shadow-light);
  overflow: hidden;
  z-index: 2000;
  transition: var(--transition-normal);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

/* 暗色模式适配 */
.music-player.dark-mode {
  --bg-light: #1e293b;
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  box-shadow: var(--shadow-dark);
}

/* 背景渐变层 */
.bg-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100%;
  z-index: -1;
  pointer-events: none;
}

/* 顶部装饰条 */
.player-accent {
  height: 4px;
  width: 100%;
  background: linear-gradient(90deg, #10b981, #34d399);
}

/* 主容器布局 */
.player-main {
  display: flex;
  align-items: center;
  padding: 24px;
  gap: 28px;
  position: relative;
  min-height: 188px;
}

/* 唱片容器 */
.record-container {
  position: relative;
  width: 140px;
  height: 140px;
  flex-shrink: 0;
}

/* 唱片旋转包装器 */
.record-wrapper {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  position: relative;
  transition: var(--transition-normal);
  animation: rotate 8s linear infinite;
  animation-play-state: paused;
}

.record-wrapper.playing {
  animation-play-state: running;
}

/* 旋转动画 */
@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 唱片主体 */
.record {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
  box-shadow: 
    0 4px 20px rgba(0, 0, 0, 0.15),
    inset 0 0 0 2px rgba(0, 0, 0, 0.05);
}

/* 唱片封面 */
.record-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  transition: var(--transition-normal);
}

.record:hover .record-cover {
  transform: scale(1.02);
}

/* 唱片纹理 */
.record-texture {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: 
    radial-gradient(circle at center, transparent 28%, rgba(0,0,0,0.06) 28.5%, transparent 30%),
    repeating-radial-gradient(
      circle at center,
      transparent 0,
      transparent 2px,
      rgba(0,0,0,0.03) 2px,
      rgba(0,0,0,0.03) 3px
    );
  pointer-events: none;
}

/* 唱片中心 */
.record-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 32%;
  height: 32%;
  border-radius: 50%;
  background: #f3f4f6;
  z-index: 2;
  box-shadow: 
    inset 0 0 0 2px rgba(0,0,0,0.08),
    0 2px 4px rgba(0,0,0,0.1);
}

.dark-mode .record-center {
  background: #273449;
}

/* 唱针轴 */
.spindle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 25%;
  height: 25%;
  border-radius: 50%;
  background: linear-gradient(135deg, #10b981, #34d399);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

/* 唱臂装饰 */
.tonearm {
  position: absolute;
  top: -10px;
  right: 10px;
  width: 80px;
  height: 20px;
  background: linear-gradient(to right, #d1d5db, #9ca3af);
  border-radius: 10px 0 0 10px;
  transform-origin: right center;
  transform: rotate(15deg);
  transition: var(--transition-normal);
  z-index: 1;
}

.tonearm.playing {
  transform: rotate(5deg);
}

.tonearm::after {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #6b7280;
}

/* 信息与控制区域 */
.meta-controls {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}

/* 元数据区域 */
.meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.title {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary, #1e293b);
  margin: 0;
  line-height: 1.2;
  position: relative;
  overflow: hidden;
}

.title .text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
  width: 100%;
}

.artist {
  font-size: 16px;
  color: var(--text-secondary, #64748b);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.reason {
  font-size: 14px;
  color: var(--text-secondary, #94a3b8);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.reason-icon {
  font-size: 12px;
  opacity: 0.7;
  flex-shrink: 0;
}

/* 进度条容器 */
.progress-container {
  width: 100%;
}

.progress-bar-wrapper {
  position: relative;
  height: 6px;
  background: rgba(226, 232, 240, 0.3);
  border-radius: 3px;
  overflow: hidden;
}

.progress-indicator {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: linear-gradient(90deg, #10b981, #34d399);
  border-radius: 3px;
  transition: width 0.1s linear;
}

.progress-slider {
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  -webkit-appearance: none;
  appearance: none;
  background: transparent;
}

.progress-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #10b981;
  cursor: pointer;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
  transition: var(--transition-fast);
}

.progress-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
  box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.3);
}

.time-display {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--text-secondary, #94a3b8);
  margin-top: 8px;
}

/* 控制按钮区域 */
.controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 控制按钮组 */
.control-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 控制按钮 */
.control-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  color: var(--text-secondary, #64748b);
  border: 1px solid rgba(100, 116, 139, 0.2);
  background: rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition-fast);
}

.control-btn:hover:not(:disabled) {
  transform: scale(1.05);
  color: var(--text-primary, #1e293b);
  border-color: rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.05);
}

.control-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-btn.active {
  color: #10b981;
  border-color: rgba(16, 185, 129, 0.6);
  background: rgba(16, 185, 129, 0.1);
}

.control-icon {
  font-size: 18px;
}

/* 播放按钮 */
.play-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition-fast);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  margin: 0 12px;
}

.play-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

.play-btn:active {
  transform: scale(0.98);
}

.play-icon, .pause-icon {
  font-size: 24px;
}

/* 音量控制 */
.volume-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mute-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 18px;
  transition: var(--transition-fast);
  color: var(--text-secondary, #64748b);
}

.mute-btn:hover {
  transform: scale(1.1);
  color: var(--text-primary, #1e293b);
}

.volume-slider {
  width: 80px;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(226, 232, 240, 0.5);
  border-radius: 2px;
  outline: none;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--text-secondary, #64748b);
  cursor: pointer;
  transition: var(--transition-fast);
}

.volume-slider::-webkit-slider-thumb:hover {
  background: #10b981;
  transform: scale(1.3);
}

/* 关闭按钮 */
.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: var(--text-secondary, #94a3b8);
  cursor: pointer;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-fast);
  backdrop-filter: blur(10px);
}

.close-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* 音频元素 */
.audio-element {
  display: none;
}

/* 减少动画偏好设置 */
@media (prefers-reduced-motion) {
  .record-wrapper {
    animation: rotate 20s linear infinite;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .music-player {
    right: 16px;
    bottom: 16px;
    width: calc(100vw - 32px);
    max-width: 500px;
  }
  
  .player-main {
    padding: 16px;
    gap: 16px;
  }
  
  .record-container {
    width: 100px;
    height: 100px;
  }
  
  .title {
    font-size: 18px;
  }
  
  .artist {
    font-size: 14px;
  }
  
  .reason {
    font-size: 12px;
  }
  
  .controls {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .control-group {
    justify-content: center;
  }
  
  .volume-controls {
    justify-content: center;
  }
}
</style>

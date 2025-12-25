<template>
  <div class="music-recommendation-view">
    <!-- 波形背景装饰 -->
    <div class="wave-bg-container">
      <div class="wave-bg wave-bg-1"></div>
      <div class="wave-bg wave-bg-2"></div>
      <div class="wave-bg wave-bg-3"></div>
    </div>
    
    <!-- 顶部推荐说明栏 -->
    <div class="recommendation-header">
      <div class="header-content">
        <div class="header-text">
          <h2 class="main-text">
            为您推荐适合当前状态的轻音乐
            <span class="recommendation-basis">（基于 {{ currentFatigueLevel }} 疲劳等级）</span>
          </h2>
          <p class="sub-text">点击卡片可查看详情</p>
        </div>
        <div style="display:flex;align-items:center;gap:12px">
          <el-tag class="fatigue-tag" :type="fatigueTagType" size="large">{{ currentFatigueLevel }} 疲劳专属</el-tag>
          <!-- 顶部添加音乐按钮 - 单独强化样式 -->
          <el-button 
            type="primary" 
            plain 
            size="small" 
            @click="openAddDialog"
            class="add-music-btn"
          >
            <el-icon><Upload /></el-icon>添加音乐
          </el-button>
        </div>
      </div>
    </div>

    <!-- 音乐推荐卡片列表 -->
    <div class="music-grid">
      <!-- 加载骨架占位 -->
      <div v-if="loading" class="skeleton-grid">
        <el-row :gutter="16">
          <el-col v-for="n in 6" :key="n" :xs="24" :sm="12" :md="8" :lg="6" :xl="6">
            <div class="music-card skeleton">
              <div class="cover-section">
                <div class="skeleton-cover"></div>
              </div>
              <div class="info-section">
                <div class="skeleton-line short"></div>
                <div class="skeleton-line"></div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      <!-- 使用虚拟滚动或分页加载优化长列表性能 -->
      <el-row :gutter="16" v-if="displayedMusicList.length > 0">
        <el-col 
          v-for="music in displayedMusicList" 
          :key="`${music.id || Math.random()}`"
          :xs="24" 
          :sm="12" 
          :md="8" 
          :lg="6" 
          :xl="6"
          class="music-col"
        >
          <div class="music-card business-card" :ref="el => el && observeMusicCard(el)">
            <!-- 封面图区域 - 修复图片加载逻辑 -->
            <div class="cover-section">
              <el-image
                :src="getCoverUrl(music)"
                :alt="`${music.title || '未知歌曲'} - ${music.artist || '未知艺术家'}`"
                class="music-cover"
                fit="cover"
                :lazy="false"
                @error="handleImageError($event, music)"
                @load="$event.target.classList.add('is-loaded')"
              >
                <template #error>
                  <div class="image-error">
                    <Headset class="music-icon" />
                  </div>
                </template>
              </el-image>
              
              <!-- 推荐指数标签 -->
              <div class="match-badge">
                {{ music.match_rate }}% 匹配
              </div>
              
              <!-- 播放按钮 -->
              <button class="play-button" type="button" @click.stop="playTrack(music)" :aria-label="'播放 ' + (music.title || '歌曲')">
                <VideoPlay class="play-svg-icon" />
              </button>
              <el-button class="delete-music-btn" type="danger" size="small" @click.stop="deleteMusic(music.id)">删除</el-button>
            </div>
            
            <!-- 信息区域 -->
            <div class="info-section">
              <h3 class="music-title">{{ music.title }}</h3>
              <p class="music-artist">{{ music.artist }}</p>
              <div class="music-meta">
                <span class="music-duration">{{ music.duration }}</span>
              </div>
              <p class="music-reason">{{ music.reason }}</p>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 空状态占位 -->
    <div v-if="musicList.length === 0 && !loading" class="empty-state">
      <div class="empty-container">
        <Headset class="empty-icon" />
        <p class="empty-text">暂无推荐音乐</p>
        <p class="empty-subtext">请先完成脑疲劳检测以获得个性化推荐</p>
        <el-button type="primary" @click="$router.push('/signal-monitor')" class="primary-button">
          前往检测
        </el-button>
      </div>
    </div>
    
    <!-- 加载更多区域 -->
    <div ref="loadMoreTrigger" class="load-more-trigger" v-if="hasMoreMusic">
      <el-skeleton :loading="isLoadingMore" animated>
        <el-skeleton-item variant="text" style="width: 30%; margin-bottom: 15px;" />
      </el-skeleton>
    </div>
    
    <!-- 加载完成提示 -->
    <div class="all-loaded" v-else-if="displayedMusicList.length > 0">
      <p>已显示全部推荐音乐</p>
    </div>
    
    <!-- 加载更多指示器 -->
    <div v-if="currentPage < totalPages && !loading" class="load-more-section">
      <el-button 
        type="primary" 
        plain 
        @click="loadMoreMusic"
        class="load-more-btn"
      >
        加载更多
      </el-button>
    </div>
  </div>
  
  <!-- 音乐播放器组件 -->
  <MusicPlayer v-if="showPlayer" :track="selectedTrack" :autoPlay="autoPlay" @close="showPlayer = false" />

  <!-- 添加音乐弹窗 -->
  <el-dialog 
    title="添加音乐" 
    v-model="showAddDialog" 
    width="600px" 
    append-to-body
    class="custom-add-music-dialog"
    style="z-index: 10000"
  >
    <el-form label-width="80px" class="music-form">
      <div class="dialog-content">
        <div class="left-section">
          <div class="cover-wrapper">
            <div class="cover-container">
              <el-image 
                :src="newMusic.cover ? resolveMediaUrl(newMusic.cover) : resolveMediaUrl('/static/music_cover/1.png')" 
                fit="cover" 
                class="cover-image"
              >
                <template #error>
                  <div class="cover-placeholder">
                    <Headset class="placeholder-icon" />
                    <span class="placeholder-text">封面预览</span>
                  </div>
                </template>
              </el-image>
              <div class="cover-ring"></div>
            </div>
          </div>

          <div class="audio-upload">
            <h4 class="upload-title">音频上传</h4>
            <div class="upload-btn-group">
              <input type="file" accept="audio/*" ref="fileInput" @change="onFileChange" class="hidden-input" />
              <el-button 
                size="small" 
                class="select-audio-btn" 
                @click="$refs.fileInput.click()"
              >
                <el-icon><Microphone /></el-icon>选择音频
              </el-button>
              <el-button 
                size="small" 
                type="primary" 
                :loading="uploading" 
                @click="uploadFile" 
                :disabled="!selectedFile"
              >
                <el-icon v-if="!uploading"><UploadFilled /></el-icon>
                <el-icon v-else><Loading /></el-icon>
                {{ uploading ? '上传中' : '上传' }}
              </el-button>
            </div>
            <div v-if="uploading" class="progress-container">
              <el-progress :percentage="uploadProgress" stroke-width="2" class="progress-bar"></el-progress>
              <span class="progress-text">{{ uploadProgress }}%</span>
            </div>
            <div class="file-info">
              <span class="file-name">{{ selectedFileName || '未选择文件' }}</span>
            </div>
            <p class="upload-hint">支持 MP3、WAV 格式，文件大小不超过 50MB</p>
          </div>
        </div>

        <div class="right-section">
          <el-form-item label="标题" class="form-item">
            <el-input 
              v-model="newMusic.title" 
              placeholder="请输入音乐标题"
              class="form-control"
            />
          </el-form-item>

          <el-form-item label="艺术家" class="form-item">
            <el-input 
              v-model="newMusic.artist" 
              placeholder="请输入艺术家/创作者"
              class="form-control"
            />
          </el-form-item>

          <el-form-item label="时长" class="form-item">
            <el-input 
              v-model="newMusic.duration" 
              placeholder="格式 05:30"
              class="form-control"
            />
            <p class="form-hint">若未填写，上传后将自动获取</p>
          </el-form-item>

          <el-form-item label="音乐类型" class="form-item">
            <el-select v-model="newMusic.music_type" placeholder="选择音乐类型" style="width:180px">
              <el-option label="自然 / Natural" value="natural"></el-option>
              <el-option label="钢琴 / Piano" value="piano"></el-option>
              <el-option label="白噪音 / WhiteNoise" value="whitenoise"></el-option>
              <el-option label="混合 / Mix" value="mix"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="适用疲劳程度" class="form-item">
            <el-select v-model="newMusic.fatigue_level" placeholder="选择适用疲劳程度" style="width:180px">
              <el-option label="轻度（Light）" value="light"></el-option>
              <el-option label="中度（Medium）" value="medium"></el-option>
              <el-option label="重度（Heavy）" value="heavy"></el-option>
            </el-select>
            <p class="form-hint">请选择这首歌适合的疲劳等级（界面显示为中文）</p>
          </el-form-item>

          <el-form-item label="封面设置" class="form-item">
            <div class="cover-setting">
              <el-input 
                v-model="newMusic.cover" 
                placeholder="封面图片 URL（可选）" 
                class="cover-url-input"
                style="margin-bottom: 8px;"
              />
              <div class="cover-btn-group">
                <input type="file" accept="image/*" ref="coverInput" @change="onCoverChange" class="hidden-input" />
                <el-button 
                  size="small" 
                  class="select-cover-btn" 
                  @click="$refs.coverInput.click()"
                >
                  <el-icon><Picture /></el-icon>选择图片
                </el-button>
                <el-button 
                  size="small" 
                  type="primary" 
                  :loading="uploadingCover" 
                  @click="uploadCover" 
                  :disabled="!selectedCoverFile"
                >
                  <el-icon v-if="!uploadingCover"><UploadFilled /></el-icon>
                  <el-icon v-else><Loading /></el-icon>
                  上传封面
                </el-button>
              </div>
            </div>
            <div v-if="selectedCoverFileName" class="cover-file-info">已选封面：{{ selectedCoverFileName }}</div>
          </el-form-item>

          <el-form-item label="推荐理由" class="form-item">
            <el-input 
              type="textarea" 
                v-model="newMusic.reason" 
                :placeholder="`说明为什么这首歌适合${currentFatigueLevel}疲劳状态...`"
              rows="4"
              class="form-control form-textarea"
            />
          </el-form-item>
        </div>
      </div>
    </el-form>

    <template #footer>
      <div class="dialog-footer" style="display: flex; justify-content: flex-end; gap: 12px;">
        <el-button class="cancel-button" @click="showAddDialog = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="uploading"
          @click="addMusic"
          style="margin-left: 12px;"
        >
          <el-icon><Check /></el-icon>添加音乐
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { Headset, VideoPlay, Upload, Loading, Picture, Check, Microphone, UploadFilled } from '@element-plus/icons-vue'
import MusicPlayer from '@/components/global/MusicPlayer.vue'
import { requestMethod } from '@/utils/request'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { resolveMedia } from '@/utils/media'
import { ElDialog, ElButton, ElSelect, ElOption } from 'element-plus'

export default {
  name: 'MusicRecommendationView',
  components: {
    Headset,
    VideoPlay,
    Upload,
    Loading,
    Picture,
    Check,
    MusicPlayer,
    ElDialog,
    ElButton,
    ElSelect,
    ElOption,
    Microphone,
    UploadFilled
  },
  data() {
    return {
      // 当前固定的疲劳等级来源：路由 query 或 localStorage（优先路由），默认 Medium
      currentFatigueLevel: (this.$route?.query?.fatigue || localStorage.getItem('current_fatigue_level') || 'Medium'),
      loading: false,
      musicList: [],
      displayedMusicList: [], // 用于虚拟滚动或分页显示的音乐列表
      currentPage: 1,
      pageSize: 12, // 每页显示的音乐数量
      observer: null, // Intersection Observer 实例
      loadMoreObserver: null, // 加载更多观察器
      isLoadingMore: false, // 是否正在加载更多
      loadMoreTrigger: null, // 加载更多触发元素引用
  selectedTrack: null,
  showPlayer: false,
  autoPlay: (function(){
        try{
          const u = JSON.parse(localStorage.getItem('user')||'null')
          return u?.preferences?.auto_play === 'true'
        }catch(e){return false}
      })(),
  // 添加音乐弹窗相关
      showAddDialog: false,
      newMusic: {
        title: '',
        artist: '',
        duration: '',
        cover: '',
        reason: '',
        music_type: 'natural',
        fatigue_level: 'medium',
        match_rate: 50,
        audio_url: ''
      },
      // upload state
      selectedFile: null,
      selectedFileName: '',
      uploading: false,
      uploadProgress: 0,
      // cover upload state
      selectedCoverFile: null,
      selectedCoverFileName: '',
      uploadingCover: false,
      coverUploadProgress: 0
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.musicList.length / this.pageSize)
    },
    hasMoreMusic() {
      return this.currentPage < this.totalPages && !this.loading
    },
    fatigueTagType() {
      const level = this.currentFatigueLevel.toLowerCase()
      if (level.includes('light') || level.includes('低')) return 'info'
      if (level.includes('medium') || level.includes('中')) return 'warning'
      if (level.includes('heavy') || level.includes('高') || level.includes('重')) return 'danger'
      return 'info'
    }
  },
  methods: {
    resolveMediaUrl(val) {
      try { return resolveMedia(val) } catch (e) { return val }
    },
    // 更新显示的音乐列表 - 优化显示逻辑
    updateDisplayedMusicList() {
      // 防御性编程：确保 musicList 是数组
      const safeMusicList = Array.isArray(this.musicList) ? this.musicList : []
      
      // 转换数据格式，确保字段正确映射
      const processedList = safeMusicList.map(music => ({
        ...music,
        id: music.id || `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        title: music.title || '未知歌曲',
        artist: music.artist || '未知艺术家',
        duration: music.duration || '00:00',
        match_rate: music.match_rate || 0,
        reason: music.reason || '暂无推荐理由',
        cover: resolveMedia(music.cover || music.cover_url || '/static/music_cover/placeholder.png')
      }))
      
      const startIndex = (this.currentPage - 1) * this.pageSize
      const endIndex = startIndex + this.pageSize
      this.displayedMusicList = processedList.slice(startIndex, endIndex)
      
      console.log('[MusicRecommendation] 显示的音乐数量:', this.displayedMusicList.length)
      
      // 在下一个 tick 执行滚动检测，确保 DOM 已更新
      this.$nextTick(() => {
        this.handleScroll()
      })
    },
    // 加载更多音乐
    loadMoreMusic() {
      if (this.currentPage < this.totalPages && !this.isLoadingMore) {
        this.isLoadingMore = true
        this.currentPage++
        this.updateDisplayedMusicList()
        // 加载完成后更新状态
        this.$nextTick(() => {
          this.isLoadingMore = false
        })
      }
    },
    // 刷新当前页
    refreshCurrentPage() {
      this.currentPage = 1
      this.updateDisplayedMusicList()
    },
    // 获取封面图片URL的辅助方法
    getCoverUrl(music) {
      // 多层级检查，确保返回有效的URL
      if (!music) return resolveMedia('/static/music_cover/placeholder.png')
      
      const coverUrl = music.cover || music.cover_url
      if (!coverUrl) return resolveMedia('/static/music_cover/placeholder.png')
      return resolveMedia(coverUrl)
    },
    
    // 监听音乐卡片，用于懒加载动画 - 简化逻辑，确保不会阻止显示
    observeMusicCard(el) {
      if (!el) return
      
      // 已经观察过的元素不再重复观察
      if (el.dataset.observed) return
      el.dataset.observed = 'true'
      
      // 确保卡片默认显示，动画作为增强
      el.style.opacity = '1'
      el.style.transform = 'translateY(0)'
      
      try {
        // 使用 Intersection Observer 监听元素可见性
        const cardObserver = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              // 元素进入视口，添加动画类
              setTimeout(() => {
                entry.target.classList.add('animate-in')
              }, 10) // 小延迟以确保DOM已完全渲染
              
              // 一旦动画完成，停止观察该元素
              cardObserver.unobserve(entry.target)
            }
          })
        }, {
          rootMargin: '100px 0px',
          threshold: 0.05
        })
        
        cardObserver.observe(el)
      } catch (error) {
        // 如果观察器失败，确保卡片仍然可见
        console.warn('卡片观察器初始化失败:', error)
      }
    },
    openAddDialog() {
      // 打开添加弹窗前，将默认 fatigue_level 设为当前页面的固定等级（映射到后端期望的值）
      const mapToBackend = (lvl) => {
        if (!lvl) return 'medium'
        const l = String(lvl).trim().toLowerCase()
        if (l === 'high') return 'heavy'
        if (l === 'low') return 'light'
        if (l === 'heavy' || l === 'light' || l === 'medium') return l
        if (l === 'high' || l === 'low') return l === 'high' ? 'heavy' : 'light'
        return 'medium'
      }
      try {
        this.newMusic.fatigue_level = mapToBackend(this.currentFatigueLevel)
      } catch (e) {}
      this.showAddDialog = true;
    },
    // 处理图片加载错误
    handleImageError(event, music) {
      // 如果图片加载失败，使用默认占位图
      const img = event.target
      img.src = resolveMedia('/static/music_cover/placeholder.png')
      
      // 也可以选择更新音乐对象的封面URL
      if (music) {
        music.cover = resolveMedia('/static/music_cover/placeholder.png')
      }
    },
    // 优化的滚动检测逻辑 - 使用 Intersection Observer API
    handleScroll() {
      // 兼容处理：优先使用 Intersection Observer，降级到传统方式
      if ('IntersectionObserver' in window && !this.observer) {
        this.observer = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              entry.target.classList.add('animate-in')
              // 一旦动画完成，停止观察该元素以减少资源消耗
              this.observer.unobserve(entry.target)
            }
          })
        }, {
          rootMargin: '100px 0px',
          threshold: 0.1
        })
        
        // 观察所有音乐卡片
        document.querySelectorAll('.music-card:not(.animate-in)').forEach(card => {
          this.observer.observe(card)
        })
      } else {
        // 降级处理：使用 requestAnimationFrame 和批量处理
        window.requestAnimationFrame(() => {
          const cards = document.querySelectorAll('.music-card:not(.animate-in)')
          // 批量处理，避免一次性处理过多元素
          Array.from(cards).slice(0, 10).forEach(card => {
            const rect = card.getBoundingClientRect()
            const isVisible = rect.top < window.innerHeight + 100
            if (isVisible) {
              card.classList.add('animate-in')
            }
          })
        })
      }
    },
    async loadMusic() {
      this.loading = true
      try {
        // 优先尝试推荐接口，传入当前 fatigue level（后端期望小写）
        let res = null
        const fatigueParam = (this.currentFatigueLevel || 'Medium').toLowerCase()
        
        // 创建一个模拟数据，用于测试音乐卡片显示
        const mockMusicData = [
          {
            id: 1,
            title: '轻柔钢琴曲',
            artist: '未知艺术家',
            duration: '02:34',
            match_rate: 95,
            reason: '舒缓的钢琴曲有助于缓解轻度疲劳',
            cover: resolveMedia('/static/music_cover/placeholder.png')
          },
          {
            id: 2,
            title: '自然雨声',
            artist: '环境音乐',
            duration: '05:12',
            match_rate: 88,
            reason: '自然音效能够帮助放松心情',
            cover: resolveMedia('/static/music_cover/placeholder.png')
          },
          {
            id: 3,
            title: '冥想音乐',
            artist: '冥想大师',
            duration: '10:00',
            match_rate: 92,
            reason: '适合深度放松，缓解工作压力',
            cover: resolveMedia('/static/music_cover/placeholder.png')
          }
        ]
        
        try {
          res = await requestMethod.get('/music/recommend', { fatigue_level: fatigueParam })
          if (res && res.data && res.data.music_list && res.data.music_list.length > 0) {
            this.musicList = res.data.music_list
            console.log('[MusicRecommendation] 成功加载推荐音乐:', this.musicList.length)
          } else {
            // 如果推荐接口没有返回数据，使用模拟数据
            console.log('推荐接口返回空数据，使用模拟数据')
            this.musicList = mockMusicData
          }
        } catch (e) {
          console.log('推荐接口调用失败，使用模拟数据进行测试', e)
          this.musicList = mockMusicData
        }

        // 初始化分页数据
        this.currentPage = 1
        this.updateDisplayedMusicList()
      } catch (e) {
        console.error('加载音乐失败', e)
        ElMessage.error('加载音乐失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    playTrack(music) {
      // 处理播放路径（兼容数据库字段），并打印日志以定位问题
      console.debug('[MusicRecommendation] playTrack called, music=', music)
      
      // 参数验证
      if (!music) {
        console.error('[MusicRecommendation] Invalid music parameter:', music)
        ElMessage.error('播放失败：音乐信息无效')
        return
      }
      
      const track = { ...music }
      
      // 增强音频URL处理逻辑
      try {
        // 确保src或audio_url存在
        if (!track.src && track.audio_url) {
          track.src = resolveMedia(track.audio_url)
        } else if (!track.src) {
          track.src = resolveMedia(`/static/music/sample${track.id || 1}.mp3`)
        }
        
        // 封面图片优先使用 cover 字段，其次 cover_url
        const coverVal = track.cover || track.cover_url
        track.cover = coverVal ? resolveMedia(coverVal) : resolveMedia('/static/music_cover/placeholder.png')
        
        // 确保 duration 为数字（秒）以避免播放器使用字符串导致问题
        const parse = (val) => {
          if (val == null) return null
          if (typeof val === 'number') return val
          if (/^\d+$/.test(String(val))) return Number(val)
          const parts = String(val).split(':').map(p => Number(p))
          if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) return parts[0]*60 + parts[1]
          if (parts.length === 3 && parts.every(p => !isNaN(p))) return parts[0]*3600 + parts[1]*60 + parts[2]
          return null
        }
        const pd = parse(track.duration)
        if (pd != null) {
          track.duration = pd
        } else {
          track.duration = 0 // 设置默认值避免播放器错误
        }
        
        console.debug('[MusicRecommendation] Processed track:', {
          id: track.id,
          title: track.title,
          src: track.src,
          duration: track.duration
        })
        
      } catch (e) {
        console.error('[MusicRecommendation] Error processing track:', e)
        ElMessage.error('播放失败：音乐数据处理错误')
        return
      }

      this.selectedTrack = track
      this.showPlayer = true
    },
    async addMusic() {
      try {
        // 验证必填字段
        if (!this.newMusic.title) {
          ElMessage.warning('请填写音乐标题')
          return
        }
        // 把前端字段 audio_url 映射为后端期望的 src
        const payload = { ...this.newMusic }
        if (payload.audio_url) {
          payload.src = payload.audio_url
          delete payload.audio_url
        }
        const res = await requestMethod.post('/music', payload)
        
        if (res && res.code === 200) {
          ElMessage.success('添加成功')
          this.showAddDialog = false
          // 重置表单，疲劳等级默认回到当前页面固定等级（映射为后端值）
          const mapToBackend = (lvl) => {
            if (!lvl) return 'medium'
            const l = String(lvl).trim().toLowerCase()
            if (l === 'high') return 'heavy'
            if (l === 'low') return 'light'
            if (['heavy','light','medium'].includes(l)) return l
            return 'medium'
          }
          this.newMusic = {
            title: '', 
            artist: '', 
            duration: '', 
            cover: '', 
            reason: '', 
            music_type: 'natural', 
            fatigue_level: mapToBackend(this.currentFatigueLevel), 
            match_rate: 50, 
            audio_url: ''
          }
          await this.loadMusic()  // 刷新列表
        } else {
          ElMessage.error(res?.msg || '添加失败')
        }
      } catch (e) {
        console.error('添加音乐失败', e)
        ElMessage.error('添加音乐失败，请检查网络或参数')
      }
    },
    onFileChange(e) {
      const file = e.target.files && e.target.files[0]
      if (!file) return
      this.selectedFile = file
      this.selectedFileName = file.name
      // 从文件名自动填充标题（用户可后续编辑）
      const name = file.name.replace(/\.[^/.]+$/, "")
      this.newMusic.title = name.replace(/[_-]+/g, ' ')
      // 计算时长前清空现有值
      this.newMusic.duration = ''
      // 尝试本地读取时长
      this.computeDurationFromFile(file).then(d => {
        if (d) this.newMusic.duration = d
      }).catch(() => {})
    },
    computeDurationFromFile(file) {
      return new Promise((resolve) => {
        try {
          const url = URL.createObjectURL(file)
          const audio = new Audio()
          audio.src = url
          audio.addEventListener('loadedmetadata', () => {
            const sec = Math.floor(audio.duration || 0)
            URL.revokeObjectURL(url)
            const mm = String(Math.floor(sec / 60)).padStart(2, '0')
            const ss = String(sec % 60).padStart(2, '0')
            resolve(`${mm}:${ss}`)
          })
          audio.addEventListener('error', () => { URL.revokeObjectURL(url); resolve(null) })
        } catch (e) { resolve(null) }
      })
    },
    async uploadFile() {
      if (!this.selectedFile) { ElMessage.warning('请先选择文件'); return }
      try {
        this.uploading = true
        this.uploadProgress = 0
        const form = new FormData()
        form.append('file', this.selectedFile)
        // 使用底层axios实例获取上传进度
        const res = await request.post('/music/upload', form, {
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              this.uploadProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            }
          }
        })
        if (res && res.code === 200 && res.data && res.data.src) {
          // 后端返回src和可能的元数据（标题、艺术家、时长、封面）
          const d = res.data
          this.newMusic.audio_url = d.src
          this.newMusic.src = d.src
          if (d.title) this.newMusic.title = d.title
          if (d.artist) this.newMusic.artist = d.artist
          if (d.duration) this.newMusic.duration = d.duration
          if (d.cover) this.newMusic.cover = d.cover
          ElMessage.success('上传成功，已填充音频信息')
        } else {
          ElMessage.error(res?.msg || '上传失败')
        }
      } catch (e) {
        console.error('上传失败', e)
        ElMessage.error('上传失败')
      } finally {
        this.uploading = false
        // 清除文件输入值以允许重新上传相同文件
        try { this.$refs.fileInput.value = null } catch (e) {}
        this.uploadProgress = 0
      }
    },
    onCoverChange(e) {
      const file = e.target.files && e.target.files[0]
      if (!file) return
      this.selectedCoverFile = file
      this.selectedCoverFileName = file.name
    },
    async uploadCover() {
      if (!this.selectedCoverFile) { ElMessage.warning('请先选择封面文件'); return }
      try {
        this.uploadingCover = true
        this.coverUploadProgress = 0
        const form = new FormData()
        form.append('file', this.selectedCoverFile)
        const res = await request.post('/music/upload_cover', form, {
          onUploadProgress: (ev) => {
            if (ev.total) this.coverUploadProgress = Math.round((ev.loaded * 100) / ev.total)
          }
        })
        if (res && res.code === 200 && res.data && res.data.cover) {
          this.newMusic.cover = res.data.cover
          ElMessage.success('封面上传成功')
        } else {
          ElMessage.error(res?.msg || '封面上传失败')
        }
      } catch (e) {
        console.error('封面上传失败', e)
        ElMessage.error('上传封面失败')
      } finally {
        this.uploadingCover = false
        try { this.$refs.coverInput.value = null } catch (e) {}
        this.coverUploadProgress = 0
      }
    },
    async deleteMusic(musicId) {
      try {
        await requestMethod.delete(`/music/${musicId}`, { delete_files: true })
        ElMessage.success('删除成功')
        this.musicList = this.musicList.filter(m => m.id !== musicId)
        // 更新显示的音乐列表
        this.updateDisplayedMusicList()
      } catch (e) {
        console.error('删除音乐失败', e)
        ElMessage.error('删除失败，请稍后重试')
      }
    }
  },
  mounted() {
    // 当页面挂载时，优先从路由 query 或 localStorage 读取固定的疲劳等级
    const routeLevel = this.$route?.query?.fatigue
    if (routeLevel) {
      try { localStorage.setItem('current_fatigue_level', routeLevel) } catch (e) {}
      this.currentFatigueLevel = routeLevel
    } else {
      this.currentFatigueLevel = localStorage.getItem('current_fatigue_level') || this.currentFatigueLevel
    }
    // 设置 tag 类型并加载音乐
    this.loadMusic()
    
    // 初始化加载更多观察器
    this.$nextTick(() => {
      if ('IntersectionObserver' in window) {
        this.loadMoreObserver = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting && this.hasMoreMusic && !this.isLoadingMore) {
              this.loadMoreMusic()
            }
          })
        }, {
          rootMargin: '100px 0px',
          threshold: 0.1
        })
        
        // 开始观察加载更多触发器
        if (this.$refs.loadMoreTrigger) {
          this.loadMoreObserver.observe(this.$refs.loadMoreTrigger)
        }
      }
    })
    
    // 监听滚动事件，但使用节流优化
    let scrollTimer = null
    window.addEventListener('scroll', () => {
      if (scrollTimer) return
      scrollTimer = setTimeout(() => {
        this.handleScroll()
        // 检查是否需要加载更多（降级方案）
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
          this.loadMoreMusic()
        }
        scrollTimer = null
      }, 100) // 100ms 节流
    })
  },
  beforeUnmount() {
    // 清理 Intersection Observer
    if (this.observer) {
      this.observer.disconnect()
    }
    // 清理加载更多观察器
    if (this.loadMoreObserver) {
      this.loadMoreObserver.disconnect()
    }
    // 清理滚动事件监听
    window.removeEventListener('scroll', this.handleScroll)
  },
}
</script>

<style lang="scss" scoped>
/* 导入设计令牌 */
@use '@/assets/styles/_design_tokens.scss' as *;

/* === ① 全局变量 & 字体 === */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root{
  --bg-music: #f5f7fa;
  --bg-card : #ffffff;
  --bg-light: #f8fafc;
  --brand-primary: #10b981;
  --brand-primary-light: rgba(16,185,129,.12);
  --brand-secondary: #0ea5e9;
  --brand-accent: #ec4899;
  --radius  : 8px;
  --shadow-sm: 0 2px 8px rgba(0,0,0,.04);
  --shadow-md: 0 4px 16px rgba(0,0,0,.08);
  --shadow-lg: 0 12px 24px rgba(0,0,0,.12);
  font-family: 'Inter',sans-serif;
}

/* 波形背景装饰 */
.wave-bg-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  overflow: hidden;
}

.wave-bg {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.2;
}

.wave-bg-1 {
  width: 600px;
  height: 600px;
  background: var(--brand-primary);
  top: -300px;
  right: -200px;
  animation: wave-move 15s ease-in-out infinite;
}

.wave-bg-2 {
  width: 400px;
  height: 400px;
  background: var(--brand-accent);
  bottom: -200px;
  left: -100px;
  animation: wave-move 18s ease-in-out infinite reverse;
}

.wave-bg-3 {
  width: 300px;
  height: 300px;
  background: var(--brand-secondary);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: wave-pulse 8s ease-in-out infinite;
}

@keyframes wave-move {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(-20px, 20px) rotate(5deg); }
  50% { transform: translate(0, 40px) rotate(0deg); }
  75% { transform: translate(20px, 20px) rotate(-5deg); }
}

@keyframes wave-pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.2; }
  50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.3; }
}

/* 顶部推荐说明栏 */
.recommendation-header{
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
  
  .header-content {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    padding: 24px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    box-shadow: var(--shadow-sm);
    
    .header-text {
      flex: 1;
      min-width: 300px;
      
      .main-text {
        margin: 0 0 12px 0;
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        background: linear-gradient(135deg, var(--brand-primary), var(--brand-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        
        .recommendation-basis {
          font-size: 16px;
          font-weight: 400;
          color: var(--text-regular);
          background: none;
          -webkit-background-clip: none;
          background-clip: none;
          -webkit-text-fill-color: var(--text-regular);
        }
      }
      
      .sub-text {
        margin: 0;
        font-size: 16px;
        color: var(--text-secondary);
      }
    }
    
    .fatigue-tag {
      border-radius: 24px;
      padding: 10px 20px;
      font-size: 16px;
      font-weight: 600;
      background: rgba(255, 183, 77, 0.25);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 183, 77, 0.35);
      color: var(--warning-color);
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
      }
    }
  }
}

/* 添加音乐按钮 */
.add-music-btn {
  padding: 10px 20px !important;
  font-weight: 600 !important;
  border-radius: 24px !important;
  background: rgba(16, 185, 129, 0.15) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(16, 185, 129, 0.3) !important;
  color: var(--brand-primary) !important;
  transition: all 0.3s ease !important;
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  z-index: 9999 !important;
  
  &:hover {
    background: var(--brand-primary) !important;
    color: white !important;
    border-color: var(--brand-primary) !important;
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }
}

/* === ③ 卡片 hover 动画 === */
.music-card{
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  transition: transform .35s, box-shadow .35s;
  will-change: transform;
  &:hover{
    transform: translateY(-6px);
    box-shadow: var(--shadow-lg);
    .cover-section .music-cover{
      transform: scale(1.08) rotate(3deg);
    }
    .play-button{
      animation: pulse 1.2s infinite;
    }
  }
}
@keyframes pulse{
  0%  {box-shadow: 0 0 0 0 rgba(16,185,129,.4);}
  70% {box-shadow: 0 0 0 12px rgba(16,185,129,0);}
  100%{box-shadow: 0 0 0 0 rgba(16,185,129,0);}
}

/* 全局样式保持不变 */
.music-recommendation-view {
  max-width: 1200px;
  margin: 0 auto;
  background: var(--bg-light);
  font-family: 'Inter', sans-serif;
  border-radius: 16px;
  padding: 24px;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.recommendation-header {
  margin-bottom: 32px;
  
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    
    .header-text {
      flex: 1;
      
      .main-text {
        margin: 0 0 8px 0;
        font-size: 24px;
        font-weight: 600;
        color: var(--text-primary);
        
        .recommendation-basis {
          font-size: 16px;
          font-weight: 400;
          color: var(--text-regular);
        }
      }
      
      .sub-text {
        margin: 0;
        font-size: 14px;
        color: var(--text-secondary);
      }
    }
    
    .fatigue-tag {
      border-radius: 20px;
      padding: 8px 16px;
      font-size: 14px;
      font-weight: 500;
    }
  }
}

/* 音乐卡片样式保持不变 */
.music-grid {
  position: relative;
  z-index: 1;
  
  .skeleton-grid {
    .music-card.skeleton {
      background: rgba(255, 255, 255, 0.8);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.5);
      box-shadow: var(--shadow-sm);
      .cover-section { 
        .skeleton-cover { 
          width: 100%; 
          height: 160px; 
          background: linear-gradient(90deg, #f0f0f0, #eaeaea, #f0f0f0); 
          border-radius: 12px; 
          animation: shimmer 1.5s infinite;
        } 
      }
      .info-section { 
        .skeleton-line { 
          height: 12px; 
          background: linear-gradient(90deg, #f0f0f0, #eaeaea, #f0f0f0); 
          margin-bottom: 8px; 
          border-radius: 6px; 
          animation: shimmer 1.5s infinite;
          &.short{ 
            width: 60%; 
          } 
        } 
      }
    }
  }
  
  .music-card {
    aspect-ratio: 3/4;
    border-radius: 16px;
    box-shadow: var(--shadow-sm);
    overflow: hidden;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.5);
    transition: all 0.35s ease;
    margin-bottom: 24px;
    opacity: 0;
    transform: translateY(20px);
    
    &.animate-in {
      opacity: 1;
      transform: translateY(0);
    }
    
    &.lazy-loaded {
      opacity: 1;
      transform: translateY(0);
    }
    
    // 图片懒加载过渡
    .music-cover {
      transition: opacity 0.5s ease;
    }
    
    .music-cover.is-loaded {
      opacity: 1;
    }
    
    &:hover {
      transform: translateY(-8px);
      box-shadow: var(--shadow-lg);
      background: rgba(255, 255, 255, 1);
      
      .cover-section .music-cover {
        transform: scale(1.08) rotate(3deg);
      }
      
      .play-button {
        animation: pulse 1.2s infinite;
        background: var(--brand-primary);
        color: white;
      }
    }
    
    .cover-section {
      position: relative;
      height: 60%;
      overflow: hidden;
      border-radius: 16px 16px 0 0;
      
      .music-cover {
        width: 100%;
        height: 100%;
        transition: transform 0.5s ease;
      }
      
      .image-error {
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #f5f5f5, #e9ecef);
        display: flex;
        align-items: center;
        justify-content: center;
        
        .music-icon {
          font-size: 48px;
          color: var(--text-placeholder);
        }
      }
      
      .match-badge {
        position: absolute;
        top: 12px;
        right: 12px;
        background: var(--brand-accent);
        color: white;
        padding: 6px 12px;
        border-radius: 16px;
        font-size: 14px;
        font-weight: 600;
        z-index: 2;
        box-shadow: 0 4px 12px rgba(236, 72, 153, 0.3);
      }
      
      .play-button {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 64px;
        height: 64px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        color: var(--brand-primary);
        cursor: pointer;
        transition: all 0.3s ease;
        z-index: 2;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        
        &:hover {
          background: var(--brand-primary);
          color: white;
          transform: translate(-50%, -50%) scale(1.1);
        }
      }

      .delete-music-btn {
        position: absolute;
        bottom: 12px;
        right: 12px;
        padding: 6px 12px;
        font-size: 12px;
        z-index: 2;
        background: rgba(239, 68, 68, 0.8) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px;
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(239, 68, 68, 1) !important;
          transform: scale(1.05);
        }
      }
    }
    
    .info-section {
      height: 40%;
      padding: 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      
      .music-title {
        margin: 0 0 8px 0;
        font-size: 18px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 1;
        line-clamp: 1;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
      
      .music-artist {
        margin: 0 0 8px 0;
        font-size: 14px;
        color: var(--text-regular);
      }
      
      .music-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        
        .music-duration {
          font-size: 12px;
          color: var(--text-secondary);
          font-family: 'SF Mono', Monaco, monospace;
          background: var(--bg-light);
          padding: 2px 8px;
          border-radius: 12px;
        }
      }
      
      .music-reason {
        margin: 0;
        font-size: 12px;
        color: var(--text-secondary);
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
    }
  }
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  position: relative;
  z-index: 1;
  
  .empty-container {
    text-align: center;
    padding: 48px 20px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    box-shadow: var(--shadow-sm);
    max-width: 400px;
    width: 100%;
    
    .empty-icon {
      font-size: 80px;
      color: var(--text-placeholder);
      margin-bottom: 24px;
      animation: float 3s ease-in-out infinite;
    }
    
    .empty-text {
      font-size: 20px;
      font-weight: 600;
      margin: 0 0 12px 0;
      color: var(--text-primary);
    }
    
    .empty-subtext {
      font-size: 16px;
      margin: 0 0 24px 0;
      color: var(--text-secondary);
      line-height: 1.5;
    }
    
    .primary-button {
      padding: 12px 24px;
      font-size: 16px;
      font-weight: 600;
      border-radius: 28px;
      background: linear-gradient(135deg, var(--brand-primary), var(--brand-secondary));
      border: none;
      color: white;
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        background: linear-gradient(135deg, var(--brand-secondary), var(--brand-primary));
      }
    }
  }
}

/* 浮动动画 */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 闪烁动画 */
@keyframes shimmer {
  0% { background-position: -468px 0; }
  100% { background-position: 468px 0; }
}

/* 脉冲动画 */
@keyframes pulse {
  0%  { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
  70% { box-shadow: 0 0 0 16px rgba(16, 185, 129, 0); }
  100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* 弹窗核心样式 - 彻底重构 */
.custom-add-music-dialog {
  --primary-color: var(--brand-primary);
  --primary-light: var(--brand-primary-light);
  --border-color: var(--border-color);
  --text-primary: var(--text-primary);
  --text-secondary: var(--text-secondary);
  --bg-light: var(--bg-light);
  
  .el-dialog__header {
    padding: 24px 24px 16px;
    border-bottom: 1px solid var(--border-color);
    background: linear-gradient(135deg, var(--brand-primary-light), var(--brand-secondary-light));
    
    .el-dialog__title {
      font-size: 20px;
      font-weight: 700;
      color: var(--text-primary);
    }
  }
  
  .el-dialog__body {
    padding: 24px;
    max-height: 70vh;
    overflow-y: auto;
  }
  
  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid var(--border-color);
    background-color: var(--bg-light);
  }
}

/* 弹窗内容布局 - 确保不会挤压按钮 */
.dialog-content {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 24px;
}

/* 左侧区域 - 确保按钮区域不被挤压 */
.left-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.cover-wrapper {
  display: flex;
  justify-content: center;
}

.cover-container {
  position: relative;
  width: 180px;
  height: 180px;
}

.cover-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 6px solid white;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease;
  
  &:hover {
    transform: scale(1.05);
  }
}

.cover-ring {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  border-radius: 50%;
  border: 2px dashed var(--border-color);
  pointer-events: none;
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  border: 6px solid white;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  
  .placeholder-icon {
    font-size: 40px;
    margin-bottom: 8px;
    color: var(--text-placeholder);
  }
  
  .placeholder-text {
    font-size: 14px;
    font-weight: 500;
  }
}

/* 音频上传区域 - 按钮区域单独设置 */
.audio-upload {
  background-color: var(--bg-light);
  border-radius: 10px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: var(--shadow-sm);
    border-color: var(--brand-primary-light);
  }
}

.upload-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

/* 按钮组 - 固定高度，确保不会被压缩 */
.upload-btn-group {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 40px;
}

/* 所有按钮强制可见 - 最高优先级 */
.select-audio-btn, .upload-audio-btn, .select-cover-btn, .upload-cover-btn, .confirm-button {
  visibility: visible !important;
  display: inline-flex !important;
  opacity: 1 !important;
  z-index: 9999 !important;
  position: relative !important;
}

.select-audio-btn {
  flex: 1;
  background-color: white;
  border-color: var(--border-color);
  
  &:hover {
    background-color: var(--bg-light);
    border-color: var(--brand-primary);
  }
}

.upload-audio-btn {
  flex: 1;
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  
  &:hover {
    background-color: var(--brand-secondary);
    border-color: var(--brand-secondary);
  }
}

.hidden-input {
  display: none;
}

.progress-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-bar {
  width: 100%;
}

.progress-text {
  font-size: 12px;
  color: var(--text-secondary);
  text-align: right;
}

.file-info {
  padding: 10px 12px;
  background-color: white;
  border-radius: 8px;
  font-size: 13px;
  border: 1px solid var(--border-color);
}

.file-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

.upload-hint {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

/* 右侧表单区域 */
.right-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-item {
  margin-bottom: 0 !important;
  
  .el-form-item__label {
    font-weight: 500;
    color: var(--text-primary);
  }
}

.form-control {
  width: 100%;
  border-radius: 8px !important;
  border-color: var(--border-color) !important;
  transition: all 0.2s ease;
  
  &:focus {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15) !important;
  }
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.form-hint {
  margin: 6px 0 0 0;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

/* 封面设置区域 - 按钮组单独布局 */
.cover-setting {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cover-url-input {
  width: 100%;
}

.cover-btn-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.select-cover-btn {
  background-color: white;
  border-color: var(--border-color);
  
  &:hover {
    background-color: var(--bg-light);
    border-color: var(--brand-primary);
  }
}

.upload-cover-btn {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  
  &:hover {
    background-color: var(--brand-secondary);
    border-color: var(--brand-secondary);
  }
}

.cover-file-info {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.cover-progress {
  color: var(--primary-color);
  font-weight: 500;
}

/* 底部按钮 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-button {
  min-width: 100px;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: var(--bg-light);
  }
}

.confirm-button {
  min-width: 120px;
  padding: 8px 24px;
  background-color: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
  border-radius: 8px;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: var(--brand-secondary) !important;
    border-color: var(--brand-secondary) !important;
  }
  
  &:disabled {
    background-color: var(--brand-primary-light) !important;
    border-color: var(--brand-primary-light) !important;
    color: white !important;
  }
}

/* 加载更多和懒加载样式 */
.load-more-trigger {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
  margin-bottom: 20px;
  padding: 20px;
}

.all-loaded {
  text-align: center;
  padding: 30px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .music-recommendation-view {
    padding: 20px;
  }
  
  .header-content {
    padding: 20px;
  }
  
  .main-text {
    font-size: 24px !important;
  }
  
  /* 优化大屏幕上的懒加载性能 */
  .music-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 992px) {
  .dialog-content {
    grid-template-columns: 1fr;
  }
  
  .cover-container {
    width: 150px;
    height: 150px;
    margin: 0 auto;
  }
}

@media (max-width: 768px) {
  .music-recommendation-view {
    padding: 16px;
    border-radius: 12px;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
    padding: 16px;
  }
  
  .header-text {
    min-width: auto !important;
  }
  
  .main-text {
    font-size: 20px !important;
  }
  
  .music-card {
    aspect-ratio: 3/4.5;
  }
  
  .form-item {
    margin-bottom: 12px !important;
  }
}

@media (max-width: 480px) {
  .music-recommendation-view {
    padding: 12px;
  }
  
  .recommendation-header {
    margin-bottom: 20px;
  }
  
  .upload-btn-group {
    flex-direction: column;
    height: auto;
    gap: 8px;
  }
  
  .select-audio-btn, .upload-audio-btn {
    width: 100%;
  }
  
  .cover-btn-group {
    flex-direction: column;
    gap: 8px;
  }
  
  .select-cover-btn, .upload-cover-btn {
    width: 100%;
  }
  
  .dialog-footer {
    flex-direction: column-reverse;
  }
  
  .cancel-button, .confirm-button {
    width: 100%;
  }
}
</style>
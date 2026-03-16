import { defineStore } from 'pinia'

export const usePlayerStore = defineStore('player', {
  state: () => ({
    currentTrack: null,
    isPlaying: false,
    duration: 0,
    currentTime: 0,
    volume: 0.15,
    isMuted: false,
    repeatMode: 'list',
    playlist: [],
    currentIndex: -1,
    showPlayer: false
  }),

  getters: {
    hasNextTrack: (state) => {
      return state.currentIndex < state.playlist.length - 1
    },
    hasPrevTrack: (state) => {
      return state.currentIndex > 0
    }
  },

  actions: {
    // 播放指定曲目
    playTrack(track, playlist = []) {
      if (!track) return
      
      this.currentTrack = track
      this.currentTime = 0
      this.duration = 0
      this.isPlaying = true
      this.showPlayer = true
      
      // 如果提供了播放列表，更新playlist和currentIndex
      if (playlist && playlist.length > 0) {
        this.playlist = playlist
        this.currentIndex = playlist.findIndex(item => item.id === track.id)
        // 如果在列表中找不到当前曲目，设置为0
        if (this.currentIndex === -1) {
          this.currentIndex = 0
        }
      }
    },
    
    // 播放AI推荐的音乐
    playMusic(musicName) {
      if (!musicName) return
      
      // 从音乐名称中提取标题和艺术家
      let title = musicName
      let artist = '未知艺术家'
      
      // 尝试从文件名中提取艺术家和标题
      const match = musicName.match(/(.+?) - (.+)\.mp3/)
      if (match) {
        artist = match[1]
        title = match[2]
      }
      
      // 创建一个临时的track对象
      const track = {
        id: Date.now(),
        title: title,
        artist: artist,
        src: `/static/music/${encodeURIComponent(musicName)}`,
        cover: '/static/music_cover/placeholder.png',
        reason: 'AI推荐'
      }
      
      this.playTrack(track)
    },

    // 关闭播放器
    closePlayer() {
      this.isPlaying = false
      this.showPlayer = false
    },

    // 设置播放状态
    setIsPlaying(playing) {
      this.isPlaying = playing
    },

    // 设置当前时间
    setCurrentTime(time) {
      this.currentTime = time
    },

    // 设置总时长
    setDuration(dur) {
      this.duration = dur
    },

    // 设置音量
    setVolume(vol) {
      this.volume = vol
    },

    // 设置静音状态
    setIsMuted(muted) {
      this.isMuted = muted
    },

    // 切换循环模式
    toggleRepeatMode() {
      const modes = ['list', 'single', 'random']
      const currentIndex = modes.indexOf(this.repeatMode)
      this.repeatMode = modes[(currentIndex + 1) % modes.length]
    },

    // 播放下一首
    playNext() {
      if (!this.hasNextTrack) return null
      
      this.currentIndex++
      const nextTrack = this.playlist[this.currentIndex]
      // 传递当前playlist，确保导航状态保持一致
      this.playTrack(nextTrack, this.playlist)
      return nextTrack
    },

    // 播放上一首
    playPrevious() {
      if (!this.hasPrevTrack) return null
      
      this.currentIndex--
      const prevTrack = this.playlist[this.currentIndex]
      // 传递当前playlist，确保导航状态保持一致
      this.playTrack(prevTrack, this.playlist)
      return prevTrack
    }
  }
})
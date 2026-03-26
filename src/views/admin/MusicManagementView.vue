<template>
  <div class="music-management-view">
    <div class="view-header">
      <h1>音乐管理</h1>
      <el-button type="primary" @click="handleAddMusic">
        <el-icon><Plus /></el-icon>
        <span>添加音乐</span>
      </el-button>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="search-filter">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索音乐标题或艺术家"
        clearable
        prefix-icon="Search"
        style="width: 300px; margin-right: 16px;"
      />
      <el-select
        v-model="filterType"
        placeholder="筛选音乐类型"
        clearable
        style="width: 160px; margin-right: 16px;"
      >
        <el-option
          v-for="type in musicTypes"
          :key="type"
          :label="type"
          :value="type"
        />
      </el-select>
      <el-button
        type="default"
        @click="handleSearch"
        style="margin-left: 16px;"
      >
        搜索
      </el-button>
    </div>
    
    <!-- 批量操作 -->
    <div class="batch-operations" v-if="selectedMusic.length > 0">
      <span>已选择 {{ selectedMusic.length }} 项</span>
      <el-button type="danger" @click="handleBatchDelete">
        <el-icon><Delete /></el-icon>
        <span>批量删除</span>
      </el-button>
    </div>
    
    <!-- 音乐列表 -->
    <el-table
      v-loading="loading"
      :data="musicList"
      style="width: 100%; margin-top: 16px;"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="标题" min-width="200">
        <template #default="scope">
          <div class="music-title">
            <img :src="scope.row.cover || '/static/avatar/default.jpg'" alt="封面" class="music-cover" />
            <span>{{ scope.row.title }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="artist" label="艺术家" min-width="120" />
      <el-table-column prop="duration" label="时长" width="100" />
      <el-table-column prop="music_type" label="类型" width="120" />
      <el-table-column prop="fatigue_level" label="适用疲劳程度" width="150">
        <template #default="scope">
          <el-tag :type="scope.row.fatigue_level === 'light' ? 'info' : scope.row.fatigue_level === 'medium' ? 'warning' : 'danger'">
            {{ scope.row.fatigue_level === 'light' ? '轻度' : scope.row.fatigue_level === 'medium' ? '中度' : '重度' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="scenes" label="适用场景" min-width="150">
        <template #default="scope">
          <div class="scenes-list">
            <el-tag 
              v-for="scene in getScenesList(scope.row.scenes)" 
              :key="scene" 
              size="small" 
              type="info" 
              effect="plain"
            >
              {{ scene === 'work' ? '工作' : scene === 'study' ? '学习' : scene === 'drive' ? '驾驶' : scene }}
            </el-tag>
            <span v-if="!scope.row.scenes || getScenesList(scope.row.scenes).length === 0" class="no-scenes">无</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="match_rate" label="匹配率" width="100">
        <template #default="scope">
          {{ scope.row.match_rate }}%
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button type="primary" size="small" @click="handleEditMusic(scope.row)" style="margin-right: 8px;">
            编辑
          </el-button>
          <el-button type="danger" size="small" @click="handleDeleteMusic(scope.row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 添加/编辑音乐对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="900px"
      class="modern-music-dialog"
    >
      <div class="dialog-content-wrapper">
        <!-- 左侧：上传区域 -->
        <div class="left-section">
          <!-- 封面上传 -->
          <div class="upload-card">
            <h3 class="upload-section-title">
              <el-icon><Picture /></el-icon>
              封面上传
            </h3>
            <div class="cover-upload-container">
              <div class="cover-preview">
                <img
                  v-if="musicForm.cover"
                  :src="musicForm.cover"
                  class="cover-image"
                  alt="封面"
                />
                <div v-else class="cover-placeholder">
                  <el-icon><Plus /></el-icon>
                  <span>封面预览</span>
                </div>
              </div>
              <div class="upload-controls">
                <input type="file" accept="image/*" ref="coverInput" @change="onCoverChange" class="hidden-input" />
                <el-button 
                  size="small" 
                  class="select-btn"
                  @click="$refs.coverInput.click()"
                >
                  <el-icon><Picture /></el-icon>选择封面
                </el-button>
                <el-button 
                  size="small" 
                  type="primary" 
                  :loading="uploadingCover" 
                  @click="uploadCover" 
                  :disabled="!selectedCoverFile"
                >
                  <el-icon><Upload /></el-icon>
                  {{ uploadingCover ? '上传中' : '上传封面' }}
                </el-button>
              </div>
              <div v-if="selectedCoverFileName" class="file-info">
                已选择：{{ selectedCoverFileName }}
              </div>
              <div v-if="uploadingCover" class="progress-container">
                <el-progress :percentage="coverUploadProgress" stroke-width="2" class="progress-bar"></el-progress>
              </div>
            </div>
          </div>

          <!-- 音频上传 -->
          <div class="upload-card">
            <h3 class="upload-section-title">
              <el-icon><Microphone /></el-icon>
              音频上传
            </h3>
            <div class="audio-upload-container">
              <div class="upload-controls">
                <input type="file" accept="audio/*" ref="fileInput" @change="onFileChange" class="hidden-input" />
                <el-button 
                  size="small" 
                  class="select-btn"
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
                  <el-icon><Upload /></el-icon>
                  {{ uploading ? '上传中' : '上传音频' }}
                </el-button>
              </div>
              <div v-if="selectedFileName" class="file-info">
                已选择：{{ selectedFileName }}
              </div>
              <div v-if="uploading" class="progress-container">
                <el-progress :percentage="uploadProgress" stroke-width="2" class="progress-bar"></el-progress>
              </div>
              <div v-if="musicForm.audio_url" class="audio-info">
                <el-icon><Check /></el-icon>
                <span>音频已上传</span>
              </div>
              <p class="upload-hint">支持 MP3、WAV 格式，文件大小不超过 50MB</p>
            </div>
          </div>
        </div>

        <!-- 右侧：表单区域 -->
        <div class="right-section">
          <el-form :model="musicForm" :rules="musicFormRules" ref="musicFormRef" class="modern-form">
            <el-form-item label="标题" prop="title" class="form-item">
              <el-input v-model="musicForm.title" placeholder="请输入音乐标题" class="form-input" />
            </el-form-item>
            <el-form-item label="艺术家" prop="artist" class="form-item">
              <el-input v-model="musicForm.artist" placeholder="请输入艺术家" class="form-input" />
            </el-form-item>
            <el-form-item label="时长" prop="duration" class="form-item">
              <el-input v-model="musicForm.duration" placeholder="格式 05:30" class="form-input" />
              <p class="form-hint">若未填写，上传后将自动获取</p>
            </el-form-item>
            <el-form-item label="音乐类型" prop="music_type" class="form-item">
              <el-select v-model="musicForm.music_type" placeholder="选择音乐类型" class="form-select">
                <el-option label="自然 / Natural" value="natural"></el-option>
                <el-option label="钢琴 / Piano" value="piano"></el-option>
                <el-option label="白噪音 / WhiteNoise" value="whitenoise"></el-option>
                <el-option label="混合 / Mix" value="mix"></el-option>
                <el-option label="古典 / Classical" value="classical"></el-option>
                <el-option label="爵士 / Jazz" value="jazz"></el-option>
                <el-option label="流行 / Pop" value="pop"></el-option>
                <el-option label="摇滚 / Rock" value="rock"></el-option>
                <el-option label="电子 / Electronic" value="electronic"></el-option>
                <el-option label="环境 / Ambient" value="ambient"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="适用疲劳程度" prop="fatigue_level" class="form-item">
              <el-select v-model="musicForm.fatigue_level" placeholder="选择适用疲劳程度" class="form-select">
                <el-option label="轻度（Light）" value="light"></el-option>
                <el-option label="中度（Medium）" value="medium"></el-option>
                <el-option label="重度（Heavy）" value="heavy"></el-option>
              </el-select>
              <p class="form-hint">请选择这首歌适合的疲劳等级</p>
            </el-form-item>
            <el-form-item label="匹配率" prop="match_rate" class="form-item">
              <div class="slider-container">
                <el-slider v-model="musicForm.match_rate" :min="0" :max="100" :step="1" class="form-slider" />
                <span class="slider-value">{{ musicForm.match_rate }}%</span>
              </div>
            </el-form-item>
            <el-form-item label="适用场景" prop="scenes" class="form-item">
              <el-checkbox-group v-model="musicForm.scenes" class="scenes-checkbox-group">
                <el-checkbox label="work" border>工作</el-checkbox>
                <el-checkbox label="study" border>学习</el-checkbox>
                <el-checkbox label="drive" border>驾驶</el-checkbox>
              </el-checkbox-group>
              <p class="form-hint">选择这首歌适合的场景（可多选）</p>
            </el-form-item>
            <el-form-item label="推荐理由" prop="reason" class="form-item">
              <el-input
                v-model="musicForm.reason"
                type="textarea"
                placeholder="说明为什么这首歌适合当前疲劳状态..."
                :rows="4"
                class="form-textarea"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" class="cancel-btn">取消</el-button>
          <el-button type="primary" @click="handleSaveMusic" class="save-btn">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { Plus, Search, Delete, Upload, Check, Microphone, Picture } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { requestMethod } from '@/utils/request';

// 数据状态
const loading = ref(false);
const musicList = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const searchKeyword = ref('');
const filterType = ref('');
const selectedMusic = ref([]);

// 对话框状态
const dialogVisible = ref(false);
const dialogTitle = ref('添加音乐');
const musicForm = ref({
  id: null,
  title: '',
  artist: '',
  duration: '',
  cover: '',
  audio_url: '',
  music_type: 'natural',
  fatigue_level: 'medium',
  match_rate: 50,
  reason: '',
  scenes: []
});
const musicFormRef = ref(null);

// 上传相关状态
const selectedFile = ref(null);
const selectedFileName = ref('');
const uploading = ref(false);
const uploadProgress = ref(0);
const selectedCoverFile = ref(null);
const selectedCoverFileName = ref('');
const uploadingCover = ref(false);
const coverUploadProgress = ref(0);

// 表单验证规则
const musicFormRules = reactive({
  title: [
    { required: true, message: '请输入音乐标题', trigger: 'blur' }
  ],
  artist: [
    { required: true, message: '请输入艺术家', trigger: 'blur' }
  ],
  duration: [
    { required: true, message: '请输入时长或上传音频文件', trigger: 'blur' }
  ],
  music_type: [
    { required: true, message: '请选择音乐类型', trigger: 'change' }
  ],
  fatigue_level: [
    { required: true, message: '请选择适用疲劳程度', trigger: 'change' }
  ],
  audio_url: [
    { required: true, message: '请上传音频文件', trigger: 'blur' }
  ],
  match_rate: [
    { required: true, message: '请设置匹配率', trigger: 'change' }
  ]
});

// 音乐类型选项
const musicTypes = ['classical', 'jazz', 'pop', 'rock', 'electronic', 'natural', 'ambient'];

// 获取场景列表
const getScenesList = (scenes) => {
  if (!scenes) return [];
  return scenes.split(',').map(scene => scene.trim()).filter(scene => scene);
};

// 加载音乐列表
const loadMusicList = async () => {
  try {
    loading.value = true;
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchKeyword.value
    };
    
    // 只有当filterType不为空时才添加music_type参数
    if (filterType.value) {
      params.music_type = filterType.value;
    }
    
    console.log('加载音乐列表参数:', params);
    
    // 使用requestMethod发送请求
    const response = await requestMethod.get('/admin/music', params);
    
    console.log('加载音乐列表响应:', response);
    
    if (response.code === 200) {
      musicList.value = response.data.items || [];
      total.value = response.data.pagination?.total || 0;
    }
  } catch (error) {
    console.error('加载音乐列表失败:', error);
    ElMessage.error('加载音乐列表失败，请重试');
  } finally {
    loading.value = false;
  }
};

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1;
  loadMusicList();
};

// 处理分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size;
  loadMusicList();
};

// 处理当前页变化
const handleCurrentChange = (page) => {
  currentPage.value = page;
  loadMusicList();
};

// 处理选择变化
const handleSelectionChange = (val) => {
  selectedMusic.value = val;
};

// 处理添加音乐
const handleAddMusic = () => {
  musicForm.value = {
    id: null,
    title: '',
    artist: '',
    duration: '',
    cover: '',
    audio_url: '',
    music_type: 'natural',
    fatigue_level: 'medium',
    match_rate: 50,
    reason: '',
    scenes: []
  };
  dialogTitle.value = '添加音乐';
  dialogVisible.value = true;
};

// 处理编辑音乐
const handleEditMusic = (music) => {
  // 将字符串形式的 scenes 转换为数组
  const scenesArray = music.scenes ? music.scenes.split(',').map(scene => scene.trim()).filter(scene => scene) : [];
  
  musicForm.value = {
    id: music.id,
    title: music.title,
    artist: music.artist,
    duration: music.duration || '',
    cover: music.cover || '',
    audio_url: music.audio_url || music.src || '',
    music_type: music.music_type || 'natural',
    fatigue_level: music.fatigue_level || 'medium',
    match_rate: music.match_rate || 50,
    reason: music.reason || '',
    scenes: scenesArray
  };
  dialogTitle.value = '编辑音乐';
  dialogVisible.value = true;
};

// 检查是否存在相同音乐
const checkDuplicateMusic = async () => {
  try {
    const response = await requestMethod.get('/admin/music', { search: musicForm.value.title });
    const existingMusic = response.data.items || [];
    
    // 检查是否存在相同标题的音乐（编辑时排除当前音乐）
    const duplicate = existingMusic.some(music => {
      return music.title === musicForm.value.title && music.id !== musicForm.value.id;
    });
    
    if (duplicate) {
      ElMessage.error('已存在相同标题的音乐');
      return true;
    }
    return false;
  } catch (error) {
    console.error('检查重复音乐失败:', error);
    return false;
  }
};

// 处理保存音乐
const handleSaveMusic = async () => {
  if (!musicFormRef.value) return;
  
  try {
    await musicFormRef.value.validate();
    
    // 添加音乐时检查是否存在相同音乐
    if (!musicForm.value.id) {
      const hasDuplicate = await checkDuplicateMusic();
      if (hasDuplicate) {
        return;
      }
    }
    
    // 准备提交数据
    const submitData = {
      title: musicForm.value.title,
      artist: musicForm.value.artist,
      duration: musicForm.value.duration,
      cover: musicForm.value.cover,
      audio_url: musicForm.value.audio_url,
      music_type: musicForm.value.music_type,
      fatigue_level: musicForm.value.fatigue_level,
      match_rate: musicForm.value.match_rate,
      reason: musicForm.value.reason,
      scenes: musicForm.value.scenes.join(',')
    };
    
    console.log('提交音乐数据:', submitData);
    
    if (musicForm.value.id) {
      // 编辑音乐
      const response = await requestMethod.put(`/admin/music/${musicForm.value.id}`, submitData);
      if (response.code === 200) {
        ElMessage.success('音乐更新成功');
      }
    } else {
      // 添加音乐
      const response = await requestMethod.post('/admin/music', submitData);
      if (response.code === 200) {
        ElMessage.success('音乐添加成功');
      }
    }
    
    dialogVisible.value = false;
    loadMusicList();
  } catch (error) {
    console.error('保存音乐失败:', error);
    console.error('错误详情:', error.response || error);
    ElMessage.error(error.message || '保存失败，请重试');
  }
};

// 处理删除音乐
const handleDeleteMusic = async (musicId) => {
  try {
    const response = await requestMethod.delete(`/admin/music/${musicId}`);
    if (response.code === 200) {
      ElMessage.success('音乐删除成功');
      loadMusicList();
    }
  } catch (error) {
    console.error('删除音乐失败:', error);
    ElMessage.error('删除失败，请重试');
  }
};

// 处理批量删除
const handleBatchDelete = async () => {
  if (selectedMusic.value.length === 0) return;
  
  try {
    const musicIds = selectedMusic.value.map(music => music.id);
    const response = await requestMethod.post('/admin/music/batch-delete', { ids: musicIds });
    if (response.code === 200) {
      ElMessage.success(`成功删除 ${selectedMusic.value.length} 条音乐`);
      selectedMusic.value = [];
      loadMusicList();
    }
  } catch (error) {
    console.error('批量删除音乐失败:', error);
    ElMessage.error('批量删除失败，请重试');
  }
};

// 处理音频文件选择
const onFileChange = (e) => {
  const file = e.target.files && e.target.files[0];
  if (!file) return;
  // 重置上传状态
  uploadProgress.value = 0;
  selectedFile.value = file;
  selectedFileName.value = file.name;
  // 从文件名自动填充标题（用户可后续编辑）
  const name = file.name.replace(/\.[^/.]+$/, "");
  musicForm.value.title = name.replace(/[_-]+/g, ' ');
  // 计算时长前清空现有值
  musicForm.value.duration = '';
  // 尝试本地读取时长
  computeDurationFromFile(file).then(d => {
    if (d) musicForm.value.duration = d;
  }).catch(() => {});
};

// 处理封面文件选择
const onCoverChange = (e) => {
  const file = e.target.files && e.target.files[0];
  if (!file) return;
  // 重置上传状态
  coverUploadProgress.value = 0;
  selectedCoverFile.value = file;
  selectedCoverFileName.value = file.name;
};

// 上传音频文件
const uploadFile = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件');
    return;
  }
  try {
    uploading.value = true;
    uploadProgress.value = 0;
    const form = new FormData();
    form.append('file', selectedFile.value);
    // 使用底层axios实例获取上传进度
    const res = await requestMethod.postForm('/music/upload', form, {}, {
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && progressEvent.loaded) {
          // 1. 计算进度并限制最大值为 100
          const progress = Math.min(Math.round((progressEvent.loaded * 100) / progressEvent.total), 100);
          // 2. 防抖：只有进度值变化时才更新，避免重复渲染
          if (progress !== uploadProgress.value) {
            uploadProgress.value = progress;
          }
        }
      },
      timeout: 30 * 1000 // 30秒超时
    });
    if (res && res.code === 200 && res.data && res.data.src) {
      // 后端返回src和可能的元数据（标题、艺术家、时长、封面）
      const d = res.data;
      musicForm.value.audio_url = d.src;
      if (d.title) musicForm.value.title = d.title;
      if (d.artist) musicForm.value.artist = d.artist;
      if (d.duration) musicForm.value.duration = d.duration;
      if (d.cover) musicForm.value.cover = d.cover;
      ElMessage.success('上传成功，已填充音频信息');
    } else {
      ElMessage.error(res?.msg || '上传失败');
    }
  } catch (e) {
    console.error('上传失败', e);
    ElMessage.error('上传失败');
  } finally {
    uploading.value = false;
    // 延迟 300ms 重置进度，避免视觉闪烁
    setTimeout(() => {
      uploadProgress.value = 0;
    }, 300);
    // 清除文件输入值以允许重新上传相同文件
    try {
      const fileInput = document.querySelector('input[type="file"].hidden-input');
      if (fileInput) {
        fileInput.value = null;
      }
    } catch (e) {}
    // 清空选中的文件和文件名
    selectedFile.value = null;
    selectedFileName.value = '';
  }
};

// 上传封面文件
const uploadCover = async () => {
  if (!selectedCoverFile.value) {
    ElMessage.warning('请先选择封面文件');
    return;
  }
  try {
    uploadingCover.value = true;
    coverUploadProgress.value = 0;
    const form = new FormData();
    form.append('file', selectedCoverFile.value);
    const res = await requestMethod.postForm('/music/upload_cover', form, {}, {
      onUploadProgress: (ev) => {
        if (ev.total && ev.loaded) {
          // 1. 计算进度并限制最大值为 100
          const progress = Math.min(Math.round((ev.loaded * 100) / ev.total), 100);
          // 2. 防抖：只有进度值变化时才更新，避免重复渲染
          if (progress !== coverUploadProgress.value) {
            coverUploadProgress.value = progress;
          }
        }
      }
    });
    if (res && res.code === 200 && res.data && res.data.cover) {
      musicForm.value.cover = res.data.cover;
      ElMessage.success('封面上传成功');
    } else {
      ElMessage.error(res?.msg || '封面上传失败');
    }
  } catch (e) {
    console.error('封面上传失败', e);
    ElMessage.error('上传封面失败');
  } finally {
    uploadingCover.value = false;
    // 延迟 300ms 重置进度，避免视觉闪烁
    setTimeout(() => {
      coverUploadProgress.value = 0;
    }, 300);
    // 清除文件输入值以允许重新上传相同文件
    try {
      const coverInput = document.querySelector('input[type="file"].hidden-input');
      if (coverInput) {
        coverInput.value = null;
      }
    } catch (e) {}
    // 清空选中的封面文件和文件名
    selectedCoverFile.value = null;
    selectedCoverFileName.value = '';
  }
};

// 计算音频时长
const computeDurationFromFile = (file) => {
  return new Promise((resolve) => {
    try {
      const url = URL.createObjectURL(file);
      const audio = new Audio();
      audio.src = url;
      audio.addEventListener('loadedmetadata', () => {
        const sec = Math.floor(audio.duration || 0);
        URL.revokeObjectURL(url);
        const mm = String(Math.floor(sec / 60)).padStart(2, '0');
        const ss = String(sec % 60).padStart(2, '0');
        resolve(`${mm}:${ss}`);
      });
      audio.addEventListener('error', () => { URL.revokeObjectURL(url); resolve(null); });
    } catch (e) { resolve(null); }
  });
};

// 初始化
onMounted(() => {
  loadMusicList();
});
</script>

<style lang="scss" scoped>
.music-management-view {
  // 管理面板占满不留空
  width: 100%;
  height: 100%;
  padding: 0;
  margin: 0;
  
  .view-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding: 0 20px;
    
    h1 {
      font-size: 24px;
      font-weight: 600;
      margin: 0;
      color: #1f2937;
    }
  }
  
  .search-filter {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    padding: 0 20px;
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .batch-operations {
    display: flex;
    align-items: center;
    margin: 16px 20px;
    padding: 12px;
    background-color: #f3f4f6;
    border-radius: 6px;
    
    span {
      margin-right: 16px;
      font-weight: 500;
    }
  }
  
  .el-table {
    margin: 0 20px;
  }
  
  .pagination {
    margin-top: 20px;
    margin-bottom: 20px;
    padding: 0 20px;
    display: flex;
    justify-content: flex-end;
  }
  
  .music-title {
    display: flex;
    align-items: center;
    
    .music-cover {
      width: 32px;
      height: 32px;
      border-radius: 4px;
      margin-right: 8px;
      object-fit: cover;
    }
  }
  
  .form-hint {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
    margin-bottom: 0;
  }
  
  // 隐藏输入文件
  .hidden-input {
    display: none;
  }
}

// 现代化对话框样式
.modern-music-dialog {
  .dialog-content-wrapper {
    display: flex;
    gap: 30px;
    padding: 20px;
  }
  
  // 左侧上传区域
  .left-section {
    flex: 0 0 300px;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }
  
  // 右侧表单区域
  .right-section {
    flex: 1;
  }
  
  // 上传卡片
  .upload-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    
    &:hover {
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      transform: translateY(-2px);
    }
  }
  
  // 上传区域标题
  .upload-section-title {
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  // 封面上传容器
  .cover-upload-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  // 封面预览
  .cover-preview {
    width: 260px;
    height: 260px;
    border-radius: 12px;
    overflow: hidden;
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px dashed #e5e7eb;
    transition: all 0.3s ease;
    
    &:hover {
      border-color: #409eff;
    }
  }
  
  // 封面图片
  .cover-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  // 封面占位符
  .cover-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    color: #9ca3af;
    
    el-icon {
      font-size: 32px;
    }
    
    span {
      font-size: 14px;
    }
  }
  
  // 音频上传容器
  .audio-upload-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  // 上传控制按钮组
  .upload-controls {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
  }
  
  // 选择按钮
  .select-btn {
    flex: 1;
    min-width: 120px;
  }
  
  // 文件信息显示
  .file-info {
    font-size: 12px;
    color: #606266;
    margin-top: 4px;
  }
  
  // 音频信息
  .audio-info {
    display: flex;
    align-items: center;
    color: #67c23a;
    gap: 6px;
    margin-top: 8px;
    
    el-icon {
      font-size: 14px;
    }
  }
  
  // 上传进度条容器
  .progress-container {
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .progress-bar {
    width: 100%;
  }
  
  .progress-text {
    font-size: 12px;
    color: #606266;
    text-align: right;
  }
  
  // 上传提示
  .upload-hint {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
  
  // 现代化表单
  .modern-form {
    .form-item {
      margin-bottom: 20px;
    }
    
    .el-form-item__label {
      width: 120px;
      text-align: right;
      font-weight: 500;
      color: #4b5563;
      padding-right: 20px;
    }
    
    .el-form-item__content {
      margin-left: 140px !important;
    }
    
    // 表单输入框
    .form-input {
      width: 100%;
      max-width: 450px;
      border-radius: 8px;
      transition: all 0.3s ease;
      
      &:focus {
        box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
      }
    }
    
    // 表单选择框
    .form-select {
      width: 100%;
      max-width: 450px;
      border-radius: 8px;
    }
    
    // 滑块容器
    .slider-container {
      display: flex;
      align-items: center;
      gap: 16px;
      width: 100%;
      max-width: 450px;
    }
    
    // 表单滑块
    .form-slider {
      flex: 1;
    }
    
    // 场景选择
    .scenes-checkbox-group {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }
    
    // 滑块值
    .slider-value {
      font-size: 14px;
      font-weight: 500;
      color: #4b5563;
      min-width: 50px;
    }
    
    // 表单文本域
    .form-textarea {
      width: 100%;
      max-width: 450px;
      min-height: 120px;
      border-radius: 8px;
    }
  }
  
  // 对话框底部
  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 20px;
    border-top: 1px solid #e5e7eb;
  }
  
  // 取消按钮
  .cancel-btn {
    border-radius: 8px;
  }
  
  // 保存按钮
  .save-btn {
    border-radius: 8px;
  }
}

// 自定义滑块样式
:deep(.el-slider__runway) {
  height: 6px;
  border-radius: 3px;
  background-color: #f0f0f0;
}

:deep(.el-slider__bar) {
  height: 6px;
  border-radius: 3px;
  background-color: #409eff;
}

:deep(.el-slider__button) {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: #409eff;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }
}

// 自定义标签样式
:deep(.el-tag) {
  margin-right: 0;
}

// 确保对话框标题居中
:deep(.el-dialog__header) {
  text-align: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

// 确保表单输入框宽度一致
:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  width: 100%;
}

// 调整文本域高度
:deep(.el-textarea__wrapper) {
  width: 100%;
  min-height: 120px;
}

// 响应式设计
@media (max-width: 1024px) {
  .modern-music-dialog {
    .dialog-content-wrapper {
      flex-direction: column;
    }
    
    .left-section {
      flex: 1;
      flex-direction: row;
      flex-wrap: wrap;
      gap: 20px;
    }
    
    .upload-card {
      flex: 1;
      min-width: 280px;
    }
  }
}

@media (max-width: 768px) {
  .music-management-view {
    .view-header,
    .search-filter,
    .batch-operations,
    .el-table,
    .pagination {
      padding: 0 12px;
      margin: 0 12px;
    }
  }
  
  .modern-music-dialog {
    width: 95% !important;
    
    .left-section {
      flex-direction: column;
    }
    
    .cover-preview {
      width: 100%;
      height: 200px;
    }
    
    .modern-form {
      .el-form-item__label {
        width: 100px;
        padding-right: 12px;
      }
      
      .el-form-item__content {
        margin-left: 112px !important;
      }
    }
  }
}
</style>
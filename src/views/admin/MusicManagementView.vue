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
      <el-select
        v-model="filterMood"
        placeholder="筛选音乐情绪"
        clearable
        style="width: 160px;"
      >
        <el-option
          v-for="mood in musicMoods"
          :key="mood"
          :label="mood"
          :value="mood"
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
      <el-table-column prop="duration" label="时长" width="100">
        <template #default="scope">
          {{ formatDuration(scope.row.duration) }}
        </template>
      </el-table-column>
      <el-table-column prop="music_type" label="类型" width="120" />
      <el-table-column prop="mood" label="情绪" width="120" />
      <el-table-column prop="play_count" label="播放量" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
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
      width="600px"
    >
      <el-form :model="musicForm" :rules="musicFormRules" ref="musicFormRef">
        <el-form-item label="标题" prop="title">
          <el-input v-model="musicForm.title" placeholder="请输入音乐标题" />
        </el-form-item>
        <el-form-item label="艺术家" prop="artist">
          <el-input v-model="musicForm.artist" placeholder="请输入艺术家" />
        </el-form-item>
        <el-form-item label="时长" prop="duration">
          <el-input-number v-model="musicForm.duration" :min="1" placeholder="请输入时长（秒）" />
        </el-form-item>
        <el-form-item label="音乐类型" prop="music_type">
          <el-select v-model="musicForm.music_type" placeholder="请选择音乐类型">
            <el-option
              v-for="type in musicTypes"
              :key="type"
              :label="type"
              :value="type"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="音乐情绪" prop="mood">
          <el-select v-model="musicForm.mood" placeholder="请选择音乐情绪">
            <el-option
              v-for="mood in musicMoods"
              :key="mood"
              :label="mood"
              :value="mood"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="musicForm.description"
            type="textarea"
            placeholder="请输入音乐描述"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="封面">
          <el-upload
            class="avatar-uploader"
            action="/admin/upload"
            :show-file-list="false"
            :on-success="handleCoverUploadSuccess"
            :before-upload="beforeCoverUpload"
          >
            <img
              v-if="musicForm.cover"
              :src="musicForm.cover"
              class="avatar"
              alt="封面"
            />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="音频文件">
          <el-upload
            class="audio-uploader"
            action="/admin/upload"
            :show-file-list="false"
            :on-success="handleAudioUploadSuccess"
            :before-upload="beforeAudioUpload"
          >
            <el-button size="small" type="primary">
              <el-icon><Upload /></el-icon>
              <span>{{ musicForm.audio_url ? '更换音频' : '上传音频' }}</span>
            </el-button>
          </el-upload>
          <div v-if="musicForm.audio_url" class="audio-info">
            <el-icon><Check /></el-icon>
            <span>音频已上传</span>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveMusic">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { Plus, Search, Delete, Upload, Check } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { useAdminStore } from '@/stores/adminStore';

const adminStore = useAdminStore();

// 数据状态
const loading = ref(false);
const musicList = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const searchKeyword = ref('');
const filterType = ref('');
const filterMood = ref('');
const selectedMusic = ref([]);

// 对话框状态
const dialogVisible = ref(false);
const dialogTitle = ref('添加音乐');
const musicForm = ref({
  id: null,
  title: '',
  artist: '',
  duration: 0,
  cover: '',
  audio_url: '',
  music_type: '',
  mood: '',
  description: ''
});
const musicFormRef = ref(null);

// 表单验证规则
const musicFormRules = reactive({
  title: [
    { required: true, message: '请输入音乐标题', trigger: 'blur' }
  ],
  artist: [
    { required: true, message: '请输入艺术家', trigger: 'blur' }
  ],
  duration: [
    { required: true, message: '请输入时长', trigger: 'blur' }
  ],
  music_type: [
    { required: true, message: '请选择音乐类型', trigger: 'change' }
  ],
  mood: [
    { required: true, message: '请选择音乐情绪', trigger: 'change' }
  ],
  audio_url: [
    { required: true, message: '请上传音频文件', trigger: 'blur' }
  ]
});

// 音乐类型和情绪选项
const musicTypes = ['classical', 'jazz', 'pop', 'rock', 'electronic', 'natural', 'ambient'];
const musicMoods = ['calm', 'energetic', 'happy', 'sad', 'relaxing', 'motivating', 'peaceful'];

// 加载音乐列表
const loadMusicList = async () => {
  try {
    loading.value = true;
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchKeyword.value,
      music_type: filterType.value,
      mood: filterMood.value
    };
    const response = await adminStore.getMusicList(params);
    musicList.value = response.items || [];
    total.value = response.pagination?.total || 0;
  } catch (error) {
    console.error('加载音乐列表失败:', error);
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
    duration: 0,
    cover: '',
    audio_url: '',
    music_type: '',
    mood: '',
    description: ''
  };
  dialogTitle.value = '添加音乐';
  dialogVisible.value = true;
};

// 处理编辑音乐
const handleEditMusic = (music) => {
  musicForm.value = {
    id: music.id,
    title: music.title,
    artist: music.artist,
    duration: music.duration,
    cover: music.cover || '',
    audio_url: music.audio_url || '',
    music_type: music.music_type,
    mood: music.mood,
    description: music.description || ''
  };
  dialogTitle.value = '编辑音乐';
  dialogVisible.value = true;
};

// 处理保存音乐
const handleSaveMusic = async () => {
  if (!musicFormRef.value) return;
  
  try {
    await musicFormRef.value.validate();
    
    if (musicForm.value.id) {
      // 编辑音乐
      await adminStore.updateMusic(musicForm.value.id, musicForm.value);
      ElMessage.success('音乐更新成功');
    } else {
      // 添加音乐
      await adminStore.createMusic(musicForm.value);
      ElMessage.success('音乐添加成功');
    }
    
    dialogVisible.value = false;
    loadMusicList();
  } catch (error) {
    console.error('保存音乐失败:', error);
    ElMessage.error('保存失败，请重试');
  }
};

// 处理删除音乐
const handleDeleteMusic = async (musicId) => {
  try {
    await adminStore.deleteMusic(musicId);
    ElMessage.success('音乐删除成功');
    loadMusicList();
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
    await adminStore.batchDeleteMusic(musicIds);
    ElMessage.success(`成功删除 ${selectedMusic.value.length} 条音乐`);
    selectedMusic.value = [];
    loadMusicList();
  } catch (error) {
    console.error('批量删除音乐失败:', error);
    ElMessage.error('批量删除失败，请重试');
  }
};

// 封面上传前校验
const beforeCoverUpload = (file) => {
  const isImage = file.type.startsWith('image/');
  const isLt2M = file.size / 1024 / 1024 < 2;
  
  if (!isImage) {
    ElMessage.error('只能上传图片文件！');
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB！');
  }
  
  return isImage && isLt2M;
};

// 音频上传前校验
const beforeAudioUpload = (file) => {
  const isAudio = file.type.startsWith('audio/');
  const isLt10M = file.size / 1024 / 1024 < 10;
  
  if (!isAudio) {
    ElMessage.error('只能上传音频文件！');
  }
  if (!isLt10M) {
    ElMessage.error('音频大小不能超过 10MB！');
  }
  
  return isAudio && isLt10M;
};

// 封面上传成功
const handleCoverUploadSuccess = (response) => {
  if (response.code === 200) {
    musicForm.value.cover = response.data.file_url;
    ElMessage.success('封面上传成功');
  } else {
    ElMessage.error('封面上传失败');
  }
};

// 音频上传成功
const handleAudioUploadSuccess = (response) => {
  if (response.code === 200) {
    musicForm.value.audio_url = response.data.file_url;
    ElMessage.success('音频上传成功');
  } else {
    ElMessage.error('音频上传失败');
  }
};

// 格式化时长
const formatDuration = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

// 初始化
onMounted(() => {
  loadMusicList();
});
</script>

<style lang="scss" scoped>
.music-management-view {
  .view-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    
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
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .batch-operations {
    display: flex;
    align-items: center;
    margin: 16px 0;
    padding: 12px;
    background-color: #f3f4f6;
    border-radius: 6px;
    
    span {
      margin-right: 16px;
      font-weight: 500;
    }
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
  
  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
  
  .avatar-uploader {
    width: 120px;
    height: 120px;
    border-radius: 8px;
    overflow: hidden;
    
    .avatar {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .avatar-uploader-icon {
      width: 120px;
      height: 120px;
      line-height: 120px;
      font-size: 24px;
      color: #999;
      background-color: #f0f0f0;
    }
  }
  
  .audio-info {
    margin-top: 12px;
    display: flex;
    align-items: center;
    color: #67c23a;
    
    el-icon {
      margin-right: 4px;
    }
  }
}
</style>

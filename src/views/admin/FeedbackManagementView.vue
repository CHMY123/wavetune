<template>
  <div class="feedback-management-view">
    <div class="view-header">
      <h1>反馈管理</h1>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="search-filter">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索反馈内容或用户名"
        clearable
        prefix-icon="Search"
        style="width: 300px; margin-right: 16px;"
      />
      <el-select
        v-model="filterType"
        placeholder="筛选反馈类型"
        clearable
        style="width: 160px; margin-right: 16px;"
      >
        <el-option label="脑疲劳检测准确性" value="accuracy" />
        <el-option label="轻音乐推荐效果" value="music" />
        <el-option label="系统功能建议" value="function" />
      </el-select>
      <el-select
        v-model="filterStatus"
        placeholder="筛选反馈状态"
        clearable
        style="width: 160px;"
      >
        <el-option label="待处理" value="pending" />
        <el-option label="已处理" value="processed" />
        <el-option label="已回复" value="replied" />
      </el-select>
      <el-button
        type="default"
        @click="handleSearch"
        style="margin-left: 16px;"
      >
        搜索
      </el-button>
    </div>
    
    <!-- 反馈列表 -->
    <el-table
      v-loading="loading"
      :data="feedbackList"
      style="width: 100%; margin-top: 16px;"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户" min-width="120">
        <template #default="scope">
          <div class="user-info">
            <el-avatar :size="24" :src="scope.row.avatar || '/static/avatar/default.jpg'">
              {{ scope.row.username?.charAt(0) || 'U' }}
            </el-avatar>
            <span>{{ scope.row.username || '未知用户' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="feedback_type" label="类型" width="180">
        <template #default="scope">
          <el-tag :type="getTypeTagType(scope.row.feedback_type)">
            {{ getTypeLabel(scope.row.feedback_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="content" label="反馈内容" min-width="300">
        <template #default="scope">
          <div class="feedback-content">
            {{ scope.row.content }}
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="scope">
          <el-tag :type="getStatusTagType(scope.row.status)">
            {{ getStatusLabel(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="reply" label="回复" min-width="200">
        <template #default="scope">
          <div class="feedback-reply" v-if="scope.row.reply">
            {{ scope.row.reply }}
          </div>
          <span v-else class="no-reply">未回复</span>
        </template>
      </el-table-column>
      <el-table-column prop="submit_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.submit_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button type="primary" size="small" @click="handleReplyFeedback(scope.row)" style="margin-right: 8px;">
            回复
          </el-button>
          <el-button type="success" size="small" @click="handleMarkProcessed(scope.row.id)">
            标记处理
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
    
    <!-- 回复反馈对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="feedbackForm" :rules="feedbackFormRules" ref="feedbackFormRef">
        <el-form-item label="反馈用户">
          <el-input v-model="feedbackForm.username" disabled />
        </el-form-item>
        <el-form-item label="反馈类型">
          <el-input :value="getTypeLabel(feedbackForm.type)" disabled />
        </el-form-item>
        <el-form-item label="反馈内容">
          <el-input
            v-model="feedbackForm.content"
            type="textarea"
            :rows="4"
            disabled
          />
        </el-form-item>
        <el-form-item label="反馈状态" prop="status">
          <el-select v-model="feedbackForm.status">
            <el-option label="待处理" value="pending" />
            <el-option label="已处理" value="processed" />
            <el-option label="已回复" value="replied" />
          </el-select>
        </el-form-item>
        <el-form-item label="回复内容" prop="reply">
          <el-input
            v-model="feedbackForm.reply"
            type="textarea"
            :rows="4"
            placeholder="请输入回复内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveFeedback">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { Search } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { useAdminStore } from '@/stores/adminStore';

const adminStore = useAdminStore();

// 数据状态
const loading = ref(false);
const feedbackList = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const searchKeyword = ref('');
const filterType = ref('');
const filterStatus = ref('');

// 对话框状态
const dialogVisible = ref(false);
const dialogTitle = ref('回复反馈');
const feedbackForm = ref({
  id: null,
  username: '',
  type: '',
  content: '',
  status: 'pending',
  reply: ''
});
const feedbackFormRef = ref(null);

// 表单验证规则
const feedbackFormRules = reactive({
  status: [
    { required: true, message: '请选择反馈状态', trigger: 'change' }
  ],
  reply: [
    { required: true, message: '请输入回复内容', trigger: 'blur' }
  ]
});

// 加载反馈列表
const loadFeedbackList = async () => {
  try {
    loading.value = true;
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchKeyword.value,
      type: filterType.value,
      status: filterStatus.value
    };
    const response = await adminStore.getFeedbackList(params);
    feedbackList.value = response.items || [];
    total.value = response.pagination?.total || 0;
  } catch (error) {
    console.error('加载反馈列表失败:', error);
  } finally {
    loading.value = false;
  }
};

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1;
  loadFeedbackList();
};

// 处理分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size;
  loadFeedbackList();
};

// 处理当前页变化
const handleCurrentChange = (page) => {
  currentPage.value = page;
  loadFeedbackList();
};

// 处理回复反馈
const handleReplyFeedback = (feedback) => {
  feedbackForm.value = {
    id: feedback.id,
    username: feedback.username || '',
    type: feedback.feedback_type || feedback.type || '',
    content: feedback.content || '',
    status: feedback.status || 'pending',
    reply: feedback.reply || ''
  };
  dialogTitle.value = '回复反馈';
  dialogVisible.value = true;
};

// 处理保存反馈
const handleSaveFeedback = async () => {
  if (!feedbackFormRef.value) return;
  
  try {
    await feedbackFormRef.value.validate();
    
    await adminStore.updateFeedback(feedbackForm.value.id, {
      status: feedbackForm.value.status,
      reply: feedbackForm.value.reply
    });
    ElMessage.success('反馈回复成功');
    dialogVisible.value = false;
    loadFeedbackList();
  } catch (error) {
    console.error('保存反馈失败:', error);
    ElMessage.error('保存失败，请重试');
  }
};

// 处理标记为已处理
const handleMarkProcessed = async (feedbackId) => {
  try {
    await adminStore.updateFeedback(feedbackId, {
      status: 'processed'
    });
    ElMessage.success('反馈已标记为已处理');
    loadFeedbackList();
  } catch (error) {
    console.error('标记反馈失败:', error);
    ElMessage.error('操作失败，请重试');
  }
};

// 获取类型标签类型
const getTypeTagType = (type) => {
  switch (type) {
    case 'accuracy':
      return 'warning';
    case 'music':
      return 'primary';
    case 'function':
      return 'info';
    case 'suggestion':
      return 'primary';
    case 'bug':
      return 'danger';
    case 'other':
      return 'info';
    default:
      return 'default';
  }
};

// 获取类型标签文本
const getTypeLabel = (type) => {
  switch (type) {
    case 'accuracy':
      return '脑疲劳检测准确性';
    case 'music':
      return '轻音乐推荐效果';
    case 'function':
      return '系统功能建议';
    case 'suggestion':
      return '功能建议';
    case 'bug':
      return 'bug报告';
    case 'other':
      return '其他';
    default:
      return '未知类型';
  }
};

// 获取状态标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case 'pending':
      return 'warning';
    case 'processed':
      return 'success';
    case 'replied':
      return 'info';
    default:
      return 'default';
  }
};

// 获取状态标签文本
const getStatusLabel = (status) => {
  switch (status) {
    case 'pending':
      return '待处理';
    case 'processed':
      return '已处理';
    case 'replied':
      return '已回复';
    default:
      return '未知状态';
  }
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

// 初始化
onMounted(() => {
  loadFeedbackList();
});
</script>

<style lang="scss" scoped>
.feedback-management-view {
  .view-header {
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
  
  .user-info {
    display: flex;
    align-items: center;
    
    el-avatar {
      margin-right: 8px;
    }
  }
  
  .feedback-content {
    line-height: 1.4;
    word-break: break-word;
  }
  
  .feedback-reply {
    line-height: 1.4;
    word-break: break-word;
    color: #6b7280;
  }
  
  .no-reply {
    color: #9ca3af;
    font-style: italic;
  }
  
  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>

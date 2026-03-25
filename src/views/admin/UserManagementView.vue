<template>
  <div class="user-management-view">
    <div class="view-header">
      <h1>用户管理</h1>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="search-filter">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索用户名、学号或邮箱"
        clearable
        prefix-icon="Search"
        style="width: 300px; margin-right: 16px;"
      />
      <el-select
        v-model="filterRole"
        placeholder="筛选用户角色"
        clearable
        style="width: 160px; margin-right: 16px;"
      >
        <el-option label="管理员" value="admin" />
        <el-option label="普通用户" value="user" />
      </el-select>
      <el-select
        v-model="filterStatus"
        placeholder="筛选用户状态"
        clearable
        style="width: 160px;"
      >
        <el-option label="激活" :value="true" />
        <el-option label="禁用" :value="false" />
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
    <div class="batch-operations" v-if="selectedUsers.length > 0">
      <span>已选择 {{ selectedUsers.length }} 项</span>
      <el-select
        v-model="batchAction"
        placeholder="批量操作"
        style="margin: 0 16px;"
      >
        <el-option label="设置为管理员" value="set_admin" />
        <el-option label="设置为普通用户" value="set_user" />
        <el-option label="激活用户" value="activate" />
        <el-option label="禁用用户" value="deactivate" />
      </el-select>
      <el-button type="primary" @click="handleBatchAction">
        执行操作
      </el-button>
    </div>
    
    <!-- 用户列表 -->
    <el-table
      v-loading="loading"
      :data="userList"
      style="width: 100%; margin-top: 16px;"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" min-width="120">
        <template #default="scope">
          <div class="user-info">
            <el-avatar :size="32" :src="scope.row.avatar || '/static/avatar/default.jpg'">
              {{ scope.row.username?.charAt(0) || 'U' }}
            </el-avatar>
            <span>{{ scope.row.username }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="student_id" label="学号" min-width="120" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column prop="phone" label="手机号" min-width="120" />
      <el-table-column prop="role" label="角色" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.role === 'admin' ? 'primary' : 'success'">
            {{ scope.row.role === 'admin' ? '管理员' : '用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
            {{ scope.row.is_active ? '激活' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="detection_count" label="检测次数" width="100" />
      <el-table-column prop="intervention_count" label="干预次数" width="100" />
      <el-table-column prop="last_login_time" label="最后登录" width="180">
        <template #default="scope">
          {{ scope.row.last_login_time ? formatDate(scope.row.last_login_time) : '从未登录' }}
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="注册时间" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button type="primary" size="small" @click="handleEditUser(scope.row)" style="margin-right: 8px;">
            编辑
          </el-button>
          <el-button
            :type="scope.row.is_active ? 'danger' : 'success'"
            size="small"
            @click="handleToggleStatus(scope.row)"
          >
            {{ scope.row.is_active ? '禁用' : '激活' }}
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
    
    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="userForm" :rules="userFormRules" ref="userFormRef">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="学号" prop="student_id">
          <el-input v-model="userForm.student_id" placeholder="请输入学号" disabled />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" type="email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="用户角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择用户角色">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item label="用户状态" prop="is_active">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
        <el-form-item label="头像">
          <el-upload
            class="avatar-uploader"
            action="/admin/upload"
            :show-file-list="false"
            :on-success="handleAvatarUploadSuccess"
            :before-upload="beforeAvatarUpload"
          >
            <el-avatar
              v-if="userForm.avatar"
              :size="120"
              :src="userForm.avatar"
            >
              {{ userForm.username?.charAt(0) || 'U' }}
            </el-avatar>
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveUser">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { Search, Plus } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { useAdminStore } from '@/stores/adminStore';

const adminStore = useAdminStore();

// 数据状态
const loading = ref(false);
const userList = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const searchKeyword = ref('');
const filterRole = ref('');
const filterStatus = ref(null);
const selectedUsers = ref([]);
const batchAction = ref('');

// 对话框状态
const dialogVisible = ref(false);
const dialogTitle = ref('编辑用户');
const userForm = ref({
  id: null,
  username: '',
  student_id: '',
  email: '',
  phone: '',
  avatar: '',
  role: 'user',
  is_active: true
});
const userFormRef = ref(null);

// 表单验证规则
const userFormRules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择用户角色', trigger: 'change' }
  ]
});

// 加载用户列表
const loadUserList = async () => {
  try {
    loading.value = true;
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchKeyword.value,
      role: filterRole.value,
      is_active: filterStatus.value
    };
    const response = await adminStore.getUserList(params);
    userList.value = response.items || [];
    total.value = response.pagination?.total || 0;
  } catch (error) {
    console.error('加载用户列表失败:', error);
  } finally {
    loading.value = false;
  }
};

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1;
  loadUserList();
};

// 处理分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size;
  loadUserList();
};

// 处理当前页变化
const handleCurrentChange = (page) => {
  currentPage.value = page;
  loadUserList();
};

// 处理选择变化
const handleSelectionChange = (val) => {
  selectedUsers.value = val;
};

// 处理编辑用户
const handleEditUser = (user) => {
  userForm.value = {
    id: user.id,
    username: user.username,
    student_id: user.student_id,
    email: user.email || '',
    phone: user.phone || '',
    avatar: user.avatar || '',
    role: user.role,
    is_active: user.is_active
  };
  dialogTitle.value = '编辑用户';
  dialogVisible.value = true;
};

// 处理保存用户
const handleSaveUser = async () => {
  if (!userFormRef.value) return;
  
  try {
    await userFormRef.value.validate();
    
    await adminStore.updateUser(userForm.value.id, userForm.value);
    ElMessage.success('用户信息更新成功');
    dialogVisible.value = false;
    loadUserList();
  } catch (error) {
    console.error('保存用户失败:', error);
    ElMessage.error('保存失败，请重试');
  }
};

// 处理切换用户状态
const handleToggleStatus = async (user) => {
  try {
    await adminStore.updateUser(user.id, {
      is_active: !user.is_active
    });
    ElMessage.success(`用户已${!user.is_active ? '激活' : '禁用'}`);
    loadUserList();
  } catch (error) {
    console.error('切换用户状态失败:', error);
    ElMessage.error('操作失败，请重试');
  }
};

// 处理批量操作
const handleBatchAction = async () => {
  if (selectedUsers.value.length === 0 || !batchAction.value) return;
  
  try {
    const userIds = selectedUsers.value.map(user => user.id);
    let updateData = {};
    
    switch (batchAction.value) {
      case 'set_admin':
        updateData = { role: 'admin' };
        break;
      case 'set_user':
        updateData = { role: 'user' };
        break;
      case 'activate':
        updateData = { is_active: true };
        break;
      case 'deactivate':
        updateData = { is_active: false };
        break;
    }
    
    // 这里需要实现批量更新用户的方法
    // 由于后端可能没有提供批量更新接口，我们可以逐个更新
    for (const userId of userIds) {
      await adminStore.updateUser(userId, updateData);
    }
    
    ElMessage.success(`成功更新 ${selectedUsers.value.length} 个用户`);
    selectedUsers.value = [];
    batchAction.value = '';
    loadUserList();
  } catch (error) {
    console.error('批量操作失败:', error);
    ElMessage.error('批量操作失败，请重试');
  }
};

// 头像上传前校验
const beforeAvatarUpload = (file) => {
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

// 头像上传成功
const handleAvatarUploadSuccess = (response) => {
  if (response.code === 200) {
    userForm.value.avatar = response.data.file_url;
    ElMessage.success('头像上传成功');
  } else {
    ElMessage.error('头像上传失败');
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
  loadUserList();
});
</script>

<style lang="scss" scoped>
.user-management-view {
  .view-header {
    margin-bottom: 24px;
    
    h1 {
      font-size: 24px;
      font-weight: 600;
      margin: 0;
      color: #1f2937;
      
      // 深色主题样式
      :global(.theme-dark) & {
        color: #f3f4f6;
      }
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
    
    // 深色主题样式
    :global(.theme-dark) & {
      background-color: #374151;
      
      span {
        color: #d1d5db;
      }
    }
    
    span {
      margin-right: 16px;
      font-weight: 500;
    }
  }
  
  .user-info {
    display: flex;
    align-items: center;
    
    el-avatar {
      margin-right: 8px;
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
    
    .avatar-uploader-icon {
      width: 120px;
      height: 120px;
      line-height: 120px;
      font-size: 24px;
      color: #999;
      background-color: #f0f0f0;
      
      // 深色主题样式
      :global(.theme-dark) & {
        color: #6b7280;
        background-color: #374151;
      }
    }
  }
}
</style>

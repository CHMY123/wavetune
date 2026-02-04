<template>
  <div class="system-config-view">
    <div class="view-header">
      <h1>系统配置</h1>
      <el-button type="primary" @click="handleAddConfig">
        <el-icon><Plus /></el-icon>
        <span>添加配置</span>
      </el-button>
    </div>
    
    <!-- 配置列表 -->
    <el-table
      v-loading="loading"
      :data="configList"
      style="width: 100%; margin-top: 16px;"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="config_key" label="配置键" min-width="200" />
      <el-table-column prop="config_value" label="配置值" min-width="300">
        <template #default="scope">
          <div class="config-value">
            {{ scope.row.config_value }}
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="配置描述" min-width="250">
        <template #default="scope">
          <div class="config-description">
            {{ scope.row.description || '无描述' }}
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="更新时间" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.updated_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-button type="primary" size="small" @click="handleEditConfig(scope.row)">
            编辑
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 添加/编辑配置对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="configForm" :rules="configFormRules" ref="configFormRef">
        <el-form-item label="配置键" prop="config_key">
          <el-input v-model="configForm.config_key" placeholder="请输入配置键" :disabled="!!configForm.id" />
        </el-form-item>
        <el-form-item label="配置值" prop="config_value">
          <el-input
            v-model="configForm.config_value"
            type="textarea"
            :rows="4"
            placeholder="请输入配置值"
          />
        </el-form-item>
        <el-form-item label="配置描述" prop="description">
          <el-input
            v-model="configForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入配置描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveConfig">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { Plus } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { useAdminStore } from '@/stores/adminStore';

const adminStore = useAdminStore();

// 数据状态
const loading = ref(false);
const configList = ref([]);

// 对话框状态
const dialogVisible = ref(false);
const dialogTitle = ref('添加配置');
const configForm = ref({
  id: null,
  config_key: '',
  config_value: '',
  description: ''
});
const configFormRef = ref(null);

// 表单验证规则
const configFormRules = reactive({
  config_key: [
    { required: true, message: '请输入配置键', trigger: 'blur' }
  ],
  config_value: [
    { required: true, message: '请输入配置值', trigger: 'blur' }
  ]
});

// 加载配置列表
const loadConfigList = async () => {
  try {
    loading.value = true;
    const configs = await adminStore.getSystemConfig();
    configList.value = configs;
  } catch (error) {
    console.error('加载配置列表失败:', error);
  } finally {
    loading.value = false;
  }
};

// 处理添加配置
const handleAddConfig = () => {
  configForm.value = {
    id: null,
    config_key: '',
    config_value: '',
    description: ''
  };
  dialogTitle.value = '添加配置';
  dialogVisible.value = true;
};

// 处理编辑配置
const handleEditConfig = (config) => {
  configForm.value = {
    id: config.id,
    config_key: config.config_key,
    config_value: config.config_value,
    description: config.description || ''
  };
  dialogTitle.value = '编辑配置';
  dialogVisible.value = true;
};

// 处理保存配置
const handleSaveConfig = async () => {
  if (!configFormRef.value) return;
  
  try {
    await configFormRef.value.validate();
    
    await adminStore.updateSystemConfig({
      config_key: configForm.value.config_key,
      config_value: configForm.value.config_value,
      description: configForm.value.description
    });
    
    ElMessage.success('配置保存成功');
    dialogVisible.value = false;
    loadConfigList();
  } catch (error) {
    console.error('保存配置失败:', error);
    ElMessage.error('保存失败，请重试');
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
  loadConfigList();
});
</script>

<style lang="scss" scoped>
.system-config-view {
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
  
  .config-value {
    line-height: 1.4;
    word-break: break-word;
  }
  
  .config-description {
    line-height: 1.4;
    word-break: break-word;
    color: #6b7280;
  }
}
</style>

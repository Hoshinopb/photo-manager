<template>
  <div class="admin-container">
    <el-card class="header-card">
      <div class="header-content">
        <h2>
          <el-icon><Setting /></el-icon>
          管理员控制台
        </h2>
        <el-tag type="danger">仅管理员可见</el-tag>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="总图片数" :value="stats.total_images">
            <template #prefix><el-icon><Picture /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="公开图片" :value="stats.public_images">
            <template #prefix><el-icon><View /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="私有图片" :value="stats.private_images">
            <template #prefix><el-icon><Hide /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="注册用户" :value="stats.total_users">
            <template #prefix><el-icon><User /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 管理标签页 -->
    <el-tabs v-model="activeTab" class="admin-tabs">
      <!-- 图片管理标签页 -->
      <el-tab-pane label="图片管理" name="images">
        <!-- 筛选栏 -->
        <el-card class="filter-card">
          <el-row :gutter="16" align="middle">
            <el-col :xs="24" :sm="8" :md="6">
              <el-input
                v-model="filters.search"
                placeholder="搜索文件名"
                clearable
                @keyup.enter="fetchImages"
              >
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </el-col>
            <el-col :xs="12" :sm="8" :md="5">
              <el-select v-model="filters.owner" placeholder="选择用户" clearable filterable @change="fetchImages">
                <el-option
                  v-for="user in users"
                  :key="user.id"
                  :label="`${user.username} (${user.image_count})`"
                  :value="user.id"
                />
              </el-select>
            </el-col>
            <el-col :xs="12" :sm="8" :md="4">
              <el-select v-model="filters.is_public" placeholder="公开状态" clearable @change="fetchImages">
                <el-option label="公开" value="true" />
                <el-option label="私有" value="false" />
              </el-select>
            </el-col>
            <el-col :xs="12" :sm="8" :md="4">
              <el-select v-model="filters.ordering" @change="fetchImages">
                <el-option label="最新上传" value="-upload_time" />
                <el-option label="最早上传" value="upload_time" />
                <el-option label="按用户名" value="owner__username" />
              </el-select>
            </el-col>
            <el-col :xs="12" :sm="8" :md="5">
              <el-button type="primary" @click="fetchImages">
                <el-icon><Search /></el-icon> 搜索
              </el-button>
              <el-button @click="resetFilters">重置</el-button>
            </el-col>
          </el-row>
        </el-card>

        <!-- 批量操作 -->
        <el-card v-if="selectedImages.length > 0" class="batch-card">
          <el-alert type="info" :closable="false">
            <template #title>
              已选择 {{ selectedImages.length }} 张图片
              <el-popconfirm
                title="确定批量删除选中的图片？"
                @confirm="batchDelete"
              >
                <template #reference>
                  <el-button type="danger" size="small" style="margin-left: 16px">
                    <el-icon><Delete /></el-icon> 批量删除
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-alert>
        </el-card>

        <!-- 图片列表 -->
        <el-card class="table-card">
          <el-table
            v-loading="loading"
            :data="images"
            style="width: 100%"
            stripe
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="45" />
            
            <el-table-column label="预览" width="80">
              <template #default="{ row }">
                <el-image
                  style="width: 50px; height: 50px"
                  :src="row.thumbnail_url || row.file_url"
                  :preview-src-list="[row.file_url]"
                  fit="cover"
                  preview-teleported
                >
                  <template #error>
                    <div class="image-error">
                      <el-icon><Picture /></el-icon>
                    </div>
                  </template>
                </el-image>
              </template>
            </el-table-column>
            
            <el-table-column prop="filename" label="文件名" min-width="140" show-overflow-tooltip />
            
            <el-table-column prop="owner_username" label="所有者" width="110">
              <template #default="{ row }">
                <el-tag size="small">{{ row.owner_username }}</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="尺寸" width="110">
              <template #default="{ row }">
                <span v-if="row.width && row.height">{{ row.width }}×{{ row.height }}</span>
                <span v-else class="text-muted">-</span>
              </template>
            </el-table-column>
            
            <el-table-column label="大小" width="90">
              <template #default="{ row }">{{ formatFileSize(row.size) }}</template>
            </el-table-column>
            
            <el-table-column label="上传时间" width="155">
              <template #default="{ row }">{{ formatDate(row.upload_time) }}</template>
            </el-table-column>
            
            <el-table-column label="公开" width="70" align="center">
              <template #default="{ row }">
                <el-switch
                  v-model="row.is_public"
                  @change="togglePublic(row)"
                />
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="140" fixed="right" align="center">
              <template #default="{ row }">
                <el-button-group size="small">
                  <el-button type="primary" @click="viewDetail(row)">
                    <el-icon><View /></el-icon>
                  </el-button>
                  <el-popconfirm title="确定删除此图片？" @confirm="handleDelete(row)">
                    <template #reference>
                      <el-button type="danger">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </template>
                  </el-popconfirm>
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 空状态 -->
          <el-empty v-if="!loading && images.length === 0" description="暂无图片" />
        </el-card>

        <!-- 用户排行 -->
        <el-card class="rank-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Trophy /></el-icon> 上传排行 Top 10</span>
            </div>
          </template>
          <el-table :data="stats.top_users || []" size="small">
            <el-table-column type="index" width="50" label="排名" />
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="image_count" label="图片数" width="100">
              <template #default="{ row }">
                <el-tag type="success">{{ row.image_count }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 用户管理标签页 (仅超级管理员可见) -->
      <el-tab-pane v-if="userStore.user?.is_superuser" label="用户管理" name="users">
        <el-card class="filter-card">
          <el-row :gutter="16" align="middle">
            <el-col :xs="16" :sm="8" :md="6">
              <el-input
                v-model="userSearch"
                placeholder="搜索用户名"
                clearable
                @clear="fetchAllUsers"
                @keyup.enter="fetchAllUsers"
              >
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </el-col>
            <el-col :xs="8" :sm="4">
              <el-button type="primary" @click="fetchAllUsers">
                <el-icon><Search /></el-icon> 搜索
              </el-button>
            </el-col>
          </el-row>
        </el-card>

        <el-card class="table-card">
          <el-table
            v-loading="usersLoading"
            :data="allUsers"
            style="width: 100%"
            stripe
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" min-width="120" />
            <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
            <el-table-column label="图片数" width="100">
              <template #default="{ row }">
                <el-tag type="info">{{ row.image_count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="角色" width="120">
              <template #default="{ row }">
                <el-tag v-if="row.is_superuser" type="danger" effect="dark">超级管理员</el-tag>
                <el-tag v-else-if="row.is_staff" type="warning" effect="dark">管理员</el-tag>
                <el-tag v-else type="info">普通用户</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                  {{ row.is_active ? '正常' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="!row.is_superuser"
                  :type="row.is_staff ? 'warning' : 'primary'"
                  size="small"
                  @click="toggleStaff(row)"
                  :loading="row.loading"
                >
                  {{ row.is_staff ? '取消管理员' : '设为管理员' }}
                </el-button>
                <el-tag v-else type="info" size="small">不可修改</el-tag>
              </template>
            </el-table-column>
          </el-table>
          
          <el-empty v-if="!usersLoading && allUsers.length === 0" description="暂无用户" />
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Setting, Picture, View, Hide, User, Search, Delete, Trophy
} from '@element-plus/icons-vue'
import {
  getAdminImages, getAdminStats, getAdminUsers,
  adminDeleteImage, adminBatchDelete, adminUpdateImage, setUserStaff
} from '../utils/adminApi'
import { useUserStore } from '../store/userStore'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const images = ref([])
const users = ref([])
const selectedImages = ref([])
const activeTab = ref('images')
const stats = ref({
  total_images: 0,
  public_images: 0,
  private_images: 0,
  total_users: 0,
  top_users: []
})

// 用户管理相关
const allUsers = ref([])
const usersLoading = ref(false)
const userSearch = ref('')

const filters = ref({
  search: '',
  owner: '',
  is_public: '',
  ordering: '-upload_time'
})

// 获取统计信息
const fetchStats = async () => {
  try {
    const response = await getAdminStats()
    stats.value = response.data
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

// 获取用户列表
const fetchUsers = async () => {
  try {
    const response = await getAdminUsers()
    users.value = response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

// 获取图片列表
const fetchImages = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.owner) params.owner = filters.value.owner
    if (filters.value.is_public) params.is_public = filters.value.is_public
    if (filters.value.ordering) params.ordering = filters.value.ordering
    
    const response = await getAdminImages(params)
    images.value = response.data
  } catch (error) {
    ElMessage.error('获取图片列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 重置筛选
const resetFilters = () => {
  filters.value = {
    search: '',
    owner: '',
    is_public: '',
    ordering: '-upload_time'
  }
  fetchImages()
}

// 选择变化
const handleSelectionChange = (selection) => {
  selectedImages.value = selection
}

// 切换公开状态
const togglePublic = async (image) => {
  try {
    await adminUpdateImage(image.id, { is_public: image.is_public })
    ElMessage.success(image.is_public ? '已设为公开' : '已设为私有')
    fetchStats()
  } catch (error) {
    ElMessage.error('操作失败')
    image.is_public = !image.is_public
  }
}

// 删除图片
const handleDelete = async (image) => {
  try {
    await adminDeleteImage(image.id)
    ElMessage.success('删除成功')
    fetchImages()
    fetchStats()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 批量删除
const batchDelete = async () => {
  const ids = selectedImages.value.map(img => img.id)
  try {
    await adminBatchDelete(ids)
    ElMessage.success(`成功删除 ${ids.length} 张图片`)
    selectedImages.value = []
    fetchImages()
    fetchStats()
  } catch (error) {
    ElMessage.error('批量删除失败')
  }
}

// 查看详情
const viewDetail = (image) => {
  router.push(`/image/${image.id}`)
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取所有用户列表（用于用户管理）
const fetchAllUsers = async () => {
  usersLoading.value = true
  try {
    const params = {}
    if (userSearch.value) {
      params.search = userSearch.value
    }
    const response = await getAdminUsers(params)
    allUsers.value = response.data.map(user => ({ ...user, loading: false }))
  } catch (error) {
    ElMessage.error('获取用户列表失败')
    console.error(error)
  } finally {
    usersLoading.value = false
  }
}

// 切换用户管理员状态
const toggleStaff = async (user) => {
  user.loading = true
  try {
    const newStaffStatus = !user.is_staff
    await setUserStaff(user.id, newStaffStatus)
    user.is_staff = newStaffStatus
    ElMessage.success(`用户 ${user.username} 已${newStaffStatus ? '设为' : '取消'}管理员`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    user.loading = false
  }
}

onMounted(() => {
  fetchStats()
  fetchUsers()
  fetchImages()
  // 如果是超级管理员，同时加载用户列表
  if (userStore.user?.is_superuser) {
    fetchAllUsers()
  }
})
</script>

<style scoped>
.admin-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-card :deep(.el-statistic__head) {
  font-size: 13px;
}

.filter-card {
  margin-bottom: 16px;
}

.batch-card {
  margin-bottom: 16px;
}

.table-card {
  margin-bottom: 20px;
}

.rank-card {
  margin-bottom: 20px;
}

.admin-tabs {
  margin-top: 16px;
}

.admin-tabs :deep(.el-tabs__content) {
  padding: 0;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.image-error {
  width: 50px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  color: #909399;
}

.text-muted {
  color: #909399;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .admin-container {
    padding: 12px;
  }

  .header-card {
    margin-bottom: 15px;
  }

  .header-content h2 {
    font-size: 18px;
  }

  .stats-row .el-col {
    margin-bottom: 12px;
  }

  .stat-card :deep(.el-statistic__head) {
    font-size: 11px;
  }

  .stat-card :deep(.el-statistic__number) {
    font-size: 20px !important;
  }

  .filter-card :deep(.el-col) {
    margin-bottom: 8px;
  }

  .batch-card :deep(.el-alert__content) {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  /* 表格适配 */
  .table-card :deep(.el-table) {
    font-size: 12px;
  }

  .table-card :deep(.el-table th),
  .table-card :deep(.el-table td) {
    padding: 8px 4px;
  }

  .table-card :deep(.el-table-column--selection) {
    width: 40px !important;
  }

  .rank-card {
    margin-bottom: 15px;
  }
}

@media screen and (max-width: 480px) {
  .admin-container {
    padding: 8px;
  }

  .header-content h2 {
    font-size: 16px;
  }

  .header-content :deep(.el-tag) {
    font-size: 10px;
    padding: 0 4px;
  }

  .stat-card :deep(.el-statistic__head) {
    font-size: 10px;
  }

  .stat-card :deep(.el-statistic__number) {
    font-size: 18px !important;
  }
}
</style>

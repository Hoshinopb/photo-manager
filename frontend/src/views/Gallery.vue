<template>
  <div class="gallery-container">
    <!-- 搜索和筛选栏 -->
    <el-card class="filter-card">
      <el-row :gutter="16" align="middle">
        <!-- 关键词搜索 -->
        <el-col :xs="24" :sm="12" :md="6" :lg="5">
          <el-input
            v-model="filters.search"
            placeholder="搜索图片名称或描述"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        
        <!-- 标签多选 -->
        <el-col :xs="24" :sm="12" :md="6" :lg="5">
          <el-select
            v-model="filters.selectedTags"
            placeholder="选择标签筛选"
            clearable
            filterable
            multiple
            collapse-tags
            collapse-tags-tooltip
            @change="fetchImages"
          >
            <el-option
              v-for="tag in allTags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.name"
            >
              <span>{{ tag.name }}</span>
              <span class="tag-count">({{ tag.image_count || tag.usage_count || 0 }})</span>
            </el-option>
          </el-select>
        </el-col>
        
        <!-- 标签筛选模式 -->
        <el-col :xs="12" :sm="6" :md="4" :lg="3">
          <el-select v-model="filters.tagMode" placeholder="标签模式" @change="fetchImages">
            <el-option label="包含全部" value="and" />
            <el-option label="包含任一" value="or" />
            <el-option label="不包含" value="not" />
          </el-select>
        </el-col>
        
        <!-- 图片归属筛选 -->
        <el-col :xs="12" :sm="6" :md="4" :lg="3">
          <el-select v-model="filters.ownerFilter" placeholder="图片归属" @change="fetchImages">
            <el-option label="全部图片" value="all" />
            <el-option label="仅我的" value="mine" />
            <el-option label="仅他人的" value="others" />
          </el-select>
        </el-col>
        
        <!-- 时间范围 -->
        <el-col :xs="12" :sm="6" :md="4" :lg="3">
          <el-select v-model="filters.timeRange" placeholder="时间范围" clearable @change="fetchImages">
            <el-option label="今天" value="today" />
            <el-option label="最近一周" value="week" />
            <el-option label="最近一月" value="month" />
          </el-select>
        </el-col>
        
        <!-- 排序和视图切换 -->
        <el-col :xs="12" :sm="6" :md="24" :lg="5" class="filter-actions">
          <el-select v-model="filters.ordering" style="width: 110px" @change="fetchImages">
            <el-option label="最新上传" value="-upload_time" />
            <el-option label="最早上传" value="upload_time" />
            <el-option label="文件最大" value="-size" />
            <el-option label="文件最小" value="size" />
          </el-select>
          <el-button-group style="margin-left: 8px">
            <el-button :type="viewMode === 'grid' ? 'primary' : ''" @click="viewMode = 'grid'" :icon="Grid" />
            <el-button :type="viewMode === 'list' ? 'primary' : ''" @click="viewMode = 'list'" :icon="List" />
          </el-button-group>
          <el-button @click="resetFilters" style="margin-left: 8px">重置</el-button>
        </el-col>
      </el-row>
      
      <!-- 已选标签显示 -->
      <div v-if="filters.selectedTags.length > 0" class="active-filters">
        <span class="filter-label">
          {{ filters.tagMode === 'and' ? '包含全部标签' : filters.tagMode === 'or' ? '包含任一标签' : '不包含标签' }}：
        </span>
        <el-tag
          v-for="tagName in filters.selectedTags"
          :key="tagName"
          closable
          :type="filters.tagMode === 'not' ? 'danger' : 'primary'"
          @close="removeTag(tagName)"
          class="selected-tag"
        >
          {{ tagName }}
        </el-tag>
        <el-button type="primary" text size="small" @click="filters.selectedTags = []; fetchImages()">
          清除全部
        </el-button>
      </div>
    </el-card>

    <!-- 统计信息 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="公开图片" :value="stats.all_public || 0" />
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="我的图片" :value="stats.my_total || 0" />
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="我的公开" :value="stats.my_public || 0" />
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="我的私有" :value="stats.my_private || 0" />
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 热门标签 -->
    <el-card v-if="popularTags.length > 0" class="tags-card">
      <template #header>
        <div class="tags-header">
          <span>热门标签</span>
          <span class="tags-hint">点击添加到筛选</span>
        </div>
      </template>
      <div class="tags-container">
        <el-tag
          v-for="tag in popularTags"
          :key="tag.id"
          :type="filters.selectedTags.includes(tag.name) ? 'primary' : 'info'"
          class="tag-item"
          effect="plain"
          @click="toggleTag(tag.name)"
        >
          {{ tag.name }}
          <span class="tag-badge">{{ tag.image_count || tag.usage_count }}</span>
        </el-tag>
      </div>
    </el-card>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 空状态 -->
    <el-empty v-else-if="filteredImages.length === 0" description="暂无符合条件的图片">
      <el-button type="primary" @click="$router.push('/upload')">上传图片</el-button>
      <el-button v-if="hasFilters" @click="resetFilters">清除筛选</el-button>
    </el-empty>

    <!-- 结果统计 -->
    <div v-else class="result-info">
      <span>共 {{ filteredImages.length }} 张图片</span>
    </div>

    <!-- 网格视图 -->
    <div v-if="!loading && filteredImages.length > 0 && viewMode === 'grid'" class="image-grid">
      <el-row :gutter="16">
        <el-col
          v-for="image in filteredImages"
          :key="image.id"
          :xs="12"
          :sm="8"
          :md="6"
          :lg="4"
        >
          <el-card class="image-card" shadow="hover" @click="viewImageDetail(image)">
            <el-image
              :src="image.file_url"
              fit="cover"
              class="card-image"
              lazy
            >
              <template #placeholder>
                <div class="image-placeholder">
                  <el-icon class="is-loading"><Loading /></el-icon>
                </div>
              </template>
              <template #error>
                <div class="image-error">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
            <div class="card-info">
              <div class="card-title" :title="image.filename">{{ image.filename }}</div>
              <div class="card-meta">
                <span :class="{ 'owner-mine': isOwner(image) }">{{ image.owner_username }}</span>
                <el-tag v-if="image.is_public" type="success" size="small">公开</el-tag>
                <el-tag v-else type="info" size="small">私有</el-tag>
              </div>
              <!-- 显示标签 -->
              <div v-if="image.tags && image.tags.length > 0" class="card-tags">
                <el-tag
                  v-for="tag in image.tags.slice(0, 3)"
                  :key="tag.id"
                  size="small"
                  :type="getTagType(tag.type)"
                  effect="plain"
                >
                  {{ tag.name }}
                </el-tag>
                <span v-if="image.tags.length > 3" class="more-tags">+{{ image.tags.length - 3 }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 列表视图 -->
    <el-card v-if="!loading && filteredImages.length > 0 && viewMode === 'list'" class="list-view">
      <el-table :data="filteredImages" style="width: 100%" stripe @row-click="viewImageDetail">
        <el-table-column label="预览" width="80">
          <template #default="{ row }">
            <el-image
              style="width: 50px; height: 50px"
              :src="row.file_url"
              fit="cover"
            >
              <template #error>
                <div class="image-error-small">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
          </template>
        </el-table-column>
        
        <el-table-column prop="filename" label="文件名" min-width="160" show-overflow-tooltip />
        
        <el-table-column prop="owner_username" label="上传者" width="100">
          <template #default="{ row }">
            <span :class="{ 'owner-mine': isOwner(row) }">{{ row.owner_username }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="标签" min-width="140">
          <template #default="{ row }">
            <el-tag
              v-for="tag in (row.tags || []).slice(0, 2)"
              :key="tag.id"
              size="small"
              :type="getTagType(tag.type)"
              effect="plain"
              class="list-tag"
            >
              {{ tag.name }}
            </el-tag>
            <span v-if="row.tags && row.tags.length > 2" class="more-tags">+{{ row.tags.length - 2 }}</span>
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
        
        <el-table-column label="上传时间" width="160">
          <template #default="{ row }">{{ formatDate(row.upload_time) }}</template>
        </el-table-column>
        
        <el-table-column label="状态" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_public ? 'success' : 'info'" size="small">
              {{ row.is_public ? '公开' : '私有' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 图片详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="currentImage?.filename"
      width="85%"
      top="3vh"
      destroy-on-close
    >
      <div v-if="currentImage" class="image-detail">
        <el-row :gutter="20">
          <el-col :xs="24" :md="16">
            <el-image
              :src="currentImage.file_url"
              fit="contain"
              class="detail-image"
              :preview-src-list="[currentImage.file_url]"
            />
          </el-col>
          <el-col :xs="24" :md="8">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="文件名">{{ currentImage.filename }}</el-descriptions-item>
              <el-descriptions-item label="上传者">
                <span :class="{ 'owner-mine': isOwner(currentImage) }">{{ currentImage.owner_username }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="尺寸">
                {{ currentImage.width }} × {{ currentImage.height }} px
              </el-descriptions-item>
              <el-descriptions-item label="大小">{{ formatFileSize(currentImage.size) }}</el-descriptions-item>
              <el-descriptions-item label="上传时间">{{ formatDate(currentImage.upload_time) }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="currentImage.is_public ? 'success' : 'info'" size="small">
                  {{ currentImage.is_public ? '公开' : '私有' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item v-if="currentImage.description" label="描述">
                {{ currentImage.description }}
              </el-descriptions-item>
            </el-descriptions>
            
            <!-- 标签显示 -->
            <div v-if="currentImage.tags && currentImage.tags.length > 0" class="detail-tags">
              <div class="detail-section-title">标签</div>
              <div class="tags-container">
                <el-tag
                  v-for="tag in currentImage.tags"
                  :key="tag.id"
                  :type="getTagType(tag.type)"
                  class="detail-tag"
                >
                  {{ tag.name }}
                </el-tag>
              </div>
            </div>
            
            <div class="detail-actions">
              <el-button type="primary" @click="goToImageDetail(currentImage)">
                查看详情页
              </el-button>
              <template v-if="isOwner(currentImage)">
                <el-button @click="togglePublic(currentImage)">
                  {{ currentImage.is_public ? '设为私有' : '设为公开' }}
                </el-button>
                <el-popconfirm title="确定删除这张图片吗？" @confirm="handleDelete(currentImage)">
                  <template #reference>
                    <el-button type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Grid, List, Picture, Loading } from '@element-plus/icons-vue'
import { useUserStore } from '../store/userStore'
import { getImages, getImageStats, deleteImage, updateImage } from '../utils/imageApi'
import { getPopularTags, getTags } from '../utils/tagApi'

const router = useRouter()
const userStore = useUserStore()

const images = ref([])
const stats = ref({})
const popularTags = ref([])
const allTags = ref([])
const loading = ref(true)
const viewMode = ref('grid')
const detailDialogVisible = ref(false)
const currentImage = ref(null)

const filters = reactive({
  search: '',
  selectedTags: [],
  tagMode: 'and',
  timeRange: '',
  ordering: '-upload_time',
  ownerFilter: 'all',
})

// 是否有筛选条件
const hasFilters = computed(() => {
  return filters.search || filters.selectedTags.length > 0 || filters.timeRange || filters.ownerFilter !== 'all'
})

// 根据归属筛选过滤图片
const filteredImages = computed(() => {
  if (filters.ownerFilter === 'all') {
    return images.value
  } else if (filters.ownerFilter === 'mine') {
    return images.value.filter(img => isOwner(img))
  } else {
    return images.value.filter(img => !isOwner(img))
  }
})

// 获取标签类型对应的颜色
const getTagType = (type) => {
  const typeMap = {
    'auto': 'success',
    'user': '',
    'ai': 'warning',
  }
  return typeMap[type] || 'info'
}

// 切换标签选择
const toggleTag = (tagName) => {
  const index = filters.selectedTags.indexOf(tagName)
  if (index === -1) {
    filters.selectedTags.push(tagName)
  } else {
    filters.selectedTags.splice(index, 1)
  }
  fetchImages()
}

// 移除标签
const removeTag = (tagName) => {
  const index = filters.selectedTags.indexOf(tagName)
  if (index !== -1) {
    filters.selectedTags.splice(index, 1)
    fetchImages()
  }
}

// 获取图片列表
const fetchImages = async () => {
  loading.value = true
  try {
    const params = {
      ordering: filters.ordering,
    }
    if (filters.search) params.search = filters.search
    if (filters.timeRange) params.time_range = filters.timeRange
    
    // 多标签筛选
    if (filters.selectedTags.length > 0) {
      params.tags = filters.selectedTags.join(',')
      params.tag_mode = filters.tagMode
    }
    
    const response = await getImages(params)
    images.value = response.data
  } catch (error) {
    ElMessage.error('获取图片列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 获取统计信息
const fetchStats = async () => {
  try {
    const response = await getImageStats()
    stats.value = response.data
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

// 获取热门标签
const fetchPopularTags = async () => {
  try {
    const response = await getPopularTags()
    popularTags.value = response.data
  } catch (error) {
    console.error('获取热门标签失败:', error)
  }
}

// 获取所有标签
const fetchAllTags = async () => {
  try {
    const response = await getTags()
    allTags.value = response.data
  } catch (error) {
    console.error('获取所有标签失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  fetchImages()
}

// 重置筛选
const resetFilters = () => {
  filters.search = ''
  filters.selectedTags = []
  filters.tagMode = 'and'
  filters.timeRange = ''
  filters.ordering = '-upload_time'
  filters.ownerFilter = 'all'
  fetchImages()
}

// 查看图片详情（对话框方式）
const viewImageDetail = (image) => {
  currentImage.value = image
  detailDialogVisible.value = true
}

// 跳转到详情页
const goToImageDetail = (image) => {
  router.push(`/image/${image.id}`)
}

// 判断是否是当前用户的图片
const isOwner = (image) => {
  return userStore.user && image.owner === userStore.user.id
}

// 切换公开状态
const togglePublic = async (image) => {
  try {
    await updateImage(image.id, { is_public: !image.is_public })
    image.is_public = !image.is_public
    ElMessage.success(image.is_public ? '已设为公开' : '已设为私有')
    fetchStats()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// 删除图片
const handleDelete = async (image) => {
  try {
    await deleteImage(image.id)
    ElMessage.success('删除成功')
    detailDialogVisible.value = false
    images.value = images.value.filter(img => img.id !== image.id)
    fetchStats()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
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
    minute: '2-digit',
  })
}

onMounted(() => {
  fetchImages()
  fetchStats()
  fetchPopularTags()
  fetchAllTags()
})
</script>

<style scoped>
.gallery-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.filter-card {
  margin-bottom: 16px;
}

.filter-card :deep(.el-card__body) {
  padding: 16px;
}

.filter-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-top: 12px;
}

@media (min-width: 1200px) {
  .filter-actions {
    margin-top: 0;
  }
}

.active-filters {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-label {
  color: #606266;
  font-size: 13px;
}

.selected-tag {
  margin-right: 0;
}

.tags-card {
  margin-bottom: 16px;
}

.tags-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tags-hint {
  font-size: 12px;
  color: #909399;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  cursor: pointer;
  transition: all 0.2s;
}

.tag-item:hover {
  transform: scale(1.05);
}

.tag-badge {
  margin-left: 4px;
  font-size: 11px;
  opacity: 0.8;
}

.tag-count {
  margin-left: 8px;
  color: #909399;
  font-size: 12px;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  text-align: center;
}

.stat-card :deep(.el-statistic__head) {
  font-size: 13px;
}

.loading-container {
  padding: 40px;
}

.result-info {
  margin-bottom: 12px;
  color: #606266;
  font-size: 14px;
}

.image-grid {
  margin-top: 8px;
}

.image-card {
  margin-bottom: 16px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.image-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.image-card :deep(.el-card__body) {
  padding: 0;
}

.card-image {
  width: 100%;
  height: 140px;
  display: block;
}

.card-info {
  padding: 10px;
}

.card-title {
  font-size: 13px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 6px;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.owner-mine {
  color: #409eff;
  font-weight: 500;
}

.card-tags {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.card-tags :deep(.el-tag) {
  max-width: 70px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.more-tags {
  font-size: 11px;
  color: #909399;
}

.image-placeholder,
.image-error {
  width: 100%;
  height: 140px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  color: #909399;
  font-size: 28px;
}

.image-error-small {
  width: 50px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  color: #909399;
}

.list-view {
  margin-top: 8px;
}

.list-tag {
  margin-right: 4px;
}

.text-muted {
  color: #909399;
}

.image-detail {
  padding: 10px 0;
}

.detail-image {
  width: 100%;
  max-height: 65vh;
}

.detail-tags {
  margin-top: 16px;
}

.detail-section-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #303133;
}

.detail-tag {
  margin-right: 6px;
  margin-bottom: 6px;
}

.detail-actions {
  margin-top: 20px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>

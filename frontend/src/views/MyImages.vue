<template>
  <div class="my-images-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="page-title">我的图片</span>
          <el-button type="primary" @click="goToUpload">
            <el-icon><Plus /></el-icon>
            上传图片
          </el-button>
        </div>
      </template>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-row :gutter="12" align="middle">
          <!-- 搜索框 -->
          <el-col :xs="24" :sm="8" :md="6">
            <el-input
              v-model="filters.search"
              placeholder="搜索文件名"
              clearable
              @clear="applyFilters"
              @keyup.enter="applyFilters"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          
          <!-- 标签多选 -->
          <el-col :xs="24" :sm="8" :md="6">
            <el-select
              v-model="filters.selectedTags"
              placeholder="选择标签筛选"
              clearable
              filterable
              multiple
              collapse-tags
              collapse-tags-tooltip
              @change="applyFilters"
            >
              <el-option
                v-for="tag in myTags"
                :key="tag.id"
                :label="tag.name"
                :value="tag.name"
              >
                <span>{{ tag.name }}</span>
                <span class="tag-count">({{ tag.usage_count || 0 }})</span>
              </el-option>
            </el-select>
          </el-col>
          
          <!-- 标签模式 -->
          <el-col :xs="12" :sm="4" :md="4">
            <el-select v-model="filters.tagMode" @change="applyFilters">
              <el-option label="包含全部" value="and" />
              <el-option label="包含任一" value="or" />
              <el-option label="不包含" value="not" />
            </el-select>
          </el-col>
          
          <!-- 公开状态筛选 -->
          <el-col :xs="12" :sm="4" :md="4">
            <el-select v-model="filters.publicFilter" @change="applyFilters">
              <el-option label="全部状态" value="all" />
              <el-option label="仅公开" value="public" />
              <el-option label="仅私有" value="private" />
            </el-select>
          </el-col>
          
          <el-col :xs="24" :sm="24" :md="4" class="filter-actions">
            <el-button @click="resetFilters">重置筛选</el-button>
          </el-col>
        </el-row>
        
        <!-- 已选标签显示 -->
        <div v-if="filters.selectedTags.length > 0" class="active-filters">
          <span class="filter-label">
            {{ filters.tagMode === 'and' ? '包含全部' : filters.tagMode === 'or' ? '包含任一' : '不包含' }}：
          </span>
          <el-tag
            v-for="tagName in filters.selectedTags"
            :key="tagName"
            closable
            :type="filters.tagMode === 'not' ? 'danger' : 'primary'"
            @close="removeTag(tagName)"
            size="small"
          >
            {{ tagName }}
          </el-tag>
        </div>
      </div>

      <!-- 我的标签展示 -->
      <div v-if="myTags.length > 0" class="my-tags-section">
        <div class="section-title">我的标签 ({{ myTags.length }})</div>
        <div class="tags-container">
          <el-tag
            v-for="tag in myTags.slice(0, showAllTags ? myTags.length : 15)"
            :key="tag.id"
            :type="filters.selectedTags.includes(tag.name) ? 'primary' : 'info'"
            effect="plain"
            class="tag-item"
            @click="toggleTag(tag.name)"
          >
            {{ tag.name }}
            <span class="tag-badge">{{ tag.usage_count }}</span>
          </el-tag>
          <el-button
            v-if="myTags.length > 15"
            text
            type="primary"
            size="small"
            @click="showAllTags = !showAllTags"
          >
            {{ showAllTags ? '收起' : `展开全部 (${myTags.length})` }}
          </el-button>
        </div>
      </div>

      <!-- 批量操作栏 -->
      <div v-if="selectedImages.length > 0" class="batch-actions">
        <span class="selection-info">已选择 {{ selectedImages.length }} 张图片</span>
        <el-button-group>
          <el-button type="primary" size="small" @click="batchSetPublic(true)">
            <el-icon><View /></el-icon>
            批量公开
          </el-button>
          <el-button type="info" size="small" @click="batchSetPublic(false)">
            <el-icon><Hide /></el-icon>
            批量私有
          </el-button>
          <el-popconfirm
            title="确定删除选中的图片吗？此操作不可恢复！"
            @confirm="batchDelete"
            width="250"
          >
            <template #reference>
              <el-button type="danger" size="small">
                <el-icon><Delete /></el-icon>
                批量删除
              </el-button>
            </template>
          </el-popconfirm>
        </el-button-group>
        <el-button size="small" @click="clearSelection">取消选择</el-button>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>

      <!-- 空状态 -->
      <el-empty
        v-else-if="filteredImages.length === 0"
        :description="hasFilters ? '没有符合条件的图片' : '暂无图片'"
      >
        <el-button type="primary" @click="goToUpload">上传图片</el-button>
        <el-button v-if="hasFilters" @click="resetFilters">清除筛选</el-button>
      </el-empty>

      <!-- 结果统计 -->
      <div v-else class="result-info">
        共 {{ filteredImages.length }} 张图片
      </div>

      <!-- 图片列表 -->
      <div v-if="!loading && filteredImages.length > 0" class="image-list">
        <el-table
          ref="tableRef"
          :data="sortedImages"
          style="width: 100%"
          stripe
          @selection-change="handleSelectionChange"
          @sort-change="handleSortChange"
        >
          <el-table-column type="selection" width="45" />
          
          <el-table-column label="预览" width="80">
            <template #default="{ row }">
              <el-image
                style="width: 50px; height: 50px"
                :src="row.file_url"
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
          
          <el-table-column
            prop="filename"
            label="文件名"
            min-width="160"
            sortable="custom"
            :sort-orders="['ascending', 'descending', null]"
            show-overflow-tooltip
          />
          
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
              <span v-if="row.tags && row.tags.length > 2" class="more-tags">
                +{{ row.tags.length - 2 }}
              </span>
            </template>
          </el-table-column>
          
          <el-table-column
            label="尺寸"
            width="120"
            sortable="custom"
            :sort-orders="['ascending', 'descending', null]"
            prop="pixels"
          >
            <template #default="{ row }">
              <span v-if="row.width && row.height">
                {{ row.width }}×{{ row.height }}
              </span>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>
          
          <el-table-column
            prop="size"
            label="大小"
            width="100"
            sortable="custom"
            :sort-orders="['ascending', 'descending', null]"
          >
            <template #default="{ row }">
              {{ formatFileSize(row.size) }}
            </template>
          </el-table-column>
          
          <el-table-column
            prop="upload_time"
            label="上传时间"
            width="155"
            sortable="custom"
            :sort-orders="['ascending', 'descending', null]"
          >
            <template #default="{ row }">
              {{ formatDate(row.upload_time) }}
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="70" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_public ? 'success' : 'info'" size="small">
                {{ row.is_public ? '公开' : '私有' }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" text @click="goToDetail(row)">
                详情
              </el-button>
              <el-button size="small" text @click="togglePublic(row)">
                {{ row.is_public ? '私有' : '公开' }}
              </el-button>
              <el-popconfirm title="确定删除？" @confirm="handleDelete(row)">
                <template #reference>
                  <el-button type="danger" size="small" text>删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 刷新按钮 -->
      <div v-if="!loading && images.length > 0" class="refresh-section">
        <el-button @click="fetchImages" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          刷新列表
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Picture, Refresh, Delete, View, Hide, Search } from '@element-plus/icons-vue'
import { getMyImages, deleteImage, updateImage } from '../utils/imageApi'
import { getMyTags } from '../utils/tagApi'

const router = useRouter()
const tableRef = ref(null)
const images = ref([])
const myTags = ref([])
const loading = ref(true)
const refreshing = ref(false)
const selectedImages = ref([])
const showAllTags = ref(false)

// 筛选条件
const filters = ref({
  search: '',
  selectedTags: [],
  tagMode: 'and',
  publicFilter: 'all',
})

// 排序状态
const sortState = ref({
  prop: null,
  order: null
})

// 是否有筛选
const hasFilters = computed(() => {
  return filters.value.search || 
         filters.value.selectedTags.length > 0 || 
         filters.value.publicFilter !== 'all'
})

// 筛选后的图片
const filteredImages = computed(() => {
  let result = images.value
  
  // 搜索筛选
  if (filters.value.search) {
    const searchLower = filters.value.search.toLowerCase()
    result = result.filter(img => 
      img.filename?.toLowerCase().includes(searchLower) ||
      img.description?.toLowerCase().includes(searchLower)
    )
  }
  
  // 公开状态筛选
  if (filters.value.publicFilter === 'public') {
    result = result.filter(img => img.is_public)
  } else if (filters.value.publicFilter === 'private') {
    result = result.filter(img => !img.is_public)
  }
  
  // 标签筛选
  if (filters.value.selectedTags.length > 0) {
    const selectedTags = filters.value.selectedTags
    
    if (filters.value.tagMode === 'and') {
      // AND: 包含所有选中的标签
      result = result.filter(img => {
        const imgTags = (img.tags || []).map(t => t.name)
        return selectedTags.every(tag => imgTags.includes(tag))
      })
    } else if (filters.value.tagMode === 'or') {
      // OR: 包含任一选中的标签
      result = result.filter(img => {
        const imgTags = (img.tags || []).map(t => t.name)
        return selectedTags.some(tag => imgTags.includes(tag))
      })
    } else if (filters.value.tagMode === 'not') {
      // NOT: 不包含任何选中的标签
      result = result.filter(img => {
        const imgTags = (img.tags || []).map(t => t.name)
        return !selectedTags.some(tag => imgTags.includes(tag))
      })
    }
  }
  
  return result
})

// 排序后的图片列表
const sortedImages = computed(() => {
  if (!sortState.value.prop || !sortState.value.order) {
    return filteredImages.value
  }
  
  const sorted = [...filteredImages.value]
  const { prop, order } = sortState.value
  const multiplier = order === 'ascending' ? 1 : -1
  
  sorted.sort((a, b) => {
    let valueA, valueB
    
    if (prop === 'filename') {
      valueA = a.filename?.toLowerCase() || ''
      valueB = b.filename?.toLowerCase() || ''
      return valueA.localeCompare(valueB) * multiplier
    } else if (prop === 'pixels') {
      valueA = (a.width || 0) * (a.height || 0)
      valueB = (b.width || 0) * (b.height || 0)
    } else if (prop === 'size') {
      valueA = a.size || 0
      valueB = b.size || 0
    } else if (prop === 'upload_time') {
      valueA = new Date(a.upload_time).getTime()
      valueB = new Date(b.upload_time).getTime()
    } else {
      return 0
    }
    
    return (valueA - valueB) * multiplier
  })
  
  return sorted
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

// 切换标签
const toggleTag = (tagName) => {
  const index = filters.value.selectedTags.indexOf(tagName)
  if (index === -1) {
    filters.value.selectedTags.push(tagName)
  } else {
    filters.value.selectedTags.splice(index, 1)
  }
}

// 移除标签
const removeTag = (tagName) => {
  const index = filters.value.selectedTags.indexOf(tagName)
  if (index !== -1) {
    filters.value.selectedTags.splice(index, 1)
  }
}

// 应用筛选
const applyFilters = () => {
  // 筛选已通过 computed 自动应用
}

// 重置筛选
const resetFilters = () => {
  filters.value.search = ''
  filters.value.selectedTags = []
  filters.value.tagMode = 'and'
  filters.value.publicFilter = 'all'
}

// 处理排序变化
const handleSortChange = ({ prop, order }) => {
  sortState.value = { prop, order }
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedImages.value = selection
}

// 清除选择
const clearSelection = () => {
  tableRef.value?.clearSelection()
}

// 获取图片列表
const fetchImages = async () => {
  refreshing.value = true
  try {
    const response = await getMyImages()
    images.value = response.data
  } catch (error) {
    ElMessage.error('获取图片列表失败')
    console.error('获取图片列表失败:', error)
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

// 获取我的标签
const fetchMyTags = async () => {
  try {
    const response = await getMyTags()
    myTags.value = response.data
  } catch (error) {
    console.error('获取标签失败:', error)
  }
}

// 删除图片
const handleDelete = async (row) => {
  try {
    await deleteImage(row.id)
    ElMessage.success('删除成功')
    images.value = images.value.filter(img => img.id !== row.id)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

// 批量删除
const batchDelete = async () => {
  const ids = selectedImages.value.map(img => img.id)
  let successCount = 0
  let failCount = 0
  
  for (const id of ids) {
    try {
      await deleteImage(id)
      successCount++
    } catch (error) {
      failCount++
    }
  }
  
  if (successCount > 0) {
    images.value = images.value.filter(img => !ids.includes(img.id))
    ElMessage.success(`成功删除 ${successCount} 张图片`)
  }
  if (failCount > 0) {
    ElMessage.warning(`${failCount} 张图片删除失败`)
  }
  
  clearSelection()
}

// 批量设置公开/私有
const batchSetPublic = async (isPublic) => {
  let successCount = 0
  let failCount = 0
  
  for (const img of selectedImages.value) {
    try {
      await updateImage(img.id, { is_public: isPublic })
      img.is_public = isPublic
      successCount++
    } catch (error) {
      failCount++
    }
  }
  
  if (successCount > 0) {
    ElMessage.success(`成功设置 ${successCount} 张图片为${isPublic ? '公开' : '私有'}`)
  }
  if (failCount > 0) {
    ElMessage.warning(`${failCount} 张图片设置失败`)
  }
  
  clearSelection()
}

// 切换公开状态
const togglePublic = async (row) => {
  try {
    await updateImage(row.id, { is_public: !row.is_public })
    row.is_public = !row.is_public
    ElMessage.success(row.is_public ? '已设为公开' : '已设为私有')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 跳转到详情页
const goToDetail = (row) => {
  router.push(`/image/${row.id}`)
}

// 跳转到上传页面
const goToUpload = () => {
  router.push('/upload')
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
  fetchMyTags()
})
</script>

<style scoped>
.my-images-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.filter-bar {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

@media (min-width: 992px) {
  .filter-actions {
    margin-top: 0;
  }
}

.active-filters {
  margin-top: 12px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-label {
  color: #606266;
  font-size: 13px;
}

.my-tags-section {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 10px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
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

.batch-actions {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 16px;
  margin-bottom: 15px;
  background: #ecf5ff;
  border-radius: 4px;
}

.selection-info {
  font-weight: 500;
  color: #409eff;
}

.loading-container {
  padding: 20px;
}

.result-info {
  margin-bottom: 12px;
  color: #606266;
  font-size: 14px;
}

.image-list {
  margin-top: 10px;
}

.list-tag {
  margin-right: 4px;
}

.more-tags {
  font-size: 11px;
  color: #909399;
}

.image-error {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 50px;
  height: 50px;
  background: #f5f7fa;
  color: #909399;
}

.text-muted {
  color: #909399;
}

.refresh-section {
  margin-top: 20px;
  text-align: center;
}

/* 排序表头样式 */
:deep(.el-table .el-table__header th) {
  cursor: pointer;
  user-select: none;
}

:deep(.el-table .el-table__header th:hover) {
  background-color: #ecf5ff;
}
</style>

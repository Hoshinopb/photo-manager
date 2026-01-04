<template>
  <div class="image-detail-container">
    <!-- 返回按钮 -->
    <el-page-header @back="goBack" class="page-header">
      <template #content>
        <span class="page-title">图片详情</span>
      </template>
      <template #extra>
        <el-button-group v-if="image && isOwner">
          <el-button type="warning" @click="openEditor">
            <el-icon><Edit /></el-icon> 编辑
          </el-button>
          <el-button @click="handleParseExif" :loading="parsingExif">
            解析EXIF
          </el-button>
          <el-button type="primary" @click="togglePublic">
            {{ image.is_public ? '设为私有' : '设为公开' }}
          </el-button>
          <el-popconfirm title="确定删除这张图片吗？" @confirm="handleDelete">
            <template #reference>
              <el-button type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </el-button-group>
      </template>
    </el-page-header>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 错误状态 -->
    <el-result v-else-if="error" icon="error" title="加载失败" :sub-title="error">
      <template #extra>
        <el-button type="primary" @click="fetchImage">重试</el-button>
        <el-button @click="goBack">返回</el-button>
      </template>
    </el-result>

    <!-- 图片详情 -->
    <div v-else-if="image" class="detail-content">
      <el-row :gutter="24">
        <!-- 图片预览区 -->
        <el-col :xs="24" :lg="16">
          <el-card class="image-card">
            <el-image
              :src="image.file_url"
              fit="contain"
              class="main-image"
              :preview-src-list="[image.file_url]"
              :initial-index="0"
            >
              <template #placeholder>
                <div class="image-placeholder">
                  <el-icon class="is-loading" size="48"><Loading /></el-icon>
                  <p>加载中...</p>
                </div>
              </template>
              <template #error>
                <div class="image-error">
                  <el-icon size="48"><Picture /></el-icon>
                  <p>图片加载失败</p>
                </div>
              </template>
            </el-image>
          </el-card>

          <!-- 标签区域 -->
          <el-card class="tags-card">
            <template #header>
              <div class="card-header">
                <span>标签</span>
                <el-tag v-if="image.exif_parsed" type="success" size="small">EXIF已解析</el-tag>
              </div>
            </template>
            
            <div class="tags-container">
              <el-tag
                v-for="tag in image.tags"
                :key="tag.id"
                :type="getTagType(tag.type)"
                :closable="isOwner"
                @close="handleRemoveTag(tag)"
                class="tag-item"
              >
                {{ tag.name }}
              </el-tag>
              <el-tag v-if="image.tags?.length === 0" type="info">暂无标签</el-tag>
            </div>
            
            <!-- 添加标签 -->
            <div v-if="isOwner" class="add-tag-section">
              <el-input
                v-model="newTagName"
                placeholder="输入标签名称"
                size="small"
                style="width: 200px"
                @keyup.enter="handleAddTag"
              >
                <template #append>
                  <el-button @click="handleAddTag" :loading="addingTag">添加</el-button>
                </template>
              </el-input>
            </div>
          </el-card>
        </el-col>

        <!-- 信息面板 -->
        <el-col :xs="24" :lg="8">
          <!-- 基本信息 -->
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <span>基本信息</span>
                <el-tag :type="image.is_public ? 'success' : 'info'">
                  {{ image.is_public ? '公开' : '私有' }}
                </el-tag>
              </div>
            </template>

            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="文件名">
                <el-tooltip :content="image.filename" placement="top">
                  <span class="truncate-text">{{ image.filename }}</span>
                </el-tooltip>
              </el-descriptions-item>
              <el-descriptions-item label="上传者">
                <el-tag size="small">{{ image.owner_username }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="图片尺寸">
                {{ image.width || '-' }} × {{ image.height || '-' }} px
              </el-descriptions-item>
              <el-descriptions-item label="文件大小">
                {{ formatFileSize(image.size) }}
              </el-descriptions-item>
              <el-descriptions-item label="上传时间">
                {{ formatDate(image.upload_time) }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <!-- EXIF 信息 -->
          <el-card v-if="image.exif_info" class="exif-card">
            <template #header>
              <span>EXIF 信息</span>
            </template>

            <el-descriptions :column="1" border size="small">
              <el-descriptions-item v-if="image.exif_info.camera_make" label="相机品牌">
                {{ image.exif_info.camera_make }}
              </el-descriptions-item>
              <el-descriptions-item v-if="image.exif_info.camera_model" label="相机型号">
                {{ image.exif_info.camera_model }}
              </el-descriptions-item>
              <el-descriptions-item v-if="image.exif_info.datetime" label="拍摄时间">
                {{ formatDate(image.exif_info.datetime) }}
              </el-descriptions-item>
              <el-descriptions-item v-if="image.exif_info.exposure_time" label="曝光时间">
                {{ image.exif_info.exposure_time }}s
              </el-descriptions-item>
              <el-descriptions-item v-if="image.exif_info.f_number" label="光圈">
                {{ image.exif_info.f_number }}
              </el-descriptions-item>
              <el-descriptions-item v-if="image.exif_info.iso" label="ISO">
                {{ image.exif_info.iso }}
              </el-descriptions-item>
              <el-descriptions-item v-if="image.exif_info.focal_length" label="焦距">
                {{ image.exif_info.focal_length }}
              </el-descriptions-item>
              <el-descriptions-item v-if="image.exif_info.gps_latitude && image.exif_info.gps_longitude" label="GPS位置">
                {{ image.exif_info.gps_latitude.toFixed(6) }}, {{ image.exif_info.gps_longitude.toFixed(6) }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <!-- 描述编辑 -->
          <el-card class="desc-card">
            <template #header>
              <span>描述</span>
            </template>
            
            <div v-if="!isOwner && image.description">
              <p>{{ image.description }}</p>
            </div>
            <div v-else-if="isOwner">
              <el-input
                v-model="editForm.description"
                type="textarea"
                :rows="3"
                placeholder="添加图片描述..."
              />
              <el-button
                type="primary"
                size="small"
                style="margin-top: 10px"
                @click="updateDescription"
                :loading="updating"
              >
                保存描述
              </el-button>
            </div>
            <div v-else>
              <el-empty description="暂无描述" :image-size="60" />
            </div>
          </el-card>

          <!-- 操作按钮 -->
          <el-card class="action-card">
            <el-button type="primary" :icon="Download" @click="downloadImage">
              下载原图
            </el-button>
            <el-button :icon="Link" @click="copyLink">
              复制链接
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 图片编辑器 -->
    <ImageEditor
      v-model="editorVisible"
      :image="image"
      @saved="onEditorSaved"
      @saved-as-new="onEditorSavedAsNew"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Picture, Loading, Download, Link, Edit } from '@element-plus/icons-vue'
import { useUserStore } from '../store/userStore'
import { getImageDetail, updateImage, deleteImage } from '../utils/imageApi'
import { addTagToImage, removeTagFromImage, parseImageExif } from '../utils/tagApi'
import ImageEditor from '../components/ImageEditor.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const image = ref(null)
const loading = ref(true)
const error = ref('')
const updating = ref(false)
const newTagName = ref('')
const addingTag = ref(false)
const parsingExif = ref(false)
const editorVisible = ref(false)

const editForm = reactive({
  description: '',
})

// 判断是否是当前用户的图片
const isOwner = computed(() => {
  return userStore.user && image.value && image.value.owner === userStore.user.id
})

// 打开图片编辑器
const openEditor = () => {
  editorVisible.value = true
}

// 编辑保存后刷新图片
const onEditorSaved = (updatedImage) => {
  // 刷新当前图片
  fetchImage()
}

// 另存为新图片后返回我的图片页面
const onEditorSavedAsNew = (newImage) => {
  ElMessage.success('已另存为新图片')
  router.push('/my-images')
}
// 获取标签类型对应的颜色
const getTagType = (type) => {
  const typeMap = {
    'auto': 'success',
    'user': '',
    'ai': 'warning',
  }
  return typeMap[type] || ''
}

// 获取图片详情
const fetchImage = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await getImageDetail(route.params.id)
    image.value = response.data
    editForm.description = image.value.description || ''
  } catch (err) {
    error.value = err.response?.data?.detail || '获取图片详情失败'
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 切换公开状态
const togglePublic = async () => {
  try {
    await updateImage(image.value.id, { is_public: !image.value.is_public })
    image.value.is_public = !image.value.is_public
    ElMessage.success(image.value.is_public ? '已设为公开' : '已设为私有')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  }
}

// 更新描述
const updateDescription = async () => {
  updating.value = true
  try {
    await updateImage(image.value.id, { description: editForm.description })
    image.value.description = editForm.description
    ElMessage.success('描述已更新')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '更新失败')
  } finally {
    updating.value = false
  }
}

// 删除图片
const handleDelete = async () => {
  try {
    await deleteImage(image.value.id)
    ElMessage.success('删除成功')
    router.push('/gallery')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '删除失败')
  }
}

// 添加标签
const handleAddTag = async () => {
  if (!newTagName.value.trim()) {
    ElMessage.warning('请输入标签名称')
    return
  }
  
  addingTag.value = true
  try {
    const response = await addTagToImage(image.value.id, newTagName.value.trim())
    ElMessage.success('标签添加成功')
    newTagName.value = ''
    // 刷新图片信息
    await fetchImage()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '添加标签失败')
  } finally {
    addingTag.value = false
  }
}

// 移除标签
const handleRemoveTag = async (tag) => {
  try {
    await removeTagFromImage(image.value.id, tag.id)
    ElMessage.success('标签已移除')
    // 从本地移除
    image.value.tags = image.value.tags.filter(t => t.id !== tag.id)
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '移除标签失败')
  }
}

// 解析 EXIF
const handleParseExif = async () => {
  parsingExif.value = true
  try {
    const response = await parseImageExif(image.value.id)
    ElMessage.success('EXIF 解析成功')
    // 刷新图片信息
    await fetchImage()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || 'EXIF 解析失败')
  } finally {
    parsingExif.value = false
  }
}

// 下载图片
const downloadImage = () => {
  if (image.value?.file_url) {
    const link = document.createElement('a')
    link.href = image.value.file_url
    link.download = image.value.filename
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

// 复制链接
const copyLink = async () => {
  if (image.value?.file_url) {
    try {
      await navigator.clipboard.writeText(image.value.file_url)
      ElMessage.success('链接已复制到剪贴板')
    } catch (err) {
      ElMessage.error('复制失败')
    }
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
    second: '2-digit',
  })
}

onMounted(() => {
  fetchImage()
})
</script>

<style scoped>
.image-detail-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.loading-container {
  padding: 40px;
}

.detail-content {
  margin-top: 20px;
}

.image-card,
.tags-card,
.info-card,
.exif-card,
.desc-card {
  margin-bottom: 20px;
}

.main-image {
  width: 100%;
  min-height: 300px;
  max-height: 70vh;
}

.main-image :deep(img) {
  object-fit: contain !important;
  max-width: 100%;
  max-height: 70vh;
}

.image-placeholder,
.image-error {
  width: 100%;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  color: #909399;
}

.image-placeholder p,
.image-error p {
  margin-top: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.truncate-text {
  display: inline-block;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}

.tag-item {
  cursor: default;
}

.add-tag-section {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.action-card :deep(.el-card__body) {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .image-detail-container {
    padding: 12px;
  }

  .page-header {
    margin-bottom: 15px;
  }

  .page-header :deep(.el-page-header__content) {
    font-size: 16px;
  }

  /* 操作按钮适配 */
  .page-header :deep(.el-page-header__extra) {
    margin-top: 12px;
  }

  .page-header :deep(.el-button-group) {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .page-header :deep(.el-button-group .el-button) {
    margin-left: 0 !important;
    border-radius: 4px !important;
    flex: 1;
    min-width: 0;
  }

  .detail-content {
    margin-top: 15px;
  }

  .main-image {
    min-height: 200px;
    max-height: 50vh;
  }

  .main-image :deep(img) {
    max-height: 50vh;
  }

  .image-placeholder,
  .image-error {
    min-height: 200px;
  }

  .image-card,
  .tags-card,
  .info-card,
  .exif-card,
  .desc-card {
    margin-bottom: 12px;
  }

  .tags-container {
    gap: 6px;
  }

  .add-tag-section :deep(.el-input-group) {
    flex-wrap: wrap;
  }

  .action-card :deep(.el-card__body) {
    gap: 8px;
  }

  .action-card :deep(.el-button) {
    flex: 1;
    min-width: 0;
  }

  .truncate-text {
    max-width: 150px;
  }
}

@media screen and (max-width: 480px) {
  .image-detail-container {
    padding: 8px;
  }

  .page-title {
    font-size: 15px;
  }

  .main-image {
    min-height: 150px;
    max-height: 40vh;
  }

  .main-image :deep(img) {
    max-height: 40vh;
  }

  .image-placeholder,
  .image-error {
    min-height: 150px;
  }

  .truncate-text {
    max-width: 100px;
  }
}
</style>

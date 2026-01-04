<template>
  <div class="upload-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>上传图片</span>
        </div>
      </template>

      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        multiple
        :auto-upload="false"
        :file-list="fileList"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :before-upload="beforeUpload"
        accept="image/jpeg,image/png,image/gif,image/webp"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将图片拖拽到此处，或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 jpg/png/gif/webp 格式，单个文件不超过 10MB
          </div>
        </template>
      </el-upload>

      <el-divider v-if="fileList.length > 0" />

      <div v-if="fileList.length > 0" class="upload-options">
        <el-form :model="uploadForm" label-width="100px">
          <el-form-item label="公开图片">
            <el-switch v-model="uploadForm.isPublic" />
            <span class="option-tip">公开后其他用户可以看到</span>
          </el-form-item>
          <el-form-item label="图片描述">
            <el-input
              v-model="uploadForm.description"
              type="textarea"
              :rows="2"
              placeholder="为图片添加描述（可选）"
            />
          </el-form-item>
        </el-form>

        <div class="upload-actions">
          <el-button @click="clearFiles">清空列表</el-button>
          <el-button type="primary" :loading="uploading" @click="handleUpload">
            {{ uploading ? '上传中...' : `上传 ${fileList.length} 个文件` }}
          </el-button>
        </div>
      </div>

      <!-- 上传进度 -->
      <div v-if="uploading" class="upload-progress">
        <el-progress
          :percentage="uploadProgress"
          :status="uploadProgress === 100 ? 'success' : ''"
        />
        <p class="progress-text">
          正在上传: {{ currentUploadIndex + 1 }} / {{ fileList.length }}
        </p>
      </div>
    </el-card>

    <!-- 上传结果 -->
    <el-card v-if="uploadResults.length > 0" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>上传结果</span>
          <el-button type="primary" text @click="goToMyImages">
            查看我的图片
          </el-button>
        </div>
      </template>

      <el-table :data="uploadResults" style="width: 100%">
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.success ? 'success' : 'danger'">
              {{ row.success ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadImage } from '../utils/imageApi'

const router = useRouter()
const uploadRef = ref(null)
const fileList = ref([])
const uploading = ref(false)
const uploadProgress = ref(0)
const currentUploadIndex = ref(0)
const uploadResults = ref([])

const uploadForm = reactive({
  isPublic: false,
  description: '',
})

// 文件变化处理
const handleFileChange = (file, uploadFileList) => {
  fileList.value = uploadFileList
}

// 文件移除处理
const handleFileRemove = (file, uploadFileList) => {
  fileList.value = uploadFileList
}

// 上传前验证
const beforeUpload = (file) => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  const isValidType = allowedTypes.includes(file.type)
  const isValidSize = file.size / 1024 / 1024 < 10

  if (!isValidType) {
    ElMessage.error('只能上传 JPG/PNG/GIF/WEBP 格式的图片')
    return false
  }
  if (!isValidSize) {
    ElMessage.error('图片大小不能超过 10MB')
    return false
  }
  return true
}

// 清空文件列表
const clearFiles = () => {
  fileList.value = []
  uploadRef.value?.clearFiles()
  uploadResults.value = []
}

// 执行上传
const handleUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择要上传的图片')
    return
  }

  uploading.value = true
  uploadProgress.value = 0
  currentUploadIndex.value = 0
  uploadResults.value = []

  for (let i = 0; i < fileList.value.length; i++) {
    currentUploadIndex.value = i
    const fileItem = fileList.value[i]
    const file = fileItem.raw

    try {
      await uploadImage(file, {
        isPublic: uploadForm.isPublic,
        description: uploadForm.description,
        onProgress: (percent) => {
          uploadProgress.value = Math.round(
            ((i + percent / 100) / fileList.value.length) * 100
          )
        },
      })

      uploadResults.value.push({
        filename: file.name,
        success: true,
        message: '上传成功',
      })
    } catch (error) {
      const errorMsg = error.response?.data?.file?.[0] || 
                       error.response?.data?.detail || 
                       '上传失败'
      uploadResults.value.push({
        filename: file.name,
        success: false,
        message: errorMsg,
      })
    }
  }

  uploading.value = false
  uploadProgress.value = 100

  const successCount = uploadResults.value.filter((r) => r.success).length
  const failCount = uploadResults.value.filter((r) => !r.success).length

  if (failCount === 0) {
    ElMessage.success(`全部 ${successCount} 个文件上传成功！`)
    clearFiles()
  } else if (successCount === 0) {
    ElMessage.error(`全部 ${failCount} 个文件上传失败`)
  } else {
    ElMessage.warning(`成功 ${successCount} 个，失败 ${failCount} 个`)
  }
}

// 跳转到我的图片页面
const goToMyImages = () => {
  router.push('/my-images')
}
</script>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
}

.upload-options {
  margin-top: 20px;
}

.option-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.upload-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.upload-progress {
  margin-top: 20px;
}

.progress-text {
  text-align: center;
  color: #909399;
  font-size: 14px;
  margin-top: 10px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .upload-container {
    padding: 12px;
  }

  .upload-area :deep(.el-upload-dragger) {
    padding: 30px 20px;
  }

  .upload-area :deep(.el-icon--upload) {
    font-size: 50px !important;
  }

  .upload-area :deep(.el-upload__text) {
    font-size: 14px;
  }

  .upload-options :deep(.el-form-item) {
    margin-bottom: 15px;
  }

  .upload-options :deep(.el-form-item__label) {
    width: 80px !important;
    font-size: 13px;
  }

  .option-tip {
    display: block;
    margin-left: 0;
    margin-top: 5px;
  }

  .upload-actions {
    flex-direction: column;
    gap: 8px;
  }

  .upload-actions .el-button {
    width: 100%;
    margin: 0;
  }

  /* 结果表格 */
  .el-table :deep(.el-table__header th),
  .el-table :deep(.el-table__body td) {
    padding: 8px 4px;
    font-size: 13px;
  }
}

@media screen and (max-width: 480px) {
  .upload-container {
    padding: 8px;
  }

  .upload-area :deep(.el-upload-dragger) {
    padding: 20px 15px;
  }

  .upload-area :deep(.el-icon--upload) {
    font-size: 40px !important;
  }

  .upload-options :deep(.el-form-item__label) {
    width: 70px !important;
    font-size: 12px;
  }
}
</style>

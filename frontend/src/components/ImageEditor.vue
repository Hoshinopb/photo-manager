<template>
  <el-dialog
    v-model="visible"
    title="图片编辑"
    width="90%"
    :close-on-click-modal="false"
    @close="handleClose"
    class="image-editor-dialog"
  >
    <div class="editor-container">
      <!-- 左侧：图片预览/裁剪区域 -->
      <div class="editor-main">
        <div class="image-wrapper" ref="imageWrapper" :style="filterStyle">
          <img
            ref="imageRef"
            :src="imageSrc"
            @load="onImageLoad"
            class="edit-image"
            crossorigin="anonymous"
          />
        </div>
      </div>

      <!-- 右侧：编辑工具 -->
      <div class="editor-tools">
        <el-tabs v-model="activeTab">
          <!-- 裁剪 -->
          <el-tab-pane label="裁剪" name="crop">
            <div class="tool-section">
              <div class="crop-presets">
                <el-button size="small" @click="setAspectRatio(0)">自由</el-button>
                <el-button size="small" @click="setAspectRatio(1)">1:1</el-button>
                <el-button size="small" @click="setAspectRatio(4/3)">4:3</el-button>
                <el-button size="small" @click="setAspectRatio(16/9)">16:9</el-button>
                <el-button size="small" @click="setAspectRatio(3/2)">3:2</el-button>
              </div>
              <el-divider />
              <el-button type="primary" @click="applyCrop" :disabled="!cropper">
                <el-icon><Scissor /></el-icon> 应用裁剪
              </el-button>
            </div>
          </el-tab-pane>

          <!-- 旋转/翻转 -->
          <el-tab-pane label="旋转" name="rotate">
            <div class="tool-section">
              <div class="tool-row">
                <span>旋转:</span>
                <el-button-group>
                  <el-button @click="rotate(-90)">
                    <el-icon><RefreshLeft /></el-icon>
                  </el-button>
                  <el-button @click="rotate(90)">
                    <el-icon><RefreshRight /></el-icon>
                  </el-button>
                </el-button-group>
              </div>
              <el-divider />
              <div class="tool-row">
                <span>翻转:</span>
                <el-button-group>
                  <el-button @click="flip('horizontal')">
                    <el-icon><Switch /></el-icon> 水平
                  </el-button>
                  <el-button @click="flip('vertical')">
                    <el-icon><Sort /></el-icon> 垂直
                  </el-button>
                </el-button-group>
              </div>
              <el-divider />
              <el-button @click="resetPosition" :disabled="!cropper">
                <el-icon><Aim /></el-icon> 重置位置
              </el-button>
            </div>
          </el-tab-pane>

          <!-- 色调调整 -->
          <el-tab-pane label="色调" name="adjust">
            <div class="tool-section adjust-section">
              <div class="slider-item">
                <div class="slider-header">
                  <span>亮度</span>
                  <span class="slider-value">{{ adjustments.brightness }}</span>
                </div>
                <div class="slider-wrapper">
                  <el-slider
                    v-model="adjustments.brightness"
                    :min="-100"
                    :max="100"
                    :show-tooltip="true"
                    @change="updatePreviewStyle"
                  />
                </div>
              </div>
              <div class="slider-item">
                <div class="slider-header">
                  <span>对比度</span>
                  <span class="slider-value">{{ adjustments.contrast }}</span>
                </div>
                <div class="slider-wrapper">
                  <el-slider
                    v-model="adjustments.contrast"
                    :min="-100"
                    :max="100"
                    :show-tooltip="true"
                    @change="updatePreviewStyle"
                  />
                </div>
              </div>
              <div class="slider-item">
                <div class="slider-header">
                  <span>饱和度</span>
                  <span class="slider-value">{{ adjustments.saturation }}</span>
                </div>
                <div class="slider-wrapper">
                  <el-slider
                    v-model="adjustments.saturation"
                    :min="-100"
                    :max="100"
                    :show-tooltip="true"
                    @change="updatePreviewStyle"
                  />
                </div>
              </div>
              <el-divider />
              <el-button @click="resetAdjustments">重置色调</el-button>
            </div>
          </el-tab-pane>
        </el-tabs>

        <!-- 操作历史 -->
        <div class="history-section">
          <h4>待应用的编辑</h4>
          <div class="history-list">
            <div v-if="pendingOperations.length === 0" class="no-operations">
              暂无编辑操作
            </div>
            <el-tag
              v-for="(op, index) in pendingOperations"
              :key="index"
              closable
              @close="removeOperation(index)"
              class="operation-tag"
            >
              {{ op.label }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-checkbox v-model="saveAsNew">保存为新图片</el-checkbox>
        <div class="footer-buttons">
          <el-button @click="handleClose">取消</el-button>
          <el-button @click="resetAll">重置全部</el-button>
          <el-button type="primary" @click="saveImage" :loading="saving">
            <el-icon><Check /></el-icon> 保存
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, nextTick, onBeforeUnmount, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Scissor, RefreshLeft, RefreshRight, Switch, Sort, Check, Aim } from '@element-plus/icons-vue'
import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'
import { editImage } from '../utils/imageApi'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  image: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'saved', 'savedAsNew'])

const visible = ref(false)
const imageRef = ref(null)
const imageWrapper = ref(null)
const cropper = ref(null)
const activeTab = ref('crop')
const saving = ref(false)
const saveAsNew = ref(false)

const imageSrc = ref('')
const pendingOperations = ref([])

const adjustments = reactive({
  brightness: 0,
  contrast: 0,
  saturation: 0
})

// CSS 滤镜预览样式 - 应用到整个 wrapper 和 cropper 容器
const filterStyle = computed(() => {
  // 将 -100~100 的值转换为 CSS filter 需要的值
  const brightness = 100 + adjustments.brightness
  const contrast = 100 + adjustments.contrast
  const saturate = 100 + adjustments.saturation
  
  return {
    filter: `brightness(${brightness}%) contrast(${contrast}%) saturate(${saturate}%)`
  }
})

// 更新预览样式（滑块改变时触发）
const updatePreviewStyle = () => {
  // 滤镜预览由 computed filterStyle 自动更新
}

// 监听 modelValue
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.image) {
    imageSrc.value = props.image.file_url
    resetAll()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
  if (!val) {
    destroyCropper()
  }
})

// 图片加载完成后初始化 Cropper
const onImageLoad = () => {
  nextTick(() => {
    initCropper()
  })
}

// 初始化 Cropper
const initCropper = () => {
  destroyCropper()
  
  if (imageRef.value && imageWrapper.value) {
    // 获取容器尺寸
    const containerRect = imageWrapper.value.getBoundingClientRect()
    
    cropper.value = new Cropper(imageRef.value, {
      viewMode: 1,  // 限制图片在容器内
      dragMode: 'move',  // 默认拖动图片而非裁剪框
      aspectRatio: NaN,
      autoCropArea: 1,  // 裁剪框默认和图片一样大
      restore: false,
      guides: true,
      center: true,
      highlight: false,
      cropBoxMovable: true,
      cropBoxResizable: true,
      toggleDragModeOnDblclick: true,  // 双击切换拖动模式
      minContainerWidth: containerRect.width || 400,
      minContainerHeight: containerRect.height || 400,
      background: true,
      responsive: true,
      checkCrossOrigin: false,
      movable: true,  // 允许移动图片
      zoomable: true, // 允许缩放图片
      rotatable: true,
      scalable: true,
      ready() {
        // Cropper 准备就绪，将图片居中到画布中心
        if (cropper.value) {
          centerImageInContainer()
        }
      }
    })
  }
}

// 将图片居中到容器中心（基于图片和画布中心，而非裁剪框）
const centerImageInContainer = () => {
  if (!cropper.value) return
  
  nextTick(() => {
    if (!cropper.value) return
    
    const containerData = cropper.value.getContainerData()
    const imageData = cropper.value.getImageData()
    
    // 如果图片数据无效，跳过
    if (!imageData.naturalWidth || !imageData.naturalHeight) return
    
    // 计算缩放比例，让图片完全在容器内显示（留10%边距）
    const scaleX = (containerData.width * 0.9) / imageData.naturalWidth
    const scaleY = (containerData.height * 0.9) / imageData.naturalHeight
    const scale = Math.min(scaleX, scaleY, 1) // 不放大超过原始尺寸
    
    // 计算新尺寸
    const newWidth = imageData.naturalWidth * scale
    const newHeight = imageData.naturalHeight * scale
    
    // 精确计算居中位置（基于容器中心）
    const newLeft = Math.round((containerData.width - newWidth) / 2)
    const newTop = Math.round((containerData.height - newHeight) / 2)
    
    // 设置画布（图片）数据，使图片居中
    cropper.value.setCanvasData({
      width: newWidth,
      height: newHeight,
      left: newLeft,
      top: newTop
    })
  })
}

// 销毁 Cropper
const destroyCropper = () => {
  if (cropper.value) {
    cropper.value.destroy()
    cropper.value = null
  }
}

// 设置裁剪比例
const setAspectRatio = (ratio) => {
  if (cropper.value) {
    cropper.value.setAspectRatio(ratio === 0 ? NaN : ratio)
  }
}

// 应用裁剪
const applyCrop = () => {
  if (!cropper.value) return
  
  const cropData = cropper.value.getData(true)
  
  // 检查裁剪区域是否有效
  if (cropData.width <= 0 || cropData.height <= 0) {
    ElMessage.warning('请先选择裁剪区域')
    return
  }
  
  pendingOperations.value.push({
    type: 'crop',
    data: {
      x: Math.round(cropData.x),
      y: Math.round(cropData.y),
      width: Math.round(cropData.width),
      height: Math.round(cropData.height)
    },
    label: `裁剪 (${Math.round(cropData.width)}×${Math.round(cropData.height)})`
  })
  
  // 更新预览 - 使用原始尺寸获取裁剪后的画布
  const canvas = cropper.value.getCroppedCanvas({
    imageSmoothingEnabled: true,
    imageSmoothingQuality: 'high'
  })
  
  if (canvas) {
    // 销毁当前 cropper
    destroyCropper()
    
    // 更新图片源
    imageSrc.value = canvas.toDataURL('image/png')
    
    // 图片会在 onImageLoad 中重新初始化 cropper
    ElMessage.success('裁剪已应用')
  }
}

// 旋转 - 注意：Cropper.js 的 rotate 是顺时针，但后端 PIL 的 transpose 是逆时针
// 所以我们需要取反保存的角度
const rotate = (angle) => {
  if (cropper.value) {
    // 旋转图片 - Cropper.js 的旋转是顺时针
    cropper.value.rotate(angle)
    
    // 使用 setTimeout 确保旋转动画完成后再重置位置
    setTimeout(() => {
      resetPosition()
    }, 50)
    
    // 记录操作 - 取反角度以匹配后端 PIL 的旋转方向
    pendingOperations.value.push({
      type: 'rotate',
      data: { angle: -angle },  // 取反：前端顺时针 -> 后端逆时针
      label: `旋转 ${angle}°`
    })
  }
}

// 重置位置 - 居中并缩放图片以适应容器（基于图片和画布中心）
const resetPosition = () => {
  if (!cropper.value) return
  
  nextTick(() => {
    if (!cropper.value) return
    
    const containerData = cropper.value.getContainerData()
    const imageData = cropper.value.getImageData()
    
    // 如果图片数据无效，跳过
    if (!imageData.naturalWidth || !imageData.naturalHeight) return
    
    // 获取当前旋转后的实际尺寸
    const canvasData = cropper.value.getCanvasData()
    const currentWidth = canvasData.naturalWidth || imageData.naturalWidth
    const currentHeight = canvasData.naturalHeight || imageData.naturalHeight
    
    // 计算缩放比例，让图片完全在容器内显示（留10%边距）
    const scaleX = (containerData.width * 0.9) / currentWidth
    const scaleY = (containerData.height * 0.9) / currentHeight
    const scale = Math.min(scaleX, scaleY)
    
    // 计算新尺寸
    const newWidth = currentWidth * scale
    const newHeight = currentHeight * scale
    
    // 精确计算居中位置（基于容器中心）
    const newLeft = Math.round((containerData.width - newWidth) / 2)
    const newTop = Math.round((containerData.height - newHeight) / 2)
    
    // 设置画布数据，使图片居中于画布/容器中心
    cropper.value.setCanvasData({
      width: newWidth,
      height: newHeight,
      left: newLeft,
      top: newTop
    })
  })
}

// 翻转
const flip = (direction) => {
  if (cropper.value) {
    const scaleX = cropper.value.getData().scaleX || 1
    const scaleY = cropper.value.getData().scaleY || 1
    
    if (direction === 'horizontal') {
      cropper.value.scaleX(-scaleX)
    } else {
      cropper.value.scaleY(-scaleY)
    }
    
    pendingOperations.value.push({
      type: 'flip',
      data: { direction },
      label: direction === 'horizontal' ? '水平翻转' : '垂直翻转'
    })
  }
}

// 重置色调
const resetAdjustments = () => {
  adjustments.brightness = 0
  adjustments.contrast = 0
  adjustments.saturation = 0
}

// 重置全部
const resetAll = () => {
  pendingOperations.value = []
  resetAdjustments()
  saveAsNew.value = false
  
  if (props.image) {
    // 重新加载原始图片
    imageSrc.value = props.image.file_url + '?t=' + Date.now()  // 添加时间戳避免缓存
    nextTick(() => {
      initCropper()
    })
  }
}

// 移除操作 - 需要重新加载原始图片并重新应用剩余操作
const removeOperation = (index) => {
  const removedOp = pendingOperations.value[index]
  pendingOperations.value.splice(index, 1)
  
  // 如果移除的是裁剪或旋转操作，需要重置图片
  if (removedOp.type === 'crop' || removedOp.type === 'rotate' || removedOp.type === 'flip') {
    // 重新从原始图片开始
    resetAll()
    // 注意：这会清空所有操作，如果需要保留其他操作，需要更复杂的逻辑
    // 目前简化处理：移除任何图像变换操作都会重置
    ElMessage.info('已重置图片，请重新编辑')
  }
}

// 保存图片
const saveImage = async () => {
  if (!props.image) return
  
  // 检查是否有编辑操作
  const hasAdjustments = adjustments.brightness !== 0 || 
                         adjustments.contrast !== 0 || 
                         adjustments.saturation !== 0
  
  if (pendingOperations.value.length === 0 && !hasAdjustments) {
    ElMessage.warning('没有需要保存的编辑操作')
    return
  }
  
  saving.value = true
  
  try {
    // 构建编辑数据
    const editData = {
      save_as_new: saveAsNew.value
    }
    
    // 添加待处理的操作
    for (const op of pendingOperations.value) {
      if (op.type === 'crop') {
        editData.crop = op.data
      } else if (op.type === 'rotate') {
        // 累加旋转角度
        if (!editData.rotate) {
          editData.rotate = { angle: 0 }
        }
        editData.rotate.angle += op.data.angle
      } else if (op.type === 'flip') {
        editData.flip = op.data
      }
    }
    
    // 添加色调调整
    if (adjustments.brightness !== 0) {
      editData.brightness = { value: adjustments.brightness }
    }
    if (adjustments.contrast !== 0) {
      editData.contrast = { value: adjustments.contrast }
    }
    if (adjustments.saturation !== 0) {
      editData.saturation = { value: adjustments.saturation }
    }
    
    const response = await editImage(props.image.id, editData)
    
    ElMessage.success(response.data.detail || '保存成功')
    
    // 如果是保存为新图片，发出 savedAsNew 事件
    if (saveAsNew.value && response.data.image) {
      emit('savedAsNew', response.data.image)
    } else {
      emit('saved', response.data.image)
    }
    handleClose()
    
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
  destroyCropper()
}

onBeforeUnmount(() => {
  destroyCropper()
})
</script>

<style scoped>
.image-editor-dialog :deep(.el-dialog__body) {
  padding: 10px 20px;
}

.editor-container {
  display: flex;
  gap: 20px;
  height: 60vh;
}

.editor-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a1a;
  border-radius: 8px;
  overflow: hidden;
  min-height: 400px;
}

.image-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.edit-image {
  max-width: 100%;
  max-height: 100%;
  display: block;
}

.editor-tools {
  width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-tools :deep(.el-tabs) {
  flex-shrink: 0;
}

.tool-section {
  padding: 10px 0;
}

.adjust-section {
  padding-right: 10px;
}

.crop-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tool-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.tool-row span {
  width: 50px;
  flex-shrink: 0;
}

.slider-item {
  margin-bottom: 20px;
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.slider-header span:first-child {
  color: #606266;
}

.slider-value {
  color: #409eff;
  font-weight: 500;
  min-width: 40px;
  text-align: right;
}

.slider-wrapper {
  padding: 0 10px;
}

.history-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.history-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
  flex-shrink: 0;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  max-height: 150px;
}

.no-operations {
  color: #909399;
  font-size: 13px;
}

.operation-tag {
  margin: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-buttons {
  display: flex;
  gap: 10px;
}

/* Cropper.js 样式覆盖 */
.image-wrapper :deep(.cropper-container) {
  width: 100% !important;
  height: 100% !important;
  max-width: 100%;
  max-height: 100%;
}

.image-wrapper :deep(.cropper-wrap-box),
.image-wrapper :deep(.cropper-canvas),
.image-wrapper :deep(.cropper-drag-box),
.image-wrapper :deep(.cropper-crop-box) {
  /* 继承父元素的 filter 样式 */
  transition: filter 0.2s ease;
}

:deep(.cropper-view-box) {
  outline: 1px solid #409eff;
  outline-color: rgba(64, 158, 255, 0.75);
}

:deep(.cropper-line) {
  background-color: #409eff;
}

:deep(.cropper-point) {
  background-color: #409eff;
}

/* 背景棋盘格样式 */
:deep(.cropper-bg) {
  background-color: #1a1a1a;
  background-image: 
    linear-gradient(45deg, #2a2a2a 25%, transparent 25%),
    linear-gradient(-45deg, #2a2a2a 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #2a2a2a 75%),
    linear-gradient(-45deg, transparent 75%, #2a2a2a 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .image-editor-dialog :deep(.el-dialog) {
    width: 95% !important;
    margin: 10px auto;
  }

  .image-editor-dialog :deep(.el-dialog__body) {
    padding: 10px;
  }

  .editor-container {
    flex-direction: column;
    height: auto;
    gap: 15px;
  }

  .editor-main {
    min-height: 250px;
    max-height: 40vh;
  }

  .editor-tools {
    width: 100%;
    max-height: 300px;
    overflow-y: auto;
  }

  .editor-tools :deep(.el-tabs__header) {
    margin-bottom: 10px;
  }

  .editor-tools :deep(.el-tabs__item) {
    padding: 0 10px;
    font-size: 13px;
  }

  .tool-section {
    padding: 5px 0;
  }

  .crop-presets {
    gap: 6px;
  }

  .crop-presets .el-button {
    padding: 6px 10px;
    font-size: 12px;
  }

  .tool-row {
    flex-wrap: wrap;
    gap: 8px;
  }

  .tool-row span {
    width: 100%;
    margin-bottom: 4px;
  }

  .slider-item {
    margin-bottom: 15px;
  }

  .slider-wrapper {
    padding: 0 5px;
  }

  .history-section {
    margin-top: 15px;
    padding-top: 12px;
  }

  .history-list {
    max-height: 100px;
  }

  .dialog-footer {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }

  .footer-buttons {
    justify-content: center;
    flex-wrap: wrap;
  }

  .footer-buttons .el-button {
    flex: 1;
    min-width: 0;
  }
}

@media screen and (max-width: 480px) {
  .editor-main {
    min-height: 200px;
    max-height: 35vh;
  }

  .editor-tools :deep(.el-tabs__item) {
    padding: 0 8px;
    font-size: 12px;
  }

  .crop-presets .el-button {
    padding: 5px 8px;
    font-size: 11px;
  }

  .tool-row .el-button-group .el-button {
    padding: 6px 8px;
  }

  .slider-header span:first-child {
    font-size: 13px;
  }
}
</style>

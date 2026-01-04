<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :md="6">
        <el-card class="profile-card">
          <template #header>
            <div class="card-header">
              <span>用户信息</span>
            </div>
          </template>

          <div v-if="userStore.user" class="user-info">
            <div class="avatar" @click="showAvatarSelector = true">
              <el-avatar 
                :size="80" 
                :src="userStore.user.avatar_url" 
                class="clickable-avatar"
              >
                <el-icon :size="40"><UserFilled /></el-icon>
              </el-avatar>
              <div class="avatar-overlay">
                <el-icon><Camera /></el-icon>
                <span>更换头像</span>
              </div>
            </div>
            <div class="info">
              <div class="info-item">
                <span class="label">用户名：</span>
                <span class="value">{{ userStore.user.username }}</span>
              </div>
              <div class="info-item">
                <span class="label">邮箱：</span>
                <span class="value">{{ userStore.user.email }}</span>
              </div>
              <div class="info-item">
                <span class="label">ID：</span>
                <span class="value">{{ userStore.user.id }}</span>
              </div>
              <div class="info-item">
                <span class="label">角色：</span>
                <span class="value">
                  <el-tag v-if="userStore.user.is_superuser" type="danger" effect="dark">超级管理员</el-tag>
                  <el-tag v-else-if="userStore.user.is_staff" type="warning" effect="dark">管理员</el-tag>
                  <el-tag v-else type="info">普通用户</el-tag>
                </span>
              </div>
            </div>
          </div>

          <el-divider />

          <el-button type="danger" @click="handleLogout" :loading="userStore.loading">
            退出登录
          </el-button>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="24" :md="18">
        <el-tabs>
          <el-tab-pane label="编辑个人信息">
            <el-card>
              <el-form
                ref="formRef"
                :model="form"
                :rules="rules"
                label-width="120px"
              >
                <el-form-item label="用户名" prop="username">
                  <el-input
                    v-model="form.username"
                    placeholder="请输入用户名"
                  />
                </el-form-item>

                <el-form-item label="邮箱" prop="email">
                  <el-input
                    v-model="form.email"
                    type="email"
                    placeholder="请输入邮箱地址"
                  />
                </el-form-item>

                <el-form-item>
                  <el-button
                    type="primary"
                    @click="handleUpdateProfile"
                    :loading="userStore.loading"
                  >
                    保存修改
                  </el-button>
                  <el-button @click="resetForm">重置</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-tab-pane>

          <el-tab-pane label="修改密码">
            <el-card>
              <el-form
                ref="passwordFormRef"
                :model="passwordForm"
                :rules="passwordRules"
                label-width="120px"
              >
                <el-form-item label="当前密码" prop="current_password">
                  <el-input
                    v-model="passwordForm.current_password"
                    type="password"
                    placeholder="请输入当前密码"
                    show-password
                  />
                </el-form-item>

                <el-form-item label="新密码" prop="new_password">
                  <el-input
                    v-model="passwordForm.new_password"
                    type="password"
                    placeholder="请输入新密码"
                    show-password
                  />
                </el-form-item>

                <el-form-item label="确认密码" prop="re_new_password">
                  <el-input
                    v-model="passwordForm.re_new_password"
                    type="password"
                    placeholder="请再次输入新密码"
                    show-password
                  />
                </el-form-item>

                <el-form-item>
                  <el-button
                    type="primary"
                    @click="handleChangePassword"
                    :loading="userStore.loading"
                  >
                    修改密码
                  </el-button>
                  <el-button @click="resetPasswordForm">重置</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-tab-pane>

          <el-tab-pane label="AI 设置">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>Vision API Key</span>
                  <el-tag v-if="hasApiKey" type="success" size="small">已配置</el-tag>
                  <el-tag v-else type="info" size="small">未配置</el-tag>
                </div>
              </template>
              
              <el-alert 
                type="info" 
                :closable="false" 
                style="margin-bottom: 16px;"
              >
                <template #title>
                  AI 描述功能需要配置 Vision API Key。您可以从 
                  <el-link type="primary" href="https://siliconflow.cn" target="_blank">SiliconFlow</el-link> 
                  获取 API Key。
                </template>
              </el-alert>

              <div v-if="hasApiKey" class="api-key-display">
                <el-input
                  v-model="maskedApiKey"
                  disabled
                  placeholder="API Key"
                >
                  <template #prepend>当前密钥</template>
                </el-input>
                <div class="api-key-actions">
                  <el-button type="primary" @click="showApiKeyInput = true">
                    更换密钥
                  </el-button>
                  <el-popconfirm title="确定删除 API Key 吗？" @confirm="deleteApiKey">
                    <template #reference>
                      <el-button type="danger" :loading="deletingApiKey">
                        删除密钥
                      </el-button>
                    </template>
                  </el-popconfirm>
                </div>
              </div>

              <div v-if="!hasApiKey || showApiKeyInput" class="api-key-form">
                <el-form @submit.prevent="saveApiKey">
                  <el-form-item>
                    <el-input
                      v-model="newApiKey"
                      type="password"
                      show-password
                      placeholder="请输入您的 Vision API Key"
                      clearable
                    >
                      <template #prepend>API Key</template>
                    </el-input>
                  </el-form-item>
                  <el-form-item>
                    <el-button 
                      type="primary" 
                      @click="saveApiKey" 
                      :loading="savingApiKey"
                      :disabled="!newApiKey"
                    >
                      保存密钥
                    </el-button>
                    <el-button v-if="showApiKeyInput" @click="showApiKeyInput = false">
                      取消
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>

    <!-- 头像选择弹窗 -->
    <el-dialog
      v-model="showAvatarSelector"
      title="选择头像"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="avatar-selector">
        <div v-if="loadingImages" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>
        <el-empty v-else-if="myImages.length === 0" description="暂无图片，请先上传图片">
          <el-button type="primary" @click="$router.push('/upload')">去上传</el-button>
        </el-empty>
        <div v-else class="avatar-grid">
          <div 
            v-for="image in myImages" 
            :key="image.id" 
            class="avatar-option"
            :class="{ selected: selectedAvatarId === image.id }"
            @click="selectedAvatarId = image.id"
          >
            <el-image
              :src="image.thumbnail_url || image.file_url"
              fit="cover"
              class="avatar-preview"
            />
            <el-icon v-if="selectedAvatarId === image.id" class="check-icon"><Check /></el-icon>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showAvatarSelector = false">取消</el-button>
        <el-button type="primary" @click="saveAvatar" :loading="savingAvatar" :disabled="!selectedAvatarId">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UserFilled, Camera, Check } from '@element-plus/icons-vue'
import { useUserStore } from '../store/userStore'
import { getMyImages } from '../utils/imageApi'
import apiClient from '../utils/api'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const passwordFormRef = ref(null)
const showAvatarSelector = ref(false)
const loadingImages = ref(false)
const myImages = ref([])
const selectedAvatarId = ref(null)
const savingAvatar = ref(false)

// API Key 相关
const hasApiKey = ref(false)
const maskedApiKey = ref('')
const newApiKey = ref('')
const showApiKeyInput = ref(false)
const savingApiKey = ref(false)
const deletingApiKey = ref(false)

const form = reactive({
  username: '',
  email: '',
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  re_new_password: '',
})

const validateNewPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入新密码'))
  } else if (value.length < 6) {
    callback(new Error('密码至少6个字符'))
  } else {
    if (passwordForm.re_new_password !== '') {
      passwordFormRef.value?.validateField('re_new_password')
    }
    callback()
  }
}

const validateReNewPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'))
  } else if (value !== passwordForm.new_password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '邮箱地址格式不正确', trigger: 'blur' },
  ],
}

const passwordRules = {
  current_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' },
  ],
  new_password: [{ validator: validateNewPassword, trigger: 'blur' }],
  re_new_password: [{ validator: validateReNewPassword, trigger: 'blur' }],
}

const initializeForm = () => {
  if (userStore.user) {
    form.username = userStore.user.username || ''
    form.email = userStore.user.email || ''
  }
}

const resetForm = () => {
  initializeForm()
}

const resetPasswordForm = () => {
  passwordForm.current_password = ''
  passwordForm.new_password = ''
  passwordForm.re_new_password = ''
}

// 加载用户图片列表
const loadMyImages = async () => {
  loadingImages.value = true
  try {
    const response = await getMyImages()
    myImages.value = response.data
    // 如果用户已有头像，找到对应的图片
    if (userStore.user?.avatar_id) {
      selectedAvatarId.value = userStore.user.avatar_id
    }
  } catch (error) {
    console.error('加载图片失败:', error)
  } finally {
    loadingImages.value = false
  }
}

// 保存头像
const saveAvatar = async () => {
  if (!selectedAvatarId.value) return
  
  savingAvatar.value = true
  try {
    const success = await userStore.updateUser({
      avatar_id: selectedAvatarId.value
    })
    if (success) {
      ElMessage.success('头像更新成功')
      showAvatarSelector.value = false
      // 刷新页面以确保头像正确显示
      window.location.reload()
    }
  } catch (error) {
    ElMessage.error('头像更新失败')
  } finally {
    savingAvatar.value = false
  }
}

// 打开头像选择器时加载图片
const openAvatarSelector = () => {
  showAvatarSelector.value = true
  loadMyImages()
}

// API Key 管理函数
const loadApiKeyStatus = async () => {
  try {
    const response = await apiClient.get('/api/user/vision-api-key/')
    hasApiKey.value = response.data.has_api_key
    maskedApiKey.value = response.data.masked_key || ''
  } catch (error) {
    console.error('获取 API Key 状态失败:', error)
  }
}

const saveApiKey = async () => {
  if (!newApiKey.value) return
  
  savingApiKey.value = true
  try {
    const response = await apiClient.post('/api/user/vision-api-key/', {
      api_key: newApiKey.value
    })
    hasApiKey.value = true
    maskedApiKey.value = response.data.masked_key
    newApiKey.value = ''
    showApiKeyInput.value = false
    ElMessage.success('API Key 保存成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'API Key 保存失败')
  } finally {
    savingApiKey.value = false
  }
}

const deleteApiKey = async () => {
  deletingApiKey.value = true
  try {
    await apiClient.delete('/api/user/vision-api-key/')
    hasApiKey.value = false
    maskedApiKey.value = ''
    ElMessage.success('API Key 已删除')
  } catch (error) {
    ElMessage.error('删除失败')
  } finally {
    deletingApiKey.value = false
  }
}

// 监听弹窗打开
import { watch } from 'vue'
watch(showAvatarSelector, (val) => {
  if (val) {
    loadMyImages()
  }
})

const handleUpdateProfile = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      const success = await userStore.updateUser({
        username: form.username,
        email: form.email,
      })
      if (success) {
        ElMessage.success('个人信息已更新')
      }
    }
  })
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      const success = await userStore.changePassword(
        passwordForm.new_password,
        passwordForm.re_new_password,
        passwordForm.current_password
      )
      if (success) {
        ElMessage.success('密码已修改')
        resetPasswordForm()
      }
    }
  })
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      await userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    })
    .catch(() => {})
}

onMounted(() => {
  initializeForm()
  loadApiKeyStatus()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  text-align: center;
}

.avatar {
  margin-bottom: 20px;
}

.info {
  text-align: left;
}

.info-item {
  display: flex;
  margin-bottom: 12px;
  font-size: 14px;
}

.info-item .label {
  font-weight: bold;
  width: 80px;
}

.info-item .value {
  flex: 1;
  word-break: break-all;
}

/* 头像样式 */
.avatar {
  position: relative;
  cursor: pointer;
  display: inline-block;
}

.clickable-avatar {
  transition: opacity 0.3s;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  opacity: 0;
  transition: opacity 0.3s;
  font-size: 12px;
}

.avatar:hover .avatar-overlay {
  opacity: 1;
}

.avatar:hover .clickable-avatar {
  opacity: 0.7;
}

/* 头像选择弹窗样式 */
.avatar-selector {
  max-height: 400px;
  overflow-y: auto;
}

.avatar-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.avatar-option {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 3px solid transparent;
  transition: all 0.2s;
}

.avatar-option:hover {
  border-color: #409eff;
}

.avatar-option.selected {
  border-color: #67c23a;
}

.avatar-preview {
  width: 100%;
  height: 100%;
}

.check-icon {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #67c23a;
  color: white;
  border-radius: 50%;
  padding: 2px;
  font-size: 16px;
}

.loading-container {
  padding: 20px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .profile-container {
    padding: 12px;
  }

  .profile-card {
    margin-bottom: 15px;
  }

  .avatar :deep(.el-avatar) {
    width: 60px !important;
    height: 60px !important;
  }

  .avatar-overlay {
    width: 60px;
    height: 60px;
  }

  .avatar-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .info-item {
    flex-direction: column;
    margin-bottom: 10px;
  }

  .info-item .label {
    width: 100%;
    margin-bottom: 4px;
  }

  /* 标签页适配 */
  .el-tabs :deep(.el-tabs__header) {
    margin-bottom: 10px;
  }

  .el-tabs :deep(.el-tabs__item) {
    padding: 0 12px;
    font-size: 14px;
  }

  /* 表单适配 */
  .el-form :deep(.el-form-item__label) {
    width: 90px !important;
    font-size: 13px;
  }

  .el-form :deep(.el-form-item__content) {
    margin-left: 90px !important;
  }

  .el-form :deep(.el-form-item:last-child .el-button) {
    width: 100%;
    margin-bottom: 8px;
    margin-left: 0;
  }
}

@media screen and (max-width: 480px) {
  .profile-container {
    padding: 8px;
  }

  .avatar :deep(.el-avatar) {
    width: 50px !important;
    height: 50px !important;
  }

  .avatar-overlay {
    width: 50px;
    height: 50px;
    font-size: 10px;
  }

  .avatar-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }

  .el-form :deep(.el-form-item__label) {
    width: 80px !important;
    font-size: 12px;
  }

  .el-form :deep(.el-form-item__content) {
    margin-left: 80px !important;
  }
}

/* API Key 样式 */
.api-key-display {
  margin-bottom: 16px;
}

.api-key-actions {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.api-key-form {
  margin-top: 16px;
}
</style>

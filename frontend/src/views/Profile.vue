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
            <div class="avatar">
              <el-avatar :size="80" icon="UserFilled" />
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

                <el-form-item label="名字" prop="first_name">
                  <el-input
                    v-model="form.first_name"
                    placeholder="请输入名字"
                  />
                </el-form-item>

                <el-form-item label="姓氏" prop="last_name">
                  <el-input
                    v-model="form.last_name"
                    placeholder="请输入姓氏"
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
        </el-tabs>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../store/userStore'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const passwordFormRef = ref(null)

const form = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
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
    form.first_name = userStore.user.first_name || ''
    form.last_name = userStore.user.last_name || ''
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

const handleUpdateProfile = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      const success = await userStore.updateUser({
        username: form.username,
        email: form.email,
        first_name: form.first_name,
        last_name: form.last_name,
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

  .el-form :deep(.el-form-item__label) {
    width: 80px !important;
    font-size: 12px;
  }

  .el-form :deep(.el-form-item__content) {
    margin-left: 80px !important;
  }
}
</style>

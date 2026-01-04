<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <span class="title">注册新账户</span>
        </div>
      </template>

      <el-form
        ref="registerFormRef"
        :model="form"
        :rules="rules"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            clearable
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="form.email"
            type="email"
            placeholder="请输入邮箱地址"
            clearable
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="re_password">
          <el-input
            v-model="form.re_password"
            type="password"
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="handleRegister"
            :loading="userStore.loading"
            style="width: 100%"
          >
            注册
          </el-button>
        </el-form-item>

        <div style="text-align: center">
          <span>已有账户？</span>
          <el-link type="primary" @click="goToLogin">登录</el-link>
        </div>
      </el-form>

      <el-alert
        v-if="userStore.error"
        :title="formatError(userStore.error)"
        type="error"
        :closable="true"
        style="margin-top: 16px"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../store/userStore'

const router = useRouter()
const userStore = useUserStore()

const registerFormRef = ref(null)

const form = reactive({
  username: '',
  email: '',
  password: '',
  re_password: '',
})

const validatePassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码至少6个字符'))
  } else {
    if (form.re_password !== '') {
      registerFormRef.value?.validateField('re_password')
    }
    callback()
  }
}

const validateRePassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
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
  password: [{ validator: validatePassword, trigger: 'blur' }],
  re_password: [{ validator: validateRePassword, trigger: 'blur' }],
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      const success = await userStore.register(
        form.username,
        form.email,
        form.password,
        form.re_password
      )
      if (success) {
        ElMessage.success('注册成功，请登录')
        router.push('/login')
      }
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}

const formatError = (error) => {
  if (typeof error === 'string') {
    return error
  }
  if (typeof error === 'object') {
    return Object.values(error)
      .flat()
      .join('; ')
  }
  return '操作失败'
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  width: 100%;
  max-width: 450px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: center;
  align-items: center;
}

.title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .register-container {
    padding: 20px;
    min-height: calc(100vh - 50px);
  }

  .register-card {
    max-width: 100%;
  }

  .title {
    font-size: 20px;
  }

  .register-card :deep(.el-form-item__label) {
    font-size: 14px;
  }
}

@media screen and (max-width: 480px) {
  .register-container {
    padding: 15px;
    align-items: flex-start;
    padding-top: 40px;
  }

  .title {
    font-size: 18px;
  }
}
</style>

<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :md="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>欢迎使用图片管理系统</span>
            </div>
          </template>

          <div v-if="userStore.user" class="welcome-content">
            <el-empty description="功能开发中...">
              <template #default>
                <div class="welcome-message">
                  <h2>欢迎，{{ userStore.user.username }}！</h2>
                  <p>图片管理系统已经为您准备好了</p>
                  <p style="font-size: 14px; color: #909399">
                    您可以在个人中心管理您的账户信息
                  </p>
                </div>
              </template>
            </el-empty>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :xs="24" :sm="12" :md="6">
        <el-statistic title="用户名" :value="userStore.user?.username || '-'" />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-statistic
          title="邮箱"
          :value="userStore.user?.email || '-'"
          style="width: 100%"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-statistic
          title="用户ID"
          :value="userStore.user?.id || '-'"
          style="width: 100%"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-statistic
          title="账户状态"
          :value="userStore.user ? '活跃' : '未登录'"
          style="width: 100%"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { useUserStore } from '../store/userStore'

const userStore = useUserStore()
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-content {
  text-align: center;
}

.welcome-message {
  margin-top: 20px;
}

.welcome-message h2 {
  margin: 20px 0 10px 0;
  color: #333;
}

.welcome-message p {
  color: #666;
  margin: 10px 0;
}
</style>

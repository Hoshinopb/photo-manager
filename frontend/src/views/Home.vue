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
            <div class="welcome-message">
              <h2>欢迎，{{ userStore.user.username }}！</h2>
              <p>图片管理系统已经为您准备好了</p>
            </div>
            
            <el-row :gutter="20" class="quick-actions">
              <el-col :xs="24" :sm="12" :md="6">
                <el-card shadow="hover" class="action-card" @click="$router.push('/gallery')">
                  <el-icon size="48" color="#409eff"><PictureFilled /></el-icon>
                  <h3>图片库</h3>
                  <p>浏览所有公开图片</p>
                </el-card>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-card shadow="hover" class="action-card" @click="$router.push('/upload')">
                  <el-icon size="48" color="#67c23a"><Upload /></el-icon>
                  <h3>上传图片</h3>
                  <p>支持拖拽上传</p>
                </el-card>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-card shadow="hover" class="action-card" @click="$router.push('/my-images')">
                  <el-icon size="48" color="#e6a23c"><Picture /></el-icon>
                  <h3>我的图片</h3>
                  <p>管理我的图片</p>
                </el-card>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-card shadow="hover" class="action-card" @click="$router.push('/profile')">
                  <el-icon size="48" color="#909399"><User /></el-icon>
                  <h3>个人中心</h3>
                  <p>管理账户信息</p>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic title="用户名" :value="userStore.user?.username || '-'" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic title="邮箱" :value="userStore.user?.email || '-'" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic title="用户ID" :value="userStore.user?.id || '-'" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic title="账户状态" :value="userStore.user ? '活跃' : '未登录'" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { Upload, Picture, User, PictureFilled } from '@element-plus/icons-vue'
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
  margin-bottom: 30px;
}

.welcome-message h2 {
  margin: 0 0 10px 0;
  color: #333;
}

.welcome-message p {
  color: #666;
  margin: 0;
}

.quick-actions {
  margin-top: 20px;
}

.action-card {
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  margin-bottom: 20px;
}

.action-card:hover {
  transform: translateY(-5px);
}

.action-card h3 {
  margin: 15px 0 10px 0;
  color: #333;
}

.action-card p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}
</style>

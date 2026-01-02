<template>
  <el-container style="height: 100vh">
    <el-header class="app-header">
      <div class="header-content">
        <div class="logo">
          <span class="logo-text">📷 图片管理</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          class="header-menu"
          v-if="userStore.isAuthenticated"
          router
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/gallery">图片库</el-menu-item>
          <el-menu-item index="/upload">上传图片</el-menu-item>
          <el-menu-item index="/my-images">我的图片</el-menu-item>
          <el-menu-item index="/profile">个人中心</el-menu-item>
        </el-menu>
        <div class="header-right">
          <el-dropdown v-if="userStore.isAuthenticated" @command="handleCommand">
            <span class="el-dropdown-link">
              {{ userStore.user?.username || '用户' }}
              <el-icon class="el-icon--right">
                <arrow-down />
              </el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <div v-else class="auth-buttons">
            <el-button type="primary" text @click="goToLogin">登录</el-button>
            <el-button @click="goToRegister">注册</el-button>
          </div>
        </div>
      </div>
    </el-header>

    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from './store/userStore'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => {
  return route.path || '/'
})

const handleCommand = async (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
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
}

const goToLogin = () => {
  router.push('/login')
}

const goToRegister = () => {
  router.push('/register')
}

onMounted(async () => {
  await userStore.initializeUser()
})
</script>

<style scoped>
.app-header {
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0;
  padding: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
}

.logo-text {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.header-menu {
  flex: 1;
  border: none;
  margin: 0 30px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.el-dropdown-link {
  cursor: pointer;
  color: #409eff;
  display: flex;
  align-items: center;
  gap: 5px;
}

.el-dropdown-link:hover {
  color: #66b1ff;
}

.auth-buttons {
  display: flex;
  gap: 10px;
}

.app-main {
  overflow: auto;
  background-color: #f5f5f5;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

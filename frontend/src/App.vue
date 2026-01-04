<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <!-- Logo -->
        <div class="logo" @click="goHome">
          <span class="logo-text">📷 图片管理</span>
        </div>

        <!-- 桌面端导航菜单 -->
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          class="header-menu desktop-menu"
          v-if="userStore.isAuthenticated"
          router
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/gallery">图片库</el-menu-item>
          <el-menu-item index="/upload">上传</el-menu-item>
          <el-menu-item index="/my-images">我的图片</el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/admin" class="admin-menu">
            <el-icon><Setting /></el-icon>管理
          </el-menu-item>
        </el-menu>

        <!-- 桌面端右侧用户菜单 -->
        <div class="header-right desktop-only">
          <el-dropdown v-if="userStore.isAuthenticated" @command="handleCommand">
            <span class="el-dropdown-link">
              {{ userStore.user?.username || '用户' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <div v-else class="auth-buttons">
            <el-button type="primary" text @click="goToLogin">登录</el-button>
            <el-button @click="goToRegister">注册</el-button>
          </div>
        </div>

        <!-- 移动端汉堡菜单按钮 -->
        <div class="mobile-menu-btn mobile-only" @click="toggleMobileMenu">
          <el-icon :size="24"><Menu /></el-icon>
        </div>
      </div>
    </el-header>

    <!-- 移动端侧边抽屉菜单 -->
    <el-drawer
      v-model="mobileMenuVisible"
      direction="rtl"
      size="70%"
      :show-close="false"
      class="mobile-drawer"
    >
      <template #header>
        <div class="drawer-header">
          <span class="drawer-title">📷 图片管理</span>
          <el-icon class="drawer-close" @click="mobileMenuVisible = false"><Close /></el-icon>
        </div>
      </template>

      <div class="mobile-menu-content">
        <!-- 用户信息 -->
        <div v-if="userStore.isAuthenticated" class="mobile-user-info">
          <el-avatar :size="50" :icon="UserFilled" />
          <div class="user-details">
            <div class="username">{{ userStore.user?.username || '用户' }}</div>
            <div class="email">{{ userStore.user?.email }}</div>
          </div>
        </div>

        <!-- 导航菜单 -->
        <el-menu
          :default-active="activeMenu"
          class="mobile-nav-menu"
          @select="handleMobileMenuSelect"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/gallery">
            <el-icon><Picture /></el-icon>
            <span>图片库</span>
          </el-menu-item>
          <el-menu-item index="/upload">
            <el-icon><Upload /></el-icon>
            <span>上传图片</span>
          </el-menu-item>
          <el-menu-item index="/my-images">
            <el-icon><FolderOpened /></el-icon>
            <span>我的图片</span>
          </el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/admin">
            <el-icon><Setting /></el-icon>
            <span>管理后台</span>
          </el-menu-item>
          <el-menu-item v-if="userStore.isAuthenticated" index="/profile">
            <el-icon><User /></el-icon>
            <span>个人中心</span>
          </el-menu-item>
        </el-menu>

        <!-- 底部操作 -->
        <div class="mobile-menu-footer">
          <template v-if="userStore.isAuthenticated">
            <el-button type="danger" plain @click="handleLogout" style="width: 100%">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-button>
          </template>
          <template v-else>
            <el-button type="primary" @click="goToLogin" style="width: 100%; margin-bottom: 10px">
              登录
            </el-button>
            <el-button @click="goToRegister" style="width: 100%">
              注册
            </el-button>
          </template>
        </div>
      </div>
    </el-drawer>

    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>

    <!-- 移动端底部导航栏 -->
    <div v-if="userStore.isAuthenticated" class="mobile-tabbar mobile-only">
      <div 
        class="tabbar-item" 
        :class="{ active: activeMenu === '/' }"
        @click="navigateTo('/')"
      >
        <el-icon><HomeFilled /></el-icon>
        <span>首页</span>
      </div>
      <div 
        class="tabbar-item" 
        :class="{ active: activeMenu === '/gallery' }"
        @click="navigateTo('/gallery')"
      >
        <el-icon><Picture /></el-icon>
        <span>图库</span>
      </div>
      <div 
        class="tabbar-item upload-btn" 
        @click="navigateTo('/upload')"
      >
        <el-icon><Plus /></el-icon>
      </div>
      <div 
        class="tabbar-item" 
        :class="{ active: activeMenu === '/my-images' }"
        @click="navigateTo('/my-images')"
      >
        <el-icon><FolderOpened /></el-icon>
        <span>我的</span>
      </div>
      <div 
        class="tabbar-item" 
        :class="{ active: activeMenu === '/profile' }"
        @click="navigateTo('/profile')"
      >
        <el-icon><User /></el-icon>
        <span>我</span>
      </div>
    </div>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowDown, Setting, Menu, Close, UserFilled, 
  HomeFilled, Picture, Upload, FolderOpened, 
  User, SwitchButton, Plus 
} from '@element-plus/icons-vue'
import { useUserStore } from './store/userStore'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const mobileMenuVisible = ref(false)

const activeMenu = computed(() => {
  return route.path || '/'
})

const goHome = () => {
  router.push('/')
}

const toggleMobileMenu = () => {
  mobileMenuVisible.value = !mobileMenuVisible.value
}

const handleMobileMenuSelect = (index) => {
  router.push(index)
  mobileMenuVisible.value = false
}

const navigateTo = (path) => {
  router.push(path)
}

const handleCommand = async (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    handleLogout()
  }
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      mobileMenuVisible.value = false
      await userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    })
    .catch(() => {})
}

const goToLogin = () => {
  mobileMenuVisible.value = false
  router.push('/login')
}

const goToRegister = () => {
  mobileMenuVisible.value = false
  router.push('/register')
}

onMounted(async () => {
  await userStore.initializeUser()
})
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0;
  padding: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  height: 60px;
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
  cursor: pointer;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.header-menu {
  flex: 1;
  border: none;
  margin: 0 30px;
}

.header-menu .admin-menu {
  color: #f56c6c !important;
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
  flex: 1;
  overflow: auto;
  background-color: #f5f5f5;
  padding-bottom: 0;
}

/* 移动端菜单按钮 */
.mobile-menu-btn {
  display: none;
  cursor: pointer;
  padding: 8px;
  color: #333;
}

/* 移动端抽屉菜单 */
.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.drawer-title {
  font-size: 18px;
  font-weight: bold;
}

.drawer-close {
  cursor: pointer;
  font-size: 20px;
}

.mobile-menu-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.mobile-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 10px;
}

.user-details .username {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.user-details .email {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.mobile-nav-menu {
  border: none;
  flex: 1;
}

.mobile-nav-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  font-size: 15px;
}

.mobile-menu-footer {
  padding: 20px 0;
  border-top: 1px solid #eee;
  margin-top: auto;
}

/* 移动端底部导航栏 */
.mobile-tabbar {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: #fff;
  border-top: 1px solid #e0e0e0;
  justify-content: space-around;
  align-items: center;
  z-index: 100;
  padding-bottom: env(safe-area-inset-bottom);
}

.tabbar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  height: 100%;
  color: #999;
  font-size: 10px;
  cursor: pointer;
  transition: color 0.2s;
}

.tabbar-item .el-icon {
  font-size: 22px;
  margin-bottom: 2px;
}

.tabbar-item.active {
  color: #409eff;
}

.tabbar-item.upload-btn {
  position: relative;
}

.tabbar-item.upload-btn .el-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border-radius: 50%;
  color: #fff;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.4);
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 桌面端显示 */
.desktop-only {
  display: flex;
}

.desktop-menu {
  display: flex;
}

/* 移动端显示 */
.mobile-only {
  display: none;
}

/* 响应式断点 */
@media screen and (max-width: 768px) {
  .desktop-only {
    display: none !important;
  }

  .desktop-menu {
    display: none !important;
  }

  .mobile-only {
    display: flex !important;
  }

  .mobile-menu-btn {
    display: flex !important;
  }

  .logo-text {
    font-size: 16px;
  }

  .header-content {
    padding: 0 12px;
  }

  .app-main {
    padding-bottom: 60px; /* 为底部导航留空间 */
  }

  .app-header {
    height: 50px;
  }
}

/* 抽屉样式覆盖 */
:deep(.mobile-drawer .el-drawer__header) {
  margin-bottom: 0;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

:deep(.mobile-drawer .el-drawer__body) {
  padding: 0 20px;
}
</style>

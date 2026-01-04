<template>
  <div class="home-container">
    <!-- 图片轮播展示 -->
    <el-card v-if="carouselImages.length > 0" class="carousel-card">
      <el-carousel height="400px" :interval="4000" indicator-position="outside">
        <el-carousel-item v-for="image in carouselImages" :key="image.id">
          <div class="carousel-item" @click="goToImage(image)">
            <el-image
              :src="image.file_url"
              fit="cover"
              class="carousel-image"
            >
              <template #placeholder>
                <div class="carousel-placeholder">
                  <el-icon class="is-loading"><Loading /></el-icon>
                </div>
              </template>
            </el-image>
            <div class="carousel-overlay">
              <h3>{{ image.filename }}</h3>
              <p>上传者：{{ image.owner_username }}</p>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </el-card>

    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :md="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>欢迎使用图片管理系统</span>
              <el-tag v-if="userStore.isAdmin" type="danger">管理员</el-tag>
            </div>
          </template>

          <div class="welcome-content">
            <div class="welcome-message">
              <h2 v-if="userStore.user">欢迎，{{ userStore.user.username }}！</h2>
              <h2 v-else>欢迎访问图片管理系统</h2>
              <p>浏览和管理精彩图片</p>
            </div>
            
            <el-row :gutter="20" class="quick-actions">
              <el-col :xs="24" :sm="12" :md="6">
                <el-card shadow="hover" class="action-card" @click="$router.push('/gallery')">
                  <el-icon size="48" color="#409eff"><PictureFilled /></el-icon>
                  <h3>图片库</h3>
                  <p>浏览所有公开图片</p>
                </el-card>
              </el-col>
              <el-col v-if="userStore.isAuthenticated" :xs="24" :sm="12" :md="6">
                <el-card shadow="hover" class="action-card" @click="$router.push('/upload')">
                  <el-icon size="48" color="#67c23a"><Upload /></el-icon>
                  <h3>上传图片</h3>
                  <p>支持拖拽上传</p>
                </el-card>
              </el-col>
              <el-col v-if="userStore.isAuthenticated" :xs="24" :sm="12" :md="6">
                <el-card shadow="hover" class="action-card" @click="$router.push('/my-images')">
                  <el-icon size="48" color="#e6a23c"><Picture /></el-icon>
                  <h3>我的图片</h3>
                  <p>管理我的图片</p>
                </el-card>
              </el-col>
              <el-col v-if="userStore.isAdmin" :xs="24" :sm="12" :md="6">
                <el-card shadow="hover" class="action-card admin-card" @click="$router.push('/admin')">
                  <el-icon size="48" color="#f56c6c"><Setting /></el-icon>
                  <h3>管理控制台</h3>
                  <p>管理所有图片</p>
                </el-card>
              </el-col>
              <el-col v-if="userStore.isAuthenticated" :xs="24" :sm="12" :md="6">
                <el-card shadow="hover" class="action-card" @click="$router.push('/profile')">
                  <el-icon size="48" color="#909399"><User /></el-icon>
                  <h3>个人中心</h3>
                  <p>管理账户信息</p>
                </el-card>
              </el-col>
              <el-col v-if="!userStore.isAuthenticated" :xs="24" :sm="12" :md="6">
                <el-card shadow="hover" class="action-card" @click="$router.push('/login')">
                  <el-icon size="48" color="#67c23a"><User /></el-icon>
                  <h3>登录</h3>
                  <p>登录以上传图片</p>
                </el-card>
              </el-col>
              <el-col v-if="!userStore.isAuthenticated" :xs="24" :sm="12" :md="6">
                <el-card shadow="hover" class="action-card" @click="$router.push('/register')">
                  <el-icon size="48" color="#409eff"><Plus /></el-icon>
                  <h3>注册</h3>
                  <p>创建新账户</p>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 用户信息统计（仅登录用户可见） -->
    <el-row v-if="userStore.user" :gutter="20" style="margin-top: 20px">
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Upload, Picture, User, PictureFilled, Setting, Plus, Loading } from '@element-plus/icons-vue'
import { useUserStore } from '../store/userStore'
import { getRandomImages } from '../utils/adminApi'

const router = useRouter()
const userStore = useUserStore()
const carouselImages = ref([])

// 获取随机图片
const fetchCarouselImages = async () => {
  try {
    const response = await getRandomImages(8)
    carouselImages.value = response.data
  } catch (error) {
    console.error('获取轮播图片失败:', error)
  }
}

// 跳转到图片详情
const goToImage = (image) => {
  if (userStore.isAuthenticated) {
    router.push(`/image/${image.id}`)
  } else {
    router.push('/login')
  }
}

onMounted(() => {
  fetchCarouselImages()
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.carousel-card {
  margin-bottom: 20px;
  overflow: hidden;
}

.carousel-card :deep(.el-card__body) {
  padding: 0;
}

.carousel-item {
  width: 100%;
  height: 100%;
  position: relative;
  cursor: pointer;
}

.carousel-image {
  width: 100%;
  height: 400px;
}

.carousel-image :deep(img) {
  object-fit: contain !important;
  width: 100%;
  height: 100%;
  background: #1a1a1a;
}

.carousel-placeholder {
  width: 100%;
  height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  font-size: 32px;
  color: #909399;
}

.carousel-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: linear-gradient(transparent, rgba(0,0,0,0.7));
  color: white;
}

.carousel-overlay h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.carousel-overlay p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
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

.action-card.admin-card {
  border: 2px solid #f56c6c;
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

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .home-container {
    padding: 12px;
  }

  .carousel-card {
    margin-bottom: 15px;
  }

  .carousel-card :deep(.el-carousel) {
    height: 250px !important;
  }

  .carousel-card :deep(.el-carousel__container) {
    height: 250px !important;
  }

  .carousel-image {
    height: 250px !important;
  }

  .carousel-overlay {
    padding: 12px;
  }

  .carousel-overlay h3 {
    font-size: 15px;
  }

  .carousel-overlay p {
    font-size: 12px;
  }

  .welcome-message h2 {
    font-size: 20px;
  }

  .welcome-message p {
    font-size: 14px;
  }

  .quick-actions .el-col {
    margin-bottom: 12px;
  }

  .action-card {
    margin-bottom: 0;
    padding: 15px 10px;
  }

  .action-card :deep(.el-icon) {
    font-size: 36px !important;
  }

  .action-card h3 {
    font-size: 15px;
    margin: 10px 0 6px 0;
  }

  .action-card p {
    font-size: 12px;
  }

  /* 统计卡片 */
  .el-row:last-child .el-col {
    margin-bottom: 12px;
  }

  .el-statistic :deep(.el-statistic__head) {
    font-size: 12px;
  }

  .el-statistic :deep(.el-statistic__content) {
    font-size: 16px;
  }
}

@media screen and (max-width: 480px) {
  .home-container {
    padding: 8px;
  }

  .carousel-card :deep(.el-carousel),
  .carousel-card :deep(.el-carousel__container),
  .carousel-image {
    height: 200px !important;
  }

  .welcome-message h2 {
    font-size: 18px;
  }

  .action-card :deep(.el-icon) {
    font-size: 32px !important;
  }

  .action-card h3 {
    font-size: 14px;
  }
}
</style>

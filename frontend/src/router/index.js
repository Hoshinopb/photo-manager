import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/userStore'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Profile from '../views/Profile.vue'
import Upload from '../views/Upload.vue'
import MyImages from '../views/MyImages.vue'
import Gallery from '../views/Gallery.vue'
import ImageDetail from '../views/ImageDetail.vue'
import Admin from '../views/Admin.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: false },
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true },
  },
  {
    path: '/upload',
    name: 'Upload',
    component: Upload,
    meta: { requiresAuth: true },
  },
  {
    path: '/my-images',
    name: 'MyImages',
    component: MyImages,
    meta: { requiresAuth: true },
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: Gallery,
    meta: { requiresAuth: true },
  },
  {
    path: '/image/:id',
    name: 'ImageDetail',
    component: ImageDetail,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 导航守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // 初始化用户（如果还没有初始化过）
  if (!userStore.user && userStore.isAuthenticated) {
    await userStore.fetchCurrentUser()
  }

  // 检查是否需要认证
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else if ((to.name === 'Login' || to.name === 'Register') && userStore.isAuthenticated) {
    // 已登录用户重定向到首页
    next('/')
  } else if (to.meta.requiresAdmin && !userStore.isAdmin) {
    // 需要管理员权限但用户不是管理员
    next('/')
  } else {
    next()
  }
})

export default router

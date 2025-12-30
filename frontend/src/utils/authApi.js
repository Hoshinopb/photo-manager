import apiClient from './api'

// 用户注册
export const register = (username, email, password, re_password) => {
  return apiClient.post('/auth/users/', {
    username,
    email,
    password,
    re_password,
  })
}

// 用户登录
export const login = (username, password) => {
  return apiClient.post('/auth/token/login/', {
    username,
    password,
  })
}

// 用户登出
export const logout = () => {
  return apiClient.post('/auth/token/logout/')
}

// 获取当前用户信息
export const getCurrentUser = () => {
  return apiClient.get('/auth/users/me/')
}

// 更新用户信息
export const updateUser = (userData) => {
  return apiClient.put('/auth/users/me/', userData)
}

// 修改密码
export const changePassword = (new_password, re_new_password, current_password) => {
  return apiClient.post('/auth/users/set_password/', {
    new_password,
    re_new_password,
    current_password,
  })
}

export default {
  register,
  login,
  logout,
  getCurrentUser,
  updateUser,
  changePassword,
}

import apiClient from './api'

// 管理员获取所有图片
export const getAdminImages = (params = {}) => {
  return apiClient.get('/api/admin/images/', { params })
}

// 管理员获取统计信息
export const getAdminStats = () => {
  return apiClient.get('/api/admin/images/stats/')
}

// 管理员获取所有用户
export const getAdminUsers = (params = {}) => {
  return apiClient.get('/api/admin/images/all_users/', { params })
}

// 管理员设置用户为管理员
export const setUserStaff = (userId, isStaff) => {
  return apiClient.post('/api/admin/images/set_staff/', {
    user_id: userId,
    is_staff: isStaff
  })
}

// 管理员删除图片
export const adminDeleteImage = (id) => {
  return apiClient.delete(`/api/admin/images/${id}/`)
}

// 管理员批量删除图片
export const adminBatchDelete = (ids) => {
  return apiClient.delete('/api/admin/images/batch_delete/', { data: { ids } })
}

// 管理员更新图片
export const adminUpdateImage = (id, data) => {
  return apiClient.patch(`/api/admin/images/${id}/`, data)
}

// 获取随机公开图片（无需管理员权限）
export const getRandomImages = (count = 6) => {
  return apiClient.get('/api/images/random/', { params: { count } })
}

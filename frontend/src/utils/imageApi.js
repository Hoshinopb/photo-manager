import apiClient from './api'

/**
 * 图片相关 API
 */

/**
 * 上传图片
 * @param {File} file - 图片文件
 * @param {Object} options - 可选参数
 * @param {boolean} options.isPublic - 是否公开
 * @param {string} options.description - 图片描述
 * @param {Function} options.onProgress - 上传进度回调
 * @returns {Promise}
 */
export const uploadImage = async (file, options = {}) => {
  const formData = new FormData()
  formData.append('file', file)
  
  if (options.isPublic !== undefined) {
    formData.append('is_public', options.isPublic)
  }
  if (options.description) {
    formData.append('description', options.description)
  }
  
  const config = {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }
  
  if (options.onProgress) {
    config.onUploadProgress = (progressEvent) => {
      const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      options.onProgress(percent)
    }
  }
  
  return apiClient.post('/api/images/', formData, config)
}

/**
 * 获取图片列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export const getImages = async (params = {}) => {
  return apiClient.get('/api/images/', { params })
}

/**
 * 获取我的图片列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export const getMyImages = async (params = {}) => {
  return apiClient.get('/api/my-images/', { params })
}

/**
 * 获取单张图片详情
 * @param {number} id - 图片ID
 * @returns {Promise}
 */
export const getImageDetail = async (id) => {
  return apiClient.get(`/api/images/${id}/`)
}

/**
 * 更新图片信息
 * @param {number} id - 图片ID
 * @param {Object} data - 更新数据
 * @returns {Promise}
 */
export const updateImage = async (id, data) => {
  return apiClient.patch(`/api/images/${id}/`, data)
}

/**
 * 删除图片
 * @param {number} id - 图片ID
 * @returns {Promise}
 */
export const deleteImage = async (id) => {
  return apiClient.delete(`/api/images/${id}/`)
}

/**
 * 获取公开图片列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export const getPublicImages = async (params = {}) => {
  return apiClient.get('/api/images/public/', { params })
}

/**
 * 获取图片统计信息
 * @returns {Promise}
 */
export const getImageStats = async () => {
  return apiClient.get('/api/images/stats/')
}

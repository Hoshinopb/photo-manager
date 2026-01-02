import apiClient from './api'

/**
 * 标签相关 API
 */

/**
 * 获取所有标签
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export const getTags = async (params = {}) => {
  return apiClient.get('/api/tags/', { params })
}

/**
 * 获取热门标签
 * @returns {Promise}
 */
export const getPopularTags = async () => {
  return apiClient.get('/api/tags/popular/')
}

/**
 * 获取当前用户的标签（用户图片使用的标签）
 * @returns {Promise}
 */
export const getMyTags = async () => {
  return apiClient.get('/api/tags/my_tags/')
}

/**
 * 获取自动生成的标签
 * @returns {Promise}
 */
export const getAutoTags = async () => {
  return apiClient.get('/api/tags/auto_tags/')
}

/**
 * 获取用户自定义标签
 * @returns {Promise}
 */
export const getUserTags = async () => {
  return apiClient.get('/api/tags/user_tags/')
}

/**
 * 创建新标签
 * @param {Object} data - 标签数据 { name, color }
 * @returns {Promise}
 */
export const createTag = async (data) => {
  return apiClient.post('/api/tags/', data)
}

/**
 * 删除标签
 * @param {number} id - 标签ID
 * @returns {Promise}
 */
export const deleteTag = async (id) => {
  return apiClient.delete(`/api/tags/${id}/`)
}

/**
 * 为图片添加标签
 * @param {number} imageId - 图片ID
 * @param {string} tagName - 标签名称
 * @returns {Promise}
 */
export const addTagToImage = async (imageId, tagName) => {
  return apiClient.post(`/api/images/${imageId}/add_tag/`, { tag_name: tagName })
}

/**
 * 移除图片的标签
 * @param {number} imageId - 图片ID
 * @param {number} tagId - 标签ID
 * @returns {Promise}
 */
export const removeTagFromImage = async (imageId, tagId) => {
  return apiClient.delete(`/api/images/${imageId}/remove_tag/${tagId}/`)
}

/**
 * 手动触发 EXIF 解析
 * @param {number} imageId - 图片ID
 * @returns {Promise}
 */
export const parseImageExif = async (imageId) => {
  return apiClient.post(`/api/images/${imageId}/parse_exif/`)
}

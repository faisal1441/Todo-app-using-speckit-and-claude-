/**
 * API Service - Centralized API client for backend communication
 *
 * Uses axios to make HTTP requests to the backend API.
 * All API calls go through this module for consistency.
 */

import axios from 'axios'

// Get API base URL from environment variable or use default
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
})

// Error interceptor for consistent error handling
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // Server responded with error status
      const errorMessage = error.response.data?.detail || error.message
      console.error(`API Error (${error.response.status}):`, errorMessage)
    } else if (error.request) {
      // Request made but no response received
      console.error('API Error: No response from server', error.request)
    } else {
      // Error setting up request
      console.error('API Error:', error.message)
    }
    return Promise.reject(error)
  }
)

/**
 * Task API endpoints
 */
export const taskAPI = {
  /**
   * Get all tasks
   * @param {string} status - Optional filter: 'pending' or 'complete'
   * @returns {Promise} Array of tasks
   */
  getAll: (status = null) => {
    const params = status ? { status } : {}
    return api.get('/tasks', { params })
  },

  /**
   * Get a single task by ID
   * @param {number} id - Task ID
   * @returns {Promise} Task object
   */
  getById: (id) => api.get(`/tasks/${id}`),

  /**
   * Create a new task
   * @param {Object} data - Task data { title, description }
   * @returns {Promise} Created task object
   */
  create: (data) => api.post('/tasks', data),

  /**
   * Update a task
   * @param {number} id - Task ID
   * @param {Object} data - Updated task data { title, description }
   * @returns {Promise} Updated task object
   */
  update: (id, data) => api.put(`/tasks/${id}`, data),

  /**
   * Delete a task
   * @param {number} id - Task ID
   * @returns {Promise} Response from delete
   */
  delete: (id) => api.delete(`/tasks/${id}`),

  /**
   * Mark a task as complete
   * @param {number} id - Task ID
   * @returns {Promise} Updated task object
   */
  markComplete: (id) => api.patch(`/tasks/${id}/complete`),

  /**
   * Mark a task as incomplete
   * @param {number} id - Task ID
   * @returns {Promise} Updated task object
   */
  markIncomplete: (id) => api.patch(`/tasks/${id}/incomplete`),

  /**
   * Get task statistics
   * @returns {Promise} Stats object { total, pending, completed }
   */
  getStats: () => api.get('/tasks/stats'),
}

export default api

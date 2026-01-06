/**
 * Custom React Hook for Task Management
 *
 * Manages task state and provides CRUD operations.
 * Handles API communication and local state synchronization.
 */

import { useState, useEffect } from 'react'
import { taskAPI } from '../services/api'

/**
 * useTasks Hook
 *
 * Provides centralized task state management for the application.
 * Automatically fetches tasks on mount and provides methods to manage them.
 *
 * @returns {Object} Tasks state and operations
 *   - tasks: Array of task objects
 *   - loading: Boolean indicating if data is being fetched
 *   - error: Error message if any
 *   - stats: Object with total, pending, completed counts
 *   - addTask: Function to create a new task
 *   - updateTask: Function to update an existing task
 *   - deleteTask: Function to delete a task
 *   - toggleComplete: Function to toggle task completion status
 *   - refresh: Function to manually refresh tasks from server
 */
export function useTasks() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [stats, setStats] = useState({ total: 0, pending: 0, completed: 0 })

  /**
   * Fetch all tasks from the server
   */
  const fetchTasks = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch tasks
      const response = await taskAPI.getAll()
      setTasks(response.data || [])

      // Fetch stats
      try {
        const statsResponse = await taskAPI.getStats()
        setStats(statsResponse.data)
      } catch (statsError) {
        console.warn('Could not fetch stats:', statsError)
        // Calculate stats locally if API fails
        const pending = response.data?.filter(t => t.status === 'pending').length || 0
        const completed = response.data?.filter(t => t.status === 'complete').length || 0
        setStats({
          total: response.data?.length || 0,
          pending,
          completed,
        })
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load tasks')
      setTasks([])
    } finally {
      setLoading(false)
    }
  }

  /**
   * Fetch tasks on component mount
   */
  useEffect(() => {
    fetchTasks()
  }, [])

  /**
   * Add a new task
   * @param {string} title - Task title
   * @param {string} description - Task description
   */
  const addTask = async (title, description = '') => {
    try {
      const response = await taskAPI.create({ title, description })
      setTasks([...tasks, response.data])
      setError(null)

      // Update stats
      setStats(prev => ({
        ...prev,
        total: prev.total + 1,
        pending: prev.pending + 1,
      }))

      return response.data
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message
      setError(`Failed to add task: ${errorMsg}`)
      throw err
    }
  }

  /**
   * Update an existing task
   * @param {number} id - Task ID
   * @param {Object} data - Updated task data
   */
  const updateTask = async (id, data) => {
    try {
      const response = await taskAPI.update(id, data)
      setTasks(tasks.map(t => t.id === id ? response.data : t))
      setError(null)
      return response.data
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message
      setError(`Failed to update task: ${errorMsg}`)
      throw err
    }
  }

  /**
   * Delete a task
   * @param {number} id - Task ID
   */
  const deleteTask = async (id) => {
    try {
      await taskAPI.delete(id)
      const deletedTask = tasks.find(t => t.id === id)
      setTasks(tasks.filter(t => t.id !== id))
      setError(null)

      // Update stats
      if (deletedTask) {
        setStats(prev => ({
          ...prev,
          total: prev.total - 1,
          [deletedTask.status === 'complete' ? 'completed' : 'pending']: prev[deletedTask.status === 'complete' ? 'completed' : 'pending'] - 1,
        }))
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message
      setError(`Failed to delete task: ${errorMsg}`)
      throw err
    }
  }

  /**
   * Toggle task completion status
   * @param {number} id - Task ID
   * @param {boolean} isComplete - Current completion status
   */
  const toggleComplete = async (id, isComplete) => {
    try {
      const response = isComplete
        ? await taskAPI.markIncomplete(id)
        : await taskAPI.markComplete(id)

      setTasks(tasks.map(t => t.id === id ? response.data : t))
      setError(null)

      // Update stats
      setStats(prev => {
        if (isComplete) {
          // Was complete, now pending
          return {
            ...prev,
            pending: prev.pending + 1,
            completed: prev.completed - 1,
          }
        } else {
          // Was pending, now complete
          return {
            ...prev,
            pending: prev.pending - 1,
            completed: prev.completed + 1,
          }
        }
      })

      return response.data
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message
      setError(`Failed to update task status: ${errorMsg}`)
      throw err
    }
  }

  return {
    tasks,
    loading,
    error,
    stats,
    addTask,
    updateTask,
    deleteTask,
    toggleComplete,
    refresh: fetchTasks,
  }
}

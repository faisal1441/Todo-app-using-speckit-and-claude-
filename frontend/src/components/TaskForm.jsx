/**
 * TaskForm Component
 *
 * Form for adding new tasks.
 */

import React, { useState } from 'react'

export function TaskForm({ onAddTask }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!title.trim()) {
      setError('Please enter a task title')
      return
    }

    try {
      setLoading(true)
      setError(null)
      await onAddTask(title, description)
      setTitle('')
      setDescription('')
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to add task')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <h2>Add New Task</h2>

        {error && <div className="error-message">{error}</div>}

        <div className="form-field">
          <input
            type="text"
            className="form-input"
            placeholder="Task title (required)"
            value={title}
            onChange={e => setTitle(e.target.value)}
            disabled={loading}
            required
          />
        </div>

        <div className="form-field">
          <textarea
            className="form-input form-textarea"
            placeholder="Task description (optional)"
            value={description}
            onChange={e => setDescription(e.target.value)}
            disabled={loading}
            rows="3"
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary btn-submit"
          disabled={loading}
        >
          {loading ? 'Adding...' : 'Add Task'}
        </button>
      </div>
    </form>
  )
}

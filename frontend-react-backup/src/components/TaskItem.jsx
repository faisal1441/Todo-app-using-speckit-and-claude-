/**
 * TaskItem Component
 *
 * Displays a single task with options to edit, delete, and toggle completion.
 * Supports inline editing mode.
 */

import React, { useState } from 'react'

export function TaskItem({ task, onUpdate, onDelete, onToggle }) {
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState(task.title)
  const [description, setDescription] = useState(task.description)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const handleSave = async () => {
    if (!title.trim()) {
      setError('Title cannot be empty')
      return
    }

    try {
      setSaving(true)
      setError(null)
      await onUpdate(task.id, { title, description })
      setEditing(false)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setTitle(task.title)
    setDescription(task.description)
    setEditing(false)
    setError(null)
  }

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      onDelete(task.id)
    }
  }

  const handleToggle = async () => {
    try {
      await onToggle(task.id, task.status === 'complete')
    } catch (err) {
      console.error('Failed to toggle task:', err)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const taskItemClass = `task-item task-${task.status}`

  if (editing) {
    return (
      <div className={taskItemClass}>
        <div className="task-edit-form">
          {error && <div className="error-message">{error}</div>}
          <input
            type="text"
            className="task-title-input"
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder="Task title"
            disabled={saving}
          />
          <textarea
            className="task-description-input"
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="Task description (optional)"
            disabled={saving}
            rows="3"
          />
          <div className="task-edit-actions">
            <button
              className="btn btn-primary"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleCancel}
              disabled={saving}
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={taskItemClass}>
      <div className="task-content">
        <div className="task-checkbox-wrapper">
          <input
            type="checkbox"
            className="task-checkbox"
            checked={task.status === 'complete'}
            onChange={handleToggle}
            aria-label={`Mark "${task.title}" as ${task.status === 'complete' ? 'incomplete' : 'complete'}`}
          />
        </div>

        <div className="task-info">
          <h3 className="task-title">{task.title}</h3>
          {task.description && <p className="task-description">{task.description}</p>}
          <div className="task-metadata">
            <small className="task-created">
              Created: {formatDate(task.created_at)}
            </small>
            {task.completed_at && (
              <small className="task-completed">
                Completed: {formatDate(task.completed_at)}
              </small>
            )}
          </div>
        </div>
      </div>

      <div className="task-actions">
        <button
          className="btn btn-icon btn-edit"
          onClick={() => setEditing(true)}
          title="Edit task"
        >
          ✏️ Edit
        </button>
        <button
          className="btn btn-icon btn-delete"
          onClick={handleDelete}
          title="Delete task"
        >
          🗑️ Delete
        </button>
      </div>
    </div>
  )
}

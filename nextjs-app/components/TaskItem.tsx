'use client'

import { useState } from 'react'
import type { Task } from '@/lib/api'

interface TaskItemProps {
  task: Task
  onUpdate: (id: number, data: { title?: string; description?: string }) => Promise<Task>
  onDelete: (id: number) => Promise<void>
  onToggle: (id: number, isComplete: boolean) => Promise<Task>
}

export function TaskItem({ task, onUpdate, onDelete, onToggle }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editTitle, setEditTitle] = useState(task.title)
  const [editDescription, setEditDescription] = useState(task.description)
  const [loading, setLoading] = useState(false)

  const handleToggle = async () => {
    try {
      setLoading(true)
      await onToggle(task.id, task.status === 'complete')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        setLoading(true)
        await onDelete(task.id)
      } finally {
        setLoading(false)
      }
    }
  }

  const handleSave = async () => {
    if (!editTitle.trim()) {
      alert('Task title cannot be empty')
      return
    }

    try {
      setLoading(true)
      await onUpdate(task.id, {
        title: editTitle,
        description: editDescription,
      })
      setIsEditing(false)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setEditTitle(task.title)
    setEditDescription(task.description)
    setIsEditing(false)
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
    } catch {
      return dateString
    }
  }

  if (isEditing) {
    return (
      <div className={`task-item ${task.status === 'complete' ? 'task-complete' : ''}`}>
        <div className="task-edit-form">
          <input
            type="text"
            className="task-title-input"
            value={editTitle}
            onChange={e => setEditTitle(e.target.value)}
            disabled={loading}
            maxLength={200}
          />
          <textarea
            className="task-description-input"
            value={editDescription}
            onChange={e => setEditDescription(e.target.value)}
            disabled={loading}
            maxLength={1000}
          />
          <div className="task-edit-actions">
            <button
              className="btn btn-primary"
              onClick={handleSave}
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleCancel}
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`task-item ${task.status === 'complete' ? 'task-complete' : ''}`}>
      <div className="task-checkbox-wrapper">
        <input
          type="checkbox"
          className="task-checkbox"
          checked={task.status === 'complete'}
          onChange={handleToggle}
          disabled={loading}
        />
      </div>

      <div className="task-content">
        <div className="task-info">
          <div className="task-title">{task.title}</div>
          {task.description && (
            <div className="task-description">{task.description}</div>
          )}
          <div className="task-metadata">
            {task.created_at && (
              <span className="task-created">
                Created: {formatDate(task.created_at)}
              </span>
            )}
            {task.completed_at && task.status === 'complete' && (
              <span className="task-completed">
                Completed: {formatDate(task.completed_at)}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="task-actions">
        <button
          className="btn btn-edit btn-icon"
          onClick={() => setIsEditing(true)}
          disabled={loading}
          title="Edit task"
        >
          Edit
        </button>
        <button
          className="btn btn-delete btn-icon"
          onClick={handleDelete}
          disabled={loading}
          title="Delete task"
        >
          Delete
        </button>
      </div>
    </div>
  )
}

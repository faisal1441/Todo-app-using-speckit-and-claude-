'use client'

import { useState } from 'react'
import type { Task } from '@/lib/api'

interface TaskFormProps {
  onAddTask: (title: string, description: string) => Promise<Task>
}

export function TaskForm({ onAddTask }: TaskFormProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!title.trim()) {
      setError('Task title cannot be empty')
      return
    }

    try {
      setLoading(true)
      await onAddTask(title, description)
      setTitle('')
      setDescription('')
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to add task'
      setError(errorMsg)
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
            maxLength={200}
          />
        </div>

        <div className="form-field">
          <textarea
            className="form-input form-textarea"
            placeholder="Task description (optional)"
            value={description}
            onChange={e => setDescription(e.target.value)}
            disabled={loading}
            maxLength={1000}
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

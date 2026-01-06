/**
 * TaskList Component
 *
 * Displays a list of tasks with loading and empty states.
 */

import React from 'react'
import { TaskItem } from './TaskItem'

export function TaskList({ tasks, loading, error, onUpdate, onDelete, onToggle }) {
  if (loading) {
    return (
      <div className="task-list-container">
        <div className="loading-spinner">Loading tasks...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="task-list-container">
        <div className="error-message">{error}</div>
      </div>
    )
  }

  if (!tasks || tasks.length === 0) {
    return (
      <div className="task-list-container">
        <div className="empty-state">
          <p className="empty-state-icon">📝</p>
          <p className="empty-state-text">No tasks yet. Create one to get started!</p>
        </div>
      </div>
    )
  }

  return (
    <div className="task-list-container">
      <div className="task-list">
        {tasks.map(task => (
          <TaskItem
            key={task.id}
            task={task}
            onUpdate={onUpdate}
            onDelete={onDelete}
            onToggle={onToggle}
          />
        ))}
      </div>
    </div>
  )
}

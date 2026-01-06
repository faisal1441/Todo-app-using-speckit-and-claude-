'use client'

import { TaskItem } from './TaskItem'
import type { Task } from '@/lib/api'

interface TaskListProps {
  tasks: Task[]
  loading: boolean
  error: string | null
  onUpdate: (id: number, data: { title?: string; description?: string }) => Promise<Task>
  onDelete: (id: number) => Promise<void>
  onToggle: (id: number, isComplete: boolean) => Promise<Task>
}

export function TaskList({
  tasks,
  loading,
  error,
  onUpdate,
  onDelete,
  onToggle,
}: TaskListProps) {
  return (
    <div className="task-list-container">
      {loading && !tasks.length ? (
        <div className="loading-spinner">Loading tasks...</div>
      ) : error && !tasks.length ? (
        <div className="empty-state">
          <div className="empty-state-icon">⚠️</div>
          <div className="empty-state-text">Error: {error}</div>
        </div>
      ) : tasks.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📭</div>
          <div className="empty-state-text">No tasks yet. Create one to get started!</div>
        </div>
      ) : (
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
      )}
    </div>
  )
}

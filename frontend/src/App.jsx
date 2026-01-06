/**
 * Main App Component
 *
 * Root component that integrates all other components.
 * Manages overall state and layout.
 */

import React, { useState, useMemo } from 'react'
import { useTasks } from './hooks/useTasks'
import { TaskStats } from './components/TaskStats'
import { TaskFilter } from './components/TaskFilter'
import { TaskForm } from './components/TaskForm'
import { TaskList } from './components/TaskList'

function App() {
  const { tasks, loading, error, stats, addTask, updateTask, deleteTask, toggleComplete } = useTasks()
  const [currentFilter, setCurrentFilter] = useState('all')

  // Filter tasks based on current filter
  const filteredTasks = useMemo(() => {
    if (currentFilter === 'all') return tasks
    if (currentFilter === 'pending') return tasks.filter(t => t.status === 'pending')
    if (currentFilter === 'complete') return tasks.filter(t => t.status === 'complete')
    return tasks
  }, [tasks, currentFilter])

  const handleFilterChange = (filter) => {
    setCurrentFilter(filter)
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>📋 Todo App</h1>
          <p className="header-subtitle">Manage your tasks efficiently</p>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          {/* Stats */}
          <TaskStats stats={stats} />

          {/* Form */}
          <TaskForm onAddTask={addTask} />

          {/* Filter */}
          <TaskFilter currentFilter={currentFilter} onFilterChange={handleFilterChange} />

          {/* Task List */}
          {error && !loading && (
            <div className="app-error">
              <p>⚠️ Error: {error}</p>
            </div>
          )}

          <TaskList
            tasks={filteredTasks}
            loading={loading}
            error={error}
            onUpdate={updateTask}
            onDelete={deleteTask}
            onToggle={toggleComplete}
          />
        </div>
      </main>

      <footer className="app-footer">
        <p>Todo App v2.0 • Built with React & FastAPI</p>
      </footer>
    </div>
  )
}

export default App

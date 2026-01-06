/**
 * TaskStats Component
 *
 * Displays task statistics (total, pending, completed).
 */

import React from 'react'

export function TaskStats({ stats = { total: 0, pending: 0, completed: 0 } }) {
  return (
    <div className="task-stats">
      <div className="stat-card">
        <div className="stat-number">{stats.total}</div>
        <div className="stat-label">Total Tasks</div>
      </div>
      <div className="stat-card">
        <div className="stat-number">{stats.pending}</div>
        <div className="stat-label">Pending</div>
      </div>
      <div className="stat-card">
        <div className="stat-number">{stats.completed}</div>
        <div className="stat-label">Completed</div>
      </div>
    </div>
  )
}

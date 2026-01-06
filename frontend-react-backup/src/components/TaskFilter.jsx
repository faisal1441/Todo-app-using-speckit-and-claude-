/**
 * TaskFilter Component
 *
 * Provides filtering by task status (all, pending, completed).
 */

import React from 'react'

export function TaskFilter({ currentFilter, onFilterChange }) {
  const filters = [
    { value: 'all', label: 'All Tasks' },
    { value: 'pending', label: 'Pending' },
    { value: 'complete', label: 'Completed' },
  ]

  return (
    <div className="task-filter">
      <div className="filter-buttons">
        {filters.map(filter => (
          <button
            key={filter.value}
            className={`btn btn-filter ${currentFilter === filter.value ? 'active' : ''}`}
            onClick={() => onFilterChange(filter.value)}
          >
            {filter.label}
          </button>
        ))}
      </div>
    </div>
  )
}

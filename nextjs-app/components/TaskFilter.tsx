'use client'

interface TaskFilterProps {
  currentFilter: string
  onFilterChange: (filter: string) => void
}

export function TaskFilter({ currentFilter, onFilterChange }: TaskFilterProps) {
  const filters = ['all', 'pending', 'complete']

  return (
    <div className="task-filter">
      <div className="filter-buttons">
        {filters.map(filter => (
          <button
            key={filter}
            className={`btn btn-filter ${currentFilter === filter ? 'active' : ''}`}
            onClick={() => onFilterChange(filter)}
          >
            {filter.charAt(0).toUpperCase() + filter.slice(1)}
          </button>
        ))}
      </div>
    </div>
  )
}

/**
 * TaskList Component
 *
 * Displays a list of tasks with filtering options and empty states.
 * Handles different view modes (all, active, completed).
 */

import { useState } from 'react'
import { Task } from '@/lib/api/tasks'
import TaskItem from './TaskItem'

interface TaskListProps {
  tasks: Task[]
  onToggleComplete?: (taskId: number) => void
  onEdit?: (taskId: number) => void
  onDelete?: (taskId: number) => void
  onAddTask?: () => void
}

type FilterMode = 'all' | 'active' | 'completed'

export default function TaskList({
  tasks,
  onToggleComplete,
  onEdit,
  onDelete,
  onAddTask,
}: TaskListProps) {
  const [filter, setFilter] = useState<FilterMode>('all')

  // Filter tasks based on selected mode
  const filteredTasks = tasks.filter((task) => {
    if (filter === 'active') return !task.completed
    if (filter === 'completed') return task.completed
    return true // 'all'
  })

  // Count statistics
  const totalTasks = tasks.length
  const activeTasks = tasks.filter((t) => !t.completed).length
  const completedTasks = tasks.filter((t) => t.completed).length

  return (
    <div className="space-y-6">
      {/* Header with Filter Tabs */}
      {totalTasks > 0 && (
        <div className="bg-white rounded-xl border-2 border-gray-200 p-1 flex items-center gap-1">
          <button
            onClick={() => setFilter('all')}
            className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-primary-100 ${
              filter === 'all'
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            All
            <span
              className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
                filter === 'all'
                  ? 'bg-primary-700'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              {totalTasks}
            </span>
          </button>

          <button
            onClick={() => setFilter('active')}
            className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-primary-100 ${
              filter === 'active'
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            Active
            <span
              className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
                filter === 'active'
                  ? 'bg-primary-700'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              {activeTasks}
            </span>
          </button>

          <button
            onClick={() => setFilter('completed')}
            className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-primary-100 ${
              filter === 'completed'
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            Completed
            <span
              className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
                filter === 'completed'
                  ? 'bg-primary-700'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              {completedTasks}
            </span>
          </button>
        </div>
      )}

      {/* Task List or Empty State */}
      {filteredTasks.length > 0 ? (
        <div className="space-y-3">
          {filteredTasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onToggleComplete={onToggleComplete}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          filter={filter}
          hasAnyTasks={totalTasks > 0}
          onAddTask={onAddTask}
        />
      )}
    </div>
  )
}

/**
 * EmptyState Component
 *
 * Displays different empty states based on context:
 * - No tasks at all (first-time user)
 * - No active tasks (all completed)
 * - No completed tasks (all active)
 */
function EmptyState({
  filter,
  hasAnyTasks,
  onAddTask,
}: {
  filter: FilterMode
  hasAnyTasks: boolean
  onAddTask?: () => void
}) {
  // No tasks at all - first-time user state
  if (!hasAnyTasks) {
    return (
      <div className="text-center py-16 px-4">
        <div className="mb-6 animate-bounce">
          <svg
            className="w-20 h-20 mx-auto text-gray-300"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>

        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          No tasks yet
        </h3>
        <p className="text-gray-600 mb-6 max-w-md mx-auto">
          Get started by creating your first task. Stay organized and track your progress!
        </p>

        {onAddTask && (
          <button
            onClick={onAddTask}
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-xl hover:shadow-primary-600/30 hover:-translate-y-0.5 focus:outline-none focus:ring-4 focus:ring-primary-100"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Create your first task
          </button>
        )}
      </div>
    )
  }

  // Has tasks but none match the filter
  if (filter === 'active') {
    return (
      <div className="text-center py-12 px-4">
        <div className="mb-4">
          <svg
            className="w-16 h-16 mx-auto text-green-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          All done!
        </h3>
        <p className="text-gray-600">
          You've completed all your tasks. Great work!
        </p>
      </div>
    )
  }

  if (filter === 'completed') {
    return (
      <div className="text-center py-12 px-4">
        <div className="mb-4">
          <svg
            className="w-16 h-16 mx-auto text-gray-300"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
            />
          </svg>
        </div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          No completed tasks
        </h3>
        <p className="text-gray-600">
          Complete a task to see it here.
        </p>
      </div>
    )
  }

  // Fallback (shouldn't happen)
  return null
}

/**
 * TaskItem Component - Phase 7 Enhanced
 *
 * Displays a single task card with delightful completion toggle.
 * Features "Moment of Achievement" micro-interactions that make
 * checking off tasks feel rewarding and satisfying.
 */

'use client'

import { useState } from 'react'
import { Task } from '@/lib/api/tasks'

interface TaskItemProps {
  task: Task
  onToggleComplete?: (taskId: number) => void
  onEdit?: (taskId: number) => void
  onDelete?: (taskId: number) => void
}

export default function TaskItem({
  task,
  onToggleComplete,
  onEdit,
  onDelete,
}: TaskItemProps) {
  const [isToggling, setIsToggling] = useState(false)
  const [showCelebration, setShowCelebration] = useState(false)

  const handleToggle = async () => {
    if (isToggling) return

    setIsToggling(true)

    // If marking as complete, show celebration
    if (!task.completed) {
      setShowCelebration(true)
      setTimeout(() => setShowCelebration(false), 1000)
    }

    // Call the parent handler
    onToggleComplete?.(task.id)

    // Reset loading state after a short delay
    setTimeout(() => setIsToggling(false), 400)
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    })
  }

  return (
    <div
      className={`group relative bg-white rounded-xl border-2 transition-all duration-300 hover:shadow-md ${
        task.completed
          ? 'border-emerald-200 bg-emerald-50/30'
          : 'border-gray-200 hover:border-primary-300'
      } ${showCelebration ? 'animate-celebration' : ''}`}
    >
      {/* Celebration Confetti Effect */}
      {showCelebration && (
        <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-xl">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
            {[...Array(8)].map((_, i) => (
              <div
                key={i}
                className="absolute w-2 h-2 bg-gradient-to-br from-emerald-400 to-green-500 rounded-full animate-confetti"
                style={{
                  transform: `rotate(${i * 45}deg) translateY(-20px)`,
                  animationDelay: `${i * 50}ms`,
                }}
              />
            ))}
          </div>
        </div>
      )}

      <div className="p-4 sm:p-5">
        <div className="flex items-start gap-4">
          {/* Completion Checkbox with Enhanced Interactions */}
          <button
            onClick={handleToggle}
            disabled={isToggling}
            className={`
              relative flex-shrink-0 mt-1 w-7 h-7 rounded-xl border-2
              transition-all duration-300 ease-out
              focus:outline-none focus:ring-4
              ${
                task.completed
                  ? 'bg-gradient-to-br from-emerald-500 to-green-600 border-emerald-600 shadow-lg shadow-emerald-500/30 focus:ring-emerald-100'
                  : 'bg-white border-gray-300 hover:border-primary-500 hover:scale-110 focus:ring-primary-100'
              }
              ${isToggling ? 'scale-95 opacity-70' : ''}
              disabled:cursor-not-allowed
            `}
            aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
          >
            {/* Loading Spinner */}
            {isToggling && !task.completed && (
              <svg
                className="absolute inset-0 w-full h-full text-primary-600 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="3"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
            )}

            {/* Checkmark Icon */}
            {task.completed && (
              <svg
                className={`w-full h-full text-white transition-all duration-300 ${
                  isToggling ? 'scale-75 opacity-0' : 'scale-100 opacity-100'
                }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={3.5}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            )}
          </button>

          {/* Task Content */}
          <div className="flex-1 min-w-0">
            {/* Title with Smooth Transition */}
            <h3
              className={`
                text-base sm:text-lg font-semibold mb-1.5
                transition-all duration-300 ease-out
                ${
                  task.completed
                    ? 'text-emerald-700 line-through decoration-2 decoration-emerald-400'
                    : 'text-gray-900'
                }
              `}
            >
              {task.title}
            </h3>

            {/* Description with Fade Transition */}
            {task.description && (
              <p
                className={`
                  text-sm mb-3 whitespace-pre-wrap break-words
                  transition-all duration-300 ease-out
                  ${task.completed ? 'text-emerald-600/70' : 'text-gray-600'}
                `}
              >
                {task.description}
              </p>
            )}

            {/* Metadata with Enhanced Completed Badge */}
            <div className="flex items-center gap-3 text-xs">
              <span className={`flex items-center gap-1 ${task.completed ? 'text-emerald-600' : 'text-gray-500'} transition-colors duration-300`}>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                {formatDate(task.created_at)}
              </span>

              {task.completed && (
                <span className="
                  inline-flex items-center gap-1.5
                  px-2.5 py-1
                  bg-gradient-to-r from-emerald-100 to-green-100
                  text-emerald-700 font-semibold
                  rounded-full
                  border border-emerald-200
                  shadow-sm
                  animate-slide-up
                ">
                  <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Done
                </span>
              )}
            </div>
          </div>

          {/* Action Buttons (future - edit/delete) */}
          {(onEdit || onDelete) && (
            <div className="flex-shrink-0 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
              {onEdit && (
                <button
                  onClick={() => onEdit(task.id)}
                  className="p-2 text-gray-400 hover:text-primary-600 rounded-lg hover:bg-gray-100 transition-colors focus:outline-none focus:ring-4 focus:ring-primary-100"
                  aria-label="Edit task"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                </button>
              )}

              {onDelete && (
                <button
                  onClick={() => onDelete(task.id)}
                  className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors focus:outline-none focus:ring-4 focus:ring-red-100"
                  aria-label="Delete task"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

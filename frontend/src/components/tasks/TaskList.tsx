'use client'

import { useState } from 'react'
import { Task } from '@/lib/api/tasks'
import TaskItem from './TaskItem'

interface TaskListProps {
  tasks: Task[]
  onToggleComplete?: (taskId: number) => void
  onEdit?: (taskId: number) => void
  onDelete?: (taskId: number) => void
  onTagAdd?: (taskId: number, tag: string) => void
  onTagRemove?: (taskId: number, tag: string) => void
  onAddTask?: () => void
  searchQuery?: string
}

type Filter = 'all' | 'active' | 'completed'

export default function TaskList({ tasks, onToggleComplete, onEdit, onDelete, onTagAdd, onTagRemove, onAddTask, searchQuery }: TaskListProps) {
  const [filter, setFilter] = useState<Filter>('all')

  const active = tasks.filter((t) => !t.completed)
  const done = tasks.filter((t) => t.completed)
  const shown = filter === 'active' ? active : filter === 'completed' ? done : tasks

  const tabs: { key: Filter; label: string; count: number }[] = [
    { key: 'all',       label: 'All',       count: tasks.length },
    { key: 'active',    label: 'Active',    count: active.length },
    { key: 'completed', label: 'Done',      count: done.length },
  ]

  if (tasks.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="w-16 h-16 bg-teal-50 rounded-2xl flex items-center justify-center mx-auto mb-4 ring-1 ring-teal-100">
          <svg className="w-8 h-8 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h3 className="text-base font-semibold text-teal-900 mb-1">No tasks yet</h3>
        <p className="text-sm text-teal-600/60 mb-5">Create your first task to get started</p>
        {onAddTask && (
          <button onClick={onAddTask}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-teal-600 hover:bg-teal-700 text-white text-sm font-semibold rounded-xl transition-all duration-150 shadow-md shadow-teal-600/25 hover:-translate-y-px cursor-pointer">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Create task
          </button>
        )}
      </div>
    )
  }

  return (
    <div>
      {/* Filter tabs */}
      <div className="flex items-center gap-0.5 p-1 bg-teal-50 border border-teal-100 rounded-xl mb-4 w-fit">
        {tabs.map(({ key, label, count }) => (
          <button key={key} onClick={() => setFilter(key)} className="cursor-pointer"
            aria-pressed={filter === key}>
            <span className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 ${
              filter === key
                ? 'bg-white text-teal-800 shadow-sm ring-1 ring-teal-100'
                : 'text-teal-600/70 hover:text-teal-700'
            }`}>
              {label}
              <span className={`min-w-4 text-center rounded-full px-1 text-xs ${
                filter === key ? 'bg-teal-100 text-teal-700' : 'text-teal-400'
              }`}>
                {count}
              </span>
            </span>
          </button>
        ))}
      </div>

      {/* Task list */}
      {shown.length === 0 ? (
        <div className="text-center py-10">
          {filter === 'active' ? (
            <>
              <div className="w-12 h-12 bg-emerald-50 rounded-xl flex items-center justify-center mx-auto mb-3 ring-1 ring-emerald-100">
                <svg className="w-6 h-6 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-sm font-semibold text-teal-900">All done!</p>
              <p className="text-xs text-teal-600/60 mt-0.5">You've completed all your tasks.</p>
            </>
          ) : (
            <p className="text-sm text-teal-600/60">No completed tasks yet.</p>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          {shown.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onToggleComplete={onToggleComplete}
              onEdit={onEdit}
              onDelete={onDelete}
              onTagAdd={onTagAdd}
              onTagRemove={onTagRemove}
              searchQuery={searchQuery}
            />
          ))}
        </div>
      )}
    </div>
  )
}

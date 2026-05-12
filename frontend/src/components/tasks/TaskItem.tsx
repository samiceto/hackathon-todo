'use client'

import { useState, useRef } from 'react'
import { Task } from '@/lib/api/tasks'
import RecurrenceDisplay from './RecurrenceDisplay'

interface TaskItemProps {
  task: Task
  onToggleComplete?: (taskId: number) => void
  onEdit?: (taskId: number) => void
  onDelete?: (taskId: number) => void
  onTagAdd?: (taskId: number, tag: string) => void
  onTagRemove?: (taskId: number, tag: string) => void
  searchQuery?: string
}

const PRIORITY_CONFIG: Record<string, { dot: string; badge: string; label: string }> = {
  urgent: { dot: 'bg-red-500',    badge: 'bg-red-50 text-red-700 border-red-200',    label: 'Urgent' },
  high:   { dot: 'bg-orange-500', badge: 'bg-orange-50 text-orange-700 border-orange-200', label: 'High'   },
  medium: { dot: 'bg-teal-500',   badge: 'bg-teal-50 text-teal-700 border-teal-200',  label: 'Medium' },
  low:    { dot: 'bg-gray-400',   badge: 'bg-gray-50 text-gray-600 border-gray-200',  label: 'Low'    },
}

function highlight(text: string, query?: string) {
  if (!query?.trim()) return <span>{text}</span>
  const words = query.trim().split(/\s+/)
  const pattern = words.map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')
  const parts = text.split(new RegExp(`(${pattern})`, 'gi'))
  return (
    <span>
      {parts.map((p, i) =>
        words.some((w) => p.toLowerCase() === w.toLowerCase()) ? (
          <mark key={i} className="bg-yellow-200 text-gray-900 rounded-sm px-0.5">{p}</mark>
        ) : (
          <span key={i}>{p}</span>
        )
      )}
    </span>
  )
}

function toUtcDate(dateStr: string): Date {
  // Backend sends naive UTC strings (no Z/offset); force UTC interpretation
  return new Date(/[Z+]/.test(dateStr) ? dateStr : dateStr + 'Z')
}

function formatRelative(dateStr: string) {
  const d = toUtcDate(dateStr), now = new Date()
  const m = Math.floor((now.getTime() - d.getTime()) / 60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  const days = Math.floor(h / 24)
  if (days < 7) return `${days}d ago`
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function getDueDateStyle(dateStr: string) {
  const due = toUtcDate(dateStr), now = new Date()
  const ms = due.getTime() - now.getTime()
  const days = Math.floor(ms / 86400000)
  if (ms < 0) return { text: days === 0 ? 'Overdue' : `Overdue ${Math.abs(days)}d`, cls: 'bg-red-50 text-red-700 border-red-200' }
  if (days === 0) return { text: `Due in ${Math.floor(ms / 3600000)}h`, cls: 'bg-orange-50 text-orange-700 border-orange-200' }
  if (days <= 7) return { text: `Due in ${days}d`, cls: 'bg-amber-50 text-amber-700 border-amber-200' }
  return { text: due.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), cls: 'bg-gray-50 text-gray-600 border-gray-200' }
}

export default function TaskItem({ task, onToggleComplete, onEdit, onDelete, onTagAdd, onTagRemove, searchQuery }: TaskItemProps) {
  const [isToggling, setIsToggling] = useState(false)
  const [showCelebration, setShowCelebration] = useState(false)
  const [isAddingTag, setIsAddingTag] = useState(false)
  const [newTag, setNewTag] = useState('')
  const tagInputRef = useRef<HTMLInputElement>(null)
  const pc = PRIORITY_CONFIG[task.priority ?? 'medium'] ?? PRIORITY_CONFIG.medium

  const handleToggle = async () => {
    if (isToggling) return
    setIsToggling(true)
    if (!task.completed) { setShowCelebration(true); setTimeout(() => setShowCelebration(false), 800) }
    onToggleComplete?.(task.id)
    setTimeout(() => setIsToggling(false), 350)
  }

  return (
    <div className={`group relative bg-white rounded-xl border transition-all duration-200 hover:shadow-md hover:-translate-y-px ${
      task.completed ? 'border-gray-100 opacity-75' : 'border-teal-100 hover:border-teal-200 hover:shadow-teal-100/50'
    } ${showCelebration ? 'animate-celebration' : ''}`}>

      {/* Priority left accent */}
      {!task.completed && (
        <div className={`absolute left-0 top-3 bottom-3 w-0.5 rounded-full ${pc.dot}`} />
      )}

      {/* Confetti particles */}
      {showCelebration && (
        <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-xl">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="absolute w-1.5 h-1.5 bg-emerald-400 rounded-full animate-confetti"
              style={{ left: `${20 + i * 12}%`, top: '40%', animationDelay: `${i * 60}ms` }} />
          ))}
        </div>
      )}

      <div className="px-4 py-3.5 pl-5">
        <div className="flex items-start gap-3">
          {/* Checkbox */}
          <button
            onClick={handleToggle}
            disabled={isToggling}
            aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
            className={`flex-shrink-0 mt-0.5 w-5 h-5 rounded-md border-2 transition-all duration-200 flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-teal-300 focus:ring-offset-1 cursor-pointer
              ${task.completed
                ? 'bg-teal-600 border-teal-600'
                : 'bg-white border-gray-300 hover:border-teal-500'
              } ${isToggling ? 'opacity-60 scale-90' : ''}`}
          >
            {isToggling ? (
              <svg className="w-3 h-3 animate-spin text-gray-400" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : task.completed ? (
              <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            ) : null}
          </button>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <h3 className={`text-sm font-semibold leading-snug mb-0.5 ${
              task.completed ? 'line-through text-gray-400 decoration-gray-300' : 'text-gray-900'
            }`}>
              {highlight(task.title, searchQuery)}
            </h3>

            {task.description && (
              <p className={`text-xs leading-relaxed mb-2 ${task.completed ? 'text-gray-400' : 'text-gray-500'}`}>
                {highlight(task.description, searchQuery)}
              </p>
            )}

            {/* Metadata row */}
            <div className="flex flex-wrap items-center gap-1.5">
              {/* Created */}
              <span className="text-xs text-gray-400">{formatRelative(task.created_at)}</span>

              {/* Priority badge (if not medium) */}
              {task.priority && task.priority !== 'medium' && (
                <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium border ${pc.badge}`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${pc.dot} flex-shrink-0`} />
                  {pc.label}
                </span>
              )}

              {/* Due date */}
              {task.due_date && !task.completed && (() => {
                const d = getDueDateStyle(task.due_date)
                return (
                  <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium border ${d.cls}`}>
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {d.text}
                  </span>
                )
              })()}

              {/* Reminder */}
              {task.reminder_offset && task.due_date && (
                <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium border bg-violet-50 text-violet-700 border-violet-200"
                  title={`${task.reminder_offset}m before due`}>
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                  Reminder
                </span>
              )}

              {/* Done badge */}
              {task.completed && (
                <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 animate-slide-up">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Done
                </span>
              )}
            </div>

            {/* Recurrence */}
            {task.recurrence_rule && (
              <div className="mt-1.5">
                <RecurrenceDisplay recurrenceRule={task.recurrence_rule} />
              </div>
            )}

            {/* Tags */}
            {((task.tags && task.tags.length > 0) || (onTagAdd && !task.completed)) && (
              <div className="mt-2 flex flex-wrap gap-1 items-center">
                {task.tags?.map((tag) => (
                  <span key={tag} className="inline-flex items-center gap-0.5 px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded-md border border-slate-200">
                    {tag}
                    {onTagRemove && !task.completed && (
                      <button onClick={(e) => { e.stopPropagation(); onTagRemove(task.id, tag) }}
                        className="ml-0.5 text-slate-400 hover:text-red-500 transition-colors" aria-label={`Remove ${tag}`}>
                        <svg className="w-2.5 h-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    )}
                  </span>
                ))}
                {onTagAdd && !task.completed && !isAddingTag && (task.tags?.length ?? 0) < 10 && (
                  <button onClick={() => setIsAddingTag(true)}
                    className="inline-flex items-center gap-0.5 px-1.5 py-0.5 text-xs text-gray-400 hover:text-teal-600 border border-dashed border-gray-300 hover:border-teal-400 rounded-md transition-colors cursor-pointer">
                    <svg className="w-2.5 h-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                    </svg>
                    tag
                  </button>
                )}
                {isAddingTag && (
                  <input ref={tagInputRef} type="text" value={newTag} onChange={(e) => setNewTag(e.target.value)} autoFocus maxLength={50} placeholder="tag…"
                    className="px-2 py-0.5 text-xs border border-teal-300 rounded-md w-20 outline-none focus:ring-1 focus:ring-teal-400"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') { const t = newTag.trim(); if (t) onTagAdd?.(task.id, t); setNewTag(''); setIsAddingTag(false) }
                      if (e.key === 'Escape') { setNewTag(''); setIsAddingTag(false) }
                    }}
                    onBlur={() => { setNewTag(''); setIsAddingTag(false) }}
                  />
                )}
              </div>
            )}
          </div>

          {/* Action buttons */}
          {(onEdit || onDelete) && (
            <div className="flex-shrink-0 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity ml-1">
              {onEdit && (
                <button onClick={() => onEdit(task.id)} aria-label="Edit task"
                  className="w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-teal-600 hover:bg-teal-50 transition-all cursor-pointer">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
              )}
              {onDelete && (
                <button onClick={() => onDelete(task.id)} aria-label="Delete task"
                  className="w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition-all">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
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

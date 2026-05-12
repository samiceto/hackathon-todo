'use client'

import React, { useState, useEffect } from 'react'
import { Task } from '@/lib/api/tasks'
import RecurrenceInput from './RecurrenceInput'
import DueDatePicker from './DueDatePicker'
import ReminderOffsetInput from './ReminderOffsetInput'
import PrioritySelector from './PrioritySelector'
import TagInput from './TagInput'

export interface TaskFormData {
  title: string
  description: string
  priority?: string
  due_date?: string | null
  recurrence_rule?: string | null
  reminder_offset?: number | null
  tags?: string[]
}

export interface TaskFormProps {
  onTaskCreated?: (task: TaskFormData) => void
  onTaskUpdated?: (taskId: number, task: TaskFormData) => void
  onCancel?: () => void
  isSubmitting?: boolean
  isExpanded?: boolean
  editTask?: Task | null
}

export const TaskForm: React.FC<TaskFormProps> = ({
  onTaskCreated,
  onTaskUpdated,
  onCancel,
  isSubmitting = false,
  isExpanded: initialExpanded = false,
  editTask = null,
}) => {
  const isEditMode = !!editTask
  const [isExpanded, setIsExpanded] = useState(initialExpanded || isEditMode)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<string>('medium')
  const [dueDate, setDueDate] = useState<string>('')
  const [recurrenceRule, setRecurrenceRule] = useState<string | null>(null)
  const [reminderOffset, setReminderOffset] = useState<string>('')
  const [tags, setTags] = useState<string[]>([])
  const [errors, setErrors] = useState<{ title?: string; reminderOffset?: string }>({})
  const [hasInteracted, setHasInteracted] = useState(false)

  useEffect(() => {
    if (editTask) {
      setTitle(editTask.title)
      setDescription(editTask.description || '')
      setPriority(editTask.priority || 'medium')
      setDueDate(editTask.due_date ? editTask.due_date.substring(0, 16) : '')
      setRecurrenceRule(editTask.recurrence_rule || null)
      setReminderOffset(editTask.reminder_offset ? String(editTask.reminder_offset) : '')
      setTags(editTask.tags || [])
      setIsExpanded(true)
      setErrors({})
      setHasInteracted(false)
    }
  }, [editTask])

  const reset = () => {
    setTitle('')
    setDescription('')
    setPriority('medium')
    setDueDate('')
    setRecurrenceRule(null)
    setReminderOffset('')
    setTags([])
    setErrors({})
    setHasInteracted(false)
  }

  const validate = () => {
    const errs: typeof errors = {}
    if (!title.trim()) errs.title = 'Title is required'
    else if (title.length > 500) errs.title = 'Max 500 characters'
    if (reminderOffset && !dueDate) errs.reminderOffset = 'Reminder requires a due date'
    else if (reminderOffset) {
      const n = parseInt(reminderOffset, 10)
      if (isNaN(n) || n <= 0) errs.reminderOffset = 'Must be a positive number'
    }
    return errs
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setHasInteracted(true)
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }

    const taskData: TaskFormData = {
      title: title.trim(),
      description: description.trim(),
      priority,
      due_date: dueDate ? new Date(dueDate).toISOString() : null,
      recurrence_rule: recurrenceRule || null,
      reminder_offset: reminderOffset ? parseInt(reminderOffset, 10) : null,
      tags: tags.length > 0 ? tags : undefined,
    }

    if (isEditMode && editTask) {
      onTaskUpdated?.(editTask.id, taskData)
    } else {
      onTaskCreated?.(taskData)
      reset()
      setIsExpanded(false)
    }
  }

  const handleCancel = () => {
    reset()
    if (!isEditMode) setIsExpanded(false)
    onCancel?.()
  }

  if (!isExpanded) {
    return (
      <button
        onClick={() => setIsExpanded(true)}
        className="w-full flex items-center gap-2 h-10 px-4 text-sm text-gray-400 hover:text-teal-500 border border-dashed border-gray-300 hover:border-teal-300 rounded-xl transition-colors"
      >
        <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
        </svg>
        Add a task...
      </button>
    )
  }

  const inputCls = 'w-full h-9 px-3 text-sm rounded-lg border outline-none transition-all focus:ring-2 focus:ring-teal-100'

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden animate-slide-down">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <h3 className="text-sm font-semibold text-gray-900">{isEditMode ? 'Edit task' : 'New task'}</h3>
        <button onClick={handleCancel} aria-label="Close"
          className="w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="p-4 space-y-4">
        {/* Title */}
        <div>
          <input
            type="text"
            value={title}
            onChange={(e) => { setTitle(e.target.value); if (hasInteracted) setErrors((p) => ({ ...p, title: undefined })) }}
            placeholder="Task title *"
            maxLength={500}
            className={`${inputCls} ${errors.title ? 'border-red-300 focus:border-red-400' : 'border-gray-200 focus:border-teal-400'}`}
          />
          {errors.title && <p className="mt-1 text-xs text-red-500">{errors.title}</p>}
        </div>

        {/* Description */}
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Description (optional)"
          rows={2}
          maxLength={5000}
          className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 outline-none focus:border-teal-400 focus:ring-2 focus:ring-teal-100 transition-all resize-none"
        />

        {/* Priority + Tags */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
          <PrioritySelector value={priority} onChange={setPriority} />
          <TagInput value={tags} onChange={setTags} maxTags={10} />
        </div>

        {/* Due date + Reminder */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <DueDatePicker value={dueDate} onChange={setDueDate} showClear />
          <ReminderOffsetInput value={reminderOffset} onChange={setReminderOffset} hasDueDate={!!dueDate} error={errors.reminderOffset} />
        </div>

        {/* Recurrence */}
        <RecurrenceInput value={recurrenceRule} onChange={setRecurrenceRule} />

        {/* Actions */}
        <div className="flex items-center gap-2 pt-2 border-t border-gray-100">
          <button
            type="submit"
            disabled={isSubmitting}
            className="h-9 px-5 bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isSubmitting ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Saving…
              </>
            ) : (isEditMode ? 'Update task' : 'Create task')}
          </button>
          <button
            type="button"
            onClick={handleCancel}
            disabled={isSubmitting}
            className="h-9 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

export default TaskForm

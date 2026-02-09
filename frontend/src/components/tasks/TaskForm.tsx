/**
 * TaskForm Component - Phases 5 & 6 + Step 5 Enhancements
 *
 * An elegant, inviting form for creating and editing tasks.
 * Designed to make task capture and updates feel effortless and rewarding.
 *
 * Step 5 Enhancements:
 * - Priority selection (low, medium, high, urgent)
 * - Due date picker with datetime support
 * - Recurrence rule input (RRULE format)
 * - Reminder offset (minutes before due date)
 */

'use client'

import React, { useState, useEffect } from 'react'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import { Task } from '@/lib/api/tasks'
import RecurrenceInput from './RecurrenceInput'
import DueDatePicker from './DueDatePicker'
import ReminderOffsetInput from './ReminderOffsetInput'
import PrioritySelector from './PrioritySelector'
import TagInput from './TagInput'

export interface TaskFormData {
  title: string
  description: string
  // Step 5: Advanced fields
  priority?: string
  due_date?: string | null
  recurrence_rule?: string | null
  reminder_offset?: number | null
  tags?: string[]
}

export interface TaskFormProps {
  /** Callback when task is successfully created */
  onTaskCreated?: (task: TaskFormData) => void
  /** Callback when task is successfully updated */
  onTaskUpdated?: (taskId: number, task: TaskFormData) => void
  /** Callback when form is cancelled */
  onCancel?: () => void
  /** Loading state during submission */
  isSubmitting?: boolean
  /** Show form in expanded state by default */
  isExpanded?: boolean
  /** Edit mode - provide existing task to edit */
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

  // Step 5: Advanced fields
  const [priority, setPriority] = useState<string>('medium')
  const [dueDate, setDueDate] = useState<string>('')
  const [recurrenceRule, setRecurrenceRule] = useState<string | null>(null)
  const [reminderOffset, setReminderOffset] = useState<string>('')
  const [tags, setTags] = useState<string[]>([])

  const [errors, setErrors] = useState<{ title?: string; description?: string; reminderOffset?: string }>({})
  const [hasInteracted, setHasInteracted] = useState(false)

  // Populate form when editing
  useEffect(() => {
    if (editTask) {
      setTitle(editTask.title)
      setDescription(editTask.description || '')

      // Step 5: Populate advanced fields
      setPriority(editTask.priority || 'medium')
      setDueDate(editTask.due_date ? editTask.due_date.substring(0, 16) : '') // Format for datetime-local input
      setRecurrenceRule(editTask.recurrence_rule || null)
      setReminderOffset(editTask.reminder_offset ? String(editTask.reminder_offset) : '')
      setTags(editTask.tags || [])

      setIsExpanded(true)
      setErrors({})
      setHasInteracted(false)
    }
  }, [editTask])

  // Validation
  const validateTitle = (value: string): string | undefined => {
    if (!value.trim()) {
      return 'Task title is required'
    }
    if (value.length > 500) {
      return 'Title must be 500 characters or less'
    }
    return undefined
  }

  const validateDescription = (value: string): string | undefined => {
    if (value.length > 5000) {
      return 'Description must be 5000 characters or less'
    }
    return undefined
  }

  // Step 5: Validate reminder offset
  const validateReminderOffset = (value: string, dueDate: string): string | undefined => {
    if (value && !dueDate) {
      return 'Reminder offset requires a due date'
    }
    if (value) {
      const offset = parseInt(value, 10)
      if (isNaN(offset) || offset <= 0) {
        return 'Reminder offset must be a positive number'
      }
    }
    return undefined
  }

  // Handle title change with validation
  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setTitle(value)
    if (hasInteracted) {
      setErrors((prev) => ({ ...prev, title: validateTitle(value) }))
    }
  }

  // Handle description change with validation
  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value
    setDescription(value)
    if (hasInteracted) {
      setErrors((prev) => ({ ...prev, description: validateDescription(value) }))
    }
  }

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setHasInteracted(true)

    // Validate all fields
    const titleError = validateTitle(title)
    const descriptionError = validateDescription(description)
    const reminderOffsetError = validateReminderOffset(reminderOffset, dueDate)

    if (titleError || descriptionError || reminderOffsetError) {
      setErrors({
        title: titleError,
        description: descriptionError,
        reminderOffset: reminderOffsetError,
      })
      return
    }

    // Build task data
    const taskData: TaskFormData = {
      title: title.trim(),
      description: description.trim(),
      priority,
      due_date: dueDate ? new Date(dueDate).toISOString() : null,
      recurrence_rule: recurrenceRule || null,
      reminder_offset: reminderOffset ? parseInt(reminderOffset, 10) : null,
      tags: tags.length > 0 ? tags : undefined,
    }

    // Submit
    if (isEditMode && editTask) {
      onTaskUpdated?.(editTask.id, taskData)
    } else {
      onTaskCreated?.(taskData)
    }

    // Reset form (except in edit mode - parent will close it)
    if (!isEditMode) {
      setTitle('')
      setDescription('')
      setPriority('medium')
      setDueDate('')
      setRecurrenceRule(null)
      setReminderOffset('')
      setTags([])
      setErrors({})
      setHasInteracted(false)
      setIsExpanded(false)
    }
  }

  // Handle cancel
  const handleCancel = () => {
    setTitle('')
    setDescription('')
    setPriority('medium')
    setDueDate('')
    setRecurrenceRule(null)
    setReminderOffset('')
    setTags([])
    setErrors({})
    setHasInteracted(false)
    if (!isEditMode) {
      setIsExpanded(false)
    }
    onCancel?.()
  }

  // Collapsed state - just a button to expand
  if (!isExpanded) {
    return (
      <div className="mb-8 animate-slide-up">
        <button
          onClick={() => setIsExpanded(true)}
          className="
            w-full
            px-6 py-5
            bg-white
            border-2 border-dashed border-gray-300
            rounded-2xl
            transition-all duration-300 ease-out
            hover:border-primary-400
            hover:bg-primary-50/50
            hover:scale-[1.01]
            focus:outline-none
            focus:ring-4
            focus:ring-primary-500/20
            group
          "
        >
          <div className="flex items-center justify-center gap-3">
            <div className="
              w-12 h-12
              bg-gradient-to-br from-primary-500 to-primary-600
              rounded-2xl
              flex items-center justify-center
              shadow-lg shadow-primary-500/30
              group-hover:shadow-xl group-hover:shadow-primary-500/40
              group-hover:scale-110
              transition-all duration-300
            ">
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={3}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <div className="text-left">
              <div className="text-lg font-bold text-gray-900 tracking-tight">
                Create New Task
              </div>
              <div className="text-sm text-gray-500 font-light">
                Click to add a task to your list
              </div>
            </div>
          </div>
        </button>
      </div>
    )
  }

  // Expanded state - full form
  return (
    <div className="mb-8 animate-slide-up">
      <div className="
        bg-white
        border-2 border-primary-200
        rounded-3xl
        shadow-xl shadow-primary-500/10
        overflow-hidden
      ">
        {/* Form header */}
        <div className="
          px-6 py-4
          bg-gradient-to-r from-primary-50 to-primary-100/50
          border-b-2 border-primary-200
        ">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="
                w-10 h-10
                bg-gradient-to-br from-primary-500 to-primary-600
                rounded-xl
                flex items-center justify-center
                shadow-lg shadow-primary-500/30
              ">
                <svg
                  className="w-5 h-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900 tracking-tight">
                  {isEditMode ? 'Edit Task' : 'New Task'}
                </h3>
                <p className="text-xs text-gray-600 font-light">
                  {isEditMode ? 'Update the task details' : 'Fill in the details below'}
                </p>
              </div>
            </div>

            {/* Close button */}
            <button
              onClick={handleCancel}
              className="
                w-8 h-8
                rounded-xl
                flex items-center justify-center
                text-gray-500
                hover:text-gray-700
                hover:bg-white
                transition-all duration-200
                focus:outline-none
                focus:ring-2
                focus:ring-primary-500
              "
              aria-label="Cancel"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Form content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Title input */}
          <Input
            label="Task Title"
            type="text"
            placeholder="e.g., Buy groceries, Finish report, Call mom..."
            value={title}
            onChange={handleTitleChange}
            error={errors.title}
            required
            showCharCount
            maxCharCount={500}
            icon={
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
            }
          />

          {/* Description input */}
          <Input
            label="Description"
            placeholder="Add any additional details (optional)..."
            value={description}
            onChange={handleDescriptionChange}
            error={errors.description}
            multiline
            rows={4}
            showCharCount
            maxCharCount={5000}
            helperText="Optional - add context, notes, or subtasks"
          />

          {/* Step 5: Priority selection */}
          <PrioritySelector
            value={priority}
            onChange={setPriority}
          />

          {/* Step 5: Tags */}
          <TagInput
            value={tags}
            onChange={setTags}
            maxTags={10}
          />

          {/* Step 5: Due date */}
          <DueDatePicker
            value={dueDate}
            onChange={setDueDate}
            label="Due Date (optional)"
            showClear
          />

          {/* Step 5: Recurrence rule */}
          <RecurrenceInput
            value={recurrenceRule}
            onChange={setRecurrenceRule}
          />

          {/* Step 5: Reminder offset */}
          <ReminderOffsetInput
            value={reminderOffset}
            onChange={setReminderOffset}
            hasDueDate={!!dueDate}
            error={errors.reminderOffset}
          />

          {/* Action buttons */}
          <div className="flex items-center gap-3 pt-2">
            <Button
              type="submit"
              variant="primary"
              size="large"
              fullWidth
              isLoading={isSubmitting}
              leftIcon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              }
            >
              {isEditMode ? 'Update Task' : 'Create Task'}
            </Button>

            <Button
              type="button"
              variant="ghost"
              size="large"
              onClick={handleCancel}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default TaskForm

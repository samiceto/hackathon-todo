import { useEffect, useRef, useCallback } from 'react'
import { Task } from '@/lib/api/tasks'

const STORAGE_KEY = 'shownReminders'

/**
 * Checks tasks every minute and fires onReminder when a task's reminder
 * time has arrived (due_date minus reminder_offset minutes).
 * Uses sessionStorage to avoid re-firing on page refresh within the same session.
 */
export function useReminderNotifications(
  tasks: Task[],
  onReminder: (task: Task) => void
) {
  const shownRef = useRef<Set<string>>(new Set())

  useEffect(() => {
    try {
      const stored = sessionStorage.getItem(STORAGE_KEY)
      if (stored) {
        shownRef.current = new Set(JSON.parse(stored))
      }
    } catch {
      // sessionStorage unavailable — silently skip
    }
  }, [])

  const checkReminders = useCallback(() => {
    const now = new Date()
    for (const task of tasks) {
      if (task.completed || !task.due_date || !task.reminder_offset) continue

      const dueDate = new Date(task.due_date)
      const reminderTime = new Date(dueDate.getTime() - task.reminder_offset * 60 * 1000)
      // Unique key: fire at most once per task+due_date+offset combination
      const key = `${task.id}-${task.due_date}-${task.reminder_offset}`

      if (now >= reminderTime && now < dueDate && !shownRef.current.has(key)) {
        shownRef.current.add(key)
        try {
          sessionStorage.setItem(STORAGE_KEY, JSON.stringify([...shownRef.current]))
        } catch {
          // ignore storage errors
        }
        onReminder(task)
      }
    }
  }, [tasks, onReminder])

  useEffect(() => {
    checkReminders()
    const interval = setInterval(checkReminders, 60_000)
    return () => clearInterval(interval)
  }, [checkReminders])
}

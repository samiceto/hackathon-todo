'use client'

/**
 * Tasks Page
 *
 * Main dashboard for authenticated users to view and manage their tasks.
 * Displays task list with filtering, loading states, and error handling.
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import authClient from '@/lib/auth/auth-client'
import { taskApi, Task } from '@/lib/api/tasks'
import TaskList from '@/components/tasks/TaskList'
import TaskForm from '@/components/tasks/TaskForm'
import Loading from '@/components/ui/Loading'
import ErrorMessage from '@/components/ui/ErrorMessage'
import DeleteConfirm from '@/components/tasks/DeleteConfirm'
import { useToast } from '@/lib/hooks/useToast'

export default function TasksPage() {
  const router = useRouter()
  const toast = useToast()
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [user, setUser] = useState<{ id: number; email: string } | null>(null)
  const [isCreatingTask, setIsCreatingTask] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [isUpdatingTask, setIsUpdatingTask] = useState(false)
  const [deletingTask, setDeletingTask] = useState<Task | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  // Fetch tasks on mount
  useEffect(() => {
    const loadTasks = async () => {
      try {
        // Get current user from token
        const currentUser = authClient.getCurrentUser()
        if (!currentUser) {
          router.push('/signin')
          return
        }

        setUser(currentUser)

        // Fetch tasks for user
        const response = await taskApi.getTasks(currentUser.id)
        setTasks(response.tasks)
        setError(null)
      } catch (err: any) {
        console.error('Failed to load tasks:', err)
        setError(err.message || 'Failed to load tasks. Please try again.')
      } finally {
        setIsLoading(false)
      }
    }

    loadTasks()
  }, [router])

  // Handle toggle completion
  const handleToggleComplete = async (taskId: number) => {
    if (!user) return

    try {
      // Optimistic update
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.id === taskId ? { ...task, completed: !task.completed } : task
        )
      )

      // API call
      const updatedTask = await taskApi.toggleComplete(user.id, taskId)

      // Update with server response
      setTasks((prevTasks) =>
        prevTasks.map((task) => (task.id === taskId ? updatedTask : task))
      )
    } catch (err: any) {
      console.error('Failed to toggle task:', err)

      // Revert optimistic update on error
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.id === taskId ? { ...task, completed: !task.completed } : task
        )
      )

      toast.error('Failed to toggle task completion. Please try again.')
    }
  }

  // Handle create task
  const handleCreateTask = async (taskData: { title: string; description: string }) => {
    if (!user) return

    setIsCreatingTask(true)
    setError(null)

    try {
      // API call to create task
      const newTask = await taskApi.createTask(user.id, taskData)

      // Add new task to the beginning of the list (newest first)
      setTasks((prevTasks) => [newTask, ...prevTasks])

      toast.success('Task created successfully!')
    } catch (err: any) {
      console.error('Failed to create task:', err)
      toast.error('Failed to create task. Please try again.')
    } finally {
      setIsCreatingTask(false)
    }
  }

  // Handle edit task (open edit form)
  const handleEditTask = (taskId: number) => {
    const task = tasks.find((t) => t.id === taskId)
    if (task) {
      setEditingTask(task)
      setError(null)
    }
  }

  // Handle update task
  const handleUpdateTask = async (
    taskId: number,
    taskData: { title: string; description: string }
  ) => {
    if (!user) return

    setIsUpdatingTask(true)
    setError(null)

    try {
      // API call to update task
      const updatedTask = await taskApi.updateTask(user.id, taskId, taskData)

      // Update task in the list
      setTasks((prevTasks) =>
        prevTasks.map((task) => (task.id === taskId ? updatedTask : task))
      )

      // Close edit form
      setEditingTask(null)

      toast.success('Task updated successfully!')
    } catch (err: any) {
      console.error('Failed to update task:', err)
      toast.error('Failed to update task. Please try again.')
    } finally {
      setIsUpdatingTask(false)
    }
  }

  // Handle cancel edit
  const handleCancelEdit = () => {
    setEditingTask(null)
    setError(null)
  }

  // Handle delete task (open confirmation modal)
  const handleDeleteTask = (taskId: number) => {
    const task = tasks.find((t) => t.id === taskId)
    if (task) {
      setDeletingTask(task)
      setError(null)
    }
  }

  // Handle confirm delete
  const handleConfirmDelete = async () => {
    if (!user || !deletingTask) return

    setIsDeleting(true)

    try {
      // API call to delete task
      await taskApi.deleteTask(user.id, deletingTask.id)

      // Remove task from the list
      setTasks((prevTasks) => prevTasks.filter((task) => task.id !== deletingTask.id))

      // Close confirmation modal
      setDeletingTask(null)

      toast.success('Task deleted successfully!')
    } catch (err: any) {
      console.error('Failed to delete task:', err)
      toast.error('Failed to delete task. Please try again.')
      setDeletingTask(null)
    } finally {
      setIsDeleting(false)
    }
  }

  // Handle cancel delete
  const handleCancelDelete = () => {
    if (!isDeleting) {
      setDeletingTask(null)
      setError(null)
    }
  }

  // Handle logout
  const handleLogout = async () => {
    await authClient.signout()
    router.push('/')
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loading message="Loading your tasks..." size="large" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-primary-50/20">
      {/* Header */}
      <header className="bg-white border-b-2 border-gray-200 sticky top-0 z-40 backdrop-blur-sm bg-white/90">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo/Title */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">My Tasks</h1>
                {user && (
                  <p className="text-xs text-gray-500">{user.email}</p>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3">
              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-xl transition-colors font-medium focus:outline-none focus:ring-4 focus:ring-gray-200"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                  />
                </svg>
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 animate-slide-up">
            <ErrorMessage
              message={error}
              onRetry={() => {
                setError(null)
                setIsLoading(true)
                window.location.reload()
              }}
            />
          </div>
        )}

        {/* Task Creation/Edit Form */}
        {editingTask ? (
          <TaskForm
            editTask={editingTask}
            onTaskUpdated={handleUpdateTask}
            onCancel={handleCancelEdit}
            isSubmitting={isUpdatingTask}
          />
        ) : (
          <TaskForm
            onTaskCreated={handleCreateTask}
            isSubmitting={isCreatingTask}
          />
        )}

        {/* Task List */}
        <TaskList
          tasks={tasks}
          onToggleComplete={handleToggleComplete}
          onEdit={handleEditTask}
          onDelete={handleDeleteTask}
        />

        {/* Delete Confirmation Modal */}
        {deletingTask && (
          <DeleteConfirm
            isOpen={!!deletingTask}
            taskTitle={deletingTask.title}
            onConfirm={handleConfirmDelete}
            onCancel={handleCancelDelete}
            isDeleting={isDeleting}
          />
        )}
      </main>
    </div>
  )
}

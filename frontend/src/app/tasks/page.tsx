'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import authClient from '@/lib/auth/auth-client'
import { taskApi, tagApi, Task } from '@/lib/api/tasks'
import TaskList from '@/components/tasks/TaskList'
import TaskForm, { TaskFormData } from '@/components/tasks/TaskForm'
import SearchBar from '@/components/tasks/SearchBar'
import FilterPanel, { FilterOptions } from '@/components/tasks/FilterPanel'
import SortControls, { SortOptions } from '@/components/tasks/SortControls'
import Pagination from '@/components/tasks/Pagination'
import Loading from '@/components/ui/Loading'
import ErrorMessage from '@/components/ui/ErrorMessage'
import DeleteConfirm from '@/components/tasks/DeleteConfirm'
import FloatingChat from '@/components/chat/FloatingChat'
import { useToast } from '@/lib/hooks/useToast'
import { useReminderNotifications } from '@/lib/hooks/useReminderNotifications'

export default function TasksPage() {
  const router = useRouter()
  const toast = useToast()
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isInitialLoad, setIsInitialLoad] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [user, setUser] = useState<{ id: number; email: string } | null>(null)
  const [isCreatingTask, setIsCreatingTask] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [isUpdatingTask, setIsUpdatingTask] = useState(false)
  const [deletingTask, setDeletingTask] = useState<Task | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [showMobileSidebar, setShowMobileSidebar] = useState(false)

  const [searchQuery, setSearchQuery] = useState<string>('')
  const [filters, setFilters] = useState<FilterOptions>({})
  const [sortOptions, setSortOptions] = useState<SortOptions>({ sortBy: null, sortOrder: 'desc' })
  const PAGE_SIZE = 10
  const [currentPage, setCurrentPage] = useState(1)
  const [totalTasks, setTotalTasks] = useState(0)

  const loadTasks = useCallback(async () => {
    try {
      const currentUser = authClient.getCurrentUser()
      if (!currentUser) { router.push('/signin'); return }
      setUser(currentUser)
      setIsLoading(true)

      const queryParams: Record<string, string> = {}
      if (searchQuery) queryParams.search = searchQuery
      if (filters.status) queryParams.status = filters.status
      if (filters.priority) queryParams.priority = filters.priority
      if (filters.tags && filters.tags.length > 0) queryParams.tags = filters.tags.join(',')
      if (filters.dueDateStart) queryParams.due_date_start = filters.dueDateStart
      if (filters.dueDateEnd) queryParams.due_date_end = filters.dueDateEnd
      if (sortOptions.sortBy) { queryParams.sort_by = sortOptions.sortBy; queryParams.sort_order = sortOptions.sortOrder }
      queryParams.limit = String(PAGE_SIZE)
      queryParams.offset = String((currentPage - 1) * PAGE_SIZE)

      const response = await taskApi.getTasks(currentUser.id, queryParams)
      setTasks(response.tasks)
      setTotalTasks(response.total)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to load tasks. Please try again.')
    } finally {
      setIsLoading(false)
      setIsInitialLoad(false)
    }
  }, [router, searchQuery, filters, sortOptions, currentPage])

  useEffect(() => { loadTasks() }, [loadTasks])

  const handleToggleComplete = async (taskId: number) => {
    if (!user) return
    setTasks((prev) => prev.map((t) => t.id === taskId ? { ...t, completed: !t.completed } : t))
    try {
      const updated = await taskApi.toggleComplete(user.id, taskId)
      setTasks((prev) => prev.map((t) => t.id === taskId ? updated : t))
    } catch {
      setTasks((prev) => prev.map((t) => t.id === taskId ? { ...t, completed: !t.completed } : t))
      toast.error('Failed to toggle task. Please try again.')
    }
  }

  const handleCreateTask = async (taskData: TaskFormData) => {
    if (!user) return
    setIsCreatingTask(true)
    setError(null)
    try {
      const newTask = await taskApi.createTask(user.id, taskData)
      setTasks((prev) => [newTask, ...prev])
      setShowCreateForm(false)
      toast.success('Task created!')
    } catch (err: any) {
      toast.error('Failed to create task. Please try again.')
    } finally {
      setIsCreatingTask(false)
    }
  }

  const handleEditTask = (taskId: number) => {
    const task = tasks.find((t) => t.id === taskId)
    if (task) { setEditingTask(task); setShowCreateForm(false); setError(null) }
  }

  const handleUpdateTask = async (taskId: number, taskData: TaskFormData) => {
    if (!user) return
    setIsUpdatingTask(true)
    setError(null)
    try {
      const updated = await taskApi.updateTask(user.id, taskId, taskData)
      setTasks((prev) => prev.map((t) => t.id === taskId ? updated : t))
      setEditingTask(null)
      toast.success('Task updated!')
    } catch (err: any) {
      toast.error('Failed to update task. Please try again.')
    } finally {
      setIsUpdatingTask(false)
    }
  }

  const handleCancelEdit = () => { setEditingTask(null); setError(null) }

  const handleDeleteTask = (taskId: number) => {
    const task = tasks.find((t) => t.id === taskId)
    if (task) { setDeletingTask(task); setError(null) }
  }

  const handleConfirmDelete = async () => {
    if (!user || !deletingTask) return
    setIsDeleting(true)
    try {
      await taskApi.deleteTask(user.id, deletingTask.id)
      setTasks((prev) => prev.filter((t) => t.id !== deletingTask.id))
      setDeletingTask(null)
      toast.success('Task deleted!')
    } catch (err: any) {
      toast.error('Failed to delete task. Please try again.')
      setDeletingTask(null)
    } finally {
      setIsDeleting(false)
    }
  }

  const handleCancelDelete = () => { if (!isDeleting) { setDeletingTask(null); setError(null) } }

  const handleTagAdd = useCallback(async (taskId: number, tag: string) => {
    if (!user) return
    setTasks((prev) => prev.map((t) => t.id === taskId ? { ...t, tags: [...(t.tags || []), tag] } : t))
    try {
      const updatedTags = await tagApi.addTag(user.id, taskId, tag)
      setTasks((prev) => prev.map((t) => t.id === taskId ? { ...t, tags: updatedTags } : t))
    } catch {
      setTasks((prev) => prev.map((t) => t.id === taskId ? { ...t, tags: (t.tags || []).filter((tg) => tg !== tag) } : t))
      toast.error('Failed to add tag.')
    }
  }, [user, toast])

  const handleTagRemove = useCallback(async (taskId: number, tag: string) => {
    if (!user) return
    setTasks((prev) => prev.map((t) => t.id === taskId ? { ...t, tags: (t.tags || []).filter((tg) => tg !== tag) } : t))
    try {
      await tagApi.removeTag(user.id, taskId, tag)
    } catch {
      setTasks((prev) => prev.map((t) => t.id === taskId ? { ...t, tags: [...(t.tags || []), tag] } : t))
      toast.error('Failed to remove tag.')
    }
  }, [user, toast])

  const handleReminder = useCallback((task: Task) => {
    const mins = task.reminder_offset!
    const label = mins >= 1440 ? `${Math.floor(mins / 1440)}d` : mins >= 60 ? `${Math.floor(mins / 60)}h` : `${mins}m`
    toast.warning(`Reminder: "${task.title}" is due in ${label}`)
  }, [toast])

  useReminderNotifications(tasks, handleReminder)

  const handleLogout = async () => { await authClient.signout(); router.push('/') }

  const hasActiveFilters = Object.values(filters).some(
    (v) => v !== null && v !== undefined && (Array.isArray(v) ? v.length > 0 : true)
  )
  const clearAll = () => { setCurrentPage(1); setSearchQuery(''); setFilters({}); setSortOptions({ sortBy: null, sortOrder: 'desc' }) }

  const sidebarInner = (
    <>
      {/* Mobile-only close row */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-teal-50 md:hidden flex-shrink-0">
        <span className="text-sm font-semibold text-gray-800">Menu</span>
        <button onClick={() => setShowMobileSidebar(false)}
          className="w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Logo */}
      <div className="px-4 py-4 flex-shrink-0 hidden md:block">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-teal-600 rounded-lg flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <span className="text-sm font-semibold text-gray-900">TaskFlow</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="px-3 pb-3 flex-shrink-0">
        <div className="flex items-center gap-2.5 px-3 py-2 rounded-lg bg-teal-50 text-teal-700 text-sm font-medium">
          <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          My Tasks
        </div>
      </nav>

      {/* Filters + Sort — scrollable */}
      <div className="flex-1 overflow-y-auto scrollbar-thin px-4 py-4 space-y-5 border-t border-teal-50">
        <FilterPanel
          onFilterChange={(newFilters) => { setCurrentPage(1); setFilters(newFilters) }}
          initialFilters={filters}
          isOpen={true}
        />
        <div className="pt-4 border-t border-teal-50">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-2 flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
            </svg>
            Sort
          </p>
          <SortControls
            onSortChange={(options) => { setCurrentPage(1); setSortOptions(options) }}
            initialSort={sortOptions}
          />
        </div>
      </div>

      {/* User + Logout */}
      <div className="px-3 py-3 border-t border-teal-50 flex-shrink-0">
        <div className="flex items-center gap-2.5 px-3 py-2 rounded-lg">
          <div className="w-7 h-7 bg-teal-100 rounded-full flex items-center justify-center text-xs font-semibold text-teal-700 flex-shrink-0">
            {user?.email?.[0]?.toUpperCase() ?? '?'}
          </div>
          <span className="flex-1 text-xs text-gray-600 truncate">{user?.email}</span>
          <button onClick={handleLogout} aria-label="Sign out"
            className="w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-all">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </>
  )

  if (isInitialLoad && isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-teal-50">
        <Loading message="Loading your tasks…" size="large" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-teal-50">
      {/* Desktop Sidebar */}
      <aside className="fixed inset-y-0 left-0 w-[248px] bg-white border-r border-teal-100 z-30 hidden md:flex flex-col overflow-hidden">
        {sidebarInner}
      </aside>

      {/* Mobile Sidebar Overlay */}
      {showMobileSidebar && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="absolute inset-0 bg-gray-900/40" onClick={() => setShowMobileSidebar(false)} />
          <aside className="absolute inset-y-0 left-0 w-72 bg-white shadow-xl flex flex-col overflow-hidden animate-slide-in-left">
            {sidebarInner}
          </aside>
        </div>
      )}

      {/* Main Content */}
      <div className="main-content min-h-screen flex flex-col">
        {/* Sticky Header */}
        <header className="sticky top-0 z-20 bg-white/95 backdrop-blur-sm border-b border-teal-100">
          <div className="flex items-center gap-3 px-4 md:px-6 h-14">
            {/* Mobile hamburger */}
            <button
              className="md:hidden w-9 h-9 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 transition-all"
              onClick={() => setShowMobileSidebar(true)}
              aria-label="Open menu"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            {/* Title */}
            <div className="flex-1 min-w-0">
              <h1 className="text-base font-semibold text-gray-900 leading-tight">My Tasks</h1>
              <p className="text-xs text-gray-400 hidden sm:block">{totalTasks} task{totalTasks !== 1 ? 's' : ''}</p>
            </div>

            {/* Search (sm+) */}
            <div className="hidden sm:block w-52">
              <SearchBar
                onSearch={(q) => { setCurrentPage(1); setSearchQuery(q) }}
                placeholder="Search…"
                debounceDelay={500}
                initialValue={searchQuery}
              />
            </div>

            {/* New Task */}
            <button
              onClick={() => { setEditingTask(null); setShowCreateForm(true) }}
              className="flex items-center gap-1.5 h-9 px-3.5 bg-teal-600 hover:bg-teal-700 text-white text-sm font-semibold rounded-lg transition-all duration-150 shadow-sm shadow-teal-600/20 hover:-translate-y-px cursor-pointer"
            >
              <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
              <span className="hidden sm:inline">New task</span>
            </button>
          </div>

          {/* Mobile search */}
          <div className="px-4 pb-3 sm:hidden">
            <SearchBar
              onSearch={(q) => { setCurrentPage(1); setSearchQuery(q) }}
              placeholder="Search tasks…"
              debounceDelay={500}
              initialValue={searchQuery}
            />
          </div>
        </header>

        {/* Page Body */}
        <main className="flex-1 px-4 md:px-6 py-6">
          <div className="max-w-3xl">
            {/* Error */}
            {error && (
              <div className="mb-4">
                <ErrorMessage message={error} onRetry={() => { setError(null); loadTasks() }} />
              </div>
            )}

            {/* Active filters banner */}
            {(searchQuery || hasActiveFilters || sortOptions.sortBy) && (
              <div className="flex items-center justify-between text-xs text-teal-700 mb-4 bg-teal-50 border border-teal-100 rounded-xl px-3 py-2">
                <span>
                  {totalTasks} task{totalTasks !== 1 ? 's' : ''}
                  {searchQuery && <> matching <strong>"{searchQuery}"</strong></>}
                  {filters.priority && <> · priority: {filters.priority}</>}
                </span>
                <button onClick={clearAll} className="text-teal-600 hover:text-teal-800 font-semibold ml-3 cursor-pointer">
                  Clear all
                </button>
              </div>
            )}

            {/* Create / Edit Form */}
            {(showCreateForm || editingTask) && (
              <div className="mb-4">
                <TaskForm
                  editTask={editingTask}
                  onTaskCreated={handleCreateTask}
                  onTaskUpdated={handleUpdateTask}
                  onCancel={editingTask ? handleCancelEdit : () => setShowCreateForm(false)}
                  isSubmitting={editingTask ? isUpdatingTask : isCreatingTask}
                  isExpanded={true}
                />
              </div>
            )}

            {/* Inline loading indicator for search/filter refreshes */}
            {isLoading && !isInitialLoad && (
              <div className="flex items-center gap-2 text-sm text-gray-400 mb-3">
                <svg className="h-4 w-4 animate-spin text-teal-500" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Updating…
              </div>
            )}

            {/* Task List */}
            <TaskList
              tasks={tasks}
              onToggleComplete={handleToggleComplete}
              onEdit={handleEditTask}
              onDelete={handleDeleteTask}
              onTagAdd={handleTagAdd}
              onTagRemove={handleTagRemove}
              searchQuery={searchQuery}
              onAddTask={() => setShowCreateForm(true)}
            />

            {/* Pagination */}
            <Pagination
              currentPage={currentPage}
              totalPages={Math.ceil(totalTasks / PAGE_SIZE)}
              totalItems={totalTasks}
              pageSize={PAGE_SIZE}
              onPageChange={setCurrentPage}
            />
          </div>
        </main>
      </div>

      {/* Delete Confirmation */}
      {deletingTask && (
        <DeleteConfirm
          isOpen={!!deletingTask}
          taskTitle={deletingTask.title}
          onConfirm={handleConfirmDelete}
          onCancel={handleCancelDelete}
          isDeleting={isDeleting}
        />
      )}

      {/* Floating Chat */}
      <FloatingChat />
    </div>
  )
}

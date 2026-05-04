/**
 * Task API Client
 *
 * Methods for interacting with task endpoints.
 * All requests automatically include JWT authentication.
 */

import { apiClient } from './client'

/**
 * Task interface matching backend TaskResponse schema
 */
export interface Task {
  id: number
  user_id: number
  title: string
  description: string
  completed: boolean
  created_at: string
  updated_at: string
  // Step 5: Advanced fields
  priority?: string
  due_date?: string | null
  recurrence_rule?: string | null
  reminder_offset?: number | null
  next_occurrence?: string | null
  tags?: string[]
}

/**
 * Task list response matching backend TaskListResponse schema
 */
export interface TaskListResponse {
  tasks: Task[]
  total: number
}

/**
 * Create task request data
 */
export interface CreateTaskData {
  title: string
  description?: string
  // Step 5: Advanced fields
  priority?: string
  due_date?: string | null
  recurrence_rule?: string | null
  reminder_offset?: number | null
  tags?: string[]
}

/**
 * Update task request data (partial update)
 */
export interface UpdateTaskData {
  title?: string
  description?: string
  // Step 5: Advanced fields
  priority?: string
  due_date?: string | null
  recurrence_rule?: string | null
  reminder_offset?: number | null
  tags?: string[]
}

/**
 * Task API methods
 */
export const taskApi = {
  /**
   * Get all tasks for the authenticated user with optional search, filter, and sort parameters.
   *
   * @param userId - ID of the user (must match authenticated user)
   * @param queryParams - Optional query parameters for search, filter, sort
   * @returns Promise<TaskListResponse> - List of tasks with total count
   * @throws ApiClientError - On authentication or network errors
   *
   * @example
   * // Get all tasks
   * const { tasks, total } = await taskApi.getTasks(userId)
   *
   * @example
   * // Search tasks
   * const { tasks } = await taskApi.getTasks(userId, { search: 'meeting' })
   *
   * @example
   * // Filter and sort tasks
   * const { tasks } = await taskApi.getTasks(userId, {
   *   status: 'incomplete',
   *   priority: 'high',
   *   sort_by: 'due_date',
   *   sort_order: 'asc'
   * })
   */
  async getTasks(userId: number, queryParams?: Record<string, string>): Promise<TaskListResponse> {
    let url = `/api/${userId}/tasks`

    // Add query parameters if provided
    if (queryParams && Object.keys(queryParams).length > 0) {
      const params = new URLSearchParams(queryParams)
      url += `?${params.toString()}`
    }

    return apiClient.get<TaskListResponse>(url)
  },

  /**
   * Get a specific task by ID.
   *
   * @param userId - ID of the user (must match authenticated user)
   * @param taskId - ID of the task to retrieve
   * @returns Promise<Task> - Task object
   * @throws ApiClientError - On authentication, not found, or network errors
   *
   * @example
   * const task = await taskApi.getTask(userId, 123)
   */
  async getTask(userId: number, taskId: number): Promise<Task> {
    return apiClient.get<Task>(`/api/${userId}/tasks/${taskId}`)
  },

  /**
   * Create a new task.
   *
   * @param userId - ID of the user (must match authenticated user)
   * @param data - Task creation data (title required, description optional)
   * @returns Promise<Task> - Newly created task object
   * @throws ApiClientError - On validation, authentication, or network errors
   *
   * @example
   * const newTask = await taskApi.createTask(userId, {
   *   title: 'Buy groceries',
   *   description: 'Milk, eggs, bread'
   * })
   */
  async createTask(userId: number, data: CreateTaskData): Promise<Task> {
    return apiClient.post<Task>(`/api/${userId}/tasks`, data)
  },

  /**
   * Update an existing task.
   *
   * Allows partial updates - provide only the fields you want to change.
   *
   * @param userId - ID of the user (must match authenticated user)
   * @param taskId - ID of the task to update
   * @param data - Update data (title and/or description)
   * @returns Promise<Task> - Updated task object
   * @throws ApiClientError - On validation, authentication, not found, or network errors
   *
   * @example
   * const updated = await taskApi.updateTask(userId, 123, {
   *   title: 'Updated title'
   * })
   */
  async updateTask(
    userId: number,
    taskId: number,
    data: UpdateTaskData
  ): Promise<Task> {
    return apiClient.put<Task>(`/api/${userId}/tasks/${taskId}`, data)
  },

  /**
   * Toggle the completion status of a task.
   *
   * If the task is complete, marks it as incomplete.
   * If the task is incomplete, marks it as complete.
   *
   * @param userId - ID of the user (must match authenticated user)
   * @param taskId - ID of the task to toggle
   * @returns Promise<Task> - Updated task object with toggled completion status
   * @throws ApiClientError - On authentication, not found, or network errors
   *
   * @example
   * const toggled = await taskApi.toggleComplete(userId, 123)
   * console.log(`Task is now ${toggled.completed ? 'complete' : 'incomplete'}`)
   */
  async toggleComplete(userId: number, taskId: number): Promise<Task> {
    return apiClient.patch<Task>(`/api/${userId}/tasks/${taskId}/complete`)
  },

  /**
   * Delete a task permanently.
   *
   * @param userId - ID of the user (must match authenticated user)
   * @param taskId - ID of the task to delete
   * @returns Promise<void> - No response body (204 No Content)
   * @throws ApiClientError - On authentication, not found, or network errors
   *
   * @example
   * await taskApi.deleteTask(userId, 123)
   * console.log('Task deleted successfully')
   */
  async deleteTask(userId: number, taskId: number): Promise<void> {
    return apiClient.delete<void>(`/api/${userId}/tasks/${taskId}`)
  },
}

/**
 * Tag API methods — dedicated endpoints for per-task tag management.
 * Use these for add/remove without re-submitting the entire task form.
 */
export const tagApi = {
  /**
   * Add a tag to a task. Returns the full updated tag list for the task.
   * Idempotent: adding an existing tag is a no-op.
   * Max 10 tags per task.
   */
  async addTag(userId: number, taskId: number, tagName: string): Promise<string[]> {
    return apiClient.post<string[]>(`/api/${userId}/tasks/${taskId}/tags`, {
      tag_name: tagName,
    })
  },

  /** Remove a single tag from a task by name. */
  async removeTag(userId: number, taskId: number, tagName: string): Promise<void> {
    return apiClient.delete<void>(
      `/api/${userId}/tasks/${taskId}/tags/${encodeURIComponent(tagName)}`
    )
  },
}

/**
 * React Hook for managing tasks (future enhancement)
 *
 * This would be implemented in a separate file (e.g., hooks/useTasks.ts)
 * using React Query or SWR for caching and optimistic updates.
 *
 * @example
 * function TasksPage() {
 *   const { tasks, isLoading, error, createTask, updateTask, deleteTask } = useTasks(userId)
 *
 *   if (isLoading) return <Loading />
 *   if (error) return <ErrorMessage message={error.message} />
 *
 *   return <TaskList tasks={tasks} onCreate={createTask} />
 * }
 */

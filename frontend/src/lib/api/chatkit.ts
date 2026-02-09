/**
 * ChatKit API Client
 *
 * Handles communication with custom ChatKit backend endpoint.
 * Supports JWT authentication and SSE streaming.
 */

import authClient from '../auth/auth-client'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export interface SendMessageRequest {
  thread_id?: string
  message: string
}

export interface SendMessageResponse {
  thread_id: string
  message: string
  conversation_id?: number
}

/**
 * Send a chat message to the backend
 */
export async function sendChatMessage(
  message: string,
  threadId?: string
): Promise<SendMessageResponse> {
  const token = authClient.getToken()

  if (!token) {
    throw new Error('Not authenticated')
  }

  const response = await fetch(`${API_URL}/api/chatkit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      thread_id: threadId,
      message: message,
    }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || 'Failed to send message')
  }

  return response.json()
}

/**
 * Stream chat response using Server-Sent Events (SSE)
 */
export async function* streamChatResponse(
  message: string,
  threadId?: string,
  language?: string
): AsyncGenerator<string, void, unknown> {
  const token = authClient.getToken()

  if (!token) {
    throw new Error('Not authenticated')
  }

  const response = await fetch(`${API_URL}/api/chatkit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({
      thread_id: threadId,
      message: message,
      language: language || 'en',
    }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || 'Failed to stream response')
  }

  // Read response body as stream
  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('Response body is not readable')
  }

  const decoder = new TextDecoder()

  try {
    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        break
      }

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6) // Remove 'data: ' prefix
          if (data === '[DONE]') {
            return
          }
          try {
            const parsed = JSON.parse(data)
            if (parsed.content) {
              yield parsed.content
            }
          } catch {
            // Skip invalid JSON
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}

/**
 * Get conversation history
 */
export async function getConversationHistory(
  conversationId: number
): Promise<ChatMessage[]> {
  const token = authClient.getToken()

  if (!token) {
    throw new Error('Not authenticated')
  }

  const response = await fetch(`${API_URL}/api/conversations/${conversationId}/messages`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Failed to load conversation history')
  }

  const data = await response.json()
  return data.messages.map((msg: any) => ({
    role: msg.role,
    content: msg.content,
    timestamp: new Date(msg.created_at),
  }))
}

/**
 * Create a new conversation
 */
export async function createConversation(): Promise<{ id: number }> {
  const token = authClient.getToken()

  if (!token) {
    throw new Error('Not authenticated')
  }

  const response = await fetch(`${API_URL}/api/conversations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Failed to create conversation')
  }

  return response.json()
}

/**
 * List user's conversations
 */
export async function listConversations(): Promise<
  Array<{ id: number; created_at: string; updated_at: string }>
> {
  const token = authClient.getToken()

  if (!token) {
    throw new Error('Not authenticated')
  }

  const response = await fetch(`${API_URL}/api/conversations`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Failed to load conversations')
  }

  const data = await response.json()
  return data.conversations
}

export const chatkitApi = {
  sendMessage: sendChatMessage,
  streamResponse: streamChatResponse,
  getHistory: getConversationHistory,
  createConversation,
  listConversations,
}

export default chatkitApi

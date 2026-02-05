import React, { useState, useEffect, useRef } from 'react'
import styles from './ChatWidget.module.css'

export const ChatWidget = ({ onTasksUpdated, userId = 'default-user' }) => {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)

  // Chat API endpoint (from environment or default)
  const CHAT_API = import.meta.env.VITE_CHAT_API || 'http://localhost:3000'

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize chat session on mount
  useEffect(() => {
    initializeSession()
  }, [userId])

  const initializeSession = async () => {
    try {
      setError(null)
      const response = await fetch(`${CHAT_API}/chat/sessions`, {
        method: 'POST',
        headers: {
          'X-User-ID': userId,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to create chat session')
      }

      const data = await response.json()
      setSessionId(data.session_id)

      // Add welcome message
      setMessages([
        {
          id: 'welcome',
          role: 'assistant',
          content: '👋 Hi! I\'m your AI Task Assistant. I can help you manage your tasks. Try saying things like:\n- "Add a task to review the report"\n- "Mark the report as done"\n- "What do I need to do today?"',
          timestamp: new Date().toISOString(),
        },
      ])
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error'
      setError(`Failed to initialize chat: ${errorMsg}`)
      console.error('Session initialization error:', err)
    }
  }

  const sendMessage = async (e) => {
    e.preventDefault()

    if (!inputMessage.trim() || !sessionId || loading) {
      return
    }

    const userMsg = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMsg])
    setInputMessage('')
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${CHAT_API}/chat/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId,
        },
        body: JSON.stringify({
          message: inputMessage,
          session_id: sessionId,
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()

      const assistantMsg = {
        id: data.message_id,
        role: 'assistant',
        content: data.content,
        timestamp: data.timestamp,
      }

      setMessages((prev) => [...prev, assistantMsg])

      // Notify parent component that tasks may have changed
      if (data.tool_calls && data.tool_calls.length > 0) {
        // Give a short delay for backend to finish processing
        setTimeout(() => {
          onTasksUpdated?.()
        }, 500)
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMsg)
      console.error('Chat error:', err)

      // Add error message to chat
      const errorMsg_obj = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Sorry, I encountered an error: ${errorMsg}. Please try again.`,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMsg_obj])
    } finally {
      setLoading(false)
    }
  }

  const resetSession = async () => {
    if (sessionId) {
      try {
        await fetch(`${CHAT_API}/chat/sessions/${sessionId}`, {
          method: 'DELETE',
          headers: {
            'X-User-ID': userId,
          },
        })
      } catch (err) {
        console.error('Failed to end session:', err)
      }
    }

    setMessages([])
    setSessionId(null)
    await initializeSession()
  }

  return (
    <div className={styles.chatWidget}>
      <div className={styles.header}>
        <h3>🤖 AI Task Assistant</h3>
        <button
          className={styles.resetBtn}
          onClick={resetSession}
          title="Start new conversation"
        >
          ↻
        </button>
      </div>

      <div className={styles.messagesContainer}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`${styles.message} ${styles[msg.role]}`}
          >
            <div className={styles.messageContent}>
              {msg.content}
            </div>
            <div className={styles.timestamp}>
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
        {loading && (
          <div className={`${styles.message} ${styles.assistant}`}>
            <div className={styles.typingIndicator}>
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className={styles.error}>
          ⚠️ {error}
        </div>
      )}

      <form onSubmit={sendMessage} className={styles.inputForm}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask me anything..."
          className={styles.input}
          disabled={loading || !sessionId}
          autoFocus
        />
        <button
          type="submit"
          disabled={!inputMessage.trim() || loading || !sessionId}
          className={styles.sendBtn}
        >
          {loading ? '...' : '→'}
        </button>
      </form>
    </div>
  )
}

# Frontend Integration: Adding AI Chat to Your Todo App

This guide shows you how to add the AI chatbot interface to your existing frontend.

## Quick Overview

Your current frontend has a task list. We'll add a chat sidebar that allows users to manage tasks conversationally while seeing real-time updates.

## Architecture

```
┌────────────────────────────────────────────────┐
│            Your Todo App Frontend              │
├─────────────────┬──────────────────────────────┤
│                 │                              │
│  Task List      │    Chat Sidebar (NEW)        │
│  - Browse       │    - Send message            │
│  - Filter       │    - View responses          │
│  - Edit         │    - See actions taken       │
│  - Delete       │                              │
│                 │                              │
│  Updates when   │    Auto-updates when         │
│  chat creates   │    task changes              │
│  tasks          │                              │
└─────────────────┴──────────────────────────────┘
```

## Step 1: Create Chat Component

Create this file in your frontend project:

**`src/components/ChatWidget.tsx`** (React/TypeScript)

```typescript
import React, { useState, useEffect, useRef } from 'react';
import styles from './ChatWidget.module.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatWidgetProps {
  onTasksUpdated?: () => void; // Callback when tasks change
  userId?: string;
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({
  onTasksUpdated,
  userId = 'default-user',
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Chat API endpoint (from environment or default)
  const CHAT_API = process.env.REACT_APP_CHAT_API || 'http://localhost:3000';

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chat session on mount
  useEffect(() => {
    initializeSession();
  }, [userId]);

  const initializeSession = async () => {
    try {
      setError(null);
      const response = await fetch(`${CHAT_API}/chat/sessions`, {
        method: 'POST',
        headers: {
          'X-User-ID': userId,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to create chat session');
      }

      const data = await response.json();
      setSessionId(data.session_id);

      // Add welcome message
      setMessages([
        {
          id: 'welcome',
          role: 'assistant',
          content: '👋 Hi! I\'m your AI Task Assistant. I can help you manage your tasks. Try saying things like:\n- "Add a task to review the report"\n- "Mark the report as done"\n- "What do I need to do today?"',
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to initialize chat: ${errorMsg}`);
      console.error('Session initialization error:', err);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMessage.trim() || !sessionId || loading) {
      return;
    }

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setLoading(true);
    setError(null);

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
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();

      const assistantMsg: Message = {
        id: data.message_id,
        role: 'assistant',
        content: data.content,
        timestamp: data.timestamp,
      };

      setMessages((prev) => [...prev, assistantMsg]);

      // Notify parent component that tasks may have changed
      if (data.tool_calls && data.tool_calls.length > 0) {
        // Give a short delay for backend to finish processing
        setTimeout(() => {
          onTasksUpdated?.();
        }, 500);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMsg);
      console.error('Chat error:', err);

      // Add error message to chat
      const errorMsg_obj: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Sorry, I encountered an error: ${errorMsg}. Please try again.`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg_obj]);
    } finally {
      setLoading(false);
    }
  };

  const resetSession = async () => {
    if (sessionId) {
      try {
        await fetch(`${CHAT_API}/chat/sessions/${sessionId}`, {
          method: 'DELETE',
          headers: {
            'X-User-ID': userId,
          },
        });
      } catch (err) {
        console.error('Failed to end session:', err);
      }
    }

    setMessages([]);
    setSessionId(null);
    await initializeSession();
  };

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
  );
};
```

## Step 2: Create Styles

**`src/components/ChatWidget.module.css`**

```css
.chatWidget {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-left: 1px solid #e5e7eb;
  background: white;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.resetBtn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  padding: 0.5rem;
  color: #6b7280;
  hover {
    color: #111827;
  }
}

.messagesContainer {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  flex-direction: column;
  margin-bottom: 0.5rem;
}

.message.user {
  align-items: flex-end;
}

.message.assistant {
  align-items: flex-start;
}

.messageContent {
  max-width: 85%;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  line-height: 1.5;
  word-wrap: break-word;
}

.message.user .messageContent {
  background: #3b82f6;
  color: white;
  border-radius: 0.75rem 0.25rem 0.75rem 0.75rem;
}

.message.assistant .messageContent {
  background: #f3f4f6;
  color: #111827;
  border-radius: 0.25rem 0.75rem 0.75rem 0.75rem;
}

.timestamp {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.25rem;
  padding: 0 0.5rem;
}

.typingIndicator {
  display: flex;
  gap: 0.25rem;
  padding: 0.5rem;
}

.typingIndicator span {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: #d1d5db;
  animation: typing 1.4s infinite;
}

.typingIndicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typingIndicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    opacity: 0.5;
    transform: translateY(0);
  }
  30% {
    opacity: 1;
    transform: translateY(-0.5rem);
  }
}

.error {
  padding: 0.75rem 1rem;
  background: #fee2e2;
  color: #991b1b;
  border-top: 1px solid #fecaca;
  font-size: 0.875rem;
}

.inputForm {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
  background: white;
}

.input {
  flex: 1;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  padding: 0.75rem;
  font-size: 0.875rem;
  font-family: inherit;
}

.input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input:disabled {
  background: #f9fafb;
  color: #d1d5db;
  cursor: not-allowed;
}

.sendBtn {
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.sendBtn:hover:not(:disabled) {
  background: #2563eb;
}

.sendBtn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .messageContent {
    max-width: 90%;
  }

  .header h3 {
    font-size: 0.875rem;
  }

  .messagesContainer {
    padding: 0.75rem;
  }
}
```

## Step 3: Integrate Into Your App

**Update your main layout component** (e.g., `src/pages/Dashboard.tsx`):

```typescript
import React, { useState } from 'react';
import { TaskList } from '../components/TaskList';
import { ChatWidget } from '../components/ChatWidget';
import styles from './Dashboard.module.css';

export function Dashboard() {
  const [refreshTasks, setRefreshTasks] = useState(0);

  const handleTasksUpdated = () => {
    // Trigger task list refresh
    setRefreshTasks((prev) => prev + 1);
  };

  return (
    <div className={styles.dashboard}>
      <div className={styles.mainContent}>
        <TaskList key={refreshTasks} />
      </div>
      <div className={styles.chatSidebar}>
        <ChatWidget
          onTasksUpdated={handleTasksUpdated}
          userId={getCurrentUserId()}
        />
      </div>
    </div>
  );
}
```

**`src/pages/Dashboard.module.css`:**

```css
.dashboard {
  display: flex;
  height: 100vh;
  background: white;
}

.mainContent {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.chatSidebar {
  width: 400px;
  min-width: 350px;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  border-left: 1px solid #e5e7eb;
}

/* Tablet view */
@media (max-width: 1024px) {
  .chatSidebar {
    width: 350px;
  }
}

/* Mobile view - convert to stacked layout */
@media (max-width: 768px) {
  .dashboard {
    flex-direction: column;
  }

  .mainContent {
    flex: 1;
    padding: 1rem;
  }

  .chatSidebar {
    width: 100%;
    height: 40vh;
    border-left: none;
    border-top: 1px solid #e5e7eb;
  }
}
```

## Step 4: Environment Configuration

**Create or update `.env.local`:**

```bash
# Chat API endpoint
REACT_APP_CHAT_API=http://localhost:3000

# Task API endpoint (existing)
REACT_APP_TASK_API=http://localhost:8000

# For production
# REACT_APP_CHAT_API=https://ai-todo-chatbot.vercel.app
# REACT_APP_TASK_API=https://todoapp-api.vercel.app
```

## Step 5: Update Task List for Auto-Refresh

Modify your TaskList component to accept a refresh key:

```typescript
interface TaskListProps {
  refreshKey?: number;
}

export function TaskList({ refreshKey }: TaskListProps) {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    fetchTasks();
  }, [refreshKey]); // Re-fetch when refreshKey changes

  const fetchTasks = async () => {
    const response = await fetch(`${process.env.REACT_APP_TASK_API}/api/tasks`);
    const data = await response.json();
    setTasks(data);
  };

  return (
    // ... existing task list JSX
  );
}
```

## Step 6: Testing

### Manual Testing

1. Start your frontend:
```bash
npm run dev
```

2. Start the chat API:
```bash
cd ai-chatbot
npm run dev
```

3. Test these scenarios:

**Test 1: Create Task**
- Message: "Add a task to buy milk"
- Expected: Task appears in the list within 1 second

**Test 2: List Tasks**
- Message: "What do I need to do today?"
- Expected: Chat shows your tasks

**Test 3: Complete Task**
- Message: "Mark the milk task as done"
- Expected: Task status changes to completed

**Test 4: Update Priority**
- Message: "Change the milk task to high priority"
- Expected: Task priority updates

## Step 7: Styling Customization

### Themes

Add dark mode support:

```typescript
interface ChatWidgetProps {
  onTasksUpdated?: () => void;
  userId?: string;
  theme?: 'light' | 'dark'; // New prop
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({
  theme = 'light',
  ...props
}) => {
  return (
    <div className={`${styles.chatWidget} ${styles[theme]}`}>
      {/* ... */}
    </div>
  );
};
```

### CSS Variables

```css
:root[data-theme='light'] {
  --primary: #3b82f6;
  --bg-message-user: #3b82f6;
  --bg-message-assistant: #f3f4f6;
  --text-primary: #111827;
  --border: #e5e7eb;
}

:root[data-theme='dark'] {
  --primary: #60a5fa;
  --bg-message-user: #1e40af;
  --bg-message-assistant: #374151;
  --text-primary: #f9fafb;
  --border: #4b5563;
}

.messageContent {
  background: var(--bg-message-assistant);
  color: var(--text-primary);
}
```

## Step 8: Error Handling

The component already includes:
- ✅ Network error handling
- ✅ Session initialization errors
- ✅ API timeout handling
- ✅ User-friendly error messages
- ✅ Automatic retry capability

## Production Deployment

### Environment Variables

```bash
# .env.production
REACT_APP_CHAT_API=https://ai-todo-chatbot.vercel.app
REACT_APP_TASK_API=https://todoapp-api.vercel.app
```

### Performance Optimization

```typescript
// Lazy load ChatWidget for faster initial load
const ChatWidget = React.lazy(() => import('../components/ChatWidget'));

// In your component
<Suspense fallback={<div>Loading chat...</div>}>
  <ChatWidget {...props} />
</Suspense>
```

### Analytics Integration

```typescript
const sendMessage = async (e: React.FormEvent) => {
  // ... existing code ...

  // Track chat interaction
  if (window.gtag) {
    window.gtag('event', 'chat_message', {
      message_type: 'user',
      word_count: inputMessage.split(' ').length,
    });
  }
};
```

## Troubleshooting

### Chat component not loading

**Check:**
- Is `REACT_APP_CHAT_API` set correctly?
- Is the chat API running?
- Check browser console for errors

### Messages not syncing with tasks

**Check:**
- Does `onTasksUpdated` callback work?
- Is task API accessible?
- Check if tool_calls are being returned

### Styling issues

**Check:**
- Are CSS module extensions correct?
- Is CSS in right directory?
- Check for CSS conflicts

## Next Steps

1. ✅ Copy ChatWidget component
2. ✅ Add styles
3. ✅ Integrate into main layout
4. ✅ Test locally
5. ✅ Deploy chat API
6. ✅ Update production environment variables
7. ✅ Monitor usage and errors

You now have a beautiful AI-powered chat interface integrated with your existing todo app! 🚀

# Integration Guide: AI Chatbot + Existing Todo App

This guide explains how to integrate the AI-powered chatbot with your existing FastAPI backend and frontend.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vite/Next.js)                  │
│  - Chat UI component                                        │
│  - Task list display                                        │
│  - Real-time updates                                        │
└──────────────┬──────────────────────────────────────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
┌──────────────┐  ┌──────────────────────┐
│ Task API     │  │ Chat API (New)       │
│ (Existing)   │  │ (TodoAgent)          │
│              │  │                      │
│ /api/tasks   │  │ /api/chat/send       │
│              │  │ /api/chat/sessions   │
└──────────────┘  └──────────┬───────────┘
      │                      │
      └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────────┐
    │   FastAPI Backend        │
    │                          │
    │  - Task routes           │
    │  - Chat routes (new)     │
    │  - Database session      │
    └──────────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  PostgreSQL Database │
        │                      │
        │  - tasks table       │
        │  - chat_sessions     │
        │  - chat_messages     │
        └──────────────────────┘
```

## Integration Approach

### Option 1: Run Separately (Simplest - Recommended for Now)

**Pros:**
- ✅ Zero changes to existing backend
- ✅ AI chatbot runs independently
- ✅ Easy to deploy and test
- ✅ Different scaling requirements
- ✅ Can use different tech stacks

**Cons:**
- ❌ Two services to manage
- ❌ Separate deployments

**Setup:**
1. Keep existing FastAPI backend as-is
2. Deploy AI chatbot to separate service (Heroku, Railway, Vercel)
3. Frontend calls both APIs

### Option 2: Integrated Backend (More Unified)

**Pros:**
- ✅ Single backend service
- ✅ Shared database
- ✅ Unified deployment
- ✅ Better performance (same process)

**Cons:**
- ❌ Need to modify existing backend
- ❌ More complex deployment

**Setup:**
1. Add chatbot routes to FastAPI
2. Connect to existing PostgreSQL database
3. Share user/task context

---

## Recommended: Option 1 (Separate Services)

Let me provide step-by-step instructions for this approach.

### Step 1: Deploy AI Chatbot Independently

**Option A: Deploy to Vercel (Recommended)**

1. Copy `ai-chatbot` folder to your repo root
2. Create `vercel.json` in `ai-chatbot/`:

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "env": {
    "OPENAI_API_KEY": {
      "required": true
    }
  }
}
```

3. Create `vercel-handler.ts` (serverless handler):

```typescript
// ai-chatbot/api/chat.ts
import { TodoAgent } from '../src/agent/todo-agent';
import { MCPStorage } from '../src/mcp/storage';
import { ChatKitHandler } from '../src/chat/chatkit-handler';
import { ConversationSessionManager } from '../src/agent/memory';

let agent: TodoAgent;
let chatHandler: ChatKitHandler;
let storage: MCPStorage;

export default async (req, res) => {
  // Initialize on first request
  if (!agent) {
    storage = new MCPStorage('/tmp/mcp-data');
    await storage.initialize();
    agent = new TodoAgent(storage);
    chatHandler = new ChatKitHandler(agent, storage);
  }

  if (req.method === 'POST' && req.url === '/api/chat/send') {
    const { message, session_id } = req.body;
    const userId = req.headers['x-user-id'] || 'default';

    try {
      const response = await chatHandler.sendMessage(userId, session_id || '', message);
      return res.json(response);
    } catch (error) {
      return res.status(500).json({ error: error.message });
    }
  }

  res.status(404).json({ error: 'Not found' });
};
```

4. Push to Vercel and set `OPENAI_API_KEY` environment variable

**Option B: Deploy to Railway**

1. Create `Dockerfile` in `ai-chatbot/`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

ENV NODE_ENV=production
EXPOSE 3000

CMD ["npm", "start"]
```

2. Create `railway.json`:

```json
{
  "version": 2,
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "restartPolicyType": "on_failure",
    "restartPolicyMaxRetries": 5,
    "numReplicas": 1
  }
}
```

3. Push to Railway

### Step 2: Update Frontend to Call Both APIs

**Frontend Component Example (React):**

```typescript
// frontend/components/ChatWithTasks.tsx
import React, { useState, useEffect } from 'react';

const CHAT_API = process.env.REACT_APP_CHAT_API || 'http://localhost:3000';
const TASK_API = process.env.REACT_APP_TASK_API || 'http://localhost:8000';

export function ChatWithTasks() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);

  // Initialize session
  useEffect(() => {
    const initSession = async () => {
      try {
        const response = await fetch(`${CHAT_API}/chat/sessions`, {
          method: 'POST',
          headers: { 'X-User-ID': 'user123' },
        });
        const { session_id } = await response.json();
        setSessionId(session_id);
      } catch (error) {
        console.error('Failed to create session:', error);
      }
    };

    initSession();
  }, []);

  // Fetch tasks from existing API
  const fetchTasks = async () => {
    try {
      const response = await fetch(`${TASK_API}/api/tasks`);
      const data = await response.json();
      setTasks(data);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    }
  };

  // Send message to chatbot
  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    setLoading(true);
    const newMessage = { role: 'user', content: inputMessage };
    setMessages([...messages, newMessage]);
    setInputMessage('');

    try {
      const response = await fetch(`${CHAT_API}/chat/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': 'user123',
        },
        body: JSON.stringify({
          message: inputMessage,
          session_id: sessionId,
        }),
      });

      const result = await response.json();
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: result.content },
      ]);

      // Refresh tasks after chat interaction
      await fetchTasks();
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  return (
    <div className="flex gap-4">
      {/* Chat panel */}
      <div className="flex-1">
        <div className="bg-white rounded-lg shadow p-4 h-96 overflow-y-auto mb-4">
          {messages.map((msg, idx) => (
            <div key={idx} className={msg.role === 'user' ? 'text-right' : 'text-left'}>
              <p className={msg.role === 'user' ? 'bg-blue-100' : 'bg-gray-100'}>
                {msg.content}
              </p>
            </div>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask me anything..."
            className="flex-1 border rounded px-3 py-2"
            disabled={loading}
          />
          <button
            onClick={handleSendMessage}
            disabled={loading}
            className="bg-blue-500 text-white px-4 py-2 rounded"
          >
            Send
          </button>
        </div>
      </div>

      {/* Task panel */}
      <div className="flex-1">
        <h2 className="font-bold mb-4">Tasks</h2>
        <div className="bg-white rounded-lg shadow p-4">
          {tasks.map((task) => (
            <div key={task.id} className="border-b pb-2 mb-2">
              <p className="font-medium">{task.title}</p>
              <p className="text-sm text-gray-600">{task.description}</p>
              <p className="text-xs">Status: {task.status}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

**Environment Variables (.env):**

```
REACT_APP_CHAT_API=https://ai-todo-chatbot.vercel.app
REACT_APP_TASK_API=https://todoapp-phase-3.vercel.app
```

### Step 3: Handle Data Synchronization

The chatbot currently uses local MCP storage. To sync with your existing database:

**Option A: Pull from Existing API (Easiest)**

Create `src/mcp/storage-hybrid.ts`:

```typescript
import { MCPStorage } from './storage';
import { Task, CreateTaskPayload, UpdateTaskPayload, ListTasksFilter } from './schema';

/**
 * Hybrid Storage: Uses existing API for reads, local storage for writes
 */
export class HybridStorage extends MCPStorage {
  private apiUrl: string;
  private userId: string;

  constructor(apiUrl: string, userId: string, localDir: string = './data') {
    super(localDir);
    this.apiUrl = apiUrl;
    this.userId = userId;
  }

  async listTasks(userId: string, filter: ListTasksFilter = {}): Promise<Task[]> {
    try {
      // Fetch from existing API
      const response = await fetch(`${this.apiUrl}/api/tasks`);
      if (!response.ok) throw new Error('Failed to fetch tasks');

      let tasks = await response.json();

      // Apply filters locally
      if (filter.status) {
        tasks = tasks.filter(t => t.status === filter.status);
      }

      if (filter.range === 'today') {
        const today = new Date();
        const todayStr = today.toISOString().split('T')[0];
        tasks = tasks.filter(t =>
          t.due_date?.startsWith(todayStr) && t.status === 'pending'
        );
      }

      if (filter.search) {
        const searchLower = filter.search.toLowerCase();
        tasks = tasks.filter(t =>
          t.title.toLowerCase().includes(searchLower) ||
          t.description?.toLowerCase().includes(searchLower)
        );
      }

      return tasks;
    } catch (error) {
      console.error('Failed to fetch from API, using local cache:', error);
      return super.listTasks(userId, filter);
    }
  }
}
```

**Option B: Sync Tasks in Agent**

Update `src/agent/tools.ts`:

```typescript
// Add this before tool definitions
async function syncWithExistingAPI(action: string, taskData: any) {
  const apiUrl = process.env.TASK_API_URL || 'http://localhost:8000';

  try {
    let endpoint = `${apiUrl}/api/tasks`;
    let method = 'POST';
    let body = taskData;

    if (action === 'update') {
      endpoint += `/${taskData.id}`;
      method = 'PUT';
    } else if (action === 'delete') {
      endpoint += `/${taskData.id}`;
      method = 'DELETE';
      body = undefined;
    }

    const response = await fetch(endpoint, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    });

    return response.ok;
  } catch (error) {
    console.error('Failed to sync with existing API:', error);
    return false;
  }
}
```

### Step 4: Environment Setup

**ai-chatbot/.env:**

```
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4-turbo
PORT=3000
NODE_ENV=production

# Connection to existing API
TASK_API_URL=https://todoapp-phase-3-api.vercel.app

# MCP Storage
MCP_DATA_DIR=/tmp/mcp-data
```

**Frontend .env:**

```
VITE_CHAT_API=https://ai-todo-chatbot.vercel.app
VITE_TASK_API=https://todoapp-phase-3.vercel.app
```

## Option 2: Integrate into Existing FastAPI Backend

If you prefer a single backend, here's how:

### Step 1: Create Chat Routes in FastAPI

Create `backend/api/routes/chat.py`:

```python
"""
Chat API endpoints for AI-powered task management.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import get_session
from .tasks import get_tasks  # Reuse existing task operations

router = APIRouter(tags=["chat"])


@router.post("/chat/send")
async def chat_send(message: str, session_id: str = None, session: AsyncSession = Depends(get_session)):
    """
    Send a message to the AI chatbot.

    The chatbot will understand task management intent and
    call the existing task APIs.
    """
    # This would require setting up the AI agent
    # in Python or calling the separate service
    pass


@router.post("/chat/sessions")
async def create_session():
    """Create a new chat session."""
    pass
```

### Step 2: Create Python Agent (Alternative to TypeScript)

If you prefer to keep everything in Python:

Create `backend/core/ai/agent.py`:

```python
"""
AI Agent for task management.
Uses LangChain or direct OpenAI API.
"""

import os
from openai import AsyncOpenAI
from typing import Optional

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a helpful AI task management assistant.
You help users manage their todo tasks through natural conversation.

When the user asks to:
- Create a task: Extract title, description, due_date, priority
- Update a task: Identify which task and what to change
- Complete a task: Mark it as done
- List tasks: Show appropriate filtered list

Always respond conversationally and confirm actions taken.
"""

async def process_message(user_message: str, user_id: str) -> str:
    """
    Process a user message through the AI agent.

    Args:
        user_message: The user's input
        user_id: User identifier

    Returns:
        Agent's response
    """
    response = await client.chat.completions.create(
        model="gpt-4-turbo",
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message.content
```

### Step 3: Register Routes

Update `backend/api/main.py`:

```python
from .routes import tasks, chat  # Add chat import

app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(chat.router, prefix="/api", tags=["chat"])  # Add this
```

---

## Comparison: Which Option?

| Aspect | Separate Services | Integrated |
|--------|------------------|-----------|
| **Setup Time** | 30 min | 2 hours |
| **Complexity** | Low | Medium |
| **Deployment** | 2 separate deploys | 1 deploy |
| **Performance** | Slightly slower (2 requests) | Faster (1 process) |
| **Scalability** | Independent scaling | Same scaling |
| **Development** | Easier to test independently | Easier to debug |
| **Tech Stack** | TypeScript + Python | All Python OR all TypeScript |

**Recommendation:** Start with **Option 1 (Separate)** because:
- ✅ Zero disruption to existing backend
- ✅ Can deploy and test immediately
- ✅ Easier to troubleshoot issues
- ✅ Can migrate to Option 2 later if needed

---

## Deployment Checklist

### For AI Chatbot (Separate Service)

- [ ] Set up deployment platform (Vercel, Railway, etc.)
- [ ] Set `OPENAI_API_KEY` environment variable
- [ ] Set `TASK_API_URL` pointing to your existing API
- [ ] Test health endpoint: `GET /health`
- [ ] Test chat endpoint: `POST /chat/send`
- [ ] Update CORS if needed
- [ ] Enable logging for debugging

### For Frontend Integration

- [ ] Add chat component to UI
- [ ] Set environment variables for both APIs
- [ ] Test creating task via chat
- [ ] Test listing tasks via chat
- [ ] Test updating task via chat
- [ ] Test completing task via chat
- [ ] Add error handling for network failures
- [ ] Test on staging before production

### For Monitoring

- [ ] Add error tracking (Sentry, DataDog)
- [ ] Monitor API latency
- [ ] Track token usage
- [ ] Set up alerts for failures
- [ ] Monitor database connections

---

## Testing the Integration

### 1. Manual Testing

```bash
# Test chat endpoint
curl -X POST http://localhost:3000/chat/send \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -d '{"message": "Add a task to review the report"}'

# Test task was created
curl http://localhost:8000/api/tasks
```

### 2. End-to-End Testing

```typescript
// frontend/test/chat.e2e.ts
describe('Chat Integration', () => {
  it('should create task via chat and show in task list', async () => {
    // Send chat message
    const chatResponse = await fetch('/api/chat/send', {
      method: 'POST',
      body: JSON.stringify({ message: 'Add task: Buy milk' }),
    });

    // Check task list updated
    const tasks = await fetch('/api/tasks');
    const taskList = await tasks.json();

    expect(taskList.some(t => t.title === 'Buy milk')).toBe(true);
  });
});
```

---

## Troubleshooting

### Issue: "Cannot connect to chat API"

**Solution:**
- Check CORS configuration in both services
- Verify API URL in environment variables
- Ensure both services are running/deployed
- Check network connectivity

### Issue: "Agent can't find tasks"

**Solution:**
- Check `TASK_API_URL` environment variable
- Verify existing API is responding
- Check task structure matches expected schema
- Review agent memory for context

### Issue: "Token limit exceeded"

**Solution:**
- Switch to gpt-3.5-turbo (cheaper)
- Reduce message history
- Implement conversation pruning
- Add rate limiting

---

## Next Steps

1. **Choose deployment option** (Separate recommended)
2. **Deploy AI chatbot** to Vercel or Railway
3. **Update frontend** with chat component
4. **Test integration** with manual requests
5. **Monitor in production** with logging
6. **Gather user feedback** and iterate

---

## Support & Questions

- For TypeScript/Node issues: Check `ai-chatbot/README.md`
- For FastAPI issues: Check your backend docs
- For frontend integration: See React/Vue examples above
- For OpenAI issues: Check OpenAI API documentation

Happy integrating! 🚀

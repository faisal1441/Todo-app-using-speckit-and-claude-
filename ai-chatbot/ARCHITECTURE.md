# Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                      │
│  (Web, Mobile, CLI, Slack, Discord, etc.)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Express.js REST API                       │
│  - POST /chat/send        (Send message)                    │
│  - POST /chat/sessions    (Create session)                  │
│  - GET /chat/sessions     (List sessions)                   │
│  - DELETE /chat/sessions  (End session)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  ChatKit Handler Layer                       │
│  - Session management                                       │
│  - Message routing                                          │
│  - Tool call tracking                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   TodoAgent (AI Agent)                       │
│  - System prompt management                                 │
│  - Intent classification                                    │
│  - Tool selection & execution                               │
│  - Response generation                                      │
└────────────┬──────────────────────────┬──────────────────────┘
             │                          │
             ▼                          ▼
┌────────────────────────┐  ┌───────────────────────────────┐
│   Conversation         │  │    Agent Tools                │
│   Memory System        │  │  - create_task                │
│                        │  │  - update_task                │
│ - Message history      │  │  - complete_task              │
│ - Task references      │  │  - delete_task                │
│ - Context tracking     │  │  - get_task                   │
│ - Auto-pruning         │  │  - list_tasks                 │
└────────────────────────┘  └───────────────┬────────────────┘
                                             │
                                             ▼
                            ┌────────────────────────────────┐
                            │   MCP Storage Layer            │
                            │  (Single Source of Truth)      │
                            │                                │
                            │ - Task CRUD operations         │
                            │ - Filtering & sorting          │
                            │ - Schema validation (Zod)      │
                            │ - File persistence             │
                            └────────────────────────────────┘
                                             │
                                             ▼
                            ┌────────────────────────────────┐
                            │   Data Storage                 │
                            │  - JSON files (./data)         │
                            │  - MCP resources (production)  │
                            │  - Database (PostgreSQL)       │
                            └────────────────────────────────┘
```

## Component Details

### 1. TodoAgent (`src/agent/todo-agent.ts`)

**Purpose**: Central AI reasoning engine

**Responsibilities**:
- Process user messages through OpenAI API
- Select appropriate tools based on intent
- Handle tool execution and result processing
- Generate natural language responses

**Key Methods**:
```typescript
processMessage(context: AgentContext): Promise<AgentResponse>
  - Main entry point
  - Builds conversation context
  - Calls OpenAI with tools
  - Returns response + tool calls

processMessages(messages: string[]): Promise<AgentResponse[]>
  - Batch processing for testing
```

**System Prompt Strategy**:
- Defines agent personality (concise, helpful, friendly)
- Specifies tool usage patterns
- Provides reasoning guidelines
- Sets constraints and safety measures

### 2. Agent Tools (`src/agent/tools.ts`)

**Purpose**: Define and execute actions on tasks

**Tool Definitions**:

```typescript
create_task()
├─ Input: title, description, due_date, priority, tags
├─ Validation: Zod schema check
├─ Execution: Call storage.createTask()
└─ Output: Created task object

update_task()
├─ Input: task_id, field updates
├─ Validation: Zod schema, task existence
├─ Execution: Call storage.updateTask()
└─ Output: Updated task object

complete_task()
├─ Input: task_id
├─ Validation: Task exists
├─ Execution: Set status = 'completed'
└─ Output: Completed task

delete_task()
├─ Input: task_id
├─ Validation: Task exists
├─ Execution: Remove from storage
└─ Output: Deletion confirmation

get_task()
├─ Input: task_id
├─ Validation: Task exists
├─ Execution: Retrieve from storage
└─ Output: Task object

list_tasks()
├─ Input: filters (range, status, priority, search)
├─ Validation: Filter parameters
├─ Execution: Query storage with filters
└─ Output: Task list + statistics
```

**Tool Execution Flow**:
1. Agent extracts parameters from message
2. Zod validation ensures type safety
3. Tool executes business logic
4. Storage layer handles persistence
5. Result returned to agent for response formatting

### 3. Conversation Memory (`src/agent/memory.ts`)

**Purpose**: Track session context for task resolution

**Key Classes**:

```typescript
ConversationMemory
├─ Constructor(userId, sessionId)
├─ addMessage(role, content)
│  └─ Appends to message history (max 50)
├─ recordTaskReference(taskId, task, context)
│  └─ Tracks mentioned tasks for resolution
├─ findTasksByDescription(description)
│  └─ Fuzzy matching for "that task"
└─ getContextForAgent()
   └─ Formatted string for system prompt

ConversationSessionManager
├─ getSession(userId, sessionId)
│  └─ Get or create memory
├─ endSession(userId, sessionId)
│  └─ Clean up resources
└─ cleanupOldSessions()
   └─ Remove stale sessions
```

**Memory Lifecycle**:
```
User sends message
    ↓
Add to message_history
    ↓
Extract task references
    ↓
Add to referenced_tasks
    ↓
Agent uses as context
    ↓
Auto-prune after 30 min
    ↓
Session ends → clear all
```

### 4. MCP Storage (`src/mcp/storage.ts`)

**Purpose**: Persistent task storage with validation

**Architecture**:
```
MCPStorage
├─ In-memory cache (Map<taskId, Task>)
├─ File system storage (./data/*.json)
└─ Zod schema validation

initialize()
  └─ Load all tasks from disk

createTask()
  ├─ Generate UUID
  ├─ Add timestamps
  ├─ Validate schema
  ├─ Persist to disk
  └─ Update cache

updateTask()
  ├─ Fetch existing
  ├─ Merge updates
  ├─ Validate schema
  ├─ Persist changes
  └─ Update cache

listTasks()
  ├─ Filter by status/priority/date/search
  ├─ Sort by due_date and priority
  └─ Return paginated results

deleteTask()
  ├─ Remove from cache
  ├─ Delete file
  └─ Confirm deletion
```

**Data Flow**:
```
Tool Input
    ↓
Zod Validation (schema.ts)
    ↓
MCPStorage Method
    ├─ In-memory operation
    ├─ Persist to disk
    └─ Update cache
         ↓
Return Validated Result
```

### 5. ChatKit Handler (`src/chat/chatkit-handler.ts`)

**Purpose**: Bridge between HTTP API and agent

**Responsibilities**:
```typescript
ChatKitHandler
├─ Session management
│  ├─ getOrCreateSession()
│  ├─ getSessionHistory()
│  └─ endSession()
├─ Message processing
│  └─ sendMessage() → calls agent
├─ Memory tracking
│  └─ Update references from tool results
└─ Statistics
   └─ getStats()
```

**Request-Response Flow**:
```
POST /chat/send
{message, session_id, user_id}
    ↓
ChatKitHandler.sendMessage()
    ├─ Get or create session
    ├─ Get conversation memory
    ├─ Add user message
    ├─ Call agent.processMessage()
    ├─ Add assistant message
    ├─ Update memory with tool results
    └─ Return ChatResponse
         ↓
{
  session_id,
  message_id,
  role: 'assistant',
  content: '...',
  tool_calls: [...]
}
```

### 6. API Layer (`src/server/api.ts`)

**Express Routes**:

```
POST /chat/send
├─ Headers: X-User-ID (required), X-Session-ID (optional)
├─ Body: {message, session_id?}
└─ Response: ChatResponse

POST /chat/sessions
├─ Creates new session
└─ Response: {session_id, user_id, created_at}

GET /chat/sessions
├─ Lists user's sessions
└─ Response: {sessions: [...]}

GET /chat/sessions/:sessionId
├─ Gets conversation history
└─ Response: {messages: [...]}

DELETE /chat/sessions/:sessionId
├─ Ends session
└─ Response: {message, session_id}

GET /health
├─ Health check
└─ Response: {status, stats}

GET /
├─ API documentation
└─ Response: {endpoints, description}
```

**Middleware**:
- Express JSON parser
- User ID extraction from headers
- Session ID handling
- Error handling and logging

## Data Flow Examples

### Example 1: Creating a Task

```
1. User sends message via API
   POST /chat/send
   {
     "message": "Add task: Review report due tomorrow",
     "session_id": "session_123"
   }

2. ChatKitHandler.sendMessage()
   - Get session "session_123"
   - Get conversation memory
   - Add to message_history

3. TodoAgent.processMessage()
   - Builds prompt with conversation context
   - Sends to OpenAI API
   - OpenAI selects "create_task" tool
   - OpenAI extracts parameters:
     - title: "Review report"
     - due_date: "2024-01-17" (tomorrow)
     - priority: "medium" (default)

4. create_task tool executes
   - Validate parameters via Zod
   - Call storage.createTask()

5. MCPStorage.createTask()
   - Generate UUID
   - Add timestamps
   - Validate full Task schema
   - Write to ./data/{uuid}.json
   - Update in-memory cache
   - Return Task object

6. Tool result: {success, task}

7. OpenAI generates response
   "I've created 'Review report' (due tomorrow)"

8. ChatKitHandler updates memory
   - recordTaskReference(task.id, task, "Review report")

9. Return ChatResponse
   {
     "session_id": "session_123",
     "content": "I've created 'Review report'...",
     "tool_calls": [{"tool": "create_task", "params": {...}}]
   }
```

### Example 2: Context-Aware Update

```
1. Previous context: "Review report" task created (id: abc123)
   Memory has: task_id=abc123, context="Review report"

2. User: "Make that high priority"
   POST /chat/send {"message": "Make that high priority"}

3. Agent reasoning:
   - Intent: Update task
   - "that" → refers to last created/mentioned task
   - Context: task_id=abc123
   - Parameters: {task_id: "abc123", priority: "high"}

4. update_task tool executes
   - Get existing task from storage
   - Merge updates: {priority: "high"}
   - Validate full schema
   - Persist changes
   - Update cache
   - Return updated Task

5. Response: "Updated 'Review report' to high priority"

6. Memory updated with new reference
```

### Example 3: List with Filtering

```
1. User: "What do I need to do today?"

2. Agent reasoning:
   - Intent: List tasks
   - Filter: range="today", status="pending"

3. list_tasks tool executes
   - Filter tasks by user_id
   - Apply range filter (due_date = today)
   - Filter status = "pending"
   - Sort by due_date, then priority
   - Calculate stats
   - Return [Task1, Task2, ...]

4. Storage returns:
   - Today's pending tasks
   - Count: 3 tasks
   - Stats: {total, pending, completed, overdue}

5. Agent formats response:
   "You have 3 tasks today:
    1. Task 1 (due 2 PM)
    2. Task 2 (due 5 PM)
    ..."

6. Memory records all returned tasks as references
```

## Design Patterns

### Pattern 1: Tool Result Handling

```typescript
Tool.execute() → {success, result, error?}
  ↓
Agent checks success flag
  ├─ true: Use result in response
  └─ false: Report error to user
       ↓
Generate conversational response
```

### Pattern 2: Task Reference Resolution

```
"Mark that as done"
  ↓
Agent extracts: {action: "complete", reference: "that"}
  ↓
Check conversation memory
  ├─ Single recent task → Use it
  ├─ Multiple tasks → Ask which one
  └─ No recent tasks → Ask user to specify
       ↓
Call complete_task(task_id)
```

### Pattern 3: Schema Validation

```typescript
Input Data
  ↓
Zod Schema Validation
  ├─ Type checking
  ├─ Range validation
  ├─ Format validation
  └─ Custom rules
       ↓
Success: Validated Data
Failure: ZodError → User-friendly message
```

## Scalability Considerations

### Current (Development)

```
File-based Storage
└─ JSON files in ./data
   └─ OK for <10K tasks
   └─ Single machine only
```

### Production (Recommended)

```
Database Persistence
├─ PostgreSQL or MongoDB
├─ Connection pooling
└─ Indexes on user_id, due_date, status

MCP Server Integration
├─ Dedicated MCP server
├─ Resource caching
└─ Multi-tenant support

Session Storage
├─ Redis for conversation memory
├─ TTL-based expiration
└─ Distributed access

Load Balancing
├─ Multiple API instances
├─ Shared Redis cache
└─ Database replication
```

## Error Handling Strategy

### Layer 1: Tool Validation
```typescript
Tool.execute()
├─ Zod schema validation
├─ Business logic validation
└─ Return {success: false, error}
```

### Layer 2: Agent Error Handling
```typescript
Agent.processMessage()
├─ Try/catch around API call
├─ Tool execution failures
└─ Return user-friendly message
```

### Layer 3: API Error Handling
```
Express route
├─ Parameter validation
├─ Authentication checks
├─ Try/catch blocks
└─ HTTP error responses
```

### Layer 4: User Communication
```
Agent → Conversational error message
├─ "I couldn't find that task"
├─ "Please tell me which task..."
└─ Never expose technical details
```

## Security Considerations

### Authentication
- Validate X-User-ID header (in production, use JWT)
- Ensure user can only access their own tasks/sessions

### Data Validation
- Zod schema validation on all inputs
- Sanitize string inputs to prevent injection

### Rate Limiting
- Implement per-user rate limits on /chat/send
- Prevent abuse of token usage

### Privacy
- User data isolated by user_id
- Sessions auto-expire after inactivity
- No sensitive data in logs

## Testing Strategy

### Unit Tests
- Tool parameter validation
- Memory management
- Schema validation

### Integration Tests
- Full conversation flows
- Tool execution with storage
- Memory context across messages

### E2E Tests
- HTTP API requests
- Session management
- Multi-turn conversations

### Load Testing
- Concurrent sessions
- Message throughput
- Storage performance

## Performance Optimization

### Caching
- In-memory task cache in MCPStorage
- Conversation memory for frequent references
- Session metadata caching

### Database
- Index on (user_id, status)
- Index on (user_id, due_date)
- Partition by user_id for sharding

### API
- Connection reuse
- Response compression
- Session pooling

## Future Enhancements

### Short Term
- [ ] Web UI with real-time updates
- [ ] Email summaries
- [ ] Recurring tasks
- [ ] Task dependencies

### Medium Term
- [ ] Calendar integration
- [ ] Slack/Teams integration
- [ ] Mobile app
- [ ] Advanced analytics

### Long Term
- [ ] Collaborative tasks
- [ ] Multi-agent workflows
- [ ] Custom domain-specific agents
- [ ] LLM fine-tuning

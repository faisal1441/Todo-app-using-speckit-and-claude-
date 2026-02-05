# Project Layout & File Guide

## Directory Structure

```
ai-chatbot/
│
├── 📄 Configuration Files
│   ├── package.json              # Dependencies & scripts
│   ├── tsconfig.json             # TypeScript configuration
│   ├── .env.example              # Environment variable template
│   └── .gitignore                # Git ignore rules
│
├── 📚 Documentation
│   ├── README.md                 # Full reference guide
│   ├── QUICKSTART.md             # 5-minute setup guide
│   ├── ARCHITECTURE.md           # System design & patterns
│   ├── EXAMPLES.md               # Example conversations
│   ├── IMPLEMENTATION_SUMMARY.md # What was delivered
│   └── PROJECT_LAYOUT.md         # This file
│
├── 📦 Source Code (src/)
│   │
│   ├── agent/                    # AI Agent System
│   │   ├── todo-agent.ts         # Main agent with OpenAI integration
│   │   │                         # - System prompt definition
│   │   │                         # - Message processing
│   │   │                         # - Model configuration
│   │   │
│   │   ├── tools.ts              # Tool definitions & handlers
│   │   │                         # - create_task
│   │   │                         # - update_task
│   │   │                         # - complete_task
│   │   │                         # - delete_task
│   │   │                         # - get_task
│   │   │                         # - list_tasks
│   │   │
│   │   └── memory.ts             # Conversation memory system
│   │                             # - ConversationMemory class
│   │                             # - SessionManager
│   │                             # - Task reference tracking
│   │
│   ├── chat/                     # Chat Interface
│   │   └── chatkit-handler.ts    # ChatKit integration
│   │                             # - Session management
│   │                             # - Message routing
│   │                             # - Tool call tracking
│   │
│   ├── mcp/                      # Model Context Protocol
│   │   ├── schema.ts             # Data schemas & validation
│   │   │                         # - Task schema
│   │   │                         # - Zod validators
│   │   │                         # - MCP resource metadata
│   │   │
│   │   └── storage.ts            # Task persistence layer
│   │                             # - MCPStorage class
│   │                             # - CRUD operations
│   │                             # - Filtering & sorting
│   │
│   ├── server/                   # REST API
│   │   └── api.ts                # Express routes
│   │                             # - /chat/send
│   │                             # - /chat/sessions
│   │                             # - /health
│   │
│   ├── types/                    # TypeScript types
│   │   └── task.ts               # Task interfaces & types
│   │
│   └── index.ts                  # Application entry point
│                                 # - Component initialization
│                                 # - Server startup
│
├── 📋 Examples
│   └── examples/
│       └── demo.ts               # Standalone demo script
│                                 # - Shows agent usage
│                                 # - Example conversation
│
└── 📁 Data (created at runtime)
    └── data/                     # Task storage (JSON files)
        └── {task-id}.json        # Individual task files
```

## File Descriptions

### Core Agent Files

#### `src/agent/todo-agent.ts` (430 lines)
**Purpose**: Main AI agent orchestration

**Key Components**:
- `SYSTEM_PROMPT`: Comprehensive system instructions
  - Agent personality and behavior
  - Intent classification rules
  - Tool usage guidelines
  - Date handling strategies
  - Priority inference logic
  - Response formatting requirements

- `TodoAgent` class:
  - `processMessage()`: Main entry point
  - `processMessages()`: Batch processing
  - `getStatus()`: Health check

**Dependencies**: OpenAI SDK, Zod

**Key Decisions**:
- Uses gpt-4-turbo by default (change to gpt-3.5-turbo for cost savings)
- Limits to 5 tool steps maximum per request
- System prompt includes concrete examples

---

#### `src/agent/tools.ts` (380 lines)
**Purpose**: Define all available agent tools

**Tools Provided**:
1. **create_task**
   - Input validation: title (required), other fields optional
   - Generates UUID and timestamps
   - Calls storage layer
   - Returns success message + task ID

2. **update_task**
   - Supports partial updates
   - Validates task exists before updating
   - Updates `updated_at` timestamp
   - Returns updated task

3. **complete_task**
   - Sets status to 'completed'
   - Validates task exists
   - Returns confirmation

4. **delete_task**
   - Validates task exists
   - Fetches for confirmation message
   - Deletes from storage
   - Returns deletion confirmation

5. **get_task**
   - Retrieves specific task by ID
   - Used for showing details
   - Returns full task object

6. **list_tasks**
   - Supports filtering: range, status, priority, search
   - Applies multiple filters sequentially
   - Sorts results intelligently
   - Includes statistics (total, pending, completed, overdue)

**Pattern**: Each tool uses Zod for validation before execution

---

#### `src/agent/memory.ts` (210 lines)
**Purpose**: Conversation context and task reference tracking

**Classes**:

1. **ConversationMemory**
   - Stores per-session conversation history (max 50 messages)
   - Tracks recently mentioned tasks
   - Auto-prunes references older than 30 minutes
   - Formats context for agent prompt
   - Enables "that task" resolution

2. **ConversationSessionManager**
   - Manages multiple concurrent sessions
   - Creates sessions on demand
   - Cleans up old sessions
   - Limits total sessions to prevent memory bloat

**Key Methods**:
- `addMessage()`: Add to history
- `recordTaskReference()`: Track mentioned task
- `findTasksByDescription()`: Fuzzy match tasks
- `getContextForAgent()`: Format for prompt
- `getLastMentionedTask()`: Get most recent task

---

### Chat & API Files

#### `src/chat/chatkit-handler.ts` (190 lines)
**Purpose**: Bridge between HTTP API and agent

**Responsibilities**:
- Session lifecycle management
- Message routing to agent
- Tool call result processing
- Memory updates from tool results

**Key Methods**:
- `sendMessage()`: Main message endpoint
- `getOrCreateSession()`: Session management
- `getSessionHistory()`: Retrieve conversation
- `endSession()`: Cleanup
- `getUserSessions()`: List all user sessions

**Design**: Thin layer that coordinates between ChatKit API and agent

---

#### `src/server/api.ts` (190 lines)
**Purpose**: Express REST API routes

**Endpoints**:
```
POST /chat/send
├─ Headers: X-User-ID (required)
├─ Body: {message, session_id?}
└─ Returns: ChatResponse with tool_calls

POST /chat/sessions
├─ Creates new session
└─ Returns: session_id, created_at

GET /chat/sessions
├─ Lists user's sessions
└─ Returns: Array of sessions

GET /chat/sessions/:sessionId
├─ Gets conversation history
└─ Returns: messages array

DELETE /chat/sessions/:sessionId
├─ Ends session
└─ Returns: confirmation

GET /health
├─ Health check
└─ Returns: status, stats

GET /
├─ API documentation
└─ Returns: endpoints, description
```

**Middleware**:
- JSON body parser
- User ID extraction from headers
- Error handling and logging

---

### Storage Files

#### `src/mcp/schema.ts` (160 lines)
**Purpose**: Data validation and schema definitions

**Schemas**:
1. **TaskSchema**: Complete task validation
   - Validates all required/optional fields
   - Enforces types and ranges
   - Includes descriptions for each field

2. **CreateTaskPayloadSchema**: Creation validation
   - title (required)
   - description, due_date, priority, tags (optional)

3. **UpdateTaskPayloadSchema**: Update validation
   - All fields optional (partial update)

4. **ListTasksFilterSchema**: Filter validation
   - range, status, priority, search (all optional)

**Validation Approach**:
- Runtime validation via Zod
- Type inference for TypeScript
- Clear error messages
- Composable schemas

**Resource URIs**:
- Format: `mcp://tasks/{userId}/{taskId}`
- Enables MCP resource identification

---

#### `src/mcp/storage.ts` (360 lines)
**Purpose**: Task persistence and data operations

**Architecture**:
- In-memory Map for fast access
- JSON file system for persistence
- Zod validation on all operations
- Ready to upgrade to database

**MCPStorage Class**:

Methods:
- `initialize()`: Load existing tasks from disk
- `createTask()`: Create new task with UUID and timestamps
- `getTask()`: Retrieve by ID
- `updateTask()`: Partial or full update
- `completeTask()`: Mark as done
- `deleteTask()`: Remove permanently
- `listTasks()`: Query with filters
- `getTaskStats()`: Count by status

**Data Flow**:
```
Input → Zod Validation → Memory Cache → File Persistence → Return Result
```

**Filtering Implementation**:
- Status filter: pending | completed
- Priority filter: low | medium | high
- Date range filter:
  - today: due today only
  - upcoming: future dates
  - overdue: past pending tasks
  - completed: finished tasks
  - all: everything
- Search filter: case-insensitive title/description

---

### Type Definitions

#### `src/types/task.ts` (60 lines)
**Purpose**: TypeScript type definitions

**Interfaces**:
- `Task`: Core task entity
- `CreateTaskPayload`: Creation input
- `UpdateTaskPayload`: Update input
- `ListTasksFilter`: Query filters
- `ConversationContext`: Session context

**Status Types**: 'pending' | 'completed'
**Priority Types**: 'low' | 'medium' | 'high'

---

### Main Application

#### `src/index.ts` (70 lines)
**Purpose**: Application entry point

**Startup Sequence**:
1. Load environment variables
2. Initialize MCP storage
3. Create TodoAgent instance
4. Create ChatKit handler
5. Setup Express API
6. Start server on configured port
7. Log startup messages

**Initialization Order**: Critical for dependency injection

---

### Examples

#### `examples/demo.ts` (80 lines)
**Purpose**: Standalone demonstration

**Shows**:
- Direct agent usage without HTTP
- Conversation memory in action
- Multiple message processing
- Tool call examples

**Usage**: `npx ts-node examples/demo.ts`

---

## Data Storage

### Task File Format

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Review documentation",
  "description": "Check for accuracy and completeness",
  "due_date": "2024-01-17T17:00:00",
  "priority": "high",
  "status": "pending",
  "created_at": "2024-01-16T10:30:00.000Z",
  "updated_at": "2024-01-16T10:30:00.000Z",
  "user_id": "user123",
  "tags": ["documentation", "review"]
}
```

### Storage Location

```
ai-chatbot/
└── data/
    ├── 550e8400-e29b-41d4-a716-446655440000.json
    ├── 660e8400-e29b-41d4-a716-446655440001.json
    └── ... (one file per task)
```

**Note**: `data/` directory created at runtime

---

## Configuration Files

### `package.json`
- **Dependencies**: OpenAI SDK, Zod, Express, dotenv
- **Dev Dependencies**: TypeScript, ts-node, Jest
- **Scripts**: dev, build, start, test, type-check

### `tsconfig.json`
- **Target**: ES2020
- **Module**: ES2020
- **Strict Mode**: Enabled
- **Output**: `./dist`

### `.env.example`
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo
PORT=3000
NODE_ENV=development
MCP_DATA_DIR=./data
```

---

## Documentation Files

### README.md
- **Sections**: Features, Installation, API, Agent Architecture, Configuration, Examples
- **Audience**: Developers and users
- **Length**: ~700 lines

### QUICKSTART.md
- **Content**: 5-minute setup, first requests, troubleshooting
- **Audience**: New users
- **Length**: ~300 lines

### ARCHITECTURE.md
- **Content**: System design, components, data flows, patterns
- **Audience**: Senior developers
- **Length**: ~800 lines

### EXAMPLES.md
- **Content**: 12 conversations, agent reasoning, decision tree
- **Audience**: Developers learning agent behavior
- **Length**: ~900 lines

### IMPLEMENTATION_SUMMARY.md
- **Content**: What was delivered, metrics, capabilities
- **Audience**: Project overview
- **Length**: ~400 lines

---

## Development Workflow

### Adding a New Tool

1. Edit `src/agent/tools.ts`
2. Define tool with Zod schema
3. Implement execute function
4. Add to `createAgentTools()` return
5. Update system prompt in `src/agent/todo-agent.ts`
6. Document in `README.md`
7. Add example in `EXAMPLES.md`

### Customizing Agent Behavior

1. Edit `SYSTEM_PROMPT` in `src/agent/todo-agent.ts`
2. Modify personality/guidelines
3. Update tool descriptions
4. Test with example messages
5. Update `EXAMPLES.md`

### Adding Database Support

1. Keep `src/mcp/storage.ts` interface
2. Create `StoragePostgres` class implementing interface
3. Switch in `src/index.ts`
4. Update `MCP_DATA_DIR` handling
5. Update deployment docs

---

## Key Design Decisions

### 1. TypeScript + Strict Mode
**Why**: Type safety, excellent IDE support, refactoring safety

### 2. Zod for Validation
**Why**: Runtime validation, type inference, clear error messages

### 3. File-based Storage
**Why**: Simple for development, easy to upgrade to database

### 4. Single Agent
**Why**: Simpler, more coherent reasoning, easier to manage state

### 5. Conversation Memory
**Why**: Enables context-aware responses, "that task" resolution

### 6. Modular Tool Design
**Why**: Easy to add/remove tools, clear boundaries

---

## Production Considerations

### Security
- Add JWT authentication
- Validate user_id from token
- Use HTTPS
- Add rate limiting
- Sanitize inputs (already done with Zod)

### Performance
- Add response caching
- Use database indexes
- Connection pooling
- Distributed sessions (Redis)

### Monitoring
- Add telemetry
- Log agent decisions
- Track tool usage
- Monitor API latency

### Scaling
- Horizontal scaling via load balancer
- Database replication
- Session storage in Redis
- Message queue for async processing

---

## Getting Started for New Developers

### First Time Reading
1. Start: `QUICKSTART.md`
2. Learn: `EXAMPLES.md`
3. Understand: `ARCHITECTURE.md`
4. Reference: `README.md`

### Making Your First Change
1. Read: Agent system prompt (`src/agent/todo-agent.ts`)
2. Modify: Example: Change SYSTEM_PROMPT
3. Test: `npm run dev` and send test message

### Debugging
1. Enable debug logging in `index.ts`
2. Check `data/` directory for stored tasks
3. Review conversation memory in agent
4. Check OpenAI API responses

---

This layout is designed for:
- ✅ Easy navigation
- ✅ Clear separation of concerns
- ✅ Production readiness
- ✅ Easy scaling and extension
- ✅ Comprehensive documentation

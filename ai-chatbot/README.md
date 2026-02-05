# 🤖 AI-Powered To-Do Chatbot

A production-ready AI chatbot for intelligent task management using OpenAI Agent SDK and MCP (Model Context Protocol).

## Features

✨ **Core Functionality**
- 📝 Add tasks via natural language
- ✏️ Update tasks (rename, reschedule, reprioritize)
- ✅ Mark tasks as completed
- 🗑️ Delete tasks
- 📋 List tasks with smart filtering (today, upcoming, overdue, completed)
- 🔍 Search tasks by keywords
- 💭 Understand ambiguous commands with clarification
- 🧠 Maintain conversational memory per session

⚙️ **Technical Stack**
- **OpenAI Agent SDK**: Agentic reasoning and tool use
- **MCP SDK**: Persistent task storage and resource management
- **ChatKit**: Conversational UI and message handling
- **Express.js**: REST API server
- **TypeScript**: Type-safe implementation
- **Zod**: Runtime schema validation

## Project Structure

```
ai-chatbot/
├── src/
│   ├── agent/
│   │   ├── todo-agent.ts         # Main agent with system prompt & reasoning
│   │   ├── tools.ts              # Tool definitions (create, update, delete, etc.)
│   │   └── memory.ts             # Conversation memory for context tracking
│   ├── chat/
│   │   └── chatkit-handler.ts    # ChatKit integration & session management
│   ├── mcp/
│   │   ├── schema.ts             # MCP resource schema & Zod validators
│   │   └── storage.ts            # Task persistence layer (MCP storage)
│   ├── server/
│   │   └── api.ts                # Express routes & API endpoints
│   ├── types/
│   │   └── task.ts               # TypeScript type definitions
│   └── index.ts                  # Application entry point
├── package.json                  # Dependencies
├── tsconfig.json                 # TypeScript configuration
├── README.md                     # This file
├── EXAMPLES.md                   # Example conversations & agent reasoning
└── .env.example                  # Environment variables template
```

## Installation

### Prerequisites
- Node.js 18+
- npm or yarn
- OpenAI API key

### Setup

1. **Clone and install dependencies**
```bash
cd ai-chatbot
npm install
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
OPENAI_API_KEY=sk-your-key-here
```

3. **Build TypeScript**
```bash
npm run build
```

4. **Start the server**
```bash
npm run dev
```

Server starts at `http://localhost:3000`

## API Usage

### Base URL
```
http://localhost:3000
```

### Authentication
Include user ID in headers:
```
X-User-ID: user123
```

### Endpoints

#### Send a Message
```bash
POST /chat/send
Content-Type: application/json
X-User-ID: user123

{
  "message": "Add a task to review the report tomorrow",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "session_id": "session_123",
  "message_id": "msg_456",
  "role": "assistant",
  "content": "I've created a task: \"Review the report\" (due tomorrow).",
  "timestamp": "2024-01-16T10:30:00.000Z",
  "tool_calls": [
    {
      "tool": "create_task",
      "params": {
        "title": "Review the report",
        "due_date": "2024-01-17"
      }
    }
  ]
}
```

#### Create Session
```bash
POST /chat/sessions
X-User-ID: user123
```

**Response:**
```json
{
  "session_id": "session_123",
  "user_id": "user123",
  "created_at": "2024-01-16T10:30:00.000Z"
}
```

#### Get Session History
```bash
GET /chat/sessions/session_123
```

**Response:**
```json
{
  "session_id": "session_123",
  "messages": [
    {
      "id": "msg_1",
      "role": "user",
      "content": "Add a task to review the report",
      "timestamp": "2024-01-16T10:30:00.000Z"
    },
    {
      "id": "msg_2",
      "role": "assistant",
      "content": "I've created that task for you.",
      "timestamp": "2024-01-16T10:30:01.000Z"
    }
  ]
}
```

#### List User Sessions
```bash
GET /chat/sessions
X-User-ID: user123
```

#### Delete Session
```bash
DELETE /chat/sessions/session_123
X-User-ID: user123
```

#### Health Check
```bash
GET /health
```

## Agent Architecture

### System Prompt

The agent operates with a comprehensive system prompt that defines:

- **Personality**: Concise, friendly, conversational
- **Intent Classification**: Recognizes add, update, complete, delete, list, get operations
- **Parameter Extraction**: Intelligently parses dates, priorities, descriptions
- **Memory Integration**: Uses conversation history to resolve task references
- **Clarification Strategy**: Asks ONE focused question when needed
- **Safety Measures**: Confirms deletions, validates parameters

See `src/agent/todo-agent.ts` for the full system prompt.

### Tool Definitions

The agent has access to 6 core tools:

```typescript
1. create_task(title, description?, due_date?, priority?, tags?)
   - Creates a new task
   - Priority: low | medium | high
   - Due date: ISO 8601 format

2. update_task(task_id, title?, description?, due_date?, priority?, status?, tags?)
   - Updates existing task fields
   - Partial updates supported

3. complete_task(task_id)
   - Marks task as completed
   - Status changes from 'pending' to 'completed'

4. delete_task(task_id)
   - Permanently deletes a task
   - Safety: requires confirmation

5. get_task(task_id)
   - Retrieves specific task details
   - Used for showing task information

6. list_tasks(range?, status?, priority?, search?)
   - Lists tasks with filtering
   - range: 'today' | 'upcoming' | 'overdue' | 'completed' | 'all'
   - status: 'pending' | 'completed'
   - priority: 'low' | 'medium' | 'high'
   - search: free-text search
```

### Conversation Memory

Each session maintains:
- **Message History**: Last 50 messages for context
- **Task References**: Recently mentioned tasks (auto-pruned after 30 min)
- **Context Tracking**: What action was last taken

This enables references like:
- "Mark that as done" → Resolves to last mentioned task
- "Change it to high priority" → Updates the task from context
- "the report task" → Matched against recent task references

## MCP Storage

### Task Resource Schema

Tasks are stored as MCP resources with this structure:

```typescript
interface Task {
  id: string;                    // UUID
  title: string;                 // Task name (required)
  description?: string;          // Detailed description
  due_date?: string;            // ISO 8601 date/time
  priority: TaskPriority;       // low | medium | high
  status: TaskStatus;           // pending | completed
  created_at: string;           // ISO 8601 timestamp
  updated_at: string;           // ISO 8601 timestamp
  user_id: string;              // Task owner
  tags?: string[];              // Categorization tags
}
```

### Storage Implementation

- **Location**: Tasks stored as JSON files in `./data` directory
- **Format**: One file per task (named by task ID)
- **Validation**: Zod schemas ensure data integrity
- **Memory Cache**: In-memory Map for fast access
- **Persistence**: Synchronous writes for consistency

To use actual MCP servers:
1. Update `MCPStorage` class to connect to MCP server
2. Replace file-based storage with MCP resource API calls
3. Use standard MCP URIs: `mcp://tasks/{userId}/{taskId}`

## Configuration

### Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo  # or gpt-3.5-turbo

# Server
PORT=3000
NODE_ENV=development

# MCP
MCP_DATA_DIR=./data
```

### Model Selection

**gpt-4-turbo** (recommended)
- More reliable reasoning
- Better context understanding
- Faster tool selection
- ~0.03 tokens per request

**gpt-3.5-turbo** (cost-effective)
- Faster responses
- Lower cost
- Good for simpler tasks
- May require more guidance

To switch models, edit `src/agent/todo-agent.ts`:
```typescript
private model = 'gpt-3.5-turbo'; // Change this line
```

## Example Conversations

See `EXAMPLES.md` for detailed example conversations showing:

- Simple task creation
- Tasks with descriptions and due dates
- Ambiguous input handling
- Context-aware task references
- Listing and filtering tasks
- Marking tasks complete
- Multi-field updates
- Natural language date parsing
- Multi-turn conversations with memory
- Agent decision-making process

## Development

### Running Tests

```bash
npm test
```

### Type Checking

```bash
npm run type-check
```

### Building for Production

```bash
npm run build
npm start
```

## Extending the Agent

### Adding New Tools

1. **Define tool in `src/agent/tools.ts`:**

```typescript
new_tool: tool({
  description: 'What this tool does',
  parameters: z.object({
    param1: z.string().describe('What this param is'),
  }),
  execute: async (params, context) => {
    // Implementation
    return { success: true, result: ... };
  }
})
```

2. **Add to `createAgentTools()` return object**

3. **Update system prompt in `src/agent/todo-agent.ts`** with new tool description

4. **Example tool: Recurring tasks**

```typescript
recurring_task: tool({
  description: 'Create a task that repeats on a schedule',
  parameters: z.object({
    title: z.string(),
    frequency: z.enum(['daily', 'weekly', 'monthly']),
    // ...
  }),
  // ...
})
```

### Customizing Agent Behavior

1. **Modify system prompt** in `src/agent/todo-agent.ts`
2. **Update personality** - change tone/style guidelines
3. **Adjust reasoning** - modify classification logic
4. **Change memory constraints** - adjust max message count or pruning

### Adding Integrations

The modular design supports adding integrations:

- **Slack**: Replace Express routes with Slack event handler
- **Discord**: Use Discord bot library, interface with ChatKitHandler
- **Web UI**: Connect frontend to `/chat/send` endpoint
- **Mobile**: Same API, add authentication middleware

## Performance Considerations

### Optimization Tips

1. **Model Choice**: Use gpt-3.5-turbo for faster, cheaper responses
2. **Caching**: Conversation memory reduces API calls
3. **Batch Processing**: Multiple messages in one session
4. **Storage**: JSON file system OK for <10K tasks per user

### Scaling for Production

1. **Database**: Replace file storage with PostgreSQL/MongoDB
2. **Caching**: Add Redis for session storage
3. **Queue**: Use message queue for async processing
4. **Load Balancing**: Deploy multiple instances
5. **Monitoring**: Add telemetry and error tracking

## Troubleshooting

### API Key Error
```
Error: Invalid API key
```
- Verify key in `.env`
- Check key has `gpt-4` model access
- Regenerate key if needed

### Tool Not Found
```
Error: Tool {tool_name} not found
```
- Ensure tool is added to return object in `createAgentTools()`
- Check spelling matches system prompt

### Memory Issues
- Check `data/` directory size
- Prune old sessions periodically
- Use database for production

## Contributing

To contribute:

1. Create feature branch
2. Add tests for new tools
3. Update EXAMPLES.md with usage
4. Submit PR with description

## License

MIT

## Support

- **Issues**: Report bugs on GitHub
- **Docs**: See EXAMPLES.md for usage patterns
- **API Reference**: GET http://localhost:3000

## Roadmap

- [ ] Web UI with real-time updates
- [ ] Mobile app (React Native)
- [ ] Integration with calendar systems
- [ ] Voice input/output
- [ ] Collaborative task sharing
- [ ] Advanced analytics and insights
- [ ] Email summaries
- [ ] Slack/Teams integration
- [ ] Database persistence (PostgreSQL)
- [ ] Multi-language support

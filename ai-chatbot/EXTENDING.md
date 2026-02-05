# Extending the AI Todo Chatbot

A guide for developers who want to customize, extend, or integrate the chatbot with additional features.

## Table of Contents

1. [Adding Custom Tools](#adding-custom-tools)
2. [Modifying Agent Behavior](#modifying-agent-behavior)
3. [Database Integration](#database-integration)
4. [Custom Integrations](#custom-integrations)
5. [Advanced Features](#advanced-features)
6. [Performance Optimization](#performance-optimization)

---

## Adding Custom Tools

### Step 1: Define the Tool in `src/agent/tools.ts`

```typescript
/**
 * Example: Add a recurring task tool
 */
recurring_task: tool({
  description: 'Create a task that repeats on a schedule',
  parameters: z.object({
    title: z.string().describe('Task title'),
    frequency: z.enum(['daily', 'weekly', 'monthly']).describe('How often'),
    start_date: z.string().optional().describe('When to start (YYYY-MM-DD)'),
    priority: z.enum(['low', 'medium', 'high']).optional(),
  }),
  execute: async (params, context) => {
    const userId = context?.userId || 'default-user';

    // Your implementation here
    const recurringTask = {
      title: params.title,
      frequency: params.frequency,
      // ...
    };

    try {
      // Store recurring task configuration
      // Create first instance
      const firstTask = await storage.createTask(userId, {
        title: params.title,
        priority: params.priority || 'medium',
        due_date: params.start_date,
      });

      return {
        success: true,
        message: `Created recurring task: "${params.title}" (${params.frequency})`,
        task_id: firstTask.id,
      };
    } catch (error) {
      return {
        success: false,
        error: `Failed to create recurring task: ${error.message}`,
      };
    }
  },
}),
```

### Step 2: Add to Tool Factory

In `createAgentTools()`:

```typescript
export function createAgentTools(storage: MCPStorage) {
  return {
    // ... existing tools ...
    recurring_task: recurring_task, // Add new tool
  };
}
```

### Step 3: Update Agent Prompt

In `src/agent/todo-agent.ts`, update `SYSTEM_PROMPT`:

```typescript
const SYSTEM_PROMPT = `...existing prompt...

NEW TOOLS:
- recurring_task(title, frequency, start_date?, priority?) - Create repeating task

...rest of prompt...
`;
```

### Step 4: Add Example in `EXAMPLES.md`

```markdown
## Example: Creating a Recurring Task

\`\`\`
USER: "Add a daily standup meeting at 9am starting next Monday"

AGENT REASONING:
- Extracted: title="Standup meeting", frequency="daily", start_date="next Monday"
- Calling: recurring_task()

RESPONSE: "Created recurring task: 'Standup meeting' (daily starting Monday)"
\`\`\`
```

### Tool Best Practices

✅ **Do**:
- Use Zod for all parameter validation
- Return `{success, message, result}` structure
- Handle errors gracefully
- Include descriptive parameter descriptions
- Document the tool thoroughly

❌ **Don't**:
- Call other tools from within a tool
- Make breaking changes to existing tools
- Assume parameter values without validation
- Ignore user_id for multi-user support

---

## Modifying Agent Behavior

### Change Agent Personality

Edit the `SYSTEM_PROMPT` in `src/agent/todo-agent.ts`:

**Before:**
```typescript
PERSONALITY & BEHAVIOR:
- You are concise, friendly, and conversational
```

**After:**
```typescript
PERSONALITY & BEHAVIOR:
- You are a professional, formal task management assistant
- Use complete sentences and technical terminology
- Provide detailed explanations
```

### Change Model

Edit `src/agent/todo-agent.ts`:

```typescript
// Use gpt-3.5-turbo for faster, cheaper responses
private model = 'gpt-3.5-turbo';

// Or use gpt-4 for better reasoning
private model = 'gpt-4';
```

**Trade-offs**:

| Model | Speed | Cost | Reasoning | Best For |
|-------|-------|------|-----------|----------|
| gpt-3.5-turbo | Fastest | Cheapest | Good | High volume |
| gpt-4-turbo | Medium | Medium | Excellent | Balanced |
| gpt-4 | Slower | Expensive | Best | Complex reasoning |

### Adjust Clarification Strategy

Modify `CLARIFICATION STRATEGY` section in system prompt:

```typescript
// More clarification
CLARIFICATION STRATEGY:
- Ask ONE clarification question maximum
- Ask specifically (e.g., "Which task?" not "What do you mean?")
- Continue without answers if context is sufficient

// Less clarification
CLARIFICATION STRATEGY:
- Never ask clarifying questions - make your best guess
- Use context to infer missing information
- If ambiguous, choose the most likely option
```

### Add Emoji Support

Update system prompt:

```typescript
RESPONSE GUIDELINES:
- Keep responses under 2 sentences unless explaining something complex
- Use emojis frequently for visual feedback
  - ✅ for completion
  - ⚠️ for warnings
  - 📝 for new tasks
  - 🎯 for important items
  - 📅 for dates
- Always confirm what action was taken
```

---

## Database Integration

### Step 1: Create Database Storage Adapter

Create `src/mcp/storage-postgres.ts`:

```typescript
import { Pool } from 'pg';
import { Task, CreateTaskPayload, UpdateTaskPayload, ListTasksFilter } from '../mcp/schema.js';

export class PostgresStorage {
  private pool: Pool;

  constructor(connectionString: string) {
    this.pool = new Pool({ connectionString });
  }

  async initialize(): Promise<void> {
    // Create tables
    await this.pool.query(`
      CREATE TABLE IF NOT EXISTS tasks (
        id UUID PRIMARY KEY,
        user_id VARCHAR NOT NULL,
        title VARCHAR(200) NOT NULL,
        description TEXT,
        due_date TIMESTAMP,
        priority VARCHAR(10),
        status VARCHAR(20),
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        tags TEXT[]
      );

      CREATE INDEX IF NOT EXISTS tasks_user_id ON tasks(user_id);
      CREATE INDEX IF NOT EXISTS tasks_due_date ON tasks(due_date);
      CREATE INDEX IF NOT EXISTS tasks_status ON tasks(status);
    `);
  }

  async createTask(userId: string, payload: CreateTaskPayload): Promise<Task> {
    const id = uuidv4();
    const now = new Date().toISOString();

    const result = await this.pool.query(
      `INSERT INTO tasks
       (id, user_id, title, description, due_date, priority, status, created_at, updated_at, tags)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
       RETURNING *`,
      [id, userId, payload.title, payload.description, payload.due_date,
       payload.priority || 'medium', 'pending', now, now, payload.tags || []]
    );

    return result.rows[0];
  }

  async getTask(taskId: string): Promise<Task | null> {
    const result = await this.pool.query(
      'SELECT * FROM tasks WHERE id = $1',
      [taskId]
    );
    return result.rows[0] || null;
  }

  // Implement other methods similarly...
}
```

### Step 2: Update Application Initialization

In `src/index.ts`:

```typescript
import { PostgresStorage } from './mcp/storage-postgres.js';

async function main() {
  // Choose storage based on environment
  const storage = process.env.DATABASE_URL
    ? new PostgresStorage(process.env.DATABASE_URL)
    : new MCPStorage(MCP_DATA_DIR);

  await storage.initialize();
  // ... rest of setup
}
```

### Step 3: Update Environment Variables

Add to `.env`:

```
DATABASE_URL=postgresql://user:password@localhost:5432/todoapp
```

---

## Custom Integrations

### Slack Integration

Create `src/integrations/slack.ts`:

```typescript
import { App } from '@slack/bolt';
import { ChatKitHandler } from '../chat/chatkit-handler.js';

export function setupSlack(chatHandler: ChatKitHandler) {
  const app = new App({
    signingSecret: process.env.SLACK_SIGNING_SECRET,
    token: process.env.SLACK_BOT_TOKEN,
  });

  app.message(/.*/, async ({ message, say }) => {
    if (message.subtype || !message.text) return;

    const response = await chatHandler.sendMessage(
      message.user,
      message.channel,
      message.text
    );

    await say(response.content);
  });

  return app;
}
```

### Discord Integration

Create `src/integrations/discord.ts`:

```typescript
import { Client, GatewayIntentBits, Message } from 'discord.js';
import { ChatKitHandler } from '../chat/chatkit-handler.js';

export function setupDiscord(chatHandler: ChatKitHandler) {
  const client = new Client({ intents: [GatewayIntentBits.MessageContent] });

  client.on('messageCreate', async (message: Message) => {
    if (message.author.bot) return;

    const response = await chatHandler.sendMessage(
      message.author.id,
      message.channelId,
      message.content
    );

    await message.reply(response.content);
  });

  return client;
}
```

### Web Socket Real-time Updates

Create `src/integrations/websocket.ts`:

```typescript
import { Server } from 'socket.io';
import http from 'http';

export function setupWebSocket(server: http.Server, chatHandler: ChatKitHandler) {
  const io = new Server(server, {
    cors: { origin: '*' }
  });

  io.on('connection', (socket) => {
    socket.on('message', async (data) => {
      const { userId, sessionId, message } = data;

      const response = await chatHandler.sendMessage(userId, sessionId, message);

      socket.emit('response', response);
    });
  });

  return io;
}
```

---

## Advanced Features

### Feature: Task Reminders

Create `src/features/reminders.ts`:

```typescript
import { MCPStorage } from '../mcp/storage.js';
import { Task } from '../mcp/schema.js';

export class ReminderSystem {
  private storage: MCPStorage;
  private checkInterval: NodeJS.Timer;

  constructor(storage: MCPStorage) {
    this.storage = storage;
  }

  start(): void {
    // Check every minute
    this.checkInterval = setInterval(() => this.checkReminders(), 60000);
  }

  stop(): void {
    clearInterval(this.checkInterval);
  }

  private async checkReminders(): Promise<void> {
    // Get all users' upcoming tasks
    // Send notifications/emails for tasks due soon
  }
}
```

### Feature: Task Collaboration

Update task schema:

```typescript
interface Task {
  // ... existing fields ...
  owner_id: string;           // Original creator
  assignees: string[];        // Shared with
  comments: TaskComment[];    // Discussion
  activity_log: ActivityEntry[];  // Changes
}

interface TaskComment {
  id: string;
  author_id: string;
  content: string;
  created_at: string;
}
```

### Feature: Task Dependencies

Add to schema:

```typescript
interface Task {
  // ... existing fields ...
  dependencies: {
    blocks: string[];         // This blocks which tasks
    blocked_by: string[];     // Blocked by which tasks
  };
}
```

Add tool:

```typescript
link_tasks: tool({
  description: 'Create a dependency between two tasks',
  parameters: z.object({
    task_a: z.string().describe('First task ID'),
    task_b: z.string().describe('Second task ID'),
    relationship: z.enum(['blocks', 'depends_on']),
  }),
  // Implementation...
})
```

---

## Performance Optimization

### Caching

Add Redis caching:

```typescript
import Redis from 'ioredis';

export class CachedStorage {
  private storage: MCPStorage;
  private redis: Redis;
  private cacheTTL = 300; // 5 minutes

  constructor(storage: MCPStorage, redis: Redis) {
    this.storage = storage;
    this.redis = redis;
  }

  async getTask(taskId: string): Promise<Task | null> {
    // Check cache first
    const cached = await this.redis.get(`task:${taskId}`);
    if (cached) return JSON.parse(cached);

    // Fetch from storage
    const task = await this.storage.getTask(taskId);
    if (task) {
      // Cache for 5 minutes
      await this.redis.setex(`task:${taskId}`, this.cacheTTL, JSON.stringify(task));
    }

    return task;
  }

  async updateTask(taskId: string, updates: UpdateTaskPayload): Promise<Task> {
    const task = await this.storage.updateTask(taskId, updates);
    // Invalidate cache
    await this.redis.del(`task:${taskId}`);
    return task;
  }
}
```

### Query Optimization

For database, add indexes:

```sql
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE status = 'pending';
CREATE INDEX idx_tasks_priority ON tasks(priority) WHERE status = 'pending';
```

### Batch Operations

```typescript
async batchCreateTasks(userId: string, payloads: CreateTaskPayload[]): Promise<Task[]> {
  return Promise.all(
    payloads.map(p => this.createTask(userId, p))
  );
}
```

---

## Testing Your Extensions

### Unit Test Example

```typescript
import { TodoAgent } from '../src/agent/todo-agent';
import { MCPStorage } from '../src/mcp/storage';

describe('Custom Tool: recurring_task', () => {
  let agent: TodoAgent;
  let storage: MCPStorage;

  beforeEach(async () => {
    storage = new MCPStorage('./test-data');
    await storage.initialize();
    agent = new TodoAgent(storage);
  });

  it('should create recurring tasks', async () => {
    const response = await agent.processMessage({
      userId: 'test-user',
      sessionId: 'test-session',
      userMessage: 'Create a daily standup at 9am',
      memory: new ConversationMemory('test-user', 'test-session'),
    });

    expect(response.message).toContain('recurring task');
    expect(response.tool_calls[0].tool).toBe('recurring_task');
  });
});
```

---

## Deployment Considerations

### Docker Deployment

Create `Dockerfile`:

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

### Kubernetes Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-todo-chatbot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-todo-chatbot
  template:
    metadata:
      labels:
        app: ai-todo-chatbot
    spec:
      containers:
      - name: chatbot
        image: your-registry/ai-todo-chatbot:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: secrets
              key: openai-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: secrets
              key: database-url
        ports:
        - containerPort: 3000
```

---

## Monitoring & Debugging

### Add Logging

```typescript
import pino from 'pino';

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: {
    target: 'pino-pretty',
  },
});

// Use in tools
logger.info({ tool: 'create_task', params }, 'Executing tool');
```

### Monitor Agent Decisions

```typescript
export function monitorAgent(agent: TodoAgent) {
  const original = agent.processMessage.bind(agent);

  agent.processMessage = async (context) => {
    const startTime = Date.now();
    const response = await original(context);
    const duration = Date.now() - startTime;

    logger.info({
      userId: context.userId,
      message: context.userMessage,
      toolsUsed: response.tool_calls.map(t => t.tool),
      duration,
    }, 'Agent processed message');

    return response;
  };
}
```

---

## Conclusion

The chatbot is designed to be extensible. Key extension points:

1. ✅ **Tools**: Add new capabilities
2. ✅ **Agent behavior**: Customize via system prompt
3. ✅ **Storage**: Swap out database implementations
4. ✅ **Integrations**: Connect to Slack, Discord, etc.
5. ✅ **Features**: Add reminders, collaboration, dependencies
6. ✅ **Performance**: Caching, batching, optimization

Start small, test thoroughly, and deploy with confidence!

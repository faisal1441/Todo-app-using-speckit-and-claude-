# Quick Start Guide

Get the AI Todo Chatbot running in 5 minutes.

## Prerequisites

- Node.js 18 or later
- npm or yarn
- OpenAI API key (get one at https://platform.openai.com)

## Setup (5 minutes)

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo
```

### 3. Start the Server
```bash
npm run dev
```

You should see:
```
✓ Server running on http://localhost:3000
```

## First Request

In a new terminal, send your first message:

```bash
curl -X POST http://localhost:3000/chat/send \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

Expected response:
```json
{
  "session_id": "session_123...",
  "message_id": "msg_456...",
  "role": "assistant",
  "content": "I've created a task: \"Buy groceries\".",
  "tool_calls": [...]
}
```

## Try These Commands

### Add a Task
```bash
curl -X POST http://localhost:3000/chat/send \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -d '{"message": "Add a task: Review report due tomorrow at 5pm, high priority"}'
```

### List Tasks
```bash
curl -X POST http://localhost:3000/chat/send \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -d '{"message": "What do I need to do today?"}'
```

### Complete a Task
From the list above, get a task ID, then:
```bash
curl -X POST http://localhost:3000/chat/send \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -d '{"message": "Mark the report task as done"}'
```

### Update a Task
```bash
curl -X POST http://localhost:3000/chat/send \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -d '{"message": "Change that to low priority"}'
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/chat/send` | Send message to chatbot |
| POST | `/chat/sessions` | Create new session |
| GET | `/chat/sessions` | List your sessions |
| GET | `/chat/sessions/{id}` | Get session history |
| DELETE | `/chat/sessions/{id}` | End a session |
| GET | `/health` | Health check |
| GET | `/` | API info |

## Using Session IDs

Sessions keep your conversation context. To use the same session:

```bash
# First message (no session)
curl -X POST http://localhost:3000/chat/send \
  -H "X-User-ID: user123" \
  -d '{"message": "Add task: Review report"}'

# Response includes session_id: "session_abc123"

# Second message (same session)
curl -X POST http://localhost:3000/chat/send \
  -H "X-User-ID: user123" \
  -d '{"message": "Mark that as done", "session_id": "session_abc123"}'
```

## What the Chatbot Can Do

### ✅ Supported Operations

1. **Add Tasks**
   - "Add a task to write documentation"
   - "Create a task: Review report due tomorrow"

2. **Update Tasks**
   - "Change the report to high priority"
   - "Reschedule the meeting to next Friday"
   - "Update the task to add more details"

3. **Complete Tasks**
   - "Mark the report as done"
   - "Finish the documentation task"

4. **Delete Tasks**
   - "Delete the old meeting"
   - "Remove that task"

5. **List Tasks**
   - "What do I need to do today?"
   - "Show me upcoming tasks"
   - "What's overdue?"
   - "Show completed tasks"

6. **Search Tasks**
   - "Find tasks about reports"
   - "Search for meeting tasks"

### 🧠 Smart Features

- **Natural language dates**: "tomorrow", "next Monday", "this week"
- **Context awareness**: "Mark that as done" remembers last mentioned task
- **Priority inference**: "ASAP" = high, "when you can" = low
- **Clarification**: Asks ONE focused question if ambiguous
- **Conversation memory**: Remembers tasks from earlier in the conversation

## Data Storage

Tasks are stored in `./data` directory as JSON files.

To reset all data:
```bash
rm -rf ./data
```

## Troubleshooting

### "API key is invalid"
- Check your OpenAI API key in `.env`
- Make sure it has `gpt-4` access
- Try regenerating the key

### "Cannot find module..."
- Run `npm install` again
- Make sure you're in the `ai-chatbot` directory

### "Port 3000 already in use"
- Change port in `.env`: `PORT=3001`
- Or kill process using port 3000

### Agent seems confused
- Make sure message is clear and specific
- Try simplifying the request
- Check `EXAMPLES.md` for working examples

## Next Steps

1. **Read the documentation**
   - `README.md` - Full reference
   - `EXAMPLES.md` - Conversation examples
   - `ARCHITECTURE.md` - Technical details

2. **Try the demo script**
   ```bash
   npx ts-node examples/demo.ts
   ```

3. **Integrate with your app**
   - Use the REST API from your frontend
   - Add authentication (see README.md)
   - Deploy to production

4. **Customize the agent**
   - Edit system prompt in `src/agent/todo-agent.ts`
   - Add new tools in `src/agent/tools.ts`
   - Modify model in `src/agent/todo-agent.ts`

## Commands for Development

```bash
# Start development server with auto-reload
npm run dev

# Type check
npm run type-check

# Build for production
npm run build

# Run production build
npm start

# Run tests
npm test
```

## Making Your First Modification

### Change the Model
Edit `src/agent/todo-agent.ts`:
```typescript
private model = 'gpt-3.5-turbo'; // Cheaper but less capable
```

### Add a New Tool
1. Edit `src/agent/tools.ts`
2. Add your tool definition
3. Update system prompt in `src/agent/todo-agent.ts`

### Change the Agent Personality
Edit the `SYSTEM_PROMPT` in `src/agent/todo-agent.ts`

## Getting Help

- **API errors**: Check response status code and message
- **Agent behavior**: Review `EXAMPLES.md` for similar cases
- **Architecture questions**: See `ARCHITECTURE.md`
- **Bugs**: Check GitHub issues or create new one

## What's Next?

The chatbot is now ready! Here are some things you can do:

1. ✅ **Add more tasks** and get comfortable with the interface
2. 📋 **Explore filtering** - try different date ranges
3. 🔗 **Integrate** - connect it to your application
4. 🎨 **Customize** - modify system prompt and behavior
5. 🚀 **Deploy** - push to production

Happy task managing! 🚀

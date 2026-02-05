# Startup Guide - Todo App with AI Chatbot

This guide explains how to run all three servers for the todo application.

## Prerequisites

Make sure you have:
- **Node.js** (v16+) - For frontend and chat API
- **Python** (3.9+) - For backend API
- **npm** or **yarn** - For package management

## Installation

First-time setup, install all dependencies:

```bash
npm run install-all
```

This will install:
- Python dependencies (backend/requirements.txt)
- Frontend dependencies (frontend/package.json)
- Chat API dependencies (ai-chatbot/package.json)

## Running All Three Servers

### Option 1: Run All Servers Together (Recommended)

```bash
npm run dev
```

This will start all three servers simultaneously:
- **Backend Task API**: http://localhost:8000/api
- **Chat API**: http://localhost:3000
- **Frontend**: http://localhost:5173

You'll see colored output from all three servers in one terminal.

### Option 2: Run Without Chat API

If you only want to run the backend and frontend:

```bash
npm run dev:no-chat
```

This starts:
- **Backend Task API**: http://localhost:8000/api
- **Frontend**: http://localhost:5173

### Option 3: Run Individual Servers

If you prefer separate terminals, run each command in a different terminal:

**Terminal 1 - Backend:**
```bash
npm run dev:backend
```

**Terminal 2 - Frontend:**
```bash
npm run dev:frontend
```

**Terminal 3 - Chat API:**
```bash
npm run dev:chat
```

## Verifying Everything is Running

### Test Backend API
```bash
curl http://localhost:8000/api/tasks
```

### Test Chat API
```bash
curl -X POST http://localhost:3000/chat/sessions \
  -H "X-User-ID: test-user" \
  -H "Content-Type: application/json"
```

### Open Frontend
Visit http://localhost:5173 in your browser.

## Troubleshooting

### Port Already in Use

If you get "port already in use" error:

```bash
# Find process using the port (Windows)
netstat -ano | findstr :3000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

Or change the port in the respective `.env` file:
- **Chat API**: `ai-chatbot/.env` (change `PORT=3000`)
- **Backend**: Add `--port 8001` to the uvicorn command
- **Frontend**: `frontend/.env.local` (change port in `package.json` dev script)

### Chat API Not Starting

Check that OpenAI API key is set:
```bash
# Check ai-chatbot/.env
cat ai-chatbot/.env | grep OPENAI_API_KEY
```

If missing, add your OpenAI API key:
```bash
# ai-chatbot/.env
OPENAI_API_KEY=sk-xxx...
```

### Frontend Can't Connect to Chat API

Make sure `VITE_CHAT_API` is set in `frontend/.env.local`:
```
VITE_CHAT_API=http://localhost:3000
```

## Environment Variables

### Backend
- **DATABASE_URL**: PostgreSQL connection string (optional, uses in-memory SQLite by default)

### Chat API (`ai-chatbot/.env`)
- **OPENAI_API_KEY**: Required - Your OpenAI API key
- **OPENAI_MODEL**: Model to use (default: gpt-4)
- **PORT**: Server port (default: 3000)
- **NODE_ENV**: development or production

### Frontend (`frontend/.env.local`)
- **VITE_API_URL**: Backend API URL (default: http://localhost:8000/api)
- **VITE_CHAT_API**: Chat API URL (default: http://localhost:3000)

## Project Structure

```
todoapp/
├── backend/              # FastAPI Python backend
│   ├── api/
│   ├── core/
│   └── requirements.txt
├── frontend/             # React Vite frontend
│   ├── src/
│   └── package.json
├── ai-chatbot/          # Express.js Chat API
│   ├── src/
│   └── package.json
└── package.json         # Root scripts
```

## Available Commands

```bash
# Development
npm run dev              # Run all three servers
npm run dev:no-chat     # Run backend + frontend only
npm run dev:backend     # Backend only
npm run dev:frontend    # Frontend only
npm run dev:chat        # Chat API only

# Building
npm run build           # Build frontend
npm run build:backend   # Show backend build info

# Setup
npm run install-all     # Install all dependencies
```

## API Endpoints

### Task API (Backend)
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task
- `PATCH /api/tasks/:id/complete` - Mark complete
- `GET /api/tasks/stats` - Get statistics

### Chat API
- `POST /chat/sessions` - Create new session
- `GET /chat/sessions` - List user sessions
- `POST /chat/send` - Send message to AI
- `GET /chat/sessions/:id` - Get session history
- `DELETE /chat/sessions/:id` - End session
- `GET /health` - Health check
- `GET /` - API info

## Next Steps

1. Start all servers: `npm run dev`
2. Open http://localhost:5173 in your browser
3. Create a task in the task list
4. Chat with the AI assistant to manage your tasks

Happy coding! 🚀

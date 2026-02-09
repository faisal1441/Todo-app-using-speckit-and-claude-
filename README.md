# Todo App - Full Stack Web Application with AI Chatbot

A modern, full-stack todo application with a FastAPI backend, React/Vite frontend, and AI-powered chatbot. Manage your tasks efficiently with a clean, intuitive web interface and intelligent task assistance.

## Features

### Task Management
- **Create Tasks**: Add new tasks with titles and optional descriptions
- **View Tasks**: Display all tasks with status, creation date, and completion information
- **Update Tasks**: Modify task titles and descriptions inline
- **Delete Tasks**: Remove tasks with confirmation
- **Toggle Status**: Mark tasks as complete or incomplete
- **Filter Tasks**: View all, pending, or completed tasks
- **Statistics**: Track total, pending, and completed task counts
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### AI Chatbot
- **Intelligent Assistant**: Get help with task management via AI chat
- **Context-Aware**: Chatbot understands your tasks and provides relevant suggestions
- **Multiple Sessions**: Maintain separate chat sessions for different topics
- **Real-time Updates**: Live chat integration with the task management system

## Technology Stack

### Task API (Backend)
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn
- **Validation**: Pydantic / SQLModel
- **Persistence**: JSON file-based (development) or SQLite (production)
- **CORS**: Enabled for cross-origin requests

### Chat API
- **Framework**: Express.js (Node.js/TypeScript)
- **LLM**: OpenAI GPT-4
- **Server**: Auto-reload development server
- **Features**: Session management, message history, user isolation

### Frontend
- **Library**: React 18
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **Styling**: Custom CSS with responsive design
- **Components**: Task management UI + Chatbot widget

### Deployment
- **Platform**: Vercel
- **Configuration**: Monorepo with separate builds for backend and frontend
- **Scale**: Serverless functions (automatic scaling)

## Project Structure

```
todo-app/
├── backend/                          # FastAPI Task API
│   ├── api/
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── routes/
│   │   │   └── tasks.py             # Task API endpoints
│   │   ├── schemas/
│   │   │   └── task_schema.py       # Pydantic models
│   │   └── middleware/
│   │       └── error_handlers.py    # Error handling
│   ├── core/
│   │   ├── models/
│   │   │   └── task.py              # Task data model
│   │   └── services/
│   │       ├── task_manager.py      # CRUD operations
│   │       └── task_persistence.py  # JSON persistence
│   ├── requirements.txt
│   └── vercel.json
│
├── frontend/                         # React/Vite Frontend
│   ├── src/
│   │   ├── App.jsx                  # Main app component
│   │   ├── main.jsx                 # React entry point
│   │   ├── components/
│   │   │   ├── TaskList.jsx         # Task list view
│   │   │   ├── TaskItem.jsx         # Individual task
│   │   │   ├── TaskForm.jsx         # Create/edit form
│   │   │   ├── TaskFilter.jsx       # Filter controls
│   │   │   ├── TaskStats.jsx        # Statistics display
│   │   │   └── ChatBot.jsx          # AI chatbot widget
│   │   ├── services/
│   │   │   ├── api.js               # Task API client
│   │   │   └── chatApi.js           # Chat API client
│   │   ├── hooks/
│   │   │   └── useTasks.js          # Task management hook
│   │   └── styles/
│   │       └── App.css              # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   └── vercel.json
│
├── ai-chatbot/                       # Express.js Chat API
│   ├── src/
│   │   ├── index.ts                 # Server entry point
│   │   ├── routes/
│   │   │   ├── chat.ts              # Chat endpoints
│   │   │   └── health.ts            # Health check
│   │   ├── services/
│   │   │   ├── chatService.ts       # OpenAI integration
│   │   │   └── sessionService.ts    # Session management
│   │   └── middleware/
│   │       └── cors.ts              # CORS configuration
│   ├── dist/                        # Compiled JavaScript
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.example
│
├── vercel.json                       # Root Vercel config
├── package.json                      # Root package.json with scripts
├── STARTUP_GUIDE.md                  # Quick start guide (this file replaces others)
└── README.md                         # This file
```

## Quick Start

### Prerequisites

- **Node.js** 16+ (for frontend and chat API)
- **Python** 3.9+ (for backend)
- **npm** or **yarn** (for package management)
- **OpenAI API Key** (for chat functionality) - [Get one here](https://platform.openai.com/api-keys)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd todoapp
```

2. **Install all dependencies**:
```bash
npm run install-all
```

This will install:
- Python dependencies: `backend/requirements.txt`
- Frontend dependencies: `frontend/package.json`
- Chat API dependencies: `ai-chatbot/package.json`

3. **Set up environment variables**:

**Backend** (optional):
```bash
# backend/.env (optional, uses SQLite by default)
DATABASE_URL=sqlite:///tasks.db
```

**Chat API** (required):
```bash
# ai-chatbot/.env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
PORT=3000
```

**Frontend**:
```bash
# frontend/.env.local
VITE_API_URL=http://localhost:8000/api
VITE_CHAT_API=http://localhost:3000
```

### Running the Application

**Option 1: Run all servers together (Recommended)**
```bash
npm run dev
```

Starts:
- Backend Task API: `http://localhost:8000/api`
- Chat API: `http://localhost:3000`
- Frontend: `http://localhost:5173`

**Option 2: Run without Chat API**
```bash
npm run dev:no-chat
```

Starts:
- Backend Task API: `http://localhost:8000/api`
- Frontend: `http://localhost:5173`

**Option 3: Run individual servers**
```bash
# Terminal 1
npm run dev:backend

# Terminal 2
npm run dev:frontend

# Terminal 3
npm run dev:chat
```

### Verify Everything is Working

```bash
# Test Task API
curl http://localhost:8000/api/tasks

# Test Chat API
curl -X POST http://localhost:3000/chat/sessions \
  -H "X-User-ID: test-user" \
  -H "Content-Type: application/json"

# Open frontend in browser
# http://localhost:5173
```

## API Documentation

### Base URL
```
http://localhost:8000/api
```

### Endpoints

#### Get All Tasks
```
GET /api/tasks?status=pending|complete
```
Query Parameters:
- `status` (optional): Filter by "pending" or "complete"

Response: `[TaskResponse]`

#### Create Task
```
POST /api/tasks
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "For Sunday dinner"
}
```

Response: `TaskResponse`

#### Get Task by ID
```
GET /api/tasks/{id}
```

Response: `TaskResponse`

#### Update Task
```
PUT /api/tasks/{id}
Content-Type: application/json

{
  "title": "New title",
  "description": "New description"
}
```

Response: `TaskResponse`

#### Delete Task
```
DELETE /api/tasks/{id}
```

Response: `204 No Content`

#### Mark Complete
```
PATCH /api/tasks/{id}/complete
```

Response: `TaskResponse`

#### Mark Incomplete
```
PATCH /api/tasks/{id}/incomplete
```

Response: `TaskResponse`

#### Get Statistics
```
GET /api/tasks/stats
```

Response:
```json
{
  "total": 10,
  "pending": 6,
  "completed": 4
}
```

#### Interactive API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

### Chat API Endpoints

Base URL: `http://localhost:3000`

#### Create Chat Session
```
POST /chat/sessions
Headers: X-User-ID: <user-id>
Content-Type: application/json

Response: { sessionId: string, userId: string, createdAt: timestamp }
```

#### Send Message
```
POST /chat/send
Headers: X-User-ID: <user-id>
Content-Type: application/json

{
  "sessionId": "session-id",
  "message": "Help me organize my tasks"
}

Response: { sessionId: string, message: string, response: string, timestamp: timestamp }
```

#### Get Session History
```
GET /chat/sessions/:sessionId
Headers: X-User-ID: <user-id>

Response: { sessionId: string, messages: [...], createdAt: timestamp }
```

#### List User Sessions
```
GET /chat/sessions
Headers: X-User-ID: <user-id>

Response: [{ sessionId: string, createdAt: timestamp }, ...]
```

#### Delete Session
```
DELETE /chat/sessions/:sessionId
Headers: X-User-ID: <user-id>

Response: 204 No Content
```

#### Health Check
```
GET /health

Response: { status: "ok", uptime: number }
```

## Building for Production

### Build Frontend
```bash
cd frontend
npm run build
```

Output: `frontend/dist/`

### Build Backend
No build needed - Python is interpreted at runtime.

### Deploy to Vercel

1. **Push to GitHub**:
```bash
git add .
git commit -m "Add web version"
git push origin main
```

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Connect your GitHub repository
   - Vercel will auto-detect the monorepo configuration
   - Set environment variables in Vercel dashboard
   - Deploy!

3. **Verify Deployment**:
   - Frontend available at your Vercel URL
   - API available at `<your-url>/api`
   - Interactive docs at `<your-url>/api/docs`

## Development Workflow

### Add a New Feature

1. **Create a test or plan**:
```bash
# Backend: Create test in tests/
# Frontend: Create in src/
```

2. **Implement the feature**:
   - Backend: Add route in `backend/api/routes/tasks.py`
   - Frontend: Create component or update existing

3. **Test locally**:
```bash
npm run dev
# Open http://localhost:5173
# Test the feature
```

4. **Commit and push**:
```bash
git add .
git commit -m "feat: add feature description"
git push origin feature-branch
```

## Troubleshooting

### Backend Issues

**Module not found errors**:
```bash
cd backend
pip install -r requirements.txt
```

**Port 8000 already in use**:
```bash
# Find and kill process (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use a different port
python -m uvicorn api.main:app --reload --port 8001
```

**Database errors**:
- Ensure `backend/api/` directory exists
- Check file permissions on `/tmp/` (Linux/Mac) or temp folder (Windows)

### Frontend Issues

**Node modules issues**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**API connection errors**:
- Check that backend is running on `http://localhost:8000`
- Check `VITE_API_URL` in `frontend/.env.local`
- Check browser console for CORS errors

**Chatbot not loading**:
- Verify `VITE_CHAT_API` is set to `http://localhost:3000`
- Check that Chat API server is running
- Check browser console for errors

### Chat API Issues

**Module not found errors**:
```bash
cd ai-chatbot
npm install
npm run build
```

**OpenAI API errors**:
- Verify `OPENAI_API_KEY` is set in `ai-chatbot/.env`
- Check API key is valid on [OpenAI dashboard](https://platform.openai.com/account/api-keys)
- Verify API quota is available

**Port 3000 already in use**:
```bash
# Find and kill process (Windows)
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or change port in ai-chatbot/.env
echo "PORT=3001" >> ai-chatbot/.env
```

**CORS errors when frontend calls Chat API**:
- Verify CORS is enabled in Chat API
- Check `VITE_CHAT_API` environment variable in frontend
- Ensure Chat API is running

### Vercel Deployment

**502 Bad Gateway**:
- Check that `backend/api/main.py` exports `app`
- Verify `vercel.json` configuration
- Check Vercel build logs

**Frontend shows 404**:
- Check that `frontend/dist` is built
- Verify `vercel.json` routes configuration

**API returns 404**:
- Make sure tasks are using `/api/` prefix
- Check `VITE_API_URL` environment variable in Vercel dashboard

## Data Persistence

### Current Implementation
- Tasks stored in `/tmp/tasks.json` (local) or `/tmp/tasks.json` on Vercel
- **Important**: Data resets on Vercel cold starts

### Migrate to Database (Future)
For production with permanent storage:

1. **Option A: Vercel PostgreSQL**
   - Use Vercel Postgres for managed PostgreSQL
   - Replace `TaskFileManager` with database queries

2. **Option B: Supabase**
   - Supabase for PostgreSQL with built-in auth
   - Update `TaskManager` to use Supabase client

3. **Option C: MongoDB Atlas**
   - MongoDB Atlas for document storage
   - Use pymongo driver

## Performance Considerations

### Backend
- TaskManager uses in-memory list for O(n) lookups
- For 1000+ tasks, consider database indexing
- JSON persistence is atomic (crash-safe writes)

### Frontend
- Vite for optimized builds
- React.memo for component optimization
- Lazy loading with React.lazy() for future routes

### Deployment
- Vercel serverless functions (cold start ~3-5s)
- Frontend cached via Vercel CDN
- API calls use axios with 10s timeout

## Testing

### Backend Unit Tests
```bash
cd backend
python -m pytest tests/unit -v
```

### Backend Integration Tests
```bash
cd backend
python -m pytest tests/integration -v
```

### Frontend Testing (optional)
```bash
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Enhancements

- **Database Integration**: Migrate to PostgreSQL/Supabase for permanent storage
- **User Authentication**: Add login/signup with JWT
- **Categories/Tags**: Organize tasks by categories
- **Due Dates**: Add task deadlines and reminders
- **Priority Levels**: Mark tasks with different priorities
- **Search/Filter**: Advanced search and filtering
- **Undo/Redo**: Revert recent changes
- **Dark Mode**: Add dark theme toggle
- **Mobile App**: React Native version
- **Real-time Sync**: WebSocket for live updates

## Known Limitations

- **Single User**: No multi-user support
- **Temporary Storage**: Vercel cold starts reset data (use database for production)
- **No Authentication**: All tasks are public
- **Concurrent Access**: Limited to single instance (database needed for scaling)

## Architecture Decisions

### Why FastAPI?
- Async support for better performance
- Built-in API documentation (Swagger UI)
- Pydantic for automatic request validation
- Easy deployment to Vercel serverless

### Why React + Vite?
- Modern component-based UI
- Hot module replacement for fast development
- Small bundle size with Vite
- Large ecosystem and community support

### Why Monorepo?
- Single deployment to Vercel
- Shared dependencies and testing
- Easier deployment workflow
- Clear separation of concerns

### Why JSON Persistence?
- No database setup required
- Simple for MVP
- Easy to migrate to database later
- Atomic writes prevent corruption

## License

This project is provided as-is for educational purposes.

## Support

For issues, questions, or suggestions:

1. Check the API documentation at `/api/docs`
2. Review error messages in browser console and terminal
3. Check Vercel deployment logs
4. Open an issue on GitHub

## Project Roadmap

### Completed ✅
- Full-stack web application (React/FastAPI)
- Task CRUD operations with persistence
- Responsive UI for all devices
- Vercel deployment support
- AI-powered chatbot integration
- Chat API with session management
- CORS support for cross-origin requests

### Planned Features 🔜
- **Database Integration**: Migrate from JSON to PostgreSQL/Supabase
- **User Authentication**: Multi-user support with JWT
- **Task Organization**: Categories, tags, and priority levels
- **Advanced Features**: Due dates, reminders, recurring tasks
- **Real-time Updates**: WebSocket support for live sync
- **Dark Mode**: Automatic theme switching
- **Mobile App**: React Native version

## Version History

### Version 3.0.0 (Current - AI Integration)
- **NEW**: AI-powered chatbot with OpenAI integration
- **NEW**: Chat API with session management
- **NEW**: Multi-session chat support with user isolation
- **NEW**: Real-time chatbot widget in frontend
- **IMPROVED**: Enhanced project structure for multiple services
- **IMPROVED**: Docker and Railway deployment configs
- **IMPROVED**: Comprehensive troubleshooting guides

### Version 2.0.0 (Web Version)
- **NEW**: Full-stack web application with React frontend
- **NEW**: FastAPI backend with RESTful API
- **NEW**: Responsive web UI with modern styling
- **NEW**: Vercel deployment support
- **IMPROVED**: Better data validation with Pydantic
- **IMPROVED**: Structured JSON file persistence
- **IMPROVED**: API documentation with Swagger UI

### Version 1.0.0 (CLI Version)
- Initial release with command-line interface
- In-memory task storage with file persistence
- 139 comprehensive tests

---

**Happy task managing!** 🚀 [Deploy to Vercel](https://vercel.com/new)

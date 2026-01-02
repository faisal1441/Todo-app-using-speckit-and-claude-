# Todo App - Full Stack Web Application

A modern, full-stack todo application with a FastAPI backend and React frontend. Manage your tasks efficiently with a clean, intuitive web interface. Deployed to Vercel for easy access anywhere.

## Features

- **Create Tasks**: Add new tasks with titles and optional descriptions
- **View Tasks**: Display all tasks with status, creation date, and completion information
- **Update Tasks**: Modify task titles and descriptions inline
- **Delete Tasks**: Remove tasks with confirmation
- **Toggle Status**: Mark tasks as complete or incomplete
- **Filter Tasks**: View all, pending, or completed tasks
- **Statistics**: Track total, pending, and completed task counts
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Data Persistence**: Tasks saved to JSON file (resets on Vercel cold start; migrate to database for production)

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn
- **Validation**: Pydantic
- **Persistence**: JSON file-based (with structured serialization)

### Frontend
- **Library**: React 18
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **Styling**: Custom CSS with responsive design

### Deployment
- **Platform**: Vercel
- **Configuration**: Monorepo with separate builds for backend and frontend

## Project Structure

```
todo-app/
├── backend/                          # FastAPI backend
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
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── App.jsx                  # Main app component
│   │   ├── main.jsx                 # React entry point
│   │   ├── components/
│   │   │   ├── TaskList.jsx
│   │   │   ├── TaskItem.jsx
│   │   │   ├── TaskForm.jsx
│   │   │   ├── TaskFilter.jsx
│   │   │   └── TaskStats.jsx
│   │   ├── services/
│   │   │   └── api.js               # API client
│   │   ├── hooks/
│   │   │   └── useTasks.js          # Custom hook
│   │   └── styles/
│   │       └── App.css              # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   └── vercel.json
│
├── vercel.json                       # Root Vercel config
├── package.json                      # Root package.json
└── README.md                         # This file
```

## Quick Start

### Prerequisites

- **Node.js** 16+ (for frontend)
- **Python** 3.9+ (for backend)
- **npm** or **yarn** (for frontend package management)

### Local Development Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd todoapp
```

2. **Install dependencies**:
```bash
npm run install-all
```

This will:
- Install Python dependencies in `backend/requirements.txt`
- Install Node dependencies in `frontend/package.json`

3. **Run locally**:

**Option A: Run frontend and backend separately**

Terminal 1 - Start backend:
```bash
cd backend
uvicorn api.main:app --reload --port 8000
```

Terminal 2 - Start frontend:
```bash
cd frontend
npm run dev
```

The app will be available at `http://localhost:5173`

**Option B: Run both with concurrently**

```bash
npm run dev
```

### Environment Variables

Create `frontend/.env` based on `.env.example`:

```
VITE_API_URL=http://localhost:8000/api
```

For Vercel deployment, set environment variables in the Vercel dashboard:
```
VITE_API_URL=https://your-domain.vercel.app/api
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
# Use a different port
uvicorn api.main:app --reload --port 8001
# Update frontend API URL to match
```

### Frontend Issues

**Node modules issues**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**API connection errors**:
- Check that backend is running on `http://localhost:8000`
- Check `VITE_API_URL` in `.env`
- Check browser console for CORS errors

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

## Changelog

### Version 2.0.0 (Current - Web Version)
- **NEW**: Full-stack web application with React frontend
- **NEW**: FastAPI backend with RESTful API
- **NEW**: Responsive web UI with modern styling
- **NEW**: Vercel deployment support
- **IMPROVED**: Better data validation with Pydantic
- **IMPROVED**: Structured JSON file persistence
- **IMPROVED**: API documentation with Swagger UI
- Backward compatible: existing CLI still available in `src/cli/`

### Version 1.1.0
- Added file persistence with JSON storage
- 86 new tests for persistence layer
- Error recovery with corrupt file backup

### Version 1.0.0
- Initial release with CLI interface
- In-memory task storage
- 139 comprehensive tests

---

**Happy task managing!** 🚀 [Deploy to Vercel](https://vercel.com/new)

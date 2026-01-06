# Todo App - Next.js Frontend

A modern Next.js 14 frontend for the Todo App, paired with a FastAPI backend powered by PostgreSQL/Neon DB.

## Technology Stack

- **Framework**: Next.js 14+ (React 18)
- **Language**: TypeScript
- **Styling**: CSS (no Tailwind for now - using custom CSS)
- **API Client**: Fetch API (built-in)
- **State Management**: React Hooks (useState, useEffect)
- **Deployment**: Vercel

## Project Structure

```
nextjs-app/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page (main app)
│   └── globals.css              # Global styles
├── components/                   # React components
│   ├── TaskStats.tsx            # Display task statistics
│   ├── TaskFilter.tsx           # Task status filter buttons
│   ├── TaskForm.tsx             # Create new task form
│   ├── TaskItem.tsx             # Individual task card with edit
│   └── TaskList.tsx             # Task list container
├── lib/                          # Utilities and hooks
│   ├── api.ts                   # API client (fetch-based)
│   └── hooks/
│       └── useTasks.ts          # Custom hook for task management
├── package.json                 # Dependencies
├── next.config.js               # Next.js configuration
├── tsconfig.json                # TypeScript configuration
└── .env.local                   # Environment variables
```

## Setup & Development

### Prerequisites

- Node.js 18+ and npm/yarn
- FastAPI backend running (see `../../backend/`)

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your backend API URL
```

### Development Server

```bash
# Start the development server
npm run dev

# Open http://localhost:3000 in your browser
```

### Building for Production

```bash
# Build the application
npm run build

# Start production server
npm start
```

## Environment Variables

### .env.local

```env
# API Configuration - Point to your FastAPI backend
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# For production (on Vercel):
# NEXT_PUBLIC_API_URL=https://your-api-domain.com/api
```

**Note**: Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser. Store sensitive data on the server only.

## Features

- ✅ **List Tasks**: View all tasks with filtering (All, Pending, Completed)
- ✅ **Create Tasks**: Add new tasks with title and description
- ✅ **Edit Tasks**: Inline editing of task details
- ✅ **Delete Tasks**: Remove tasks with confirmation
- ✅ **Toggle Completion**: Mark tasks as complete/incomplete
- ✅ **Task Statistics**: Display total, pending, and completed counts
- ✅ **Error Handling**: User-friendly error messages
- ✅ **Loading States**: Visual feedback during API operations
- ✅ **Responsive Design**: Mobile-friendly UI
- ✅ **Type Safety**: Full TypeScript support

## API Integration

The app communicates with the FastAPI backend through the `lib/api.ts` client:

### Available Endpoints

```typescript
// Get all tasks (with optional status filter)
taskAPI.getAll(status?: string): Promise<Task[]>

// Get single task
taskAPI.getById(id: number): Promise<Task>

// Create task
taskAPI.create(data: { title, description? }): Promise<Task>

// Update task
taskAPI.update(id, data: { title?, description? }): Promise<Task>

// Delete task
taskAPI.delete(id: number): Promise<void>

// Mark complete/incomplete
taskAPI.markComplete(id: number): Promise<Task>
taskAPI.markIncomplete(id: number): Promise<Task>

// Get statistics
taskAPI.getStats(): Promise<TaskStats>
```

## Custom Hook: useTasks

The `useTasks` hook provides centralized state management for tasks:

```typescript
const {
  tasks,           // Array of Task objects
  loading,         // Boolean indicating data fetch status
  error,           // Error message if any
  stats,           // TaskStats { total, pending, completed }
  addTask,         // (title, description?) => Promise<Task>
  updateTask,      // (id, data) => Promise<Task>
  deleteTask,      // (id) => Promise<void>
  toggleComplete,  // (id, isComplete) => Promise<Task>
  refresh,         // () => Promise<void>
} = useTasks()
```

## Component Hierarchy

```
page.tsx (Home)
├── TaskStats      (Display statistics)
├── TaskForm       (Add new task)
├── TaskFilter     (Filter tasks by status)
├── TaskList       (Display filtered tasks)
│   └── TaskItem   (Individual task with edit/delete)
└── Footer
```

## Styling

Global CSS is in `app/globals.css` with:
- CSS Variables for theming
- Responsive grid layouts
- Mobile-first design
- Accessibility-friendly component styling
- Print-friendly styles

### CSS Variable Customization

Edit `app/globals.css` to customize colors, spacing, and sizes:

```css
:root {
  --primary-color: #4f46e5;
  --primary-hover: #4338ca;
  /* ... more variables ... */
}
```

## Deployment

### Vercel (Recommended)

The project is configured for Vercel deployment:

1. Push code to GitHub
2. Import project in Vercel
3. Set environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy automatically

See `../vercel.json` for complete monorepo configuration.

### Self-Hosted

```bash
# Build
npm run build

# Start production server
npm start

# Server listens on http://localhost:3000
```

## Development Guidelines

### Adding a New Component

1. Create component file in `components/`
2. Use `'use client'` at the top for client-side components
3. Type props with TypeScript interfaces
4. Import and use in parent component

### Adding API Endpoints

1. Add method to `lib/api.ts` (taskAPI object)
2. Define TypeScript interfaces for request/response
3. Use in components via `useTasks` hook or direct call

### Error Handling

Errors are handled at multiple levels:
- **API Level**: `lib/api.ts` catches and logs API errors
- **Hook Level**: `useTasks` catches errors and sets error state
- **Component Level**: Components display error messages to users

## Testing the Connection

1. Start backend: `python -m uvicorn backend.api.main:app --reload --port 8000`
2. Start frontend: `npm run dev`
3. Visit http://localhost:3000
4. Try creating, editing, and deleting tasks

## Troubleshooting

### API Connection Issues

**Problem**: "Failed to load tasks" error

**Solutions**:
- Check if backend is running on port 8000
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check CORS settings in `backend/api/main.py`
- Check browser console for network errors

### Build Issues

**Problem**: TypeScript compilation errors

**Solutions**:
- Run `npm install` to ensure all dependencies
- Check TypeScript types: `npx tsc --noEmit`
- Restart development server

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and test
3. Commit: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Create Pull Request

## License

MIT

## Related Documentation

- [Backend Documentation](../backend/README.md)
- [Main Project README](../README.md)
- [Deployment Guide](../docs/deployment.md)

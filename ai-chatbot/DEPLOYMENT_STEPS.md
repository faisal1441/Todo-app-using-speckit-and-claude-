# Deployment Steps: From Development to Production

A step-by-step guide to deploy the AI chatbot with your existing Todo app.

## Timeline Estimate

- **Phase 1 (Dev Setup)**: 15-30 minutes
- **Phase 2 (Backend Deployment)**: 10-15 minutes
- **Phase 3 (Frontend Integration)**: 20-30 minutes
- **Phase 4 (Testing)**: 10-15 minutes
- **Total**: ~1 hour for complete integration

---

## Phase 1: Development Setup (Local Testing)

### Step 1.1: Install Dependencies

```bash
cd ai-chatbot
npm install
```

### Step 1.2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4-turbo
PORT=3000
NODE_ENV=development
MCP_DATA_DIR=./data
```

### Step 1.3: Start Development Server

```bash
npm run dev
```

Expected output:
```
✓ Server running on http://localhost:3000
```

### Step 1.4: Test Locally

In another terminal:

```bash
# Test health check
curl http://localhost:3000/health

# Test chat endpoint
curl -X POST http://localhost:3000/chat/send \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -d '{"message": "Add a task to test the chatbot"}'
```

✅ If you see a JSON response with a message, development setup is complete!

---

## Phase 2: Deploy Chat Backend

### Option A: Deploy to Vercel (Recommended - 5 minutes)

#### 2A.1: Prepare for Vercel

Create `ai-chatbot/vercel.json`:

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

#### 2A.2: Push to GitHub

```bash
cd /path/to/your/todoapp
git add ai-chatbot/
git commit -m "Add AI chatbot implementation"
git push origin main
```

#### 2A.3: Deploy on Vercel

1. Go to https://vercel.com
2. Click "Import Project"
3. Select your GitHub repository
4. Click "Configure" and select `ai-chatbot` directory
5. Add Environment Variable:
   - Name: `OPENAI_API_KEY`
   - Value: `sk-your-actual-key`
6. Click "Deploy"

**Wait for deployment to complete** (usually 2-3 minutes)

Once complete, you'll get a URL like:
```
https://ai-chatbot-xxx.vercel.app
```

Test it:
```bash
curl https://ai-chatbot-xxx.vercel.app/health
```

### Option B: Deploy to Railway (Alternative - 10 minutes)

#### 2B.1: Prepare Dockerfile

Already created in `ai-chatbot/`. No changes needed.

#### 2B.2: Deploy

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Choose your repository
5. Select root directory: `ai-chatbot`
6. Add environment variable: `OPENAI_API_KEY`
7. Wait for deployment

Get your public URL from Railway dashboard.

---

## Phase 3: Integrate with Frontend

### 3.1: Copy Chat Component

Copy files to your frontend:

```bash
# From todoapp root
cp ai-chatbot/FRONTEND_INTEGRATION.md frontend/

# Create chat component directory
mkdir -p frontend/src/components/Chat
```

Create `frontend/src/components/Chat/ChatWidget.tsx`:
- Copy the code from `ai-chatbot/FRONTEND_INTEGRATION.md`
- Adjust paths if needed

Create `frontend/src/components/Chat/ChatWidget.module.css`:
- Copy the styles from `ai-chatbot/FRONTEND_INTEGRATION.md`

### 3.2: Update Environment Variables

Edit `frontend/.env.local`:

```bash
# For local development
VITE_CHAT_API=http://localhost:3000
VITE_TASK_API=http://localhost:8000

# Or if deploying to Vercel:
# VITE_CHAT_API=https://ai-chatbot-xxx.vercel.app
# VITE_TASK_API=https://todoapp-api.vercel.app
```

### 3.3: Update Main Layout

Modify your main dashboard/layout component to include ChatWidget:

```typescript
// frontend/src/pages/Dashboard.tsx
import { ChatWidget } from '../components/Chat/ChatWidget';

export function Dashboard() {
  const [refreshTasks, setRefreshTasks] = useState(0);

  return (
    <div className="flex h-screen">
      <div className="flex-1 overflow-auto">
        {/* Your existing task list */}
        <TaskList key={refreshTasks} />
      </div>
      <div className="w-96 border-l">
        <ChatWidget
          onTasksUpdated={() => setRefreshTasks(prev => prev + 1)}
          userId="user123" // Replace with actual user ID
        />
      </div>
    </div>
  );
}
```

### 3.4: Test Locally

```bash
# Terminal 1: Start chat API
cd ai-chatbot
npm run dev

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Start task API
cd backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:5173` (or your dev port) and test:

1. Type: "Add a task to test integration"
2. Verify task appears in task list within 1 second
3. Type: "What do I need to do?"
4. Verify tasks are listed in chat

✅ If both work, integration is successful!

---

## Phase 4: Production Deployment

### 4.1: Deploy Frontend to Vercel

```bash
cd frontend
vercel deploy --prod
```

Or:

1. Push to GitHub: `git push origin main`
2. Go to Vercel
3. Select frontend project
4. Deploy is automatic on push

Add environment variables in Vercel:
```
VITE_CHAT_API=https://ai-chatbot-xxx.vercel.app
VITE_TASK_API=https://todoapp-api.vercel.app
```

### 4.2: Verify All Deployments

```bash
# Check chat API
curl https://ai-chatbot-xxx.vercel.app/health

# Check task API
curl https://todoapp-api.vercel.app/health

# Check frontend loads
curl https://your-frontend-domain.vercel.app
```

### 4.3: Update CORS (if needed)

If you get CORS errors, update backend CORS configuration:

Edit `backend/api/main.py`:

```python
origins = [
    # ... existing origins ...
    "https://your-frontend-domain.vercel.app",
    "https://ai-chatbot-xxx.vercel.app",
]
```

Redeploy backend.

---

## Phase 5: Monitoring & Verification

### 5.1: Check Logs

**Vercel (Chat API):**
1. Go to Vercel dashboard
2. Select project
3. Click "Deployments"
4. View logs for errors

**Vercel (Frontend):**
1. Check browser console (F12)
2. Check network tab for API calls

**Backend:**
```bash
# If on Railway/Heroku
heroku logs --tail

# If locally
python -m uvicorn api.main:app --reload
```

### 5.2: Test Production

Visit your live frontend and test:

```
Test Cases:
1. Create task via chat
   Input: "Add task: Demo the AI chatbot"
   Expected: Task appears in list

2. List tasks
   Input: "What are my tasks?"
   Expected: Chat lists all tasks

3. Complete task
   Input: "Mark the demo task as done"
   Expected: Task status changes

4. Update task
   Input: "Change priority to high"
   Expected: Task priority updates
```

### 5.3: Performance Baseline

Monitor these metrics:

```
Chat Response Time: < 2 seconds
Task List Update: < 1 second
API Latency: < 500ms
Error Rate: < 0.1%
```

---

## Troubleshooting Checklist

### Issue: "Cannot connect to chat API"

```bash
# Check if endpoint is accessible
curl https://ai-chatbot-xxx.vercel.app/health

# Check environment variables
echo $VITE_CHAT_API

# Check CORS headers in frontend
# Browser DevTools → Network → Request Headers
```

**Solution:**
- Verify chat API URL in `.env.local`
- Check CORS configuration in `backend/api/main.py`
- Ensure chat API is deployed and healthy

### Issue: "Chat creates tasks but list doesn't update"

```bash
# Check task API is working
curl https://todoapp-api.vercel.app/api/tasks

# Check database connection
# In backend logs, look for "Connected to database"
```

**Solution:**
- Verify `VITE_TASK_API` environment variable
- Check database connectivity
- Ensure `onTasksUpdated` callback is working

### Issue: "Chatbot doesn't understand my commands"

**Likely cause:** Model performing poorly on specific input

**Solutions:**
1. Use simpler language: "Add task" instead of "I need to add a task"
2. Be specific about what needs to change
3. Provide full context: "Change the report task to high priority"
4. Check system prompt is loaded correctly

### Issue: "Token limit exceeded"

**Solutions:**
1. Switch to cheaper model:
   ```
   OPENAI_MODEL=gpt-3.5-turbo
   ```
2. Clear conversation history more frequently
3. Reduce chat history retention:
   ```typescript
   // In src/agent/memory.ts
   private maxMessages: number = 20; // Reduce from 50
   ```

---

## Post-Deployment Checklist

- [ ] Chat API deployed and health check passing
- [ ] Frontend deployed with correct environment variables
- [ ] CORS configured on backend
- [ ] Can create tasks via chat
- [ ] Task list updates when chat creates tasks
- [ ] Can complete tasks via chat
- [ ] Can list tasks in chat
- [ ] No console errors in frontend
- [ ] API response times < 2 seconds
- [ ] All 6 tools working (create, update, complete, delete, get, list)
- [ ] Error messages are user-friendly
- [ ] Session management working (chat history persists)

---

## Monitoring & Maintenance

### Weekly Checks

```bash
# Check error logs
# Check token usage on OpenAI dashboard
# Monitor API latency
# Review user feedback
```

### Monthly Tasks

- [ ] Review OpenAI usage and costs
- [ ] Check for any errors in production logs
- [ ] Update dependencies: `npm update`
- [ ] Test all tools are working
- [ ] Gather user feedback and iterate

---

## Rollback Plan

If something goes wrong:

### Rollback Chat API

**Vercel:**
1. Go to Deployments
2. Click the previous working deployment
3. Click "Redeploy"

**Railway:**
1. Go to Deployments
2. Select previous deployment
3. Click "Activate"

### Rollback Frontend

**Vercel:**
1. Go to Deployments
2. Select previous working version
3. Click "Promote to Production"

### Rollback Backend

```bash
# If using git
git revert <commit-hash>
git push
```

---

## Cost Analysis

### Monthly Costs

```
OpenAI API (ChatGPT-4):
- Average: $0.05 per task interaction
- Estimated usage: 1000 interactions/month
- Cost: $50/month

Vercel (Chat API):
- Free tier for up to 100 functions
- Pro: $20/month (if exceeding)

Vercel (Frontend):
- Free tier
- Pro: $20/month (optional)

PostgreSQL (Database):
- Free tier: 5GB included
- Paid: $9/month for additional storage

Total: $50-100/month
```

**Cost Optimization:**
- Use gpt-3.5-turbo instead: $10/month
- Implement caching: -20% API costs
- Add rate limiting: prevent abuse

---

## Next Steps After Deployment

### Week 1
- [ ] Gather user feedback
- [ ] Monitor error logs
- [ ] Check API costs
- [ ] Fix any bugs

### Week 2-4
- [ ] Add more tools (reminders, recurring tasks)
- [ ] Implement Slack/Discord integration
- [ ] Add advanced filtering options
- [ ] Improve error messages

### Month 2+
- [ ] Collaborative tasks
- [ ] Task dependencies
- [ ] Analytics dashboard
- [ ] Mobile app

---

## Getting Help

If you encounter issues:

1. **Check logs first:**
   - Vercel: Deployments → Logs
   - Browser: F12 → Console
   - Railway: Dashboard → Logs

2. **Review documentation:**
   - `README.md` - Overview
   - `ARCHITECTURE.md` - System design
   - `EXAMPLES.md` - Example conversations
   - `EXTENDING.md` - Custom modifications

3. **Common issues:**
   - See "Troubleshooting Checklist" above

4. **Debug locally first:**
   ```bash
   npm run dev  # Chat API
   npm run dev  # Frontend
   python -m uvicorn api.main:app --reload  # Backend
   ```

---

## Success Criteria

You've successfully deployed when:

✅ Frontend loads without errors
✅ Chat sidebar visible and functional
✅ Can send messages to chatbot
✅ Chatbot understands and responds
✅ Creating task via chat updates task list
✅ Listing tasks via chat shows all tasks
✅ Completing task via chat works
✅ Updating task via chat works
✅ No console errors
✅ API latency < 2 seconds
✅ Error messages are clear

---

## Deployment Success! 🎉

Your AI-powered Todo Chatbot is now live and integrated with your existing app!

**Next:**
- Share with users
- Gather feedback
- Iterate and improve
- Consider Phase 2 enhancements

Happy task managing! 🚀

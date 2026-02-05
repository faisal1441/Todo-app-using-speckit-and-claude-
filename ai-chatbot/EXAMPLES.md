# AI Todo Chatbot - Example Conversations

This document shows realistic example conversations with the TodoAgent, demonstrating its capabilities and reasoning.

---

## Example 1: Simple Task Creation

```
USER: "Remind me to submit the report tomorrow evening"

AGENT REASONING:
- User intent: Create a task
- Extracted from message:
  - title: "Submit the report"
  - due_date: Tomorrow at 5 PM (end of business day)
  - priority: high (implied by "reminder" and specific time)
- Calling: create_task(title, due_date, priority)

AGENT RESPONSE: "I've created a task: 'Submit the report' (due 2024-01-17T17:00:00).
This is marked as high priority since you want it done tomorrow evening."

TOOLS CALLED:
- create_task:
  {
    "title": "Submit the report",
    "due_date": "2024-01-17T17:00:00",
    "priority": "high"
  }
```

---

## Example 2: Task with Details

```
USER: "Add a task: Review the design proposal. It's for the client meeting next week
and it's really important. Add some notes: Check for inconsistencies and performance issues."

AGENT REASONING:
- User intent: Create a task with description and details
- Extracted:
  - title: "Review the design proposal"
  - description: "Check for inconsistencies and performance issues"
  - due_date: Next week (Monday of following week)
  - priority: high (client meeting, marked as "really important")
- Calling: create_task with all details

AGENT RESPONSE: "Created task: 'Review the design proposal' with high priority,
due next Monday (2024-01-22). I've added notes about checking for inconsistencies
and performance issues."

TOOLS CALLED:
- create_task:
  {
    "title": "Review the design proposal",
    "description": "Check for inconsistencies and performance issues",
    "due_date": "2024-01-22",
    "priority": "high",
    "tags": ["client", "design"]
  }
```

---

## Example 3: Ambiguous Input with Clarification

```
USER: "Update the report"

AGENT REASONING:
- User intent: Update a task
- Problem: Which report? Need clarification
- Only ONE clarification question allowed
- Checking conversation memory: First time mentioning "report"
- Cannot proceed without more details

AGENT RESPONSE: "I want to help! Which task did you mean?
- Submit the report (due tomorrow)
- Review the design proposal (due Monday)

Or tell me what you'd like to change about a task?"

(No tools called - waiting for clarification)
```

---

## Example 4: Context-Aware Task Reference

```
Previous context: Just created "Submit the report" task

USER: "Make that high priority"

AGENT REASONING:
- User intent: Update a task with "Make that high priority"
- Context: Last created task was "Submit the report" with id: abc123
- Parameter extraction:
  - task_id: abc123 (from conversation memory)
  - priority: "high"
- Calling: update_task(task_id, {priority: "high"})

AGENT RESPONSE: "Done! I've marked 'Submit the report' as high priority."

TOOLS CALLED:
- update_task:
  {
    "task_id": "abc123",
    "priority": "high"
  }
```

---

## Example 5: Listing Tasks

```
USER: "What do I need to do today?"

AGENT REASONING:
- User intent: List tasks with time filter
- Extracted:
  - range: "today" (today's tasks)
  - status: "pending" (don't show completed tasks by default)
- Calling: list_tasks(range="today", status="pending")

AGENT RESPONSE: "You have 3 tasks today:

✓ 📝 Meeting prep (due today at 2 PM)
✓ 📧 Email client about schedule (due today at 5 PM)
✓ 📊 Finalize budget report (due today at 6 PM)

Looks like you have a busy day! Let me know if you need to reprioritize anything."

TOOLS CALLED:
- list_tasks:
  {
    "range": "today",
    "status": "pending"
  }
```

---

## Example 6: Marking Tasks Complete

```
Previous context: "Meeting prep" task has id: task456

USER: "I finished the meeting prep"

AGENT REASONING:
- User intent: Mark task as complete
- Context check: "meeting prep" mentioned earlier, id: task456
- Calling: complete_task(task_id: task456)

AGENT RESPONSE: "Great job! I've marked 'Meeting prep' as complete. ✓"

TOOLS CALLED:
- complete_task:
  {
    "task_id": "task456"
  }
```

---

## Example 7: Complex Update

```
USER: "Change the design review from Monday to Friday and make it medium priority instead"

AGENT REASONING:
- User intent: Update a task with multiple changes
- From context: "Review the design proposal" is the recent design task
- task_id: task789
- Changes:
  - due_date: This Friday (2024-01-19)
  - priority: medium
- Calling: update_task with both fields

AGENT RESPONSE: "Updated 'Review the design proposal':
moved to Friday (2024-01-19) and set to medium priority."

TOOLS CALLED:
- update_task:
  {
    "task_id": "task789",
    "due_date": "2024-01-19",
    "priority": "medium"
  }
```

---

## Example 8: Delete with Confirmation

```
USER: "Delete the old meeting task"

AGENT REASONING:
- User intent: Delete a task
- Problem: Which task? Need clarification
- Response: Ask for confirmation (safety check)

AGENT RESPONSE: "I want to make sure before deleting.
Are you sure you want to delete 'Meeting prep'?
Reply 'yes' to confirm."

(Waiting for user confirmation)
```

---

## Example 9: Search Tasks

```
USER: "Show me all tasks about reports"

AGENT REASONING:
- User intent: List tasks with search filter
- Extracted:
  - search: "reports"
  - status: "pending" (show active tasks)
- Calling: list_tasks(search="reports")

AGENT RESPONSE: "Found 2 tasks with 'reports':

1. Submit the report (due tomorrow)
2. Finalize budget report (due today)

Want to update any of these?"

TOOLS CALLED:
- list_tasks:
  {
    "search": "reports",
    "status": "pending"
  }
```

---

## Example 10: Overdue Tasks

```
USER: "What's overdue?"

AGENT REASONING:
- User intent: List overdue tasks
- Extracted:
  - range: "overdue"
- Calling: list_tasks(range="overdue")

AGENT RESPONSE: "⚠️ You have 2 overdue tasks:

1. Update client presentation (was due 2024-01-10)
2. Complete performance review (was due 2024-01-12)

Would you like to reschedule these?"

TOOLS CALLED:
- list_tasks:
  {
    "range": "overdue"
  }
```

---

## Example 11: Natural Date Parsing

```
USER: "Add a task to review the Q1 budget due next Friday at 10am"

AGENT REASONING:
- User intent: Create task with natural language date
- Extracted:
  - title: "Review the Q1 budget"
  - due_date: "2024-01-19T10:00:00" (next Friday at 10 AM)
  - priority: "medium" (default for financial tasks)
- Calling: create_task

AGENT RESPONSE: "Created 'Review the Q1 budget' with deadline Friday, Jan 19 at 10 AM."

TOOLS CALLED:
- create_task:
  {
    "title": "Review the Q1 budget",
    "due_date": "2024-01-19T10:00:00",
    "priority": "medium"
  }
```

---

## Example 12: Multi-Turn Conversation

```
USER: "I need to handle three things: call Sarah, buy groceries, and finish the presentation"

AGENT REASONING:
- User intent: Create multiple tasks
- This is a list of 3 separate items
- Create 3 separate tasks
- Extracted:
  1. "Call Sarah" - phone call, medium priority, no due date
  2. "Buy groceries" - errand, low priority
  3. "Finish the presentation" - work, high priority

AGENT RESPONSE: "I've created 3 tasks:
1. ✓ Call Sarah
2. ✓ Buy groceries
3. ✓ Finish the presentation (high priority)

Do any of these need due dates or more details?"

TOOLS CALLED:
- create_task (3 times):
  1. {title: "Call Sarah", priority: "medium"}
  2. {title: "Buy groceries", priority: "low"}
  3. {title: "Finish the presentation", priority: "high"}

USER: "The presentation is due tomorrow and Sarah needs to be called today by 3pm"

AGENT REASONING:
- User adding due dates to previously created tasks
- From context: task_ids are known from memory
- Update 2 tasks with due dates

AGENT RESPONSE: "Updated both tasks:
- 'Call Sarah' - today by 3 PM
- 'Finish the presentation' - tomorrow

All set!"

TOOLS CALLED:
- update_task:
  {
    "task_id": "task_id_for_call_sarah",
    "due_date": "2024-01-16T15:00:00"
  }
- update_task:
  {
    "task_id": "task_id_for_presentation",
    "due_date": "2024-01-17"
  }
```

---

## Agent Decision Tree

Here's how the agent decides what to do:

```
USER MESSAGE
    ↓
INTENT CLASSIFICATION
    ├── "add/create/new" → create_task
    ├── "update/change/rename/reschedule" → update_task (or clarify which task)
    ├── "done/complete/finish/mark" → complete_task (or clarify which task)
    ├── "delete/remove" → delete_task (or clarify + confirm)
    ├── "show/list/what/how many" → list_tasks (with appropriate filters)
    ├── "tell me about/show me details" → get_task
    └── "unclear" → ASK ONE CLARIFICATION QUESTION
        ↓
PARAMETER EXTRACTION
    ├── From message text
    ├── From conversation memory (recent task references)
    └── Apply defaults (priority=medium, status=pending, etc.)
        ↓
VALIDATION
    ├── Have all required params?
    │   ├── Yes → CALL TOOL
    │   └── No → ASK FOR MISSING INFO
    └── Is task reference ambiguous?
        ├── Yes → ASK WHICH TASK
        └── No → CALL TOOL
            ↓
TOOL EXECUTION
    ↓
FORMAT RESPONSE (conversational, confirm action)
    ↓
UPDATE MEMORY (add to conversation context)
```

---

## Key Agent Behaviors to Note

1. **Concise Responses**: Responses are 1-2 sentences usually
2. **Confirmation**: Always confirm what was done
3. **Context Awareness**: Uses conversation memory to understand "that" and "it"
4. **Smart Defaults**: Infers priority and dates from context
5. **One Question at a Time**: If clarification needed, asks ONE question
6. **Natural Date Parsing**: "Tomorrow", "next Friday", "this week" all work
7. **Task Grouping**: Can create multiple tasks in one message
8. **Safety**: Confirms before deleting
9. **Helpful Suggestions**: Offers next steps when appropriate
10. **Error Handling**: Clear error messages without technical jargon

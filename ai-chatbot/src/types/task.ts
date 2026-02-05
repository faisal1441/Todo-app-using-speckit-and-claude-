/**
 * Task Type Definitions
 * Defines the structure of tasks as they are stored and managed in MCP
 */

export type TaskStatus = 'pending' | 'completed';
export type TaskPriority = 'low' | 'medium' | 'high';

/**
 * Core Task interface
 * Represents a single to-do item
 */
export interface Task {
  id: string;
  title: string;
  description?: string;
  due_date?: string; // ISO 8601 date string (YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss)
  priority: TaskPriority;
  status: TaskStatus;
  created_at: string; // ISO 8601 timestamp
  updated_at: string; // ISO 8601 timestamp
  user_id: string; // For multi-user support
  tags?: string[];
}

/**
 * Task creation payload (what the agent sends)
 */
export interface CreateTaskPayload {
  title: string;
  description?: string;
  due_date?: string;
  priority?: TaskPriority;
  tags?: string[];
}

/**
 * Task update payload (partial updates)
 */
export interface UpdateTaskPayload {
  title?: string;
  description?: string;
  due_date?: string;
  priority?: TaskPriority;
  status?: TaskStatus;
  tags?: string[];
}

/**
 * List tasks filter options
 */
export interface ListTasksFilter {
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string; // Filter by specific date
  range?: 'today' | 'upcoming' | 'overdue' | 'completed' | 'all';
  search?: string; // Search in title and description
}

/**
 * Conversation context for short-term memory
 */
export interface ConversationContext {
  user_id: string;
  session_id: string;
  message_history: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>;
  referenced_tasks: Map<string, Task>; // Recently mentioned tasks
  last_action: {
    type: string;
    task_id?: string;
    timestamp: string;
  } | null;
}

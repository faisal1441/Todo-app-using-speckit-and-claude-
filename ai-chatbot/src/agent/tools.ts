/**
 * Agent Tools
 * Defines the tools available to the TodoAgent for task management
 * Each tool is invoked by the agent to perform operations on tasks
 */

import { tool } from 'ai';
import { z } from 'zod';
import { MCPStorage } from '../mcp/storage.js';
import {
  CreateTaskPayloadSchema,
  UpdateTaskPayloadSchema,
  ListTasksFilterSchema,
} from '../mcp/schema.js';

/**
 * Tool factory function that creates all available tools
 * Takes MCPStorage instance for persistence
 */
export function createAgentTools(storage: MCPStorage) {
  return {
    /**
     * create_task: Add a new task
     * Agent calls this when user wants to add a task
     *
     * Example agent reasoning:
     * "User said 'Remind me to submit the report tomorrow evening'
     *  I need to extract:
     *  - title: 'Submit the report'
     *  - due_date: '2024-01-17T18:00:00'
     *  - priority: 'high' (implied by 'report' and specific time)
     *  Calling create_task..."
     */
    create_task: tool({
      description: 'Create a new task with title, optional description, due date, and priority',
      parameters: z.object({
        title: z.string().describe('Task title (required)'),
        description: z.string().optional().describe('Detailed task description'),
        due_date: z.string().optional().describe('Due date in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss)'),
        priority: z.enum(['low', 'medium', 'high']).optional().describe('Task priority'),
        tags: z.array(z.string()).optional().describe('Tags for organizing tasks'),
      }),
      execute: async (params, context: any) => {
        const userId = context?.userId || 'default-user';
        const payload = CreateTaskPayloadSchema.parse(params);

        try {
          const task = await storage.createTask(userId, payload);
          return {
            success: true,
            message: `Created task: "${task.title}"${task.due_date ? ` (due ${task.due_date})` : ''}`,
            task_id: task.id,
            task,
          };
        } catch (error) {
          return {
            success: false,
            error: `Failed to create task: ${(error as Error).message}`,
          };
        }
      },
    }),

    /**
     * update_task: Modify an existing task
     * Agent calls this when user wants to change task details
     *
     * Example agent reasoning:
     * "User said 'Change the report task to high priority'
     *  From context, I know task_id for the report task
     *  I need to update the priority field
     *  Calling update_task with those changes..."
     */
    update_task: tool({
      description: 'Update an existing task with new information',
      parameters: z.object({
        task_id: z.string().describe('ID of task to update'),
        title: z.string().optional().describe('New task title'),
        description: z.string().optional().describe('New task description'),
        due_date: z.string().optional().describe('New due date'),
        priority: z.enum(['low', 'medium', 'high']).optional().describe('New priority'),
        tags: z.array(z.string()).optional().describe('New tags'),
      }),
      execute: async (params, context: any) => {
        const { task_id, ...updates } = params;
        const payload = UpdateTaskPayloadSchema.parse(updates);

        try {
          const task = await storage.updateTask(task_id, payload);
          return {
            success: true,
            message: `Updated task: "${task.title}"`,
            task_id: task.id,
            task,
          };
        } catch (error) {
          return {
            success: false,
            error: `Failed to update task: ${(error as Error).message}`,
          };
        }
      },
    }),

    /**
     * complete_task: Mark a task as done
     * Agent calls this when user says task is complete
     *
     * Example agent reasoning:
     * "User said 'Mark the report as done'
     *  From recent conversation context, I know the report task_id
     *  Calling complete_task to set status to 'completed'..."
     */
    complete_task: tool({
      description: 'Mark a task as completed',
      parameters: z.object({
        task_id: z.string().describe('ID of task to complete'),
      }),
      execute: async (params, context: any) => {
        try {
          const task = await storage.completeTask(params.task_id);
          return {
            success: true,
            message: `Completed task: "${task.title}" ✓`,
            task_id: task.id,
            task,
          };
        } catch (error) {
          return {
            success: false,
            error: `Failed to complete task: ${(error as Error).message}`,
          };
        }
      },
    }),

    /**
     * delete_task: Remove a task permanently
     * Agent calls this when user wants to delete a task
     *
     * Example agent reasoning:
     * "User said 'Delete the old meeting task'
     *  I need to confirm with user or use context to identify which task
     *  Calling delete_task if confirmed..."
     */
    delete_task: tool({
      description: 'Delete a task permanently',
      parameters: z.object({
        task_id: z.string().describe('ID of task to delete'),
      }),
      execute: async (params, context: any) => {
        try {
          // Fetch task details before deletion for confirmation message
          const task = await storage.getTask(params.task_id);
          if (!task) {
            return {
              success: false,
              error: 'Task not found',
            };
          }

          await storage.deleteTask(params.task_id);
          return {
            success: true,
            message: `Deleted task: "${task.title}"`,
            task_id: params.task_id,
          };
        } catch (error) {
          return {
            success: false,
            error: `Failed to delete task: ${(error as Error).message}`,
          };
        }
      },
    }),

    /**
     * get_task: Retrieve a specific task by ID
     * Agent calls this to get details about a task
     *
     * Example agent reasoning:
     * "User mentioned 'the report task' but I need the full details
     *  From context I have task_id, fetching with get_task..."
     */
    get_task: tool({
      description: 'Get details of a specific task by ID',
      parameters: z.object({
        task_id: z.string().describe('ID of task to retrieve'),
      }),
      execute: async (params, context: any) => {
        try {
          const task = await storage.getTask(params.task_id);
          if (!task) {
            return {
              success: false,
              error: 'Task not found',
            };
          }

          return {
            success: true,
            task,
          };
        } catch (error) {
          return {
            success: false,
            error: `Failed to get task: ${(error as Error).message}`,
          };
        }
      },
    }),

    /**
     * list_tasks: Retrieve tasks with optional filtering
     * Agent calls this when user asks to view tasks
     *
     * Example agent reasoning:
     * "User asked 'What do I need to do today?'
     *  This is a list_tasks call with filter: { range: 'today' }
     *  I'll retrieve pending tasks due today..."
     */
    list_tasks: tool({
      description: 'List tasks with optional filtering by status, priority, date range, or search',
      parameters: z.object({
        range: z
          .enum(['today', 'upcoming', 'overdue', 'completed', 'all'])
          .optional()
          .describe('Filter by date range'),
        status: z.enum(['pending', 'completed']).optional().describe('Filter by status'),
        priority: z.enum(['low', 'medium', 'high']).optional().describe('Filter by priority'),
        search: z.string().optional().describe('Search in task titles and descriptions'),
      }),
      execute: async (params, context: any) => {
        const userId = context?.userId || 'default-user';
        const filter = ListTasksFilterSchema.parse(params);

        try {
          const tasks = await storage.listTasks(userId, filter);
          const stats = await storage.getTaskStats(userId);

          if (tasks.length === 0) {
            return {
              success: true,
              message: 'No tasks found matching your criteria',
              tasks: [],
              stats,
            };
          }

          return {
            success: true,
            message: `Found ${tasks.length} task(s)`,
            tasks,
            stats,
          };
        } catch (error) {
          return {
            success: false,
            error: `Failed to list tasks: ${(error as Error).message}`,
          };
        }
      },
    }),
  };
}

/**
 * Tool descriptions for the agent system prompt
 * These are referenced in the agent's instructions
 */
export const TOOL_DESCRIPTIONS = `
AVAILABLE TOOLS:
1. create_task(title, description?, due_date?, priority?, tags?) - Create a new task
2. update_task(task_id, fields) - Update existing task fields
3. complete_task(task_id) - Mark task as completed
4. delete_task(task_id) - Delete a task
5. get_task(task_id) - Get task details
6. list_tasks(range?, status?, priority?, search?) - List filtered tasks

Date format: ISO 8601 (YYYY-MM-DDTHH:mm:ss or YYYY-MM-DD)
Priorities: low, medium, high
`;

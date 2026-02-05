/**
 * MCP Resource Schema
 * Defines the structure and validation for task resources stored via MCP
 */

import { z } from 'zod';

/**
 * Zod schemas for runtime validation
 * These ensure type safety and validation of all task data
 */

export const TaskStatusSchema = z.enum(['pending', 'completed']);
export const TaskPrioritySchema = z.enum(['low', 'medium', 'high']);

export const TaskSchema = z.object({
  id: z.string().uuid().describe('Unique task identifier'),
  title: z.string().min(1).max(200).describe('Task title'),
  description: z.string().max(2000).optional().describe('Detailed task description'),
  due_date: z.string().optional().describe('ISO 8601 date/time when task is due'),
  priority: TaskPrioritySchema.default('medium').describe('Task priority level'),
  status: TaskStatusSchema.default('pending').describe('Current task status'),
  created_at: z.string().describe('ISO 8601 creation timestamp'),
  updated_at: z.string().describe('ISO 8601 last update timestamp'),
  user_id: z.string().describe('User who owns this task'),
  tags: z.array(z.string()).optional().describe('Tags for categorizing tasks'),
});

export const CreateTaskPayloadSchema = z.object({
  title: z.string().min(1).max(200).describe('Task title'),
  description: z.string().max(2000).optional(),
  due_date: z.string().optional(),
  priority: TaskPrioritySchema.optional(),
  tags: z.array(z.string()).optional(),
});

export const UpdateTaskPayloadSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  description: z.string().max(2000).optional(),
  due_date: z.string().optional(),
  priority: TaskPrioritySchema.optional(),
  status: TaskStatusSchema.optional(),
  tags: z.array(z.string()).optional(),
});

export const ListTasksFilterSchema = z.object({
  status: TaskStatusSchema.optional(),
  priority: TaskPrioritySchema.optional(),
  due_date: z.string().optional(),
  range: z.enum(['today', 'upcoming', 'overdue', 'completed', 'all']).optional(),
  search: z.string().optional(),
});

/**
 * MCP Resource URI scheme for tasks
 * Format: mcp://tasks/{userId}/{taskId}
 * This allows MCP to uniquely identify and manage each task resource
 */
export const MCPTaskResourceURI = (userId: string, taskId: string): string => {
  return `mcp://tasks/${userId}/${taskId}`;
};

/**
 * Resource metadata for MCP
 */
export const TaskResourceMetadata = {
  type: 'task',
  version: '1.0.0',
  description: 'To-Do task resource managed via MCP',
  schema: TaskSchema,
};

// Export types inferred from schemas
export type Task = z.infer<typeof TaskSchema>;
export type CreateTaskPayload = z.infer<typeof CreateTaskPayloadSchema>;
export type UpdateTaskPayload = z.infer<typeof UpdateTaskPayloadSchema>;
export type ListTasksFilter = z.infer<typeof ListTasksFilterSchema>;
export type TaskStatus = z.infer<typeof TaskStatusSchema>;
export type TaskPriority = z.infer<typeof TaskPrioritySchema>;

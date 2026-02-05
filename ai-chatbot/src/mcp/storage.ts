/**
 * MCP Storage Layer
 * Handles persistence and retrieval of tasks
 * In production, this would connect to actual MCP servers or databases
 */

import { randomUUID } from 'crypto';
import * as fs from 'fs/promises';
import * as path from 'path';
import {
  Task,
  CreateTaskPayload,
  UpdateTaskPayload,
  ListTasksFilter,
  TaskSchema,
} from './schema.js';

export class MCPStorage {
  private dataDir: string;
  private tasksMap: Map<string, Task> = new Map();

  constructor(dataDir: string = './data') {
    this.dataDir = dataDir;
  }

  /**
   * Initialize storage and load existing tasks
   */
  async initialize(): Promise<void> {
    try {
      await fs.mkdir(this.dataDir, { recursive: true });
      const files = await fs.readdir(this.dataDir);

      for (const file of files) {
        if (file.endsWith('.json')) {
          const content = await fs.readFile(path.join(this.dataDir, file), 'utf-8');
          const task = JSON.parse(content);
          const validated = TaskSchema.parse(task);
          this.tasksMap.set(validated.id, validated);
        }
      }
    } catch (error) {
      console.error('Failed to initialize storage:', error);
    }
  }

  /**
   * Create a new task
   * Returns the created task with generated ID and timestamps
   */
  async createTask(userId: string, payload: CreateTaskPayload): Promise<Task> {
    const now = new Date().toISOString();
    const task: Task = {
      id: randomUUID(),
      title: payload.title,
      description: payload.description,
      due_date: payload.due_date,
      priority: payload.priority || 'medium',
      status: 'pending',
      created_at: now,
      updated_at: now,
      user_id: userId,
      tags: payload.tags || [],
    };

    // Validate schema
    const validated = TaskSchema.parse(task);

    // Persist to storage
    await this.persistTask(validated);

    // Cache in memory
    this.tasksMap.set(validated.id, validated);

    return validated;
  }

  /**
   * Get a single task by ID
   */
  async getTask(taskId: string): Promise<Task | null> {
    return this.tasksMap.get(taskId) || null;
  }

  /**
   * Update an existing task
   */
  async updateTask(taskId: string, updates: UpdateTaskPayload): Promise<Task> {
    const existing = this.tasksMap.get(taskId);
    if (!existing) {
      throw new Error(`Task ${taskId} not found`);
    }

    const updated: Task = {
      ...existing,
      ...updates,
      updated_at: new Date().toISOString(),
    };

    // Validate schema
    const validated = TaskSchema.parse(updated);

    // Persist changes
    await this.persistTask(validated);

    // Update cache
    this.tasksMap.set(taskId, validated);

    return validated;
  }

  /**
   * Mark a task as completed
   */
  async completeTask(taskId: string): Promise<Task> {
    return this.updateTask(taskId, { status: 'completed' });
  }

  /**
   * Delete a task
   */
  async deleteTask(taskId: string): Promise<void> {
    if (!this.tasksMap.has(taskId)) {
      throw new Error(`Task ${taskId} not found`);
    }

    this.tasksMap.delete(taskId);

    // Delete from disk
    const filePath = path.join(this.dataDir, `${taskId}.json`);
    try {
      await fs.unlink(filePath);
    } catch (error) {
      console.error(`Failed to delete file ${filePath}:`, error);
    }
  }

  /**
   * List tasks with optional filtering
   */
  async listTasks(userId: string, filter: ListTasksFilter = {}): Promise<Task[]> {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    let results = Array.from(this.tasksMap.values()).filter(
      (task) => task.user_id === userId
    );

    // Apply filters
    if (filter.status) {
      results = results.filter((task) => task.status === filter.status);
    }

    if (filter.priority) {
      results = results.filter((task) => task.priority === filter.priority);
    }

    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      results = results.filter(
        (task) =>
          task.title.toLowerCase().includes(searchLower) ||
          task.description?.toLowerCase().includes(searchLower)
      );
    }

    // Apply date range filters
    if (filter.range) {
      results = results.filter((task) => {
        if (!task.due_date) return filter.range === 'all';

        const dueDate = new Date(task.due_date);
        const dueDay = new Date(dueDate.getFullYear(), dueDate.getMonth(), dueDate.getDate());

        switch (filter.range) {
          case 'today':
            return dueDay.getTime() === today.getTime() && task.status === 'pending';
          case 'upcoming':
            return dueDay.getTime() > today.getTime() && task.status === 'pending';
          case 'overdue':
            return dueDay.getTime() < today.getTime() && task.status === 'pending';
          case 'completed':
            return task.status === 'completed';
          case 'all':
            return true;
        }
      });
    }

    // Sort by due date and priority
    results.sort((a, b) => {
      if (a.due_date && b.due_date) {
        return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
      }
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });

    return results;
  }

  /**
   * Persist a task to disk (simulating MCP resource storage)
   */
  private async persistTask(task: Task): Promise<void> {
    const filePath = path.join(this.dataDir, `${task.id}.json`);
    try {
      await fs.writeFile(filePath, JSON.stringify(task, null, 2), 'utf-8');
    } catch (error) {
      console.error(`Failed to persist task ${task.id}:`, error);
      throw error;
    }
  }

  /**
   * Get statistics about user's tasks
   */
  async getTaskStats(userId: string): Promise<{
    total: number;
    pending: number;
    completed: number;
    overdue: number;
  }> {
    const tasks = await this.listTasks(userId, { range: 'all' });
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    const pending = tasks.filter((t) => t.status === 'pending');
    const overdue = pending.filter(
      (t) =>
        t.due_date &&
        new Date(t.due_date) < today
    );

    return {
      total: tasks.length,
      pending: pending.length,
      completed: tasks.filter((t) => t.status === 'completed').length,
      overdue: overdue.length,
    };
  }
}

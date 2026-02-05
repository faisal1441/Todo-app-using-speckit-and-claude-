/**
 * Conversation Memory System
 * Maintains short-term conversational context for task resolution
 */

import { Task } from '../mcp/schema.js';

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface TaskReference {
  task_id: string;
  task: Task;
  context: string; // How it was mentioned (e.g., "the report task", "task about meeting")
  mentioned_at: string;
}

/**
 * ConversationMemory tracks the context of a single conversation
 * allowing the agent to understand references to previously mentioned tasks
 */
export class ConversationMemory {
  private userId: string;
  private sessionId: string;
  private messages: ConversationMessage[] = [];
  private referencedTasks: Map<string, TaskReference> = new Map();
  private maxMessages: number = 50; // Keep last N messages

  constructor(userId: string, sessionId: string) {
    this.userId = userId;
    this.sessionId = sessionId;
  }

  /**
   * Add a message to the conversation history
   */
  addMessage(role: 'user' | 'assistant', content: string): void {
    const now = new Date().toISOString();
    this.messages.push({
      role,
      content,
      timestamp: now,
    });

    // Keep memory bounded
    if (this.messages.length > this.maxMessages) {
      this.messages = this.messages.slice(-this.maxMessages);
    }
  }

  /**
   * Track a task that was mentioned in conversation
   * This allows "the report task" or "that task" to be resolved
   */
  recordTaskReference(taskId: string, task: Task, context: string): void {
    this.referencedTasks.set(taskId, {
      task_id: taskId,
      task,
      context,
      mentioned_at: new Date().toISOString(),
    });
  }

  /**
   * Clear task references older than maxAge milliseconds
   */
  pruneOldReferences(maxAgeMs: number = 30 * 60 * 1000): void {
    const now = Date.now();
    const toDelete: string[] = [];

    for (const [taskId, ref] of this.referencedTasks) {
      if (now - new Date(ref.mentioned_at).getTime() > maxAgeMs) {
        toDelete.push(taskId);
      }
    }

    toDelete.forEach((id) => this.referencedTasks.delete(id));
  }

  /**
   * Get the most recently mentioned task
   */
  getLastMentionedTask(): TaskReference | null {
    let last: TaskReference | null = null;
    let lastTime = 0;

    for (const ref of this.referencedTasks.values()) {
      const time = new Date(ref.mentioned_at).getTime();
      if (time > lastTime) {
        lastTime = time;
        last = ref;
      }
    }

    return last;
  }

  /**
   * Find tasks matching a description (e.g., "the report")
   */
  findTasksByDescription(description: string): TaskReference[] {
    const descLower = description.toLowerCase();
    return Array.from(this.referencedTasks.values()).filter((ref) =>
      ref.context.toLowerCase().includes(descLower) ||
      ref.task.title.toLowerCase().includes(descLower) ||
      ref.task.description?.toLowerCase().includes(descLower)
    );
  }

  /**
   * Get conversation context as formatted string for agent prompt
   */
  getContextForAgent(): string {
    let context = '';

    // Add recent messages
    if (this.messages.length > 0) {
      context += 'Recent conversation:\n';
      const recentMessages = this.messages.slice(-10);
      for (const msg of recentMessages) {
        context += `${msg.role.toUpperCase()}: ${msg.content}\n`;
      }
    }

    // Add task references
    if (this.referencedTasks.size > 0) {
      context += '\nRecently mentioned tasks:\n';
      for (const ref of Array.from(this.referencedTasks.values()).slice(-5)) {
        context += `- "${ref.task.title}" (${ref.context})\n`;
      }
    }

    return context;
  }

  /**
   * Get memory statistics for debugging
   */
  getStats() {
    return {
      session_id: this.sessionId,
      user_id: this.userId,
      message_count: this.messages.length,
      referenced_tasks: this.referencedTasks.size,
    };
  }

  /**
   * Clear all memory (useful for session reset)
   */
  clear(): void {
    this.messages = [];
    this.referencedTasks.clear();
  }
}

/**
 * Session manager for multiple concurrent conversations
 */
export class ConversationSessionManager {
  private sessions: Map<string, ConversationMemory> = new Map();

  /**
   * Get or create a conversation session
   */
  getSession(userId: string, sessionId: string): ConversationMemory {
    const key = `${userId}:${sessionId}`;

    if (!this.sessions.has(key)) {
      this.sessions.set(key, new ConversationMemory(userId, sessionId));
    }

    return this.sessions.get(key)!;
  }

  /**
   * End a session and clean up
   */
  endSession(userId: string, sessionId: string): void {
    const key = `${userId}:${sessionId}`;
    this.sessions.delete(key);
  }

  /**
   * Clean up old sessions
   */
  cleanupOldSessions(maxAgeMs: number = 60 * 60 * 1000): void {
    // This would track session creation times and remove old ones
    // Simplified version for now
    if (this.sessions.size > 100) {
      // If we have too many sessions, start removing
      const keysToDelete = Array.from(this.sessions.keys()).slice(0, 50);
      keysToDelete.forEach((key) => this.sessions.delete(key));
    }
  }
}

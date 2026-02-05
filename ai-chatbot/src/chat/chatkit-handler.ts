/**
 * ChatKit Integration
 * Handles HTTP routes and message processing for the chat interface
 */

import { TodoAgent } from '../agent/todo-agent.js';
import { MCPStorage } from '../mcp/storage.js';
import { ConversationSessionManager } from '../agent/memory.js';

/**
 * ChatMessage format for API requests/responses
 */
export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatSession {
  session_id: string;
  user_id: string;
  created_at: string;
  messages: ChatMessage[];
}

export interface ChatResponse {
  session_id: string;
  message_id: string;
  role: 'assistant';
  content: string;
  timestamp: string;
  tool_calls?: Array<{
    tool: string;
    params: Record<string, unknown>;
  }>;
}

/**
 * ChatKit handler manages sessions and messages
 */
export class ChatKitHandler {
  private agent: TodoAgent;
  private storage: MCPStorage;
  private sessionManager: ConversationSessionManager;
  private sessions: Map<string, ChatSession> = new Map();

  constructor(agent: TodoAgent, storage: MCPStorage) {
    this.agent = agent;
    this.storage = storage;
    this.sessionManager = new ConversationSessionManager();
  }

  /**
   * Initialize or get a chat session
   */
  getOrCreateSession(userId: string, sessionId?: string): ChatSession {
    const sid = sessionId || this.generateSessionId();

    if (this.sessions.has(sid)) {
      return this.sessions.get(sid)!;
    }

    const session: ChatSession = {
      session_id: sid,
      user_id: userId,
      created_at: new Date().toISOString(),
      messages: [],
    };

    this.sessions.set(sid, session);
    return session;
  }

  /**
   * Send a message and get a response
   * This is the main chat endpoint
   */
  async sendMessage(
    userId: string,
    sessionId: string,
    userMessage: string
  ): Promise<ChatResponse> {
    // Get or create session
    const session = this.getOrCreateSession(userId, sessionId);

    // Get conversation memory
    const memory = this.sessionManager.getSession(userId, sessionId);

    // Add user message to session
    const userMsg: ChatMessage = {
      id: this.generateMessageId(),
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    session.messages.push(userMsg);

    // Process message with agent
    const agentResponse = await this.agent.processMessage({
      userId,
      sessionId,
      userMessage,
      memory,
    });

    // Add assistant message to session
    const messageId = this.generateMessageId();
    const assistantMsg: ChatMessage = {
      id: messageId,
      role: 'assistant',
      content: agentResponse.message,
      timestamp: new Date().toISOString(),
    };
    session.messages.push(assistantMsg);

    // Update task references in memory if tools were called
    for (const toolCall of agentResponse.tool_calls) {
      const result = toolCall.result as any;
      if (toolCall.tool === 'create_task' && result?.task) {
        const task = result.task;
        memory.recordTaskReference(task.id, task, userMessage);
      } else if (
        (toolCall.tool === 'complete_task' || toolCall.tool === 'update_task') &&
        result?.task
      ) {
        const task = result.task;
        memory.recordTaskReference(task.id, task, `Updated: ${task.title}`);
      } else if (toolCall.tool === 'list_tasks' && result?.tasks) {
        const tasks = result.tasks as any[];
        for (const task of tasks) {
          memory.recordTaskReference(task.id, task, task.title);
        }
      }
    }

    return {
      session_id: session.session_id,
      message_id: messageId,
      role: 'assistant',
      content: agentResponse.message,
      timestamp: new Date().toISOString(),
      tool_calls: agentResponse.tool_calls.map((tc) => ({
        tool: tc.tool,
        params: tc.params,
      })),
    };
  }

  /**
   * Get session history
   */
  getSessionHistory(sessionId: string): ChatMessage[] {
    const session = this.sessions.get(sessionId);
    return session?.messages || [];
  }

  /**
   * End a session
   */
  endSession(userId: string, sessionId: string): void {
    this.sessions.delete(sessionId);
    this.sessionManager.endSession(userId, sessionId);
  }

  /**
   * Get all sessions for a user
   */
  getUserSessions(userId: string): ChatSession[] {
    return Array.from(this.sessions.values()).filter((s) => s.user_id === userId);
  }

  /**
   * Generate a unique session ID
   */
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Generate a unique message ID
   */
  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get handler statistics
   */
  getStats() {
    return {
      active_sessions: this.sessions.size,
      agent_status: this.agent.getStatus(),
    };
  }
}

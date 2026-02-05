/**
 * Express Server Setup
 * REST API routes for chat interface
 */

import express, { Express, Request, Response } from 'express';
import { ChatKitHandler, ChatMessage, ChatResponse } from '../chat/chatkit-handler.js';

export interface APIRequest extends Request {
  userId?: string;
  sessionId?: string;
}

export function setupAPI(app: Express, chatHandler: ChatKitHandler): void {
  /**
   * Middleware to extract user info from headers
   * In production, this would validate JWT tokens
   */
  app.use((req: APIRequest, res, next) => {
    req.userId = req.headers['x-user-id'] as string || 'default-user';
    req.sessionId = req.headers['x-session-id'] as string;
    next();
  });

  /**
   * POST /chat/send
   * Send a message and get a response from TodoAgent
   */
  app.post('/chat/send', async (req: APIRequest, res: Response) => {
    try {
      const { message, session_id } = req.body;
      const userId = req.userId;

      if (!message) {
        return res.status(400).json({
          error: 'Message is required',
        });
      }

      if (!userId) {
        return res.status(401).json({
          error: 'User ID is required',
        });
      }

      const response = await chatHandler.sendMessage(
        userId,
        session_id || req.sessionId || '',
        message
      );

      res.json(response);
    } catch (error) {
      console.error('Chat error:', error);
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Internal server error',
      });
    }
  });

  /**
   * GET /chat/sessions/:sessionId
   * Get chat history for a session
   */
  app.get('/chat/sessions/:sessionId', (req: APIRequest, res: Response) => {
    try {
      const { sessionId } = req.params;
      const history = chatHandler.getSessionHistory(sessionId);

      res.json({
        session_id: sessionId,
        messages: history,
      });
    } catch (error) {
      console.error('Session history error:', error);
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Internal server error',
      });
    }
  });

  /**
   * POST /chat/sessions
   * Create a new chat session
   */
  app.post('/chat/sessions', (req: APIRequest, res: Response) => {
    try {
      const userId = req.userId;

      if (!userId) {
        return res.status(401).json({
          error: 'User ID is required',
        });
      }

      const session = chatHandler.getOrCreateSession(userId);

      res.status(201).json({
        session_id: session.session_id,
        user_id: session.user_id,
        created_at: session.created_at,
      });
    } catch (error) {
      console.error('Session creation error:', error);
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Internal server error',
      });
    }
  });

  /**
   * GET /chat/sessions
   * List all sessions for user
   */
  app.get('/chat/sessions', (req: APIRequest, res: Response) => {
    try {
      const userId = req.userId;

      if (!userId) {
        return res.status(401).json({
          error: 'User ID is required',
        });
      }

      const sessions = chatHandler.getUserSessions(userId);

      res.json({
        sessions: sessions.map((s) => ({
          session_id: s.session_id,
          created_at: s.created_at,
          message_count: s.messages.length,
        })),
      });
    } catch (error) {
      console.error('Sessions list error:', error);
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Internal server error',
      });
    }
  });

  /**
   * DELETE /chat/sessions/:sessionId
   * End a chat session
   */
  app.delete('/chat/sessions/:sessionId', (req: APIRequest, res: Response) => {
    try {
      const { sessionId } = req.params;
      const userId = req.userId;

      if (!userId) {
        return res.status(401).json({
          error: 'User ID is required',
        });
      }

      chatHandler.endSession(userId, sessionId);

      res.json({
        message: 'Session ended',
        session_id: sessionId,
      });
    } catch (error) {
      console.error('Session end error:', error);
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Internal server error',
      });
    }
  });

  /**
   * GET /health
   * Health check endpoint
   */
  app.get('/health', (req: Request, res: Response) => {
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      stats: chatHandler.getStats(),
    });
  });

  /**
   * GET /
   * API info endpoint
   */
  app.get('/', (req: Request, res: Response) => {
    res.json({
      name: 'AI Todo Chatbot API',
      version: '1.0.0',
      description: 'AI-powered task management chatbot using OpenAI Agent SDK and MCP',
      endpoints: {
        'POST /chat/send': 'Send a message to TodoAgent',
        'POST /chat/sessions': 'Create a new chat session',
        'GET /chat/sessions': 'List user sessions',
        'GET /chat/sessions/:sessionId': 'Get session history',
        'DELETE /chat/sessions/:sessionId': 'End a session',
        'GET /health': 'Health check',
      },
    });
  });
}

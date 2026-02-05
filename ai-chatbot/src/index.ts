/**
 * Main Entry Point
 * Initializes all components and starts the server
 */

import 'dotenv/config';
import express, { Express } from 'express';
import { MCPStorage } from './mcp/storage.js';
import { TodoAgent } from './agent/todo-agent.js';
import { ChatKitHandler } from './chat/chatkit-handler.js';
import { setupAPI } from './server/api.js';

const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';
const MCP_DATA_DIR = process.env.MCP_DATA_DIR || './data';

/**
 * Initialize and start the application
 */
async function main() {
  console.log('🤖 AI Todo Chatbot starting...');
  console.log(`Environment: ${NODE_ENV}`);
  console.log(`Data directory: ${MCP_DATA_DIR}`);

  // 1. Initialize MCP Storage
  console.log('📦 Initializing MCP storage...');
  const storage = new MCPStorage(MCP_DATA_DIR);
  await storage.initialize();
  console.log('✓ MCP storage ready');

  // 2. Initialize TodoAgent
  console.log('🧠 Initializing TodoAgent...');
  const agent = new TodoAgent(storage);
  console.log('✓ TodoAgent ready');

  // 3. Initialize ChatKit Handler
  console.log('💬 Initializing ChatKit handler...');
  const chatHandler = new ChatKitHandler(agent, storage);
  console.log('✓ ChatKit handler ready');

  // 4. Setup Express server
  console.log('🌐 Setting up Express API...');
  const app: Express = express();

  // Middleware
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // Request logging in development
  if (NODE_ENV === 'development') {
    app.use((req, res, next) => {
      console.log(`${req.method} ${req.path}`);
      next();
    });
  }

  // Setup API routes
  setupAPI(app, chatHandler);

  // 5. Start server
  app.listen(PORT, () => {
    console.log(`✓ Server running on http://localhost:${PORT}`);
    console.log(`\nAPI Documentation:`);
    console.log(`  GET  http://localhost:${PORT}/`);
    console.log(`  POST http://localhost:${PORT}/chat/send`);
    console.log(`\nExample request:`);
    console.log(`  curl -X POST http://localhost:${PORT}/chat/send \\`);
    console.log(`    -H "Content-Type: application/json" \\`);
    console.log(`    -H "X-User-ID: user123" \\`);
    console.log(`    -d '{"message": "Add a task to write documentation"}'`);
  });
}

// Error handling
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

// Run main
main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});

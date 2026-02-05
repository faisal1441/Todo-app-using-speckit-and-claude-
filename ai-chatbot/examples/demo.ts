/**
 * Demo Script
 * Example usage of the ChatBot without the HTTP server
 * Useful for testing and understanding the agent behavior
 *
 * Usage: npx ts-node examples/demo.ts
 */

import 'dotenv/config';
import { MCPStorage } from '../src/mcp/storage.js';
import { TodoAgent } from '../src/agent/todo-agent.js';
import { ConversationMemory } from '../src/agent/memory.js';

/**
 * Example conversation demonstrating various capabilities
 */
async function runDemo() {
  console.log('🤖 AI Todo Chatbot Demo\n');
  console.log('=' .repeat(60) + '\n');

  // Initialize components
  const storage = new MCPStorage('./demo-data');
  await storage.initialize();

  const agent = new TodoAgent(storage);
  const memory = new ConversationMemory('demo-user', 'demo-session');

  // Example messages that showcase agent capabilities
  const messages = [
    'Add a task to write documentation by tomorrow at 5pm',
    'Also need to review the design proposal next Monday - mark it as high priority',
    'What do I need to do today?',
    'Mark the documentation task as done',
    'Can you show me all my tasks?',
  ];

  console.log('Running example conversation...\n');

  for (const message of messages) {
    console.log('👤 USER: ' + message);
    console.log('');

    try {
      const response = await agent.processMessage({
        userId: 'demo-user',
        sessionId: 'demo-session',
        userMessage: message,
        memory,
      });

      console.log('🤖 AGENT: ' + response.message);

      if (response.tool_calls.length > 0) {
        console.log('\n📋 Tools Called:');
        for (const call of response.tool_calls) {
          console.log(`   - ${call.tool}(${JSON.stringify(call.params)})`);
        }
      }
    } catch (error) {
      console.error('❌ Error:', error instanceof Error ? error.message : error);
    }

    console.log('\n' + '-'.repeat(60) + '\n');
  }

  // Show conversation memory
  console.log('📝 Conversation Memory:');
  console.log(memory.getStats());
  console.log('\nRecent context:');
  console.log(memory.getContextForAgent());
}

// Run the demo
runDemo().catch((error) => {
  console.error('Demo failed:', error);
  process.exit(1);
});

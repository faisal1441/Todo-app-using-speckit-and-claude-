/**
 * TodoAgent - Main AI Agent
 * Handles task management through natural language conversation
 *
 * Architecture:
 * 1. Receives user message
 * 2. Builds context from conversation memory
 * 3. Calls OpenAI with system prompt and tools
 * 4. Processes tool calls and gathers results
 * 5. Returns conversational response
 */

import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { MCPStorage } from '../mcp/storage.js';
import { createAgentTools } from './tools.js';
import { ConversationMemory } from './memory.js';

const SYSTEM_PROMPT = `You are TodoAgent, a helpful and intelligent task management assistant.

PERSONALITY & BEHAVIOR:
- You are concise, friendly, and conversational
- You help users manage their tasks through natural language
- You ask clarification questions when intent is ambiguous (but only ONE question at a time)
- You provide confirmation messages after actions
- You proactively suggest task details when user input is vague

CORE RESPONSIBILITIES:
1. Extract task information from natural language:
   - Identify task title, due date, priority, and description
   - Infer priority from context (e.g., "ASAP" = high, "when you get a chance" = low)
   - Parse dates flexibly ("tomorrow", "next Monday", "2024-01-20", etc.)

2. Resolve task references in conversation:
   - When user says "that task" or "the report", use conversation memory to identify it
   - If ambiguous, ask which task they mean (never assume)

3. Maintain conversation context:
   - Remember recently mentioned tasks
   - Use context to make intelligent tool calls
   - Track the last action for reference in follow-ups

4. Handle different user intents:
   - "Add/Create" → create_task
   - "Update/Change/Rename" → update_task
   - "Done/Complete/Finish" → complete_task
   - "Remove/Delete" → delete_task
   - "Show/List/What are" → list_tasks
   - "Show details/What is" → get_task

RESPONSE GUIDELINES:
- Keep responses under 2 sentences unless explaining something complex
- Always confirm what action was taken
- Use emoji sparingly and only when appropriate (✓ for completion, ⚠️ for warnings)
- Format task lists clearly with checkboxes and due dates
- If no tasks found, be encouraging

CLARIFICATION STRATEGY:
- Ask ONE clarification question maximum
- Ask specifics (e.g., "Which task?" not "What do you mean?")
- Continue without answers if context is sufficient

DATE HANDLING:
- Today: current date
- Tomorrow: tomorrow's date
- "This week": within next 7 days
- "Next week": 7-14 days from now
- "Next [day name]": next occurrence of that day
- Specific dates: use as provided
- If time not specified: assume end of business day (5 PM)

PRIORITY INFERENCE:
- High: urgent, ASAP, deadline approaching, important
- Medium: normal, regular work (default)
- Low: when possible, eventually, low priority

IMPORTANT CONSTRAINTS:
- NEVER create multiple tasks from a single message unless explicitly requested
- NEVER assume personal information or make tasks for others
- NEVER use tools speculatively - only call tools when confident about parameters
- ALWAYS validate task_id when updating/completing/deleting before calling tool
- If task_id is needed but unknown, ask user to clarify which task

TOOL USAGE PATTERN:
1. Analyze user intent
2. Extract parameters from message + context
3. Validate you have required parameters
4. Call appropriate tool(s)
5. Process results
6. Respond conversationally

Remember: You're an assistant, not just a command executor. Make the experience natural and helpful.`;

export interface AgentContext {
  userId: string;
  sessionId: string;
  userMessage: string;
  memory: ConversationMemory;
}

export interface AgentResponse {
  message: string;
  tool_calls: Array<{
    tool: string;
    params: Record<string, unknown>;
    result: unknown;
  }>;
  thinking?: string; // Reasoning before tool calls
}

export class TodoAgent {
  private storage: MCPStorage;
  private tools: ReturnType<typeof createAgentTools>;
  private model = 'gpt-4-turbo'; // or gpt-3.5-turbo for faster, cheaper responses

  constructor(storage: MCPStorage) {
    this.storage = storage;
    this.tools = createAgentTools(storage);
  }

  /**
   * Process a user message and generate a response
   * This is the main entry point for the agent
   */
  async processMessage(context: AgentContext): Promise<AgentResponse> {
    // Add user message to memory
    context.memory.addMessage('user', context.userMessage);

    // Build the conversation context for the agent
    const conversationContext = context.memory.getContextForAgent();

    try {
      // Call OpenAI with tools
      const { text, toolResults } = await generateText({
        model: openai(this.model),
        system: SYSTEM_PROMPT,
        tools: {
          create_task: this.tools.create_task,
          update_task: this.tools.update_task,
          complete_task: this.tools.complete_task,
          delete_task: this.tools.delete_task,
          get_task: this.tools.get_task,
          list_tasks: this.tools.list_tasks,
        },
        messages: [
          {
            role: 'user',
            content: `Context from conversation:\n${conversationContext}\n\nUser message: ${context.userMessage}`,
          },
        ],
        maxSteps: 5, // Prevent infinite loops
      });

      // Add assistant response to memory
      context.memory.addMessage('assistant', text);

      // Extract tool calls for response
      const toolCalls = toolResults?.map((result) => ({
        tool: result.toolName,
        params: result.args as Record<string, unknown>,
        result: result.result,
      })) || [];

      return {
        message: text,
        tool_calls: toolCalls,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      const response = `I encountered an error processing your request: ${errorMessage}`;

      context.memory.addMessage('assistant', response);

      return {
        message: response,
        tool_calls: [],
      };
    }
  }

  /**
   * Batch process multiple messages in sequence
   * Useful for testing or scripts
   */
  async processMessages(
    userId: string,
    sessionId: string,
    messages: string[],
    memory: ConversationMemory
  ): Promise<AgentResponse[]> {
    const responses: AgentResponse[] = [];

    for (const message of messages) {
      const response = await this.processMessage({
        userId,
        sessionId,
        userMessage: message,
        memory,
      });
      responses.push(response);
    }

    return responses;
  }

  /**
   * Health check and debugging
   */
  getStatus() {
    return {
      status: 'ready',
      model: this.model,
      system_prompt_size: SYSTEM_PROMPT.length,
    };
  }
}

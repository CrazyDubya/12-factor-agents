#!/usr/bin/env node

import { startCLI } from './cli';

/**
 * 12-Factor Agents Ollama Demo
 * 
 * This demo showcases the 12-factor agent principles:
 * 
 * Factor 1: Natural Language to Tool Calls
 * Factor 2: Own your prompts (in BAML files)
 * Factor 3: Own your context window (XML formatting)
 * Factor 4: Tools are just structured outputs
 * Factor 5: Unify execution state and business state
 * Factor 6: Launch/Pause/Resume with simple APIs
 * Factor 7: Contact humans with tool calls
 * Factor 8: Own your control flow
 * Factor 9: Compact Errors into Context Window
 * Factor 10: Small, Focused Agents
 * Factor 11: Trigger from anywhere, meet users where they are
 * Factor 12: Make your agent a stateless reducer
 */

async function main() {
  try {
    // Set default environment variables if not provided
    if (!process.env.OLLAMA_BASE_URL) {
      process.env.OLLAMA_BASE_URL = 'http://localhost:11434';
    }
    
    if (!process.env.SELECTED_MODEL) {
      process.env.SELECTED_MODEL = 'llama3.1:8b';
    }

    const args = process.argv.slice(2);
    await startCLI(args);
  } catch (error) {
    console.error('Fatal error:', error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Goodbye!');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n👋 Goodbye!');
  process.exit(0);
});

if (require.main === module) {
  main();
}
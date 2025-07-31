#!/usr/bin/env node

import { AgentServer } from './server';

async function main() {
  try {
    // Set default environment variables if not provided
    if (!process.env.OLLAMA_BASE_URL) {
      process.env.OLLAMA_BASE_URL = 'http://localhost:11434';
    }
    
    if (!process.env.SELECTED_MODEL) {
      process.env.SELECTED_MODEL = 'llama3.1:8b';
    }

    const port = parseInt(process.env.PORT || '3000');
    const server = new AgentServer();
    
    console.log('🚀 Starting 12-Factor Agents Ollama Demo Server...');
    console.log('');
    
    server.start(port);
  } catch (error) {
    console.error('Fatal error:', error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Server shutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n👋 Server shutting down gracefully...');
  process.exit(0);
});

if (require.main === module) {
  main();
}
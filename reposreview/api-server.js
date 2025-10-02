#!/usr/bin/env node

/**
 * API Server for Repository Dashboard V5
 * Provides REST API for GitHub CLI and Cloudflare Wrangler operations
 */

const express = require('express');
const cors = require('cors');

// Import route modules
const githubRoutes = require('./routes/github');
const cloudflareRoutes = require('./routes/cloudflare');
const combinedRoutes = require('./routes/combined');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Logging middleware
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

// Health check
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Mount route modules
app.use('/api/github', githubRoutes);
app.use('/api/cloudflare', cloudflareRoutes);
app.use('/api/combined', combinedRoutes);

// Error handling
app.use((err, _req, res, _next) => {
  console.error('Server error:', err);
  res.status(500).json({
    success: false,
    error: 'Internal server error',
    message: err.message
  });
});

app.listen(PORT, () => {
  console.log(`\n🚀 API Server running on http://localhost:${PORT}`);
  console.log('\nAvailable endpoints:');
  console.log('  GET  /health');
  console.log('\n  📦 GitHub Repositories:');
  console.log('  GET  /api/github/repos');
  console.log('  GET  /api/github/repo/:owner/:name');
  console.log('  POST /api/github/repo/create');
  console.log('  POST /api/github/repo/clone');
  console.log('\n  🐛 GitHub Issues:');
  console.log('  GET  /api/github/issue/list');
  console.log('  GET  /api/github/issue/view/:number');
  console.log('  POST /api/github/issue/create');
  console.log('  POST /api/github/issue/close');
  console.log('  POST /api/github/issue/comment');
  console.log('\n  🔀 GitHub Pull Requests:');
  console.log('  GET  /api/github/pr/list');
  console.log('  POST /api/github/pr/create');
  console.log('  POST /api/github/pr/merge');
  console.log('  GET  /api/github/pr/checks/:number');
  console.log('\n  ☁️  Cloudflare Pages:');
  console.log('  GET  /api/cloudflare/projects');
  console.log('  POST /api/cloudflare/project/create');
  console.log('  POST /api/cloudflare/deploy');
  console.log('\n  🐳 Cloudflare Containers:');
  console.log('  POST /api/cloudflare/container/deploy');
  console.log('  GET  /api/cloudflare/container/list');
  console.log('\n  🔗 Combined Operations:');
  console.log('  POST /api/combined/clone-and-deploy');
  console.log('\n✨ Ready to handle GitHub + Cloudflare operations!\n');
});

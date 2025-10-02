#!/bin/bash

# Repository Dashboard V5 - Complete Startup Script
# Starts API server + Static server + Opens browser

echo "🚀 Starting Repository Dashboard V5..."
echo ""

# Kill existing servers on ports 3000 and 8899
echo "🧹 Cleaning up existing servers..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8899 | xargs kill -9 2>/dev/null || true

# Check dependencies
echo "📦 Checking dependencies..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js first."
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI (gh) not found. GitHub features will not work."
    echo "   Install with: brew install gh"
fi

if ! command -v wrangler &> /dev/null; then
    echo "⚠️  Cloudflare Wrangler not found. Cloudflare features will not work."
    echo "   Install with: npm install -g wrangler"
fi

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📥 Installing Node.js dependencies..."
    npm install
fi

# Start API server in background
echo "🔧 Starting API server on port 3000..."
node api-server.js > /tmp/api-server.log 2>&1 &
API_PID=$!
echo "   PID: $API_PID"

# Wait for API server to start
sleep 2

# Check if API server is running
if ! lsof -ti:3000 > /dev/null; then
    echo "❌ API server failed to start. Check /tmp/api-server.log for errors."
    exit 1
fi

echo "✅ API server running at http://localhost:3000"

# Start static file server in background
echo "🌐 Starting static server on port 8899..."
python3 -m http.server 8899 > /tmp/static-server.log 2>&1 &
STATIC_PID=$!
echo "   PID: $STATIC_PID"

# Wait for static server to start
sleep 2

# Check if static server is running
if ! lsof -ti:8899 > /dev/null; then
    echo "❌ Static server failed to start."
    kill $API_PID 2>/dev/null
    exit 1
fi

echo "✅ Static server running at http://localhost:8899"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Dashboard V5 is ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Dashboard:  http://localhost:8899/dashboard-v5.html"
echo "🔧 API Server: http://localhost:3000/health"
echo ""
echo "Server PIDs:"
echo "  API Server:    $API_PID"
echo "  Static Server: $STATIC_PID"
echo ""
echo "Logs:"
echo "  API:    tail -f /tmp/api-server.log"
echo "  Static: tail -f /tmp/static-server.log"
echo ""
echo "To stop servers:"
echo "  kill $API_PID $STATIC_PID"
echo "  or press Ctrl+C"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Open browser
echo "🌐 Opening dashboard in browser..."
sleep 1

if command -v open &> /dev/null; then
    # macOS
    open http://localhost:8899/dashboard-v5.html
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open http://localhost:8899/dashboard-v5.html
else
    echo "   Please open http://localhost:8899/dashboard-v5.html manually"
fi

echo ""
echo "✨ Features enabled:"
echo "  ⚡ Re-Analyze (requires Ollama with expanded models)"
echo "  ☁️  Deploy to Cloudflare Pages"
echo "  📥 Load repos from GitHub CLI"
echo "  ➕ Create new GitHub repositories"
echo "  📋 View Cloudflare projects"
echo ""
echo "Press Ctrl+C to stop all servers..."

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Shutting down servers...'; kill $API_PID $STATIC_PID 2>/dev/null; echo '✅ Servers stopped'; exit 0" SIGINT SIGTERM

# Keep script running
wait

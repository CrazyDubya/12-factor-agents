#!/bin/bash

# Start local HTTP server and open enhanced dashboard

PORT=8080
URL="http://localhost:${PORT}/dashboard-v3.html"

echo ""
echo "🎯 ONE DASHBOARD. ONE TRUTH. (v3 + v4 Integration)"

# Kill any existing server on the port
lsof -ti:${PORT} | xargs kill -9 2>/dev/null

# Start Python HTTP server in background
echo "🚀 Starting HTTP server on port ${PORT}..."
python3 -m http.server ${PORT} > /dev/null 2>&1 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 1

# Open in default browser
echo "📊 Opening enhanced dashboard at ${URL}..."
if command -v open &> /dev/null; then
    open "${URL}"
elif command -v xdg-open &> /dev/null; then
    xdg-open "${URL}"
else
    echo "Please open manually: ${URL}"
fi

echo ""
echo "✅ Server running (PID: ${SERVER_PID})"
echo "📊 Dashboard URL: ${URL}"
echo ""
echo "✨ UNIFIED DASHBOARD FEATURES:"
echo ""
echo "   🌐 COMPLETE PORTFOLIO (199 repositories):"
echo "   • 📊 13 main categories with AI-powered classification"
echo "   • ⭐ Quality ratings (Excellent: 110, Good: 52, Fair: 29, Poor: 8)"
echo "   • 🔍 Deep search (README content + fuzzy matching)"
echo "   • 📈 Activity tracking & complexity analysis"
echo ""
echo "   🤖 AI/ML DEEP DIVE (80 repositories):"
echo "   • 9 specialized sub-categories (LLM, Agents, RAG, Vision, etc.)"
echo "   • 🔧 Framework detection (OpenAI: 34, Anthropic: 21, HuggingFace: 14)"
echo "   • 📚 Model type analysis (Transformer: 30, CNN, RNN, etc.)"
echo "   • 🚀 53 deployment-ready, 46 research-oriented, 14 with pre-trained models"
echo "   • 💡 Click AI/ML category to drill down into sub-categories!"
echo ""
echo "   🔬 v4 DEEP DIVE INTEGRATION (NEW!):"
echo "   • Click '🔬 Deep Dive' on any repository for AI-powered analysis"
echo "   • Ollama-powered README generation, code analysis, security scans"
echo "   • Chat interface with repository context"
echo "   • Persistent storage in IndexedDB"
echo "   • Multi-turn analysis workflows"
echo ""
echo "   🎯 ONE SOURCE OF TRUTH - All data unified in single dashboard"
echo ""
echo "💡 TIP: Click '🔬 Deep Dive' on any repo to use v4 AI features"
echo ""
echo "Press Ctrl+C to stop the server"

# Wait for Ctrl+C
trap "kill ${SERVER_PID} 2>/dev/null; echo ''; echo '🛑 Server stopped.'; exit 0" INT
wait ${SERVER_PID}
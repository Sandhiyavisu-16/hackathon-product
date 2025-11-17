#!/bin/bash

# Start All Services Script

echo "🚀 Starting Innovation Idea Submission Platform..."

# Start LiteLLM Service
echo "📦 Starting LiteLLM Service..."
cd litellm_service
python main.py &
LITELLM_PID=$!
cd ..

# Wait for LiteLLM to start
sleep 3

# Start Node.js Backend
echo "🟢 Starting Node.js Backend..."
npm run dev &
NODE_PID=$!

echo "✅ All services started!"
echo "   - LiteLLM Service: http://localhost:8001"
echo "   - Node.js Backend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "echo '🛑 Stopping services...'; kill $LITELLM_PID $NODE_PID; exit" INT
wait

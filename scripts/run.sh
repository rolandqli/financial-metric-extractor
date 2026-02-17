#!/bin/bash

# Run from project root (script lives in scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT" || exit 1

# Ensure logs directory exists
mkdir -p logs

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Earnings PDF Processor${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM

# Check if backend .env exists and has API key
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}✗ backend/.env file not found${NC}"
    echo -e "${YELLOW}Run './scripts/install.sh' first to set up the project${NC}"
    exit 1
fi

# Check if OPENAI_API_KEY is set (not the example value)
if grep -q "your-openai-api-key-here" backend/.env 2>/dev/null; then
    echo -e "${RED}✗ Please set your OPENAI_API_KEY in backend/.env${NC}"
    echo -e "${YELLOW}Edit backend/.env and replace 'your-openai-api-key-here' with your actual API key${NC}"
    exit 1
fi

# Check if frontend-next node_modules exists
if [ ! -d "frontend-next/node_modules" ]; then
    echo -e "${RED}✗ Frontend dependencies not installed${NC}"
    echo -e "${YELLOW}Run './scripts/install.sh' first to set up the project${NC}"
    exit 1
fi

echo -e "${YELLOW}Starting backend server...${NC}"
echo -e "${YELLOW}(Backend may take 15–30 seconds to start while loading the AI model.)${NC}"
cd backend || exit 1
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > "$ROOT/logs/backend.log" 2>&1 &
BACKEND_PID=$!
cd "$ROOT" || exit 1

# Wait for backend to actually respond (handles slow spaCy/model loading)
echo -n "Waiting for backend to be ready"
for i in {1..60}; do
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health 2>/dev/null | grep -q 200; then
        echo ""
        echo -e "${GREEN}✓ Backend running on http://localhost:8000 (PID: $BACKEND_PID)${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo ""
        echo -e "${RED}✗ Backend failed to start. Check logs/backend.log for errors${NC}"
        exit 1
    fi
    if [ $i -eq 60 ]; then
        echo ""
        echo -e "${RED}✗ Backend did not become ready in time. Check logs/backend.log${NC}"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
done

echo ""
echo -e "${YELLOW}Starting frontend (Next.js) server...${NC}"
cd frontend-next || exit 1
npm run dev > "$ROOT/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
cd "$ROOT" || exit 1

# Wait a moment for frontend to start (Next.js on port 3000)
sleep 3

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}✗ Frontend failed to start. Check logs/frontend.log for errors${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Frontend running on http://localhost:3000 (PID: $FRONTEND_PID)${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Application is running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Backend API:  ${BLUE}http://localhost:8000${NC}"
echo -e "Frontend App: ${BLUE}http://localhost:3000${NC}"
echo -e "Logs:         ${BLUE}logs/backend.log${NC}, ${BLUE}logs/frontend.log${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Wait for processes
wait

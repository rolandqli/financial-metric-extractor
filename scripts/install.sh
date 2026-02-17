#!/bin/bash

# Run from project root (script lives in scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT" || exit 1

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Earnings PDF Processor - Installer${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check for required tools
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed. Please install Python 3.10+ first.${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js ${NODE_VERSION} found${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm is not installed. Please install npm first.${NC}"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ npm ${NPM_VERSION} found${NC}"

echo ""
echo -e "${YELLOW}Installing backend dependencies...${NC}"
cd backend || exit 1

# Use pip3 if pip is not available
if command -v pip &> /dev/null; then
    PIP=pip
elif command -v pip3 &> /dev/null; then
    PIP=pip3
else
    echo -e "${RED}✗ Neither pip nor pip3 found. Please install pip for Python 3.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Using $PIP${NC}"

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    $PIP install --upgrade pip
    $PIP install -r requirements.txt
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi

# Download spaCy model
echo ""
echo -e "${YELLOW}Downloading spaCy English model...${NC}"
python3 -m spacy download en_core_web_sm
echo -e "${GREEN}✓ spaCy model downloaded${NC}"

# Setup .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo -e "${YELLOW}Creating backend .env file...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file from .env.example${NC}"
        echo -e "${YELLOW}⚠ Please edit backend/.env and add your OPENAI_API_KEY${NC}"
    else
        echo -e "${YELLOW}⚠ .env.example not found. Creating basic .env file...${NC}"
        echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
        echo -e "${YELLOW}⚠ Please edit backend/.env and add your OPENAI_API_KEY${NC}"
    fi
else
    echo -e "${GREEN}✓ Backend .env file already exists${NC}"
fi

cd "$ROOT" || exit 1

echo ""
echo -e "${YELLOW}Installing frontend (Next.js) dependencies...${NC}"
cd frontend-next || exit 1

# Install Node dependencies
if [ -f "package.json" ]; then
    npm install
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${RED}✗ package.json not found${NC}"
    exit 1
fi

# Setup .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo -e "${YELLOW}Creating frontend-next .env file...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file from .env.example${NC}"
    else
        echo -e "${YELLOW}⚠ .env.example not found. Creating basic .env file...${NC}"
        echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env
    fi
else
    echo -e "${GREEN}✓ Frontend .env file already exists${NC}"
fi

cd "$ROOT" || exit 1

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit backend/.env and add your OPENAI_API_KEY"
echo "2. (Optional) Edit frontend-next/.env if you need a different API URL"
echo "3. Run './scripts/run.sh' to start the application"
echo ""

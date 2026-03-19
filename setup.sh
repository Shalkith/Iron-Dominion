#!/bin/bash
# War Game Setup Script for Unix/Linux/Mac
# This script provides a simple way to set up and run the game

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "============================================"
echo "          WAR GAME SETUP"
echo "============================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python is not installed${NC}"
    echo "Please install Python 3.9+ from https://python.org"
    exit 1
fi

# Check if Node is available
if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js is not installed${NC}"
    echo "Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

echo -e "${BLUE}Prerequisites check passed!${NC}"
echo ""

# Run the Python setup script
python3 setup.py "$@"

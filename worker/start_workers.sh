#!/bin/bash
# Start Temporal Workers Script
#
# Usage:
#   ./worker/start_workers.sh all      # Start all workers
#   ./worker/start_workers.sh default  # Start default worker only
#   ./worker/start_workers.sh ml       # Start ML worker only
#   ./worker/start_workers.sh openai   # Start OpenAI worker only

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if Temporal server is running
check_temporal() {
    echo -e "${YELLOW}Checking Temporal server...${NC}"
    if ! curl -s http://localhost:7233 > /dev/null 2>&1; then
        echo -e "${RED}Error: Temporal server not accessible at localhost:7233${NC}"
        echo "Please start Temporal server first:"
        echo "  docker compose -f docker-compose.temporal.yml up -d"
        exit 1
    fi
    echo -e "${GREEN}✓ Temporal server is running${NC}"
}

# Function to start default worker
start_default() {
    echo -e "${GREEN}Starting Default Worker (default-queue)...${NC}"
    python worker/default_worker.py
}

# Function to start ML worker
start_ml() {
    echo -e "${GREEN}Starting ML Worker (ml-queue)...${NC}"
    echo -e "${YELLOW}Note: Requires torch, transformers, peft, trl${NC}"
    python worker/ml_worker.py
}

# Function to start OpenAI worker
start_openai() {
    echo -e "${GREEN}Starting OpenAI Worker (openai-queue)...${NC}"
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${YELLOW}Warning: OPENAI_API_KEY not set${NC}"
        echo "Set it with: export OPENAI_API_KEY='your-key-here'"
    fi
    python worker/openai_worker.py
}

# Function to start all workers in background
start_all() {
    echo -e "${GREEN}Starting all Temporal workers...${NC}"

    # Start default worker
    echo -e "${YELLOW}Starting Default Worker in background...${NC}"
    python worker/default_worker.py &
    DEFAULT_PID=$!
    echo "Default Worker PID: $DEFAULT_PID"

    # Start ML worker
    echo -e "${YELLOW}Starting ML Worker in background...${NC}"
    python worker/ml_worker.py &
    ML_PID=$!
    echo "ML Worker PID: $ML_PID"

    # Start OpenAI worker
    echo -e "${YELLOW}Starting OpenAI Worker in background...${NC}"
    python worker/openai_worker.py &
    OPENAI_PID=$!
    echo "OpenAI Worker PID: $OPENAI_PID"

    echo ""
    echo -e "${GREEN}All workers started!${NC}"
    echo "To stop all workers:"
    echo "  kill $DEFAULT_PID $ML_PID $OPENAI_PID"
    echo ""
    echo "Monitoring Temporal UI: http://localhost:8233"

    # Wait for all background processes
    wait
}

# Main script
check_temporal

case "${1:-all}" in
    all)
        start_all
        ;;
    default)
        start_default
        ;;
    ml)
        start_ml
        ;;
    openai)
        start_openai
        ;;
    *)
        echo "Usage: $0 {all|default|ml|openai}"
        echo ""
        echo "Examples:"
        echo "  $0 all      # Start all workers"
        echo "  $0 default  # Start default worker only"
        echo "  $0 ml       # Start ML worker only"
        echo "  $0 openai   # Start OpenAI worker only"
        exit 1
        ;;
esac

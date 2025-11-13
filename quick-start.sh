#!/bin/bash
# Quick Start Script for Z-GPT
# This script helps you set up and run Z-GPT quickly

set -e

echo "================================"
echo "  Z-GPT Quick Start Setup"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
check_docker() {
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}✓${NC} Docker and Docker Compose are installed"
        return 0
    else
        echo -e "${RED}✗${NC} Docker or Docker Compose not found"
        echo "Please install Docker and Docker Compose first:"
        echo "  https://docs.docker.com/get-docker/"
        return 1
    fi
}

# Check if .env exists
check_env() {
    if [ -f .env ]; then
        echo -e "${GREEN}✓${NC} .env file exists"
        return 0
    else
        echo -e "${YELLOW}!${NC} .env file not found"
        if [ -f .env.example ]; then
            echo "Creating .env from .env.example..."
            cp .env.example .env
            echo -e "${YELLOW}!${NC} Please edit .env and add your Hugging Face API token"
            echo ""
            echo "Get your token from: https://huggingface.co/settings/tokens"
            echo ""
            read -p "Press Enter after you've updated the .env file..."
            return 0
        else
            echo -e "${RED}✗${NC} .env.example not found"
            return 1
        fi
    fi
}

# Start services
start_services() {
    echo ""
    echo "Starting Z-GPT services..."
    echo ""
    
    # Pull latest images (if available)
    docker-compose pull || true
    
    # Build and start services
    docker-compose up -d --build
    
    echo ""
    echo -e "${GREEN}✓${NC} Services started successfully!"
    echo ""
}

# Show status
show_status() {
    echo "Checking service status..."
    echo ""
    docker-compose ps
    echo ""
}

# Show URLs
show_urls() {
    echo "================================"
    echo "  Z-GPT is now running!"
    echo "================================"
    echo ""
    echo "Frontend:  http://localhost:3000"
    echo "Backend:   http://localhost:8000"
    echo "API Docs:  http://localhost:8000/docs"
    echo ""
    echo "Logs: docker-compose logs -f"
    echo "Stop: docker-compose down"
    echo ""
}

# Main execution
main() {
    echo "Checking prerequisites..."
    echo ""
    
    # Check Docker
    if ! check_docker; then
        exit 1
    fi
    
    # Check .env
    if ! check_env; then
        exit 1
    fi
    
    # Start services
    start_services
    
    # Wait a bit for services to start
    echo "Waiting for services to initialize..."
    sleep 5
    
    # Show status
    show_status
    
    # Show URLs
    show_urls
    
    # Offer to show logs
    read -p "Would you like to view the logs? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose logs -f
    fi
}

# Run main function
main

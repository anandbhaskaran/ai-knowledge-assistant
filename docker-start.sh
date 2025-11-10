#!/bin/bash

# AI Knowledge Assistant - Docker Startup Script
set -e

echo "=========================================="
echo "AI Knowledge Assistant - Docker Setup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create a .env file with your API keys."
    echo ""
    echo "Required variables:"
    echo "  OPENAI_API_KEY=your-key"
    echo "  TAVILY_API_KEY=your-key"
    exit 1
fi

# Check for required API keys
if ! grep -q "OPENAI_API_KEY=" .env || ! grep -q "TAVILY_API_KEY=" .env; then
    echo "Warning: Make sure your .env file contains:"
    echo "  - OPENAI_API_KEY"
    echo "  - TAVILY_API_KEY"
    echo ""
fi

echo "Starting services..."
echo ""

# Start Docker Compose
docker-compose -f docker-compose.yml up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 5

# Check service status
docker-compose ps

echo ""
echo "=========================================="
echo "Services Started Successfully!"
echo "=========================================="
echo ""
echo "Access the application at:"
echo "  Frontend:        http://localhost:3000"
echo "  Backend API:     http://localhost:8000"
echo "  API Docs:        http://localhost:8000/docs"
echo "  Qdrant Dashboard: http://localhost:6333/dashboard"
echo ""
echo "Useful commands:"
echo "  View logs:       docker-compose logs -f"
echo "  Stop services:   docker-compose down"
echo "  Restart:         docker-compose restart"
echo ""
echo "To ingest articles:"
echo "  docker-compose exec backend python -m app.services.ingestion data/articles --clear"
echo ""

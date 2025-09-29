#!/bin/bash

# Antifragile Flow - Vector Store Test Setup
# This script sets up the environment and runs all vector store tests

echo "🚀 Antifragile Flow - Vector Store Test Setup"
echo "============================================"

# Check if running from correct directory
if [ ! -f "docker-compose.test.yml" ]; then
    echo "❌ Please run this script from the service/vector_store directory"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No virtual environment detected. It's recommended to use a virtual environment."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please activate a virtual environment and run again."
        exit 1
    fi
fi

# Install required packages
if ! pip install neo4j weaviate-client requests; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

echo "✅ Python dependencies installed"

# Start Docker services
echo ""
echo "🐳 Starting Docker services..."
if ! docker-compose -f docker-compose.test.yml up -d; then
    echo "❌ Failed to start Docker services"
    exit 1
fi

echo "✅ Docker services started"

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."

# Check Neo4j
for i in {1..30}; do
    if docker exec antifragile-neo4j-test cypher-shell -u neo4j -p testpassword "RETURN 1" &> /dev/null; then
        echo "✅ Neo4j is ready"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "❌ Neo4j failed to start"
        echo "💡 Check logs: docker-compose -f docker-compose.test.yml logs neo4j"
        exit 1
    fi
    sleep 2
done

# Check Weaviate
for i in {1..30}; do
    if curl -s -f http://localhost:8080/v1/.well-known/ready &> /dev/null; then
        echo "✅ Weaviate is ready"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "❌ Weaviate failed to start"
        echo "💡 Check logs: docker-compose -f docker-compose.test.yml logs weaviate"
        exit 1
    fi
    sleep 2
done

# Run tests
echo ""
echo "🧪 Running all vector store tests..."
if python run_all_tests.py; then
    echo ""
    echo "🎉 Setup and testing completed successfully!"
    echo ""
    echo "🔗 Access your services:"
    echo "  Neo4j Browser: http://localhost:7474"
    echo "  Login: neo4j/testpassword"
    echo "  Weaviate API: http://localhost:8080/v1"
    echo ""
    echo "🛑 To stop services:"
    echo "  docker-compose -f docker-compose.test.yml down"
else
    echo ""
    echo "❌ Some tests failed. Check the output above for details."
fi

#!/bin/bash

# AURA Dashboard Docker Build Script
echo "🚀 Building AURA Dashboard Docker Container..."

# Set variables
IMAGE_NAME="aura-dashboard"
IMAGE_TAG="v1.1.0"
CONTAINER_NAME="aura-dashboard"

# Create necessary directories
mkdir -p logs/nginx

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t $IMAGE_NAME:$IMAGE_TAG .

# Tag as latest
docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:latest

echo "✅ Build complete!"
echo ""
echo "🎯 Available commands:"
echo "   docker run -d -p 8080:80 --name $CONTAINER_NAME $IMAGE_NAME:latest"
echo "   docker-compose up -d"
echo "   docker logs $CONTAINER_NAME"
echo ""
echo "🌐 Access at: http://localhost:8080"
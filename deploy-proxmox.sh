#!/bin/bash
# Proxmox deployment script for Audio Book Converter
# This script should be run on your Proxmox server

set -e

# Configuration
REPO_URL="https://github.com/dmytro-vasyliev/audio_book_converter.git"
DEPLOY_DIR="/opt/audiobook-converter"

# Parse command line arguments
COMMIT_OR_TAG=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--commit)
            COMMIT_OR_TAG="$2"
            shift 2
            ;;
        -t|--tag)
            COMMIT_OR_TAG="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [-c|--commit COMMIT_HASH] [-t|--tag TAG_NAME]"
            echo "Deploy Audio Book Converter to the server"
            echo ""
            echo "Options:"
            echo "  -c, --commit COMMIT_HASH   Deploy specific commit hash"
            echo "  -t, --tag TAG_NAME        Deploy specific tag"
            echo "  -h, --help                Show this help message"
            echo ""
            echo "If no commit or tag is specified, the latest main branch will be deployed."
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Run '$0 --help' for usage information"
            exit 1
            ;;
    esac
done

# Create deployment directory if it doesn't exist
mkdir -p $DEPLOY_DIR
cd $DEPLOY_DIR

echo "=== Audio Book Converter Deployment ==="
echo "Deploying to: $DEPLOY_DIR"

# Clone repository if it doesn't exist
if [ ! -d ".git" ]; then
    echo "Cloning repository..."
    git clone $REPO_URL .
fi

# Fetch latest changes
echo "Fetching latest changes..."
git fetch --all
git fetch --tags

# Checkout specific version if provided
if [ -z "$COMMIT_OR_TAG" ]; then
    echo "Checking out latest version from main branch..."
    git checkout main
else
    echo "Checking out specific version: $COMMIT_OR_TAG..."
    git checkout $COMMIT_OR_TAG
fi

# Build and start Docker containers
echo "Building and starting Docker containers..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Audio Book Converter is now running!"
echo "You can access it at: http://$(hostname -I | awk '{print $1}'):7860"

# Display deployed version info
echo ""
echo "=== Deployed Version Information ==="
echo "Commit: $(git rev-parse HEAD)"
echo "Date: $(git log -1 --format=%cd --date=local)"
echo "Message: $(git log -1 --format=%s)"

#!/bin/bash
# Proxmox deployment script for Audio Book Converter
# This script should be run on your Proxmox server

set -e

# Configuration
REPO_URL="https://github.com/dmytro-vasyliev/audio_book_converter.git"
DEPLOY_DIR="/opt/audiobook-converter"
WEBHOOK_SECRET="$(openssl rand -hex 20)"  # Generate a secure random string

# Create deployment directory if it doesn't exist
mkdir -p $DEPLOY_DIR
cd $DEPLOY_DIR

echo "=== Audio Book Converter Deployment ==="
echo "Deploying to: $DEPLOY_DIR"

# Check if repository exists, clone or pull
if [ -d ".git" ]; then
    echo "Repository exists, pulling latest changes..."
    git pull
else
    echo "Cloning repository..."
    git clone $REPO_URL .
fi

# Build and start Docker containers
echo "Building and starting Docker containers..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

echo "=== Deployment complete ==="
echo "The Audio Book Converter is now running at http://$(hostname -I | awk '{print $1}'):7860"

# Optional: Set up a simple webhook listener for automatic updates
echo """
To set up automatic updates:

1. Create a GitHub webhook in your repository:
   - URL: http://your-server-ip:9000/webhook
   - Content type: application/json
   - Secret: $WEBHOOK_SECRET

2. Run the webhook listener in a screen or tmux session:
   
   screen -S webhook
   python -c '
import http.server
import hmac
import hashlib
import json
import os
import subprocess

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != \"/webhook\":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers[\"Content-Length\"])
        payload = self.rfile.read(length)
        signature = self.headers.get(\"X-Hub-Signature-256\", \"\")
        
        # Verify signature
        if not signature.startswith(\"sha256=\"):
            self.send_response(400)
            self.end_headers()
            return
            
        secret = \"$WEBHOOK_SECRET\".encode()
        computed = \"sha256=\" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(signature, computed):
            self.send_response(403)
            self.end_headers()
            return
            
        # Process webhook
        try:
            event = json.loads(payload)
            if event.get(\"ref\") == \"refs/heads/main\":
                print(\"Received push to main, deploying...\")
                subprocess.run([\"/bin/bash\", \"$DEPLOY_DIR/deploy-proxmox.sh\"])
                
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b\"OK\")
        except Exception as e:
            print(f\"Error: {e}\")
            self.send_response(500)
            self.end_headers()
            
print(\"Starting webhook listener on port 9000...\")
server = http.server.HTTPServer((\"\", 9000), WebhookHandler)
server.serve_forever()
   '
   
   # Press Ctrl+A, D to detach from screen
"""

#!/bin/bash

echo "--- 🛠️ Cleaning up Port 4000 ---"
# Find the ID of whatever is running on 4000 and kill it
fuser -k 4000/tcp || true

echo "--- 📦 Installing Dependencies ---"
pip install flask flask-cors requests

echo "--- 🚀 Launching Multi-Chat Server ---"
python chat_app.py &
APP_PID=$!

sleep 2

# GitHub Codespace Port Forwarding (Manual Backup)
echo "------------------------------------------------"
echo "1. Look at the 'Ports' tab at the bottom."
echo "2. If you don't see 4000, click 'Add Port' and type 4000."
echo "3. RIGHT CLICK the lock icon on Port 4000."
echo "4. Set 'Port Visibility' to PUBLIC."
echo "------------------------------------------------"

wait $APP_PID

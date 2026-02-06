#!/bin/bash

# File to store messages
CHAT_FILE="chat.txt"

# Ensure the chat file exists
touch "$CHAT_FILE"

echo "--- Shared Codespace Chat ---"
echo "Type your message and press Enter."

# Run a background process to listen for new messages
tail -f "$CHAT_FILE" &
TAIL_PID=$!

# Handle exiting the chat
trap "kill $TAIL_PID; exit" INT TERM

# Read input and append to the chat file
while read -r message; do
    if [[ -n "$message" ]]; then
        echo "$(whoami) [$(date +%H:%M)]: $message" >> "$CHAT_FILE"
    fi
done

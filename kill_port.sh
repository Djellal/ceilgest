#!/bin/bash

# Check if a port number was provided
if [ -z "$1" ]; then
  echo "Usage: $0 <port>"
  exit 1
fi

PORT=$1

# Find and kill processes using the specified port
PIDS=$(lsof -i :$PORT -t)

if [ -z "$PIDS" ]; then
  echo "No process is using port $PORT."
else
  echo "Killing process(es) using port $PORT: $PIDS"
  kill -9 $PIDS
fi

#!/bin/bash
set -o pipefail

# Activate poetry shell
poetry shell

# Display banner
figlet "been"

# Set a base default path
IMAGE_PATH=/trips

# Check if the user has provided a path
if [ -z "$1" ]
then
    echo "No path provided, using default path: $IMAGE_PATH"
else
    IMAGE_PATH=$1
fi

# Run the main script
python src/main.py $IMAGE_PATH
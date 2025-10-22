#!/bin/bash

# Script to create a standard project directory structure.
# Usage: ./create_project.sh "Your Project Name"

PROJECT_NAME="$1"

# Check if a project name was provided
if [ -z "$PROJECT_NAME" ]; then
  echo "Error: No project name provided."
  echo "Usage: ./create_project.sh "Your Project Name""
  exit 1
fi

# Create the directory structure
echo "Creating project: $PROJECT_NAME"
mkdir -p "$PROJECT_NAME"/{_source,assets,drafts,final_report}

echo "Project structure for '$PROJECT_NAME' created successfully."
ls -R "$PROJECT_NAME"

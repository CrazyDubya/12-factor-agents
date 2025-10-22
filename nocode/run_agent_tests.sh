#!/bin/bash

# =============================================================================
# Automated Test Harness for CLI AI Agent Capabilities
#
# Purpose: To rigorously and automatically validate the core functionalities
#          of a CLI-based AI agent.
#
# Usage:
# 1. Place this script in the directory where the agent is active.
# 2. Grant execution permissions: `chmod +x run_agent_tests.sh`
# 3. Run the script: `./run_agent_tests.sh`
#
# The script will then prompt the user to ask the AI agent to perform
# a series of tasks. It waits for the user to confirm before validating
# the result of each task.
# =============================================================================

# --- Configuration ---
TEST_DIR="agent_test_sandbox"
PASS_COUNT=0
FAIL_COUNT=0
TEST_COUNT=0

# --- Colors for logging ---
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Helper Functions ---

# Sets up a clean environment for tests
setup() {
  echo "--- Setting up test environment ---"
  rm -rf "$TEST_DIR"
  mkdir "$TEST_DIR"
  echo "Created sandbox directory: $TEST_DIR"
  echo "---------------------------------"
}

# Cleans up the test environment
cleanup() {
  echo "--- Tearing down test environment ---"
  rm -rf "$TEST_DIR"
  echo "Removed sandbox directory: $TEST_DIR"
  echo "-----------------------------------"
}

# Prompts the user to give the agent a command and waits for them to continue
prompt_agent() {
  TEST_COUNT=$((TEST_COUNT + 1))
  echo -e "\n${YELLOW}ACTION REQUIRED:${NC}"
  echo -e "Please ask the agent to perform the following task:"
  echo -e "\n  ${GREEN}>>> $1${NC}\n"
  read -p "Once the agent has completed the task, press [Enter] to continue and validate..."
}

# Assertion functions
# assert_exists [path]: Fails if the file or directory does not exist.
assert_exists() {
  if [ -e "$1" ]; then
    echo -e "  ${GREEN}PASS:${NC} '$1' exists."
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo -e "  ${RED}FAIL:${NC} '$1' does not exist."
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

# assert_not_exists [path]: Fails if the file or directory exists.
assert_not_exists() {
  if [ ! -e "$1" ]; then
    echo -e "  ${GREEN}PASS:${NC} '$1' does not exist."
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo -e "  ${RED}FAIL:${NC} '$1' still exists."
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

# assert_contains [file] [string]: Fails if the file does not contain the string.
assert_contains() {
  if grep -q "$2" "$1"; then
    echo -e "  ${GREEN}PASS:${NC} '$1' contains the expected content."
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo -e "  ${RED}FAIL:${NC} '$1' does not contain the expected content."
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}


# --- Test Cases ---

test_file_creation() {
  echo "--- Test Case 1: File Creation ---"
  local FILE_PATH="$TEST_DIR/test_file.txt"
  prompt_agent "Create a new file at '$FILE_PATH' with the content 'hello world'."
  assert_exists "$FILE_PATH"
  assert_contains "$FILE_PATH" "hello world"
}

test_directory_creation() {
  echo "--- Test Case 2: Directory Creation ---"
  local DIR_PATH="$TEST_DIR/new_directory"
  prompt_agent "Create a new directory at '$DIR_PATH'."
  assert_exists "$DIR_PATH"
}

test_file_deletion() {
  echo "--- Test Case 3: File Deletion ---"
  local FILE_TO_DELETE="$TEST_DIR/file_to_delete.txt"
  touch "$FILE_TO_DELETE" # Create a file to be deleted
  prompt_agent "Delete the file at '$FILE_TO_DELETE'."
  assert_not_exists "$FILE_TO_DELETE"
}

test_content_search_and_edit() {
    echo "--- Test Case 4: Content Search and Edit ---"
    local FILE_PATH="$TEST_DIR/search_and_edit.txt"
    echo "Initial content for testing." > "$FILE_PATH"
    prompt_agent "In the file '$FILE_PATH', replace the word 'Initial' with 'Modified'."
    assert_contains "$FILE_PATH" "Modified content"
}


# --- Main Execution ---
main() {
  setup

  # Run all test cases
  test_file_creation
  test_directory_creation
  test_file_deletion
  test_content_search_and_edit

  cleanup

  # --- Final Report ---
  echo -e "\n--- TEST-SUITE COMPLETE ---"
  echo "Total Tests: $TEST_COUNT"
  echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
  echo -e "${RED}Failed: $FAIL_COUNT${NC}"
  echo "---------------------------"

  if [ "$FAIL_COUNT" -ne 0 ]; then
    exit 1
  fi
}

# Run the main function
main

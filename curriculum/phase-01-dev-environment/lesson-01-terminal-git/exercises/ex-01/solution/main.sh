#!/usr/bin/env bash
# =============================================================================
# Exercise: Your First Git Repository — Solution
# =============================================================================

# Move to the directory where this script lives (so paths are predictable)
cd "$(dirname "$0")"

# TODO 1: Create a directory called "my-project"
mkdir -p my-project

# TODO 2: Change into the "my-project" directory
cd my-project

# TODO 3: Initialize a new Git repository
git init

# TODO 4: Create a file called "hello.txt" that contains the text "Hello, AI world!"
echo "Hello, AI world!" > hello.txt

# TODO 5: Stage the file for commit
git add hello.txt

# TODO 6: Commit with the message "Initial commit"
git commit -m "Initial commit"

echo "Done! Run the tests to see if everything looks good."

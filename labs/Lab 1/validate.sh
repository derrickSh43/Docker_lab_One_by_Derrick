#!/bin/bash

# 1. Navigating the File System
if [ "$(pwd)" != "/home/student" ]; then
    echo "❌ Validation Failed: You are not in the correct directory."
    exit 1
fi

# 2. Managing Files and Directories
if [ ! -d /home/student/devops_lab ]; then
    echo "❌ Validation Failed: Directory 'devops_lab' not created."
    exit 1
fi
if [ ! -f /home/student/devops_lab/lab.txt ]; then
    echo "❌ Validation Failed: 'lab.txt' not created."
    exit 1
fi
if [ ! -f /home/student/devops_lab/backup.txt ]; then
    echo "❌ Validation Failed: 'backup.txt' not copied."
    exit 1
fi
if [ ! -f /home/student/devops_lab/task.txt ]; then
    echo "❌ Validation Failed: 'task.txt' not renamed."
    exit 1
fi

# 3. Working with Processes
if ! ps aux | grep -q "top"; then
    echo "❌ Validation Failed: 'ps' command did not show processes."
    exit 1
fi

# 4. System Information and Networking
if ! df -h | grep -q "/"; then
    echo "❌ Validation Failed: 'df -h' did not show disk usage."
    exit 1
fi
if ! free -h | grep -q "Mem"; then
    echo "❌ Validation Failed: 'free -h' did not show memory usage."
    exit 1
fi
if ! ping -c 1 google.com; then
    echo "❌ Validation Failed: 'ping' did not reach google.com."
    exit 1
fi

# 5. Basic Text Processing
if ! grep -q "hello world" /home/student/task.txt; then
    echo "❌ Validation Failed: 'task.txt' does not contain the correct text."
    exit 1
fi

# 6. Managing Users and Permissions
if [ "$(stat -c %A /home/student/task.txt)" != "-rw-------" ]; then
    echo "❌ Validation Failed: 'task.txt' does not have the correct permissions."
    exit 1
fi

if ! id -u clouduser > /dev/null 2>&1; then
    echo "❌ Validation Failed: User 'clouduser' was not created."
    exit 1
fi

echo "✅ Validation Passed: All tasks completed successfully!"
exit 0

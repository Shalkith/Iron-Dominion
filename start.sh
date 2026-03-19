#!/bin/bash
# Quick start for Unix/Mac

for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        $cmd start.py "$@"
        exit $?
    fi
done

echo "ERROR: Python not found"
exit 1

#!/bin/bash

# Script to build macOS executable for printer-dont-die
# This script must be run from the project root directory

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to project root (where this script is located)
cd "$SCRIPT_DIR"

echo "Building macOS executable..."
echo "Working directory: $(pwd)"

# Install dependencies from pyproject.toml
echo "Installing dependencies..."
if command -v pip &> /dev/null; then
    pip install -e . > /dev/null 2>&1 || pip install loguru pyinstaller
else
    echo "ERROR: pip is not installed"
    exit 1
fi

# Run pyinstaller
pyinstaller --onefile --name printer-dont-die --target-arch arm64 --hidden-import loguru --add-data "config.json:." --add-data "app/resources:app/resources" app/main.py

# Check if dist directory exists
if [ ! -d "dist" ]; then
    echo "ERROR: dist directory was not created"
    exit 1
fi

# Check if config.json exists in dist, if not copy it from root
if [ ! -f "dist/config.json" ]; then
    echo "config.json not found in dist/, copying from root..."
    if [ -f "config.json" ]; then
        cp config.json dist/config.json
        echo "✓ Copied config.json to dist/"
    else
        echo "WARNING: config.json not found in root directory"
    fi
else
    echo "✓ config.json already exists in dist/"
fi

echo ""
echo "Build complete!"
echo "Executable location: dist/printer-dont-die"
echo "To run: ./dist/printer-dont-die"

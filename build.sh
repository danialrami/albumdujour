#!/bin/bash

# Music Library Website Builder
# This script builds a static website from your Google Sheets music data

set -e  # Exit on any error

echo "🎵 Music Library Website Builder"
echo "================================"

# Get the current directory (should be the v3 website directory)
WEBSITE_DIR="$(pwd)"
echo "📁 Website directory: $WEBSITE_DIR"

# Check if credentials file exists in current directory
CREDENTIALS_FILE="concrete-spider-446700-f9-4646496845d1.json"
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo "❌ Error: Credentials file not found at '$CREDENTIALS_FILE'"
    echo "Expected: $WEBSITE_DIR/$CREDENTIALS_FILE"
    exit 1
fi
echo "✅ Found credentials file"

# Check if Apple Music tokens exist in current directory
APPLE_TOKEN_DIR="$WEBSITE_DIR/musickit"
if [ ! -d "$APPLE_TOKEN_DIR" ]; then
    echo "❌ Error: Apple Music token directory not found at '$APPLE_TOKEN_DIR'"
    exit 1
fi

if [ ! -f "$APPLE_TOKEN_DIR/musickit-developer-token.txt" ]; then
    echo "❌ Error: Apple Music developer token not found at '$APPLE_TOKEN_DIR/musickit-developer-token.txt'"
    exit 1
fi

if [ ! -f "$APPLE_TOKEN_DIR/music_user_token.txt" ]; then
    echo "❌ Error: Apple Music user token not found at '$APPLE_TOKEN_DIR/music_user_token.txt'"
    exit 1
fi
echo "✅ Found Apple Music tokens"

# Check if Python script exists
BUILD_SCRIPT="build_music_site.py"
if [ ! -f "$BUILD_SCRIPT" ]; then
    echo "❌ Error: Build script '$BUILD_SCRIPT' not found!"
    echo "Please make sure the build script is in the current directory."
    exit 1
fi
echo "✅ Found build script"

# Virtual environment management
VENV_DIR="venv"
PYTHON_CMD="python3"

echo ""
echo "🔧 Setting up Python environment..."

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment created successfully"
    else
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

if [ $? -eq 0 ]; then
    echo "✅ Virtual environment activated"
    echo "🐍 Using Python: $(which python)"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Function to cleanup and deactivate venv on exit
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate 2>/dev/null || true
        echo "✅ Virtual environment deactivated"
    fi
}

# Set up trap to ensure cleanup happens
trap cleanup EXIT

# Upgrade pip and install required packages
echo "📥 Installing/updating required packages..."
pip install --upgrade pip --quiet
if [ $? -eq 0 ]; then
    echo "✅ pip upgraded"
else
    echo "⚠️  pip upgrade failed, continuing anyway"
fi

pip install gspread --quiet
if [ $? -eq 0 ]; then
    echo "✅ gspread installed/updated"
else
    echo "❌ Failed to install gspread"
    exit 1
fi

echo "✅ All dependencies ready"

# Run the build script
echo ""
echo "🚀 Building website..."
echo "📊 Reading from Google Sheets..."
echo "🎵 Processing music data..."

# Run the Python script (it will auto-detect paths in current directory)
python "$BUILD_SCRIPT"

# Check if build was successful
if [ -d "build" ] && [ -f "build/index.html" ]; then
    echo ""
    echo "🎉 Build successful!"
    echo "📂 Website generated in: ./build/"
    echo "🌐 Open build/index.html in your browser"
    echo ""
    
    # Show some stats about the generated site
    if [ -f "build/index.html" ]; then
        CARD_COUNT=$(grep -o "music-card" build/index.html | wc -l | tr -d ' ' 2>/dev/null || echo "0")
        echo "📊 Generated $CARD_COUNT music cards"
    fi
    
    # Show build folder size
    if command -v du &> /dev/null; then
        BUILD_SIZE=$(du -sh build/ 2>/dev/null | cut -f1 || echo "unknown")
        echo "💾 Build size: $BUILD_SIZE"
    fi
    
    # List build contents
    echo "📄 Build contents:"
    ls -la build/ | head -10
    
    # Optional: Open in browser (macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo ""
        read -p "Open in browser? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open "build/index.html"
        fi
    fi
    
    # Deploy suggestions
    echo ""
    echo "💡 To deploy:"
    echo "   - Upload the 'build' folder to any web server"
    echo "   - Or use: python3 -m http.server 8000 (from build directory)"
    echo "   - Or deploy to GitHub Pages, Netlify, Vercel, etc."
    echo ""
    echo "🔄 To rebuild: just run ./build.sh again"
    echo "🗂️  Files ready for deployment are in the ./build/ directory"
    
else
    echo ""
    echo "❌ Build failed - no output files generated"
    echo "🔍 Checking for error details..."
    
    if [ ! -d "build" ]; then
        echo "   - build/ directory was not created"
    fi
    
    if [ ! -f "build/index.html" ]; then
        echo "   - index.html was not generated"
    fi
    
    exit 1
fi
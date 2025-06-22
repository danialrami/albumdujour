#!/bin/bash

# Music Library Website Builder with Git Deployment
# This script builds a static website from your Google Sheets music data and deploys it

set -e  # Exit on any error

echo "🎵 Music Library Website Builder with Git Deployment"
echo "===================================================="

# Get the current directory (should be the v3 website directory)
WEBSITE_DIR="$(pwd)"
echo "📁 Website directory: $WEBSITE_DIR"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository!"
    echo "Please run this script from the root of your git repository."
    exit 1
fi
echo "✅ Git repository detected"

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

# Check if virtual environment exists and is valid
if [ -d "$VENV_DIR" ]; then
    # Test if the venv is working properly
    if "$VENV_DIR/bin/python" --version &>/dev/null; then
        echo "✅ Virtual environment already exists and is valid"
    else
        echo "⚠️  Virtual environment exists but is broken, recreating..."
        rm -rf "$VENV_DIR"
        $PYTHON_CMD -m venv "$VENV_DIR"
        if [ $? -eq 0 ]; then
            echo "✅ Virtual environment recreated successfully"
        else
            echo "❌ Failed to recreate virtual environment"
            exit 1
        fi
    fi
else
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment created successfully"
    else
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

if [ $? -eq 0 ]; then
    echo "✅ Virtual environment activated"
    echo "🐍 Using Python: $(which python 2>/dev/null || echo 'python not found')"
    echo "🐍 Python3 available: $(which python3 2>/dev/null || echo 'python3 not found')"
    echo "🔍 Virtual env: $VIRTUAL_ENV"
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
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
if [ $? -eq 0 ]; then
    echo "✅ pip upgraded"
else
    echo "⚠️  pip upgrade failed, continuing anyway"
fi

"$VENV_DIR/bin/pip" install gspread --quiet
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

# Run the Python script using the venv's Python directly
echo "🐍 Using venv Python: $VENV_DIR/bin/python"
"$VENV_DIR/bin/python" "$BUILD_SCRIPT"

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
    
    # Deactivate virtual environment before git operations
    cleanup
    trap - EXIT  # Remove the trap since we're manually cleaning up
    
    # Git operations start here
    echo ""
    echo "🔄 Starting Git deployment process..."
    
    # Store current branch name
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
    echo "📍 Current branch: $CURRENT_BRANCH"
    
    # Create timestamp for commit message
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 1. First, commit any changes to the current branch (main/master)
    echo ""
    echo "📝 Committing source changes to $CURRENT_BRANCH branch..."
    
    # Check if there are any changes to commit
    if git diff --staged --quiet && git diff --quiet; then
        echo "ℹ️  No source changes to commit"
    else
        git add .
        git commit -m "Update website source - $TIMESTAMP" || {
            echo "⚠️  Nothing to commit or commit failed, continuing..."
        }
        echo "✅ Source changes committed to $CURRENT_BRANCH"
    fi
    
    # 2. Create/switch to build branch and deploy build files
    echo ""
    echo "🌿 Setting up build branch..."
    
    # Check if build branch exists
    if git show-ref --verify --quiet refs/heads/build; then
        echo "✅ Build branch exists, switching to it"
        git checkout build
    else
        echo "📝 Creating new build branch"
        git checkout -b build
    fi
    
    # Clear the build branch (keep only build files)
    echo "🧹 Cleaning build branch..."
    
    # Remove all files except .git, build/, and .gitignore
    find . -maxdepth 1 -not -name '.git' -not -name 'build' -not -name '.gitignore' -not -path '.' -exec rm -rf {} + 2>/dev/null || true
    
    # Move build contents to root
    echo "📦 Moving build files to repository root..."
    if [ -d "build" ]; then
        mv build/* . 2>/dev/null || true
        mv build/.* . 2>/dev/null || true  # Move hidden files if any
        rmdir build 2>/dev/null || true
    fi
    
    # Create a simple .gitignore for the build branch
    echo "# Build branch - only contains generated website files" > .gitignore
    
    # Add and commit build files
    echo "📤 Committing build files..."
    git add .
    git commit -m "Deploy website build - $TIMESTAMP" || {
        echo "⚠️  No build changes to commit"
    }
    
    # 3. Push both branches
    echo ""
    echo "🚀 Pushing to remote repository..."
    
    # Push build branch
    echo "📤 Pushing build branch..."
    git push origin build || {
        echo "❌ Failed to push build branch"
        git checkout "$CURRENT_BRANCH"
        exit 1
    }
    echo "✅ Build branch pushed successfully"
    
    # Switch back to original branch and push it too
    echo "📤 Pushing $CURRENT_BRANCH branch..."
    git checkout "$CURRENT_BRANCH"
    git push origin "$CURRENT_BRANCH" || {
        echo "⚠️  Failed to push $CURRENT_BRANCH branch (may be up to date)"
    }
    echo "✅ Source branch pushed successfully"
    
    # 4. Clean up - rebuild the build directory locally for testing
    echo ""
    echo "🔧 Rebuilding local build directory for testing..."
    
    # Re-run just the Python build script to regenerate build folder locally
    source "$VENV_DIR/bin/activate" 2>/dev/null || {
        echo "⚠️  Could not reactivate virtual environment"
        echo "💡 You may need to run the build script again if you want to test locally"
    }
    
    if [ -n "$VIRTUAL_ENV" ]; then
        # Use venv Python directly
        "$VENV_DIR/bin/python" "$BUILD_SCRIPT" || {
            echo "⚠️  Could not rebuild local build directory"
        }
        deactivate
    fi
    
    # Final status
    echo ""
    echo "🎊 Deployment complete!"
    echo "================================"
    echo "✅ Source code: $CURRENT_BRANCH branch"
    echo "✅ Website: build branch"
    echo ""
    echo "🌐 Your website is now deployed on the 'build' branch"
    echo "📋 Hostinger setup:"
    echo "   1. Connect your GitHub repository to Hostinger"
    echo "   2. Set deployment branch to: build"
    echo "   3. Set build directory to: / (root)"
    echo ""
    echo "🔗 Branch URLs:"
    echo "   Source: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^.]*\).*/\1/')/tree/$CURRENT_BRANCH"
    echo "   Website: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^.]*\).*/\1/')/tree/build"
    echo ""
    echo "🔄 To rebuild and redeploy: just run ./build.sh again"
    
    # Optional: Open in browser (macOS)
    if [[ "$OSTYPE" == "darwin"* ]] && [ -f "build/index.html" ]; then
        echo ""
        read -p "Open local build in browser? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open "build/index.html"
        fi
    fi
    
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
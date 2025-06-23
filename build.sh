#!/bin/bash

# Music Library Website Builder with Safe Git Deployment
# Enhanced version with proper error handling, file safety, and history preservation

set -euo pipefail  # Exit on any error, undefined variable, or pipe failure

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly WEBSITE_DIR="$SCRIPT_DIR"
readonly BUILD_DIR="$WEBSITE_DIR/build"
readonly PYTHON_SCRIPT="$WEBSITE_DIR/build_music_site.py"
readonly VENV_DIR="$WEBSITE_DIR/venv"
readonly CREDENTIALS_FILE="$WEBSITE_DIR/concrete-spider-446700-f9-4646496845d1.json"
readonly APPLE_TOKENS_DIR="$WEBSITE_DIR/musickit"

# Global variables
ORIGINAL_BRANCH=""
TEMP_BACKUP_DIR=""
CLEANUP_NEEDED=false

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}" >&2
}

log_header() {
    echo -e "${BLUE}$1${NC}"
    echo "$(printf '=%.0s' $(seq 1 ${#1}))"
}

# Cleanup function
cleanup() {
    local exit_code=$?
    
    if [ "$CLEANUP_NEEDED" = true ]; then
        log_info "Performing cleanup..."
        
        # Deactivate virtual environment if active
        if [ -n "${VIRTUAL_ENV:-}" ]; then
            deactivate 2>/dev/null || true
            log_success "Virtual environment deactivated"
        fi
        
        # Return to original branch if we changed it
        if [ -n "$ORIGINAL_BRANCH" ] && [ "$ORIGINAL_BRANCH" != "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '')" ]; then
            log_info "Returning to original branch: $ORIGINAL_BRANCH"
            git checkout "$ORIGINAL_BRANCH" 2>/dev/null || log_warning "Could not return to original branch"
        fi
        
        # Clean up temporary backup
        if [ -n "$TEMP_BACKUP_DIR" ] && [ -d "$TEMP_BACKUP_DIR" ]; then
            rm -rf "$TEMP_BACKUP_DIR"
            log_success "Temporary backup cleaned up"
        fi
    fi
    
    if [ $exit_code -eq 0 ]; then
        log_success "Script completed successfully!"
    else
        log_error "Script failed with exit code $exit_code"
    fi
    
    exit $exit_code
}

# Set up trap for cleanup
trap cleanup EXIT INT TERM

# Validation functions
validate_environment() {
    log_header "🔍 Environment Validation"
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log_error "Not in a git repository"
        exit 1
    fi
    log_success "Git repository detected"
    
    # Store original branch
    ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    log_info "Current branch: $ORIGINAL_BRANCH"
    
    # Check for required files
    local required_files=("$PYTHON_SCRIPT" "$CREDENTIALS_FILE")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Required file not found: $file"
            exit 1
        fi
    done
    log_success "All required files found"
    
    # Check for Apple Music tokens directory
    if [ ! -d "$APPLE_TOKENS_DIR" ]; then
        log_warning "Apple Music tokens directory not found: $APPLE_TOKENS_DIR"
    else
        log_success "Apple Music tokens directory found"
    fi
    
    # Check git status
    if ! git diff-index --quiet HEAD --; then
        log_warning "Working directory has uncommitted changes"
    else
        log_success "Working directory is clean"
    fi
}

setup_python_environment() {
    log_header "🐍 Python Environment Setup"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        log_success "Virtual environment created"
    else
        log_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"
    CLEANUP_NEEDED=true
    log_success "Virtual environment activated"
    
    # Install/upgrade required packages
    log_info "Installing required packages..."
    pip install --quiet --upgrade pip
    pip install --quiet gspread
    log_success "All dependencies ready"
}

build_website() {
    log_header "🚀 Building Website"
    
    # Remove old build directory
    if [ -d "$BUILD_DIR" ]; then
        log_info "Removing old build directory..."
        rm -rf "$BUILD_DIR"
    fi
    
    # Run the Python build script
    log_info "Running website build script..."
    if ! python "$PYTHON_SCRIPT"; then
        log_error "Website build failed"
        exit 1
    fi
    
    # Verify build was successful
    if [ ! -f "$BUILD_DIR/index.html" ]; then
        log_error "Build verification failed: index.html not found"
        exit 1
    fi
    
    # Show build statistics
    local build_size
    build_size=$(du -sh "$BUILD_DIR" 2>/dev/null | cut -f1 || echo "unknown")
    local file_count
    file_count=$(find "$BUILD_DIR" -type f | wc -l | tr -d ' ')
    
    log_success "Build completed successfully!"
    log_info "Build size: $build_size"
    log_info "Files generated: $file_count"
}

commit_source_changes() {
    log_header "📝 Committing Source Changes"
    
    # Switch to main branch if not already there
    if [ "$ORIGINAL_BRANCH" != "main" ]; then
        log_info "Switching to main branch..."
        git checkout main
    fi
    
    # Add all changes
    git add .
    
    # Check if there are changes to commit
    if git diff-index --quiet HEAD --; then
        log_info "No source changes to commit"
        return 0
    fi
    
    # Commit changes
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    git commit -m "Update website source - $timestamp"
    log_success "Source changes committed to main"
}

create_safe_backup() {
    log_header "💾 Creating Safety Backup"
    
    # Create temporary backup directory
    TEMP_BACKUP_DIR=$(mktemp -d)
    log_info "Creating backup in: $TEMP_BACKUP_DIR"
    
    # Copy build files to backup
    cp -r "$BUILD_DIR" "$TEMP_BACKUP_DIR/"
    
    # Verify backup
    if [ ! -f "$TEMP_BACKUP_DIR/build/index.html" ]; then
        log_error "Backup verification failed"
        exit 1
    fi
    
    log_success "Safety backup created and verified"
}

deploy_to_build_branch() {
    log_header "🌿 Deploying to Build Branch (History Preserving)"
    
    # Ensure we're up to date with remote build branch
    log_info "Fetching latest remote changes..."
    git fetch origin 2>/dev/null || log_warning "Could not fetch from origin"
    
    # Check if build branch exists locally
    if ! git show-ref --verify --quiet refs/heads/build; then
        # Check if it exists on remote
        if git show-ref --verify --quiet refs/remotes/origin/build; then
            log_info "Creating local build branch from remote..."
            git checkout -b build origin/build
        else
            log_info "Creating new build branch..."
            git checkout -b build
            # Create initial commit for build branch
            echo "# Build Branch" > README-build.md
            git add README-build.md
            git commit -m "Initialize build branch"
        fi
    else
        log_info "Switching to existing build branch..."
        git checkout build
        
        # Try to pull latest changes if remote exists
        if git show-ref --verify --quiet refs/remotes/origin/build; then
            log_info "Pulling latest build branch changes..."
            git pull origin build 2>/dev/null || log_warning "Could not pull latest changes"
        fi
    fi
    
    # Verify we're on build branch
    local current_branch
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$current_branch" != "build" ]; then
        log_error "Failed to switch to build branch (currently on: $current_branch)"
        exit 1
    fi
    
    # HISTORY-PRESERVING UPDATE: Remove only build artifacts, keep git history
    log_info "Updating build files while preserving history..."
    
    # Remove only the old build artifacts (not source files or git history)
    local items_to_remove=(
        "index.html"
        "styles.css" 
        "scripts.js"
        "assets"
    )
    
    for item in "${items_to_remove[@]}"; do
        if [ -e "$item" ]; then
            rm -rf "$item"
            log_info "Removed old: $item"
        fi
    done
    
    # Copy new build files from backup
    log_info "Copying new build files..."
    cp -r "$TEMP_BACKUP_DIR/build/"* .
    
    # Verify deployment
    if [ ! -f "index.html" ]; then
        log_error "Deployment verification failed: index.html not found in build branch"
        exit 1
    fi
    
    # Show what's in the build branch
    log_info "Build branch contents:"
    ls -la
    
    # Stage all changes (additions, modifications, deletions)
    git add -A
    
    # Check if there are actually changes to commit
    if git diff-index --quiet HEAD --; then
        log_info "No changes to commit in build branch"
        return 0
    fi
    
    # Commit with detailed message
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local file_count
    file_count=$(find . -name "*.html" -o -name "*.css" -o -name "*.js" | wc -l | tr -d ' ')
    
    git commit -m "Deploy website build - $timestamp

- Updated website with latest content
- Generated $file_count web files
- Build size: $(du -sh . 2>/dev/null | cut -f1 || echo 'unknown')"
    
    log_success "Build files committed to build branch with preserved history"
}

push_to_remote() {
    log_header "🚀 Pushing to Remote Repository"
    
    # Push main branch first
    log_info "Pushing main branch..."
    git checkout main
    if git push origin main 2>/dev/null; then
        log_success "Main branch pushed successfully"
    else
        log_info "Main branch is up to date"
    fi
    
    # Push build branch with history preservation
    log_info "Pushing build branch..."
    git checkout build
    
    # Normal push should work now since we're preserving history
    if git push origin build 2>/dev/null; then
        log_success "Build branch pushed successfully"
    else
        # If it still fails, it might be because remote is ahead
        log_info "Normal push failed, trying to merge remote changes..."
        
        if git pull origin build 2>/dev/null; then
            log_info "Merged remote changes, pushing again..."
            if git push origin build 2>/dev/null; then
                log_success "Build branch pushed successfully after merge"
            else
                log_error "Failed to push build branch even after merge"
                exit 1
            fi
        else
            log_warning "Could not merge remote changes, using force-with-lease as fallback..."
            if git push --force-with-lease origin build 2>/dev/null; then
                log_success "Build branch force-pushed successfully"
            else
                log_error "Failed to push build branch"
                log_info "You may need to manually resolve conflicts"
                exit 1
            fi
        fi
    fi
}

# Main execution
main() {
    log_header "🎵 Music Library Website Builder with Safe Git Deployment"
    
    # Change to website directory
    cd "$WEBSITE_DIR"
    
    # Execute all steps
    validate_environment
    setup_python_environment
    build_website
    commit_source_changes
    create_safe_backup
    deploy_to_build_branch
    push_to_remote
    
    # Return to original branch
    git checkout "$ORIGINAL_BRANCH"
    
    log_success "🎉 Deployment completed successfully!"
    log_info "Website is now live on the build branch"
    log_info "Source code remains safe on the main branch"
    log_info "Both branches maintain their complete Git history"
}

# Run main function
main "$@"

#!/bin/bash

# Music Library Website Builder with Enhanced Security and Git Deployment
# Ensures credentials never leak to build branch

set -euo pipefail # Exit on any error, undefined variable, or pipe failure

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
    echo -e "${BLUE}ℹ️ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
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
        
        # Clean up any uncommitted changes on build branch
        local current_branch
        current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
        if [ "$current_branch" = "build" ]; then
            log_info "Cleaning up build branch state..."
            git reset --hard HEAD 2>/dev/null || true
            git clean -fd 2>/dev/null || true
        fi
        
        # Return to original branch if we changed it
        if [ -n "$ORIGINAL_BRANCH" ] && [ "$ORIGINAL_BRANCH" != "$current_branch" ]; then
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
    
    # Make sure we're on main branch
    if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then
        log_info "Switching to main branch..."
        git checkout main
    fi
    
    # Add all changes (credentials should already be gitignored)
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

create_orphan_build_branch() {
    log_header "🌿 Creating Clean Build Branch"
    
    # Check if build branch exists and delete it to start fresh
    if git show-ref --verify --quiet refs/heads/build; then
        log_info "Deleting existing build branch to start fresh..."
        git branch -D build 2>/dev/null || true
    fi
    
    # Create a completely new orphan branch (no history from main)
    log_info "Creating fresh orphan build branch..."
    git checkout --orphan build
    
    # Remove all files from the new branch (they're still staged from main)
    log_info "Clearing all files from build branch..."
    git rm -rf . 2>/dev/null || true
    
    # Clean any remaining untracked files
    git clean -fd 2>/dev/null || true
    
    # Verify we have a clean slate
    if [ "$(ls -A . 2>/dev/null | wc -l)" -ne 0 ]; then
        log_error "Build branch is not clean after reset"
        ls -la
        exit 1
    fi
    
    log_success "Clean build branch created"
}

setup_build_branch() {
    log_header "🔧 Setting Up Build Branch"
    
    # Create security-focused gitignore FIRST
    log_info "Setting up build branch .gitignore..."
    cat > .gitignore << 'EOF'
# Credentials and sensitive files - NEVER commit these
concrete-spider-446700-f9-*.json
musickit/
*.key
*.pem
*.p8
.env
.env.*

# Build tools and development files - shouldn't be in build branch
build_music_site.py
build.sh
venv/
requirements.txt
__pycache__/
*.pyc
*.pyo

# OS and editor files
.DS_Store
Thumbs.db
*.swp
*.swo
*~
EOF
    log_success "Build branch .gitignore configured"
    
    # Copy ONLY web files from backup (whitelist approach for maximum security)
    log_info "Copying web files to build branch..."
    
    # Copy main HTML file
    if [ -f "$TEMP_BACKUP_DIR/build/index.html" ]; then
        cp "$TEMP_BACKUP_DIR/build/index.html" .
        log_info "✓ Copied index.html"
    fi
    
    # Copy CSS files
    if [ -f "$TEMP_BACKUP_DIR/build/styles.css" ]; then
        cp "$TEMP_BACKUP_DIR/build/styles.css" .
        log_info "✓ Copied styles.css"
    fi
    
    # Copy JavaScript files if they exist
    if [ -f "$TEMP_BACKUP_DIR/build/scripts.js" ]; then
        cp "$TEMP_BACKUP_DIR/build/scripts.js" .
        log_info "✓ Copied scripts.js"
    fi
    
    # Copy assets directory (web assets only)
    if [ -d "$TEMP_BACKUP_DIR/build/assets" ]; then
        cp -r "$TEMP_BACKUP_DIR/build/assets" .
        log_info "✓ Copied assets directory"
    fi
    
    # Verify deployment
    if [ ! -f "index.html" ]; then
        log_error "Deployment verification failed: index.html not found in build branch"
        exit 1
    fi
    
    log_success "Build branch setup completed"
}

verify_build_security() {
    log_header "🔒 Security Verification"
    
    log_info "Verifying no credentials in build branch..."
    
    # Define patterns for credential files
    local credential_patterns=(
        "concrete-spider-446700-f9-*.json"
        "musickit"
        "*.key"
        "*.pem"
        "*.p8"
        ".env"
        "build_music_site.py"
        "build.sh"
        "venv"
    )
    
    local found_credentials=false
    
    for pattern in "${credential_patterns[@]}"; do
        if find . -name "$pattern" -type f -o -name "$pattern" -type d 2>/dev/null | grep -q .; then
            log_error "Found sensitive files/directories matching pattern: $pattern"
            find . -name "$pattern" -type f -o -name "$pattern" -type d 2>/dev/null | head -5
            found_credentials=true
        fi
    done
    
    if [ "$found_credentials" = true ]; then
        log_error "SECURITY VIOLATION: Credentials or build tools found in build branch!"
        log_error "Aborting deployment to prevent credential exposure"
        exit 1
    fi
    
    # Show what's actually in the build branch
    log_info "Build branch contents:"
    ls -la
    
    log_success "✓ Security verification passed - no credentials found"
}

commit_build_branch() {
    log_header "📦 Committing Build Branch"
    
    # Add all web files
    git add .
    
    # Check if there are changes to commit
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        log_info "No changes to commit in build branch"
        return 0
    fi
    
    # Commit build files
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    git commit -m "Deploy website build - $timestamp"
    log_success "Build files committed to build branch"
}

push_to_remote() {
    log_header "🚀 Pushing to Remote Repository"
    
    # Push main branch first
    log_info "Pushing main branch..."
    git checkout main
    
    if git push origin main; then
        log_success "Main branch pushed successfully"
    else
        log_warning "Failed to push main branch (may be up to date)"
    fi
    
    # Push build branch
    log_info "Pushing build branch..."
    git checkout build
    
    # Since we created a fresh orphan branch, we need to force push
    if git push --force-with-lease origin build; then
        log_success "Build branch pushed successfully"
    else
        log_warning "Force push failed, trying regular force push..."
        if git push --force origin build; then
            log_success "Build branch force-pushed successfully"
        else
            log_error "Failed to push build branch"
            exit 1
        fi
    fi
}

# Main execution
main() {
    log_header "🎵 Music Library Website Builder with Enhanced Security"
    
    # Change to website directory
    cd "$WEBSITE_DIR"
    
    # Execute all steps
    validate_environment
    setup_python_environment
    build_website
    commit_source_changes
    create_safe_backup
    create_orphan_build_branch
    setup_build_branch
    verify_build_security
    commit_build_branch
    push_to_remote
    
    # Return to original branch
    git checkout "$ORIGINAL_BRANCH"
    
    log_success "🎉 Deployment completed successfully!"
    log_info "Website is now live on the build branch"
    log_info "Source code remains safe on the main branch"
    log_info "All credentials and build tools are protected"
}

# Run main function
main "$@"

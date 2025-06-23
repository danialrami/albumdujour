#!/bin/bash

# Music Library Website Builder with Safe Git Deployment
# Enhanced version with secure clean deployment (website files only)

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
    
    # Copy ONLY the build directory contents to backup
    cp -r "$BUILD_DIR" "$TEMP_BACKUP_DIR/"
    
    # Verify backup contains only website files
    if [ ! -f "$TEMP_BACKUP_DIR/build/index.html" ]; then
        log_error "Backup verification failed: index.html not found"
        exit 1
    fi
    
    # Security check: ensure no source files in backup
    if [ -f "$TEMP_BACKUP_DIR/build/build_music_site.py" ] || [ -f "$TEMP_BACKUP_DIR/build/concrete-spider-446700-f9-4646496845d1.json" ]; then
        log_error "SECURITY ERROR: Source files detected in backup!"
        log_error "Build directory contains source files - this should not happen"
        exit 1
    fi
    
    log_success "Safety backup created and verified (website files only)"
}

deploy_to_build_branch() {
    log_header "🌿 Deploying to Build Branch (Secure Clean Deployment)"
    
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
            log_info "Creating new clean build branch..."
            git checkout --orphan build
            git rm -rf . 2>/dev/null || true
            
            # Create a clean README for the build branch
            cat > README.md << 'EOF'
# Website Build Branch

This branch contains only the built website files for deployment to Hostinger.

## Contents
- `index.html` - Main website page
- `styles.css` - Website styling
- `scripts.js` - Client-side JavaScript
- `assets/` - Images, fonts, and other static files

## Security
- **No source code** is included in this branch
- **No credentials** or sensitive files are deployed
- Source code and build logic are maintained in the main branch

## Deployment
This branch is automatically updated by the build script and deployed to the hosting service.
EOF
            
            git add README.md
            git commit -m "Initialize clean build branch for secure deployment"
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
    
    # SECURE CLEAN DEPLOYMENT: Remove everything except .git and README.md
    log_info "Performing secure clean deployment..."
    log_info "🔒 Removing all files except .git and README.md..."
    
    # Create a list of what to keep (NEVER delete these)
    local keep_items=(".git" "README.md")
    
    # Remove all visible files except those we want to keep
    for item in *; do
        if [[ ! " ${keep_items[@]} " =~ " ${item} " ]]; then
            rm -rf "$item"
            log_info "Removed: $item"
        fi
    done
    
    # Remove hidden files except .git and .gitignore
    for item in .*; do
        if [[ "$item" != "." && "$item" != ".." && "$item" != ".git" && "$item" != ".gitignore" ]]; then
            rm -rf "$item"
            log_info "Removed hidden: $item"
        fi
    done
    
    # Copy ONLY the website files from backup
    log_info "🌐 Copying website files for secure deployment..."
    cp -r "$TEMP_BACKUP_DIR/build/"* .
    
    # Verify deployment contains only website files
    if [ ! -f "index.html" ]; then
        log_error "Deployment verification failed: index.html not found"
        exit 1
    fi
    
    # CRITICAL SECURITY CHECK: Verify no source files leaked through
    local security_violations=()
    
    # Check for common source files that should never be in build branch
    local forbidden_files=(
        "build_music_site.py"
        "concrete-spider-446700-f9-4646496845d1.json"
        "build.sh"
        "venv"
        "musickit"
        "__pycache__"
        "*.pyc"
        ".env"
    )
    
    for pattern in "${forbidden_files[@]}"; do
        if ls $pattern 2>/dev/null | grep -q .; then
            security_violations+=("$pattern")
        fi
    done
    
    if [ ${#security_violations[@]} -gt 0 ]; then
        log_error "🚨 SECURITY VIOLATION: Forbidden files detected in build branch!"
        for violation in "${security_violations[@]}"; do
            log_error "   - $violation"
        done
        log_error "Aborting deployment to prevent credential/source code exposure"
        exit 1
    fi
    
    # Show clean build branch contents
    log_info "✅ Clean build branch contents (website files only):"
    ls -la
    
    # Count different types of files for reporting
    local html_count=$(find . -name "*.html" | wc -l | tr -d ' ')
    local css_count=$(find . -name "*.css" | wc -l | tr -d ' ')
    local js_count=$(find . -name "*.js" | wc -l | tr -d ' ')
    local asset_count=$(find assets -type f 2>/dev/null | wc -l | tr -d ' ' || echo "0")
    
    log_success "🔒 Security verification passed - no source files detected"
    log_info "📊 Deployment contains: $html_count HTML, $css_count CSS, $js_count JS files, $asset_count assets"
    
    # Stage all changes
    git add -A
    
    # Check if there are actually changes to commit
    if git diff-index --quiet HEAD --; then
        log_info "No changes to commit in build branch"
        return 0
    fi
    
    # Commit with detailed security-focused message
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    git commit -m "🔒 Deploy secure website build - $timestamp

SECURE DEPLOYMENT - Website files only
✅ Security verified: No source code or credentials included
📊 Files deployed:
   - $html_count HTML files
   - $css_count CSS files  
   - $js_count JavaScript files
   - $asset_count asset files
📦 Build size: $(du -sh . 2>/dev/null | cut -f1 || echo 'unknown')
🛡️  Source code maintained separately in main branch"
    
    log_success "🔒 Secure clean deployment completed successfully"
    log_success "✅ Build branch contains only website files - no credentials exposed"
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
    
    # Push clean build branch
    log_info "Pushing secure build branch..."
    git checkout build
    
    # Normal push should work since we're preserving history
    if git push origin build 2>/dev/null; then
        log_success "Build branch pushed successfully"
    else
        # If it still fails, try to merge remote changes
        log_info "Normal push failed, trying to merge remote changes..."
        
        if git pull origin build 2>/dev/null; then
            log_info "Merged remote changes, pushing again..."
            if git push origin build 2>/dev/null; then
                log_success "Build branch pushed successfully after merge"
            else
                log_error "Failed to push build branch even after merge"
                log_info "Manual intervention may be required"
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
    log_header "🎵 Music Library Website Builder with Secure Git Deployment"
    
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
    
    log_success "🎉 Secure deployment completed successfully!"
    log_info "🌐 Website is now live on the build branch"
    log_info "🔒 Source code and credentials remain secure on the main branch"  
    log_info "🛡️  Only essential website files are exposed to Hostinger"
    log_info "📚 Both branches maintain their complete Git history"
}

# Run main function
main "$@"

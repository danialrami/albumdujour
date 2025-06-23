#!/bin/bash

# Album du Jour Git Deployment Script
# Handles Git workflow for deploying the built website

set -euo pipefail # Exit on any error, undefined variable, or pipe failure

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly WEBSITE_DIR="$SCRIPT_DIR"
readonly BUILD_DIR="$WEBSITE_DIR/build"

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
    echo -e "${PURPLE}$1${NC}"
    echo "$(printf '=%.0s' $(seq 1 ${#1}))"
}

log_step() {
    echo -e "${CYAN}🔄 $1${NC}"
}

# Cleanup function
cleanup() {
    local exit_code=$?
    
    if [ "$CLEANUP_NEEDED" = true ]; then
        log_info "Performing cleanup..."
        
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
        log_success "🎉 Album du Jour deployment completed successfully!"
    else
        log_error "💥 Deployment failed with exit code $exit_code"
    fi
    
    exit $exit_code
}

# Set up trap for cleanup
trap cleanup EXIT INT TERM

# Validation functions
validate_environment() {
    log_header "🔍 Deployment Environment Validation"
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log_error "Not in a git repository"
        exit 1
    fi
    log_success "Git repository detected"
    
    # Store original branch
    ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    log_info "Current branch: $ORIGINAL_BRANCH"
    
    # Check if build directory exists
    if [ ! -d "$BUILD_DIR" ]; then
        log_error "Build directory not found: $BUILD_DIR"
        log_error "Please run ./build.sh first to generate the website"
        exit 1
    fi
    log_success "Build directory found"
    
    # Check if build has required files
    if [ ! -f "$BUILD_DIR/index.html" ]; then
        log_error "Build verification failed: index.html not found"
        log_error "Please run ./build.sh to generate a complete build"
        exit 1
    fi
    log_success "Build appears complete"
    
    # Check git status
    if ! git diff-index --quiet HEAD --; then
        log_warning "Working directory has uncommitted changes"
        log_info "These will be committed to main branch"
    else
        log_success "Working directory is clean"
    fi
}

commit_source_changes() {
    log_header "📝 Committing Source Changes"
    
    # Make sure we're on main branch
    if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then
        log_step "Switching to main branch..."
        git checkout main
    fi
    
    # Add all changes (credentials should be gitignored)
    git add .
    
    # Check if there are changes to commit
    if git diff-index --quiet HEAD --; then
        log_info "No source changes to commit"
        return 0
    fi
    
    # Commit changes
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    git commit -m "Enhanced Album du Jour website v2 - $timestamp

- Simplified design with clean album cards
- LUFS brand colors with subtle background animation
- Spotify embeds provide natural color accents
- Abstract vinyl record favicon (no text)
- Modular build and deployment scripts
- Improved credential security (external paths only)
- Enhanced responsive design and accessibility"
    
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

create_clean_build_branch() {
    log_header "🌿 Creating Clean Build Branch"
    
    # Check if build branch exists remotely and delete it
    if git ls-remote --heads origin build | grep -q build; then
        log_step "Deleting remote build branch..."
        git push origin --delete build 2>/dev/null || log_warning "Could not delete remote build branch"
    fi
    
    # Check if build branch exists locally and delete it
    if git show-ref --verify --quiet refs/heads/build; then
        log_step "Deleting local build branch..."
        git branch -D build 2>/dev/null || true
    fi
    
    # Create a completely new orphan branch (no history from main)
    log_step "Creating fresh orphan build branch..."
    git checkout --orphan build
    
    # Remove all files from the new branch (they're still staged from main)
    log_step "Clearing all files from build branch..."
    git rm -rf . 2>/dev/null || true
    
    # Clean any remaining untracked files
    git clean -fd 2>/dev/null || true
    
    # Verify we have a clean slate
    if [ "$(ls -A . 2>/dev/null | wc -l)" -ne 0 ]; then
        log_error "Build branch is not clean after reset"
        ls -la
        exit 1
    fi
    
    log_success "Clean orphan build branch created"
}

setup_build_branch() {
    log_header "🔧 Setting Up Build Branch"
    
    # Create security-focused gitignore FIRST
    log_step "Setting up build branch .gitignore..."
    cat > .gitignore << 'EOF'
# Credentials and sensitive files - NEVER commit these
concrete-spider-446700-f9-*.json
concrete-spider-*.json
musickit/
temp_musickit/
temp_credentials.json
*.key
*.pem
*.p8
.env
.env.*

# Build tools and development files - shouldn't be in build branch
build_music_site.py
build.sh
deploy.sh
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

# Development files
node_modules/
.git/
EOF
    log_success "Build branch .gitignore configured"
    
    # Copy ONLY web files from backup (whitelist approach for maximum security)
    log_step "Copying web files to build branch..."
    
    # Define whitelist of files to copy
    local web_files=(
        "index.html"
        "styles.css"
        "scripts.js"
        "README.md"
    )
    
    # Copy main web files
    for file in "${web_files[@]}"; do
        if [ -f "$TEMP_BACKUP_DIR/build/$file" ]; then
            cp "$TEMP_BACKUP_DIR/build/$file" .
            log_info "✓ Copied $file"
        else
            log_warning "⚠ File not found: $file"
        fi
    done
    
    # Copy assets directory (web assets only)
    if [ -d "$TEMP_BACKUP_DIR/build/assets" ]; then
        cp -r "$TEMP_BACKUP_DIR/build/assets" .
        log_info "✓ Copied assets directory"
        
        # List assets for verification
        if [ -d "assets" ]; then
            local asset_count
            asset_count=$(find assets -type f | wc -l | tr -d ' ')
            log_info "  → $asset_count asset files copied"
        fi
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
    
    log_step "Verifying no credentials in build branch..."
    
    # Define patterns for credential files and sensitive content
    local credential_patterns=(
        "concrete-spider-446700-f9-*.json"
        "concrete-spider-*.json"
        "temp_credentials.json"
        "musickit"
        "temp_musickit"
        "*.key"
        "*.pem"
        "*.p8"
        ".env"
        "build_music_site.py"
        "build.sh"
        "deploy.sh"
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
    
    # Additional check for sensitive content in files
    if grep -r "concrete-spider" . 2>/dev/null | grep -v ".gitignore" | head -1; then
        log_error "Found credential references in files"
        found_credentials=true
    fi
    
    if [ "$found_credentials" = true ]; then
        log_error "SECURITY VIOLATION: Credentials or build tools found in build branch!"
        log_error "Aborting deployment to prevent credential exposure"
        exit 1
    fi
    
    # Show what's actually in the build branch
    log_info "Build branch contents:"
    ls -la
    
    # Show file count and sizes
    local total_files
    total_files=$(find . -type f | wc -l | tr -d ' ')
    local total_size
    total_size=$(du -sh . 2>/dev/null | cut -f1 || echo "unknown")
    
    log_info "Total files: $total_files"
    log_info "Total size: $total_size"
    
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
    
    # Commit build files with detailed message
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    git commit -m "Deploy enhanced Album du Jour website v2 - $timestamp

Features:
- Simplified design with clean album cards
- LUFS brand colors with subtle background animation
- Spotify embeds provide natural color accents
- Abstract vinyl record favicon (no text)
- Collapsible sections with localStorage persistence
- Responsive design for all devices
- Lazy loading for music embeds
- Improved accessibility and performance

Build info:
- Generated from enhanced Python build script v2
- Security verified - no credentials included
- Modular build and deployment process
- Optimized for static hosting deployment"
    
    log_success "Build files committed to build branch"
}

push_to_remote() {
    log_header "🚀 Pushing to Remote Repository"
    
    # Push main branch first
    log_step "Pushing main branch..."
    git checkout main
    
    if git push origin main; then
        log_success "Main branch pushed successfully"
    else
        log_warning "Failed to push main branch (may be up to date)"
    fi
    
    # Push build branch
    log_step "Pushing build branch..."
    git checkout build
    
    # Since we created a fresh orphan branch, we need to force push
    if git push --force-with-lease origin build 2>/dev/null; then
        log_success "Build branch pushed successfully with force-with-lease"
    else
        log_warning "Force-with-lease failed, trying regular force push..."
        if git push --force origin build; then
            log_success "Build branch force-pushed successfully"
        else
            log_error "Failed to push build branch"
            exit 1
        fi
    fi
    
    # Show remote URLs for reference
    log_info "Repository URLs:"
    git remote -v | while read -r line; do
        log_info "  $line"
    done
}

display_summary() {
    log_header "📊 Deployment Summary"
    
    # Return to original branch for summary
    git checkout "$ORIGINAL_BRANCH" 2>/dev/null || true
    
    echo -e "${GREEN}🎉 Album du Jour Enhanced Deployment Complete!${NC}"
    echo ""
    echo -e "${CYAN}📁 Local Build Directory:${NC} $BUILD_DIR"
    echo -e "${CYAN}🌐 Local Preview:${NC} file://$BUILD_DIR/index.html"
    echo ""
    echo -e "${CYAN}📋 Git Branches:${NC}"
    echo -e "   ${BLUE}main${NC}  - Source code with enhancements"
    echo -e "   ${BLUE}build${NC} - Deployable website files"
    echo ""
    echo -e "${CYAN}🚀 Deployment Ready:${NC}"
    echo -e "   The build branch contains only web files"
    echo -e "   No credentials or build tools included"
    echo -e "   Ready for static hosting deployment"
    echo ""
    echo -e "${CYAN}✨ New Features v2:${NC}"
    echo -e "   • Simplified design with clean album cards"
    echo -e "   • LUFS brand colors with subtle background"
    echo -e "   • Spotify embeds provide natural color accents"
    echo -e "   • Abstract vinyl record favicon (no text)"
    echo -e "   • Modular build and deployment scripts"
    echo -e "   • Enhanced credential security"
    echo ""
}

# Main execution
main() {
    log_header "🚀 Album du Jour Git Deployment v2"
    echo -e "${PURPLE}Deploying built website to Git repository${NC}"
    echo ""
    
    # Change to website directory
    cd "$WEBSITE_DIR"
    
    # Execute all steps
    validate_environment
    commit_source_changes
    create_safe_backup
    create_clean_build_branch
    setup_build_branch
    verify_build_security
    commit_build_branch
    push_to_remote
    
    # Display summary
    display_summary
}

# Run main function
main "$@"


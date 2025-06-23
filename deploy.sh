#!/bin/bash

# Album du Jour Git Deployment Script v3
# Uses git subtree split for safe deployment (inspired by sync_obsidian-to-hugo.sh)

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
        
        # Clean up temporary deployment branch if it exists
        if git branch --list | grep -q 'build-deploy'; then
            git branch -D build-deploy 2>/dev/null || true
            log_success "Cleaned up temporary deployment branch"
        fi
        
        # Return to original branch if we changed it
        local current_branch
        current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
        if [ -n "$ORIGINAL_BRANCH" ] && [ "$ORIGINAL_BRANCH" != "$current_branch" ]; then
            log_info "Returning to original branch: $ORIGINAL_BRANCH"
            git checkout "$ORIGINAL_BRANCH" 2>/dev/null || log_warning "Could not return to original branch"
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
    
    # Check for remote origin
    if ! git remote | grep -q 'origin'; then
        log_error "No 'origin' remote found. Please add a remote repository."
        log_info "Example: git remote add origin https://github.com/username/repository.git"
        exit 1
    fi
    log_success "Git remote 'origin' found"
    
    # Verify no credentials in build directory
    verify_build_security
}

verify_build_security() {
    log_step "Verifying no credentials in build directory..."
    
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
    )
    
    local found_credentials=false
    
    for pattern in "${credential_patterns[@]}"; do
        if find "$BUILD_DIR" -name "$pattern" -type f -o -name "$pattern" -type d 2>/dev/null | grep -q .; then
            log_error "Found sensitive files/directories in build: $pattern"
            find "$BUILD_DIR" -name "$pattern" -type f -o -name "$pattern" -type d 2>/dev/null | head -5
            found_credentials=true
        fi
    done
    
    # Additional check for sensitive content in files
    if grep -r "concrete-spider" "$BUILD_DIR" 2>/dev/null | head -1; then
        log_error "Found credential references in build files"
        found_credentials=true
    fi
    
    if [ "$found_credentials" = true ]; then
        log_error "SECURITY VIOLATION: Credentials found in build directory!"
        log_error "Please run ./build.sh again to regenerate clean build"
        exit 1
    fi
    
    log_success "✓ Security verification passed - no credentials found in build"
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
    if git diff --cached --quiet; then
        log_info "No source changes to commit"
        return 0
    fi
    
    # Commit changes
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    git commit -m "Enhanced Album du Jour website v3 - $timestamp

- Fixed Git deployment using subtree split
- Minimal abstract favicon design
- Improved embed functionality
- Modular build and deployment scripts
- Enhanced security with external credentials"
    
    log_success "Source changes committed to main"
}

push_main_branch() {
    log_header "🚀 Pushing Main Branch"
    
    # Make sure we're on main branch
    if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then
        git checkout main
    fi
    
    log_step "Pushing main branch to origin..."
    if git push origin main; then
        log_success "Main branch pushed successfully"
    else
        log_warning "Failed to push main branch (may be up to date or need to pull first)"
        log_info "You may need to run: git pull origin main"
    fi
}

deploy_build_branch() {
    log_header "🌿 Deploying Build Branch using Subtree Split"
    
    # Make sure we're on main branch
    if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then
        git checkout main
    fi
    
    CLEANUP_NEEDED=true
    
    # Clean up any existing temporary deployment branch
    if git branch --list | grep -q 'build-deploy'; then
        log_step "Cleaning up existing temporary deployment branch..."
        git branch -D build-deploy 2>/dev/null || true
    fi
    
    # Create subtree split for build directory
    log_step "Creating subtree split for build directory..."
    if ! git subtree split --prefix build -b build-deploy; then
        log_error "Subtree split failed. Make sure the build directory is committed."
        log_info "Try running: git add . && git commit -m 'Add build files'"
        exit 1
    fi
    log_success "Subtree split created successfully"
    
    # Push the build-deploy branch to origin as 'build' branch
    log_step "Pushing build branch to origin..."
    if git push origin build-deploy:build --force; then
        log_success "Build branch pushed successfully"
    else
        log_error "Failed to push build branch"
        exit 1
    fi
    
    # Clean up temporary branch
    log_step "Cleaning up temporary deployment branch..."
    git branch -D build-deploy
    log_success "Temporary deployment branch cleaned up"
}

display_summary() {
    log_header "📊 Deployment Summary"
    
    # Return to original branch for summary
    git checkout "$ORIGINAL_BRANCH" 2>/dev/null || true
    
    echo -e "${GREEN}🎉 Album du Jour Enhanced Deployment v3 Complete!${NC}"
    echo ""
    echo -e "${CYAN}📁 Local Build Directory:${NC} $BUILD_DIR"
    echo -e "${CYAN}🌐 Local Preview:${NC} file://$BUILD_DIR/index.html"
    echo ""
    echo -e "${CYAN}📋 Git Branches:${NC}"
    echo -e "   ${BLUE}main${NC}  - Source code with enhancements"
    echo -e "   ${BLUE}build${NC} - Deployable website files (subtree split)"
    echo ""
    echo -e "${CYAN}🚀 Deployment Method:${NC}"
    echo -e "   Uses git subtree split for safe deployment"
    echo -e "   Build branch contains only website files"
    echo -e "   No credentials or source code included"
    echo ""
    echo -e "${CYAN}✨ New Features v3:${NC}"
    echo -e "   • Fixed Git deployment using subtree split"
    echo -e "   • Minimal abstract favicon design"
    echo -e "   • Enhanced embed functionality"
    echo -e "   • Improved security verification"
    echo -e "   • Repeatable deployment process"
    echo ""
    echo -e "${CYAN}🌐 Hosting:${NC}"
    echo -e "   Your hosting provider should serve from the 'build' branch"
    echo -e "   The build branch is now ready for static hosting"
    echo ""
}

# Main execution
main() {
    log_header "🚀 Album du Jour Git Deployment v3"
    echo -e "${PURPLE}Safe deployment using git subtree split${NC}"
    echo ""
    
    # Change to website directory
    cd "$WEBSITE_DIR"
    
    # Execute all steps
    validate_environment
    commit_source_changes
    push_main_branch
    deploy_build_branch
    
    # Display summary
    display_summary
}

# Run main function
main "$@"


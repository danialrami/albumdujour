#!/bin/bash

# Simplified Album du Jour Website Builder
# Focuses only on building the website, not Git management

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
readonly PYTHON_SCRIPT="$WEBSITE_DIR/build_music_site.py"
readonly VENV_DIR="$WEBSITE_DIR/venv"

# Alternative credential paths (external to repo)
readonly ALT_CREDENTIALS_PATH="/mnt/barracuda/Nextcloud/ore/Notes/Life/concrete-spider-446700-f9-4646496845d1.json"
readonly ALT_APPLE_TOKENS_PATH="/mnt/barracuda/Nextcloud/ore/Notes/Life/utilities/musickit"

# Global variables
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
        
        # Deactivate virtual environment if active
        if [ -n "${VIRTUAL_ENV:-}" ]; then
            deactivate 2>/dev/null || true
            log_success "Virtual environment deactivated"
        fi
    fi
    
    if [ $exit_code -eq 0 ]; then
        log_success "🎉 Album du Jour build completed successfully!"
        log_info "📁 Build files are in: $BUILD_DIR"
        log_info "🌐 Open $BUILD_DIR/index.html to preview"
        log_info "🚀 Use ./deploy.sh to deploy to Git repository"
    else
        log_error "💥 Build failed with exit code $exit_code"
    fi
    
    exit $exit_code
}

# Set up trap for cleanup
trap cleanup EXIT INT TERM

# Validation functions
validate_environment() {
    log_header "🔍 Environment Validation"
    
    # Check for Python script
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        log_error "Required file not found: $PYTHON_SCRIPT"
        exit 1
    fi
    log_success "Python build script found"
    
    # Check for alternative credential paths
    check_credentials
}

check_credentials() {
    log_step "Checking credential files..."
    
    # Check alternative credentials path
    if [ ! -f "$ALT_CREDENTIALS_PATH" ]; then
        log_error "Google Sheets credentials not found at: $ALT_CREDENTIALS_PATH"
        log_error "Please ensure your credentials are available at this path"
        exit 1
    else
        log_success "Google Sheets credentials found at alternative path"
    fi
    
    # Check Apple Music tokens directory (optional)
    if [ ! -d "$ALT_APPLE_TOKENS_PATH" ]; then
        log_warning "Apple Music tokens not found at: $ALT_APPLE_TOKENS_PATH"
        log_info "Continuing without Apple Music tokens"
    else
        log_success "Apple Music tokens found at alternative path"
    fi
}

setup_python_environment() {
    log_header "🐍 Python Environment Setup"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        log_step "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        log_success "Virtual environment created"
    else
        log_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    log_step "Activating virtual environment..."
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"
    CLEANUP_NEEDED=true
    log_success "Virtual environment activated"
    
    # Install/upgrade required packages
    log_step "Installing required packages..."
    pip install --quiet --upgrade pip
    pip install --quiet gspread
    log_success "All dependencies ready"
}

build_website() {
    log_header "🚀 Building Enhanced Website"
    
    # Remove old build directory
    if [ -d "$BUILD_DIR" ]; then
        log_step "Removing old build directory..."
        rm -rf "$BUILD_DIR"
    fi
    
    # Run the enhanced Python build script
    log_step "Running enhanced website build script..."
    if ! python "$PYTHON_SCRIPT"; then
        log_error "Website build failed"
        exit 1
    fi
    
    # Verify build was successful
    if [ ! -f "$BUILD_DIR/index.html" ]; then
        log_error "Build verification failed: index.html not found"
        exit 1
    fi
    
    # Verify all expected files exist
    local expected_files=("index.html" "styles.css" "scripts.js" "README.md")
    for file in "${expected_files[@]}"; do
        if [ ! -f "$BUILD_DIR/$file" ]; then
            log_warning "Expected file not found: $file"
        else
            log_success "✓ $file"
        fi
    done
    
    # Check for assets
    if [ -d "$BUILD_DIR/assets" ]; then
        log_success "Assets directory created"
        if [ -f "$BUILD_DIR/assets/favicon.svg" ]; then
            log_success "✓ Custom favicon found"
        fi
    fi
    
    # Show build statistics
    local build_size
    build_size=$(du -sh "$BUILD_DIR" 2>/dev/null | cut -f1 || echo "unknown")
    local file_count
    file_count=$(find "$BUILD_DIR" -type f | wc -l | tr -d ' ')
    
    log_success "Enhanced build completed successfully!"
    log_info "Build size: $build_size"
    log_info "Files generated: $file_count"
}

display_summary() {
    log_header "📊 Build Summary"
    
    echo -e "${GREEN}🎉 Album du Jour Enhanced Build Complete!${NC}"
    echo ""
    echo -e "${CYAN}📁 Local Build Directory:${NC} $BUILD_DIR"
    echo -e "${CYAN}🌐 Local Preview:${NC} file://$BUILD_DIR/index.html"
    echo ""
    echo -e "${CYAN}✨ New Features:${NC}"
    echo -e "   • Simplified design with clean album cards"
    echo -e "   • LUFS brand colors with subtle background animation"
    echo -e "   • Spotify embeds provide natural color accents"
    echo -e "   • Abstract vinyl record favicon (no text)"
    echo -e "   • Collapsible sections with localStorage persistence"
    echo -e "   • Responsive design for all devices"
    echo -e "   • Lazy loading and performance optimizations"
    echo ""
    echo -e "${CYAN}🚀 Next Steps:${NC}"
    echo -e "   1. Preview: Open $BUILD_DIR/index.html in your browser"
    echo -e "   2. Deploy: Run ./deploy.sh to push to Git repository"
    echo -e "   3. Customize: Modify colors or layout as needed"
    echo ""
}

# Main execution
main() {
    log_header "🎵 Album du Jour Enhanced Website Builder v2"
    echo -e "${PURPLE}Simplified build process with modular Git management${NC}"
    echo ""
    
    # Change to website directory
    cd "$WEBSITE_DIR"
    
    # Execute all steps
    validate_environment
    setup_python_environment
    build_website
    
    # Display summary
    display_summary
}

# Run main function
main "$@"


#!/bin/bash

# Album du Jour Master Build Pipeline v3
# Runs build.sh followed by deploy.sh for complete automation

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
readonly BUILD_SCRIPT="$WEBSITE_DIR/build.sh"
readonly DEPLOY_SCRIPT="$WEBSITE_DIR/deploy.sh"

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

# Validation functions
validate_environment() {
    log_header "🔍 Master Pipeline Validation"
    
    # Check if build script exists and is executable
    if [ ! -f "$BUILD_SCRIPT" ]; then
        log_error "Build script not found: $BUILD_SCRIPT"
        exit 1
    fi
    
    if [ ! -x "$BUILD_SCRIPT" ]; then
        log_error "Build script is not executable: $BUILD_SCRIPT"
        log_info "Run: chmod +x $BUILD_SCRIPT"
        exit 1
    fi
    log_success "Build script found and executable"
    
    # Check if deploy script exists and is executable
    if [ ! -f "$DEPLOY_SCRIPT" ]; then
        log_error "Deploy script not found: $DEPLOY_SCRIPT"
        exit 1
    fi
    
    if [ ! -x "$DEPLOY_SCRIPT" ]; then
        log_error "Deploy script is not executable: $DEPLOY_SCRIPT"
        log_info "Run: chmod +x $DEPLOY_SCRIPT"
        exit 1
    fi
    log_success "Deploy script found and executable"
    
    # Check if we're in a git repository (for deploy step)
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log_error "Not in a git repository"
        log_info "Initialize with: git init && git remote add origin <your-repo-url>"
        exit 1
    fi
    log_success "Git repository detected"
}

run_build_step() {
    log_header "🏗️  Step 1: Building Website"
    
    log_step "Running build script..."
    if "$BUILD_SCRIPT"; then
        log_success "Build step completed successfully"
    else
        log_error "Build step failed"
        log_info "Check the build script output above for details"
        exit 1
    fi
}

run_deploy_step() {
    log_header "🚀 Step 2: Deploying to Git"
    
    log_step "Running deploy script..."
    if "$DEPLOY_SCRIPT"; then
        log_success "Deploy step completed successfully"
    else
        log_error "Deploy step failed"
        log_info "Check the deploy script output above for details"
        exit 1
    fi
}

display_final_summary() {
    log_header "🎉 Master Pipeline Complete"
    
    echo -e "${GREEN}🎉 Album du Jour Master Build Pipeline v3 Complete!${NC}"
    echo ""
    echo -e "${CYAN}📋 Pipeline Steps Completed:${NC}"
    echo -e "   ${GREEN}✅${NC} Step 1: Website Build (build.sh)"
    echo -e "   ${GREEN}✅${NC} Step 2: Git Deployment (deploy.sh)"
    echo ""
    echo -e "${CYAN}📁 Local Files:${NC}"
    echo -e "   ${BLUE}build/${NC} - Generated website files"
    echo -e "   ${BLUE}file://$(pwd)/build/index.html${NC} - Local preview"
    echo ""
    echo -e "${CYAN}📋 Git Branches:${NC}"
    echo -e "   ${BLUE}main${NC}  - Source code with enhancements"
    echo -e "   ${BLUE}build${NC} - Deployable website files"
    echo ""
    echo -e "${CYAN}🌐 Hosting:${NC}"
    echo -e "   Your hosting provider should serve from the 'build' branch"
    echo -e "   The website is now live and ready for visitors"
    echo ""
    echo -e "${CYAN}✨ Features Deployed:${NC}"
    echo -e "   • Enhanced Album du Jour website with LUFS branding"
    echo -e "   • Simplified design with clean album cards"
    echo -e "   • Spotify embeds with natural color accents"
    echo -e "   • Minimal abstract favicon"
    echo -e "   • Collapsible sections with localStorage persistence"
    echo -e "   • Responsive design for all devices"
    echo -e "   • Lazy loading and performance optimizations"
    echo ""
    echo -e "${CYAN}🔄 Future Updates:${NC}"
    echo -e "   Run ${BLUE}./master-build.sh${NC} again to rebuild and redeploy"
    echo -e "   Or run ${BLUE}./build.sh${NC} and ${BLUE}./deploy.sh${NC} separately"
    echo ""
}

# Parse command line arguments
SKIP_DEPLOY=false
HELP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --build-only)
            SKIP_DEPLOY=true
            shift
            ;;
        --help|-h)
            HELP=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            HELP=true
            shift
            ;;
    esac
done

# Show help if requested
if [ "$HELP" = true ]; then
    echo -e "${PURPLE}Album du Jour Master Build Pipeline v3${NC}"
    echo ""
    echo -e "${CYAN}Usage:${NC}"
    echo -e "  ./master-build.sh [OPTIONS]"
    echo ""
    echo -e "${CYAN}Options:${NC}"
    echo -e "  --build-only    Run only the build step, skip deployment"
    echo -e "  --help, -h      Show this help message"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo -e "  ./master-build.sh                # Full pipeline: build + deploy"
    echo -e "  ./master-build.sh --build-only   # Build only, no deployment"
    echo ""
    echo -e "${CYAN}Individual Scripts:${NC}"
    echo -e "  ./build.sh      # Build website only"
    echo -e "  ./deploy.sh     # Deploy to Git only (requires existing build)"
    echo ""
    exit 0
fi

# Main execution
main() {
    log_header "🎵 Album du Jour Master Build Pipeline v3"
    echo -e "${PURPLE}Complete automation: build website + deploy to Git${NC}"
    echo ""
    
    # Change to website directory
    cd "$WEBSITE_DIR"
    
    # Validate environment
    validate_environment
    
    # Run build step
    run_build_step
    
    # Run deploy step (unless skipped)
    if [ "$SKIP_DEPLOY" = false ]; then
        run_deploy_step
    else
        log_info "Skipping deployment step (--build-only flag used)"
        echo ""
        log_info "To deploy later, run: ./deploy.sh"
    fi
    
    # Display final summary
    display_final_summary
}

# Run main function
main "$@"


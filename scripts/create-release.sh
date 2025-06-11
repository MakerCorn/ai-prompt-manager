#!/bin/bash

# AI Prompt Manager Release Creation Script
# This script helps create new releases with proper versioning

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
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
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]] || [[ ! -f "README.md" ]]; then
    log_error "This script must be run from the ai-prompt-manager root directory"
    exit 1
fi

# Check if git is clean
if [[ -n $(git status --porcelain) ]]; then
    log_error "Working directory is not clean. Please commit or stash your changes."
    git status --short
    exit 1
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    log_warning "You are not on the main branch (current: $CURRENT_BRANCH)"
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Release creation cancelled"
        exit 0
    fi
fi

# Get current version
CURRENT_VERSION=$(grep -E '^version = ' pyproject.toml | sed 's/version = "//; s/"//')
log_info "Current version: v$CURRENT_VERSION"

# Get version from user
echo
echo "📋 Version Format Examples:"
echo "  - Major release: 1.0.0"
echo "  - Minor release: 1.1.0" 
echo "  - Patch release: 1.0.1"
echo "  - Pre-release: 1.0.0-alpha.1, 1.0.0-beta.1, 1.0.0-rc.1"
echo

read -p "Enter new version (without 'v' prefix): " NEW_VERSION

# Validate version format
if [[ ! "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+(\.[0-9]+)?)?$ ]]; then
    log_error "Invalid version format. Use semantic versioning (e.g., 1.0.0, 1.0.0-alpha.1)"
    exit 1
fi

TAG_NAME="v$NEW_VERSION"

# Check if tag already exists
if git tag | grep -q "^$TAG_NAME$"; then
    log_error "Tag $TAG_NAME already exists"
    exit 1
fi

# Determine if it's a pre-release
IS_PRERELEASE=false
if [[ "$NEW_VERSION" =~ (alpha|beta|rc|pre) ]]; then
    IS_PRERELEASE=true
    log_warning "This will be marked as a pre-release"
fi

# Show summary
echo
echo "📋 Release Summary:"
echo "  Current version: v$CURRENT_VERSION"
echo "  New version: $TAG_NAME"
echo "  Pre-release: $IS_PRERELEASE"
echo "  Branch: $CURRENT_BRANCH"
echo

# Confirm with user
read -p "Create release $TAG_NAME? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Release creation cancelled"
    exit 0
fi

# Update pyproject.toml version
log_info "Updating pyproject.toml version..."
if command -v poetry &> /dev/null; then
    poetry version "$NEW_VERSION"
    log_success "Updated pyproject.toml to version $NEW_VERSION"
else
    # Fallback to sed if poetry is not available
    sed -i.bak "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
    rm pyproject.toml.bak
    log_success "Updated pyproject.toml to version $NEW_VERSION (using sed)"
fi

# Update version in other files if needed
if grep -q "version.*$CURRENT_VERSION" *.py 2>/dev/null; then
    log_info "Found version references in Python files..."
    for file in *.py; do
        if grep -q "version.*$CURRENT_VERSION" "$file"; then
            sed -i.bak "s/version.*$CURRENT_VERSION/version = \"$NEW_VERSION\"/" "$file"
            rm "$file.bak"
            log_success "Updated version in $file"
        fi
    done
fi

# Check if CHANGELOG.md exists and prompt for update
if [[ -f "CHANGELOG.md" ]]; then
    log_info "CHANGELOG.md found"
    echo
    echo "Please update CHANGELOG.md with the new version before continuing."
    echo "Add a section for version $NEW_VERSION with the changes in this release."
    echo
    read -p "Have you updated CHANGELOG.md? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Please update CHANGELOG.md and run this script again"
        # Restore original version
        if command -v poetry &> /dev/null; then
            poetry version "$CURRENT_VERSION"
        else
            sed -i.bak "s/version = \"$NEW_VERSION\"/version = \"$CURRENT_VERSION\"/" pyproject.toml
            rm pyproject.toml.bak
        fi
        exit 0
    fi
fi

# Commit version changes
log_info "Committing version changes..."
git add pyproject.toml CHANGELOG.md 2>/dev/null || git add pyproject.toml
git add *.py 2>/dev/null || true  # Add Python files if they were updated

if git diff --staged --quiet; then
    log_warning "No changes to commit"
else
    git commit -m "Bump version to $NEW_VERSION

🔖 Prepare for release $TAG_NAME

This commit updates the version number in preparation for the
$TAG_NAME release. The automated release workflow will build
and publish packages and Docker images.

Generated with AI Prompt Manager release script"
    log_success "Committed version changes"
fi

# Create and push tag
log_info "Creating tag $TAG_NAME..."
git tag -a "$TAG_NAME" -m "Release $TAG_NAME

🚀 AI Prompt Manager $NEW_VERSION

This release includes:
- Enhanced prompt optimization with multi-service support
- Improved multi-language interface
- Updated documentation and examples
- Security improvements and bug fixes

For detailed changes, see CHANGELOG.md

Assets:
- Python packages (wheel and source)
- Docker images (linux/amd64, linux/arm64)
- Complete source archives with installation scripts

Docker: ghcr.io/makercorn/ai-prompt-manager:$TAG_NAME

Generated automatically by release workflow"

log_success "Created tag $TAG_NAME"

# Push changes and tag
log_info "Pushing changes and tag to origin..."
git push origin "$CURRENT_BRANCH"
git push origin "$TAG_NAME"
log_success "Pushed changes and tag to origin"

echo
log_success "Release $TAG_NAME created successfully!"
echo
echo "🚀 What happens next:"
echo "  1. GitHub Actions will automatically start the release workflow"
echo "  2. Tests will be run to validate the release"
echo "  3. Python packages will be built and uploaded"
echo "  4. Docker images will be built and pushed to GHCR"
echo "  5. A GitHub release will be created with all artifacts"
echo
echo "📋 Monitor progress:"
echo "  https://github.com/$(git remote get-url origin | sed 's/.*github\.com[:/]\([^.]*\)\.git/\1/')/actions"
echo
echo "🐳 Docker image will be available at:"
echo "  ghcr.io/makercorn/ai-prompt-manager:$TAG_NAME"
echo
if [[ "$IS_PRERELEASE" == "true" ]]; then
    log_warning "This is a pre-release and will be marked as such on GitHub"
else
    echo "📦 This release will also be tagged as 'stable' and 'latest'"
fi
echo
log_info "Release creation complete! 🎉"
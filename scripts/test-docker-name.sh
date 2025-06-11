#!/bin/bash

# Test Docker image name conversion script
# This simulates the GitHub Actions lowercase conversion

echo "🐳 Testing Docker Image Name Conversion"
echo "========================================"

# Test cases
test_repos=(
    "MakerCorn/ai-prompt-manager"
    "makercorn/ai-prompt-manager"
    "UPPERCASE/repo-name"
    "MixedCase/AI-Prompt-Manager"
)

echo "📋 Test Cases:"
for repo in "${test_repos[@]}"; do
    lowercase_repo=$(echo "$repo" | tr '[:upper:]' '[:lower:]')
    
    echo "  Original:  $repo"
    echo "  Lowercase: $lowercase_repo"
    echo "  Docker:    ghcr.io/$lowercase_repo:latest"
    echo ""
done

echo "✅ All repository names have been converted to lowercase format"
echo "🔧 This ensures compatibility with Docker registry requirements"

# Test the specific repository name that was causing issues
echo "🎯 Specific Test for Current Repository:"
original="MakerCorn/ai-prompt-manager"
converted=$(echo "$original" | tr '[:upper:]' '[:lower:]')

echo "  Original failing format: ghcr.io/$original:v0.1.0"
echo "  Fixed working format:    ghcr.io/$converted:v0.1.0"

if [[ "$converted" == "makercorn/ai-prompt-manager" ]]; then
    echo "  ✅ Conversion successful!"
else
    echo "  ❌ Conversion failed!"
    exit 1
fi

echo ""
echo "🚀 Docker commands that will now work:"
echo "  docker pull ghcr.io/$converted:latest"
echo "  docker run -p 7860:7860 ghcr.io/$converted:latest"
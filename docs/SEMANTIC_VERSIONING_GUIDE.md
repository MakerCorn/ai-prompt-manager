# Semantic Versioning Release Guide

This guide explains how to use the new semantic versioning release workflow for the AI Prompt Manager project.

## 🎯 Overview

The AI Prompt Manager now uses semantic versioning with automatic version bumping, making releases more predictable and following industry standards.

## 📋 Version Types

| Type | Description | Example | When to Use |
|------|-------------|---------|-------------|
| **Patch** | Bug fixes, small improvements | `0.3.2` → `0.3.3` | Bug fixes, documentation updates, minor improvements |
| **Minor** | New features, backwards compatible | `0.3.2` → `0.4.0` | New features, enhancements, API additions |
| **Major** | Breaking changes | `0.3.2` → `1.0.0` | Breaking API changes, major architecture changes |

## 🚀 How to Create a Release

### Step 1: Prepare Your Changes
1. Ensure all your code is committed and pushed to the `main` branch
2. Update the `CHANGELOG.md` with your changes in the `[Unreleased]` section
3. Test your changes locally and via CI/CD

### Step 2: Trigger the Release
1. Go to **GitHub Actions** in your repository
2. Click on **"Semantic Version Release"** workflow
3. Click **"Run workflow"** button
4. Select your parameters:
   - **Branch**: `main` (usually pre-selected)
   - **Version bump type**: Choose `patch`, `minor`, or `major`
   - **Pre-release**: Check if this is a pre-release (beta, alpha, etc.)
   - **Draft**: Check if you want to create a draft release first

### Step 3: Monitor the Release
The workflow will automatically:
1. ✅ Calculate the new version number
2. ✅ Update `pyproject.toml` with the new version
3. ✅ Extract and format changelog content
4. ✅ Create a git tag and commit the version bump
5. ✅ Build Python packages and Docker images
6. ✅ Publish to PyPI (for stable releases)
7. ✅ Create a GitHub release with comprehensive notes
8. ✅ Sign Docker images with Cosign for security

## 📦 What Gets Created

### Python Package
- **PyPI Package**: `pip install promptman==NEW_VERSION`
- **Wheel and Source**: Available as release assets

### Docker Images
- **Versioned**: `ghcr.io/makercorn/ai-prompt-manager:vX.Y.Z`
- **Latest**: `ghcr.io/makercorn/ai-prompt-manager:latest`
- **Stable**: `ghcr.io/makercorn/ai-prompt-manager:stable` (for non-pre-releases)

### GitHub Release
- **Release Notes**: Auto-generated with changelog content
- **Assets**: Python packages and checksums
- **Documentation Links**: Automatically linked to docs

## 🎯 Best Practices

### Before Creating a Release
- [ ] All tests are passing
- [ ] Documentation is updated
- [ ] CHANGELOG.md has entries in the `[Unreleased]` section
- [ ] Breaking changes are documented
- [ ] API changes are tested

### Choosing Version Types
```bash
# Patch (0.3.2 → 0.3.3) - Use for:
- Bug fixes
- Documentation updates
- Performance improvements (non-breaking)
- Security patches

# Minor (0.3.2 → 0.4.0) - Use for:
- New features
- New API endpoints
- New configuration options
- Deprecations (with backwards compatibility)

# Major (0.3.2 → 1.0.0) - Use for:
- Breaking API changes
- Major architecture changes
- Removed functionality
- Changed default behavior
```

### Pre-releases and Drafts
- **Pre-release**: Use for beta versions, release candidates
  - Creates release but marks as pre-release
  - Does not publish to PyPI
  - Good for testing before stable release

- **Draft**: Use for testing the release process
  - Creates draft release (not visible to public)
  - Does not publish to PyPI
  - Good for validating release notes and assets

## 🔍 Troubleshooting

### Common Issues

**"No changelog content found"**
- Make sure you have a section starting with `## [Unreleased]` in CHANGELOG.md
- Add your changes under this section before releasing

**"Version already exists"**
- Check if the calculated version already has a git tag
- You may need to manually create a patch release or choose a different version type

**"PyPI publishing failed"**
- Check that PYPI_API_TOKEN secret is configured
- Verify the package name and version don't already exist on PyPI

**"Docker build failed"**
- Check the Dockerfile is valid
- Ensure all required files are present in the repository

### Getting Help
- Check the workflow logs in GitHub Actions
- Review the [GitHub Issues](https://github.com/MakerCorn/ai-prompt-manager/issues) for similar problems
- Create a new issue if you encounter problems

## 📖 Examples

### Creating a Patch Release
You fixed a bug in the prompt optimization feature:

1. Update CHANGELOG.md:
   ```markdown
   ## [Unreleased] - Bug Fixes
   
   ### 🐛 Bug Fixes
   - Fixed prompt optimization timeout issue
   - Corrected token calculation for large prompts
   ```

2. Go to Actions → Semantic Version Release → Run workflow
3. Select: `patch` (0.3.2 → 0.3.3)
4. Result: New version 0.3.3 with bug fixes

### Creating a Minor Release
You added a new AI service integration:

1. Update CHANGELOG.md:
   ```markdown
   ## [Unreleased] - New Features
   
   ### 🚀 New Features
   - Added Claude 3.5 Sonnet integration
   - New prompt template system
   - Enhanced multi-language support
   ```

2. Go to Actions → Semantic Version Release → Run workflow
3. Select: `minor` (0.3.2 → 0.4.0)
4. Result: New version 0.4.0 with new features

### Creating a Major Release
You made breaking changes to the API:

1. Update CHANGELOG.md:
   ```markdown
   ## [Unreleased] - Breaking Changes
   
   ### 💥 Breaking Changes
   - API v2 with new endpoint structure
   - Changed authentication method
   - Removed deprecated features
   
   ### 🚀 New Features
   - Complete API redesign
   - Better performance and security
   ```

2. Go to Actions → Semantic Version Release → Run workflow
3. Select: `major` (0.3.2 → 1.0.0)
4. Result: New version 1.0.0 with breaking changes

---

This semantic versioning system makes releases predictable, automated, and follows industry best practices for version management.
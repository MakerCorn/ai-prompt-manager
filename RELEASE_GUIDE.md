# 🚀 AI Prompt Manager Release Guide

Complete guide for creating and managing releases of the AI Prompt Manager project.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Release](#quick-release)
- [Release Types](#release-types)
- [Release Process](#release-process)
- [Artifacts](#artifacts)
- [Troubleshooting](#troubleshooting)

---

## 🔍 Overview

The AI Prompt Manager uses automated GitHub Actions workflows to create comprehensive releases that include:

- **Python Packages**: Wheel and source distributions
- **Docker Images**: Multi-platform containers (linux/amd64, linux/arm64)
- **Source Archives**: Complete source code with installation scripts
- **Documentation**: Release manifests and installation guides

All releases are:
- ✅ **Tested**: Comprehensive test suite before release
- ✅ **Secure**: SHA256 checksums and signed Docker images
- ✅ **Reproducible**: Deterministic build process
- ✅ **Documented**: Complete release notes and installation guides

---

## ⚡ Quick Release

### Using the Release Script (Recommended)

```bash
# Run the interactive release script
./scripts/create-release.sh

# Follow the prompts to:
# 1. Enter new version number
# 2. Confirm version and type
# 3. Update CHANGELOG.md
# 4. Automatic commit, tag, and push
```

### Manual Release

```bash
# Update version and create tag
poetry version 1.0.0
git add pyproject.toml
git commit -m "Bump version to 1.0.0"
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

---

## 🎯 Release Types

### Stable Releases
```bash
v1.0.0    # Major release
v1.1.0    # Minor release  
v1.0.1    # Patch release
```

### Pre-releases
```bash
v1.0.0-alpha.1    # Alpha release
v1.0.0-beta.1     # Beta release
v1.0.0-rc.1       # Release candidate
```

### Docker Tags
| Release Type | Docker Tags |
|--------------|-------------|
| **Stable** | `latest`, `stable`, `v1.0.0` |
| **Pre-release** | `v1.0.0-alpha.1` (no latest/stable) |

---

## 📋 Release Process

### 1. Preparation

**Check Requirements:**
- [ ] All changes committed and pushed
- [ ] Working directory clean (`git status`)
- [ ] On main branch (recommended)
- [ ] Tests passing locally

**Update Documentation:**
- [ ] Update `CHANGELOG.md` with new version
- [ ] Update `README.md` if needed
- [ ] Update version in `pyproject.toml`

### 2. Version Selection

Follow semantic versioning (SemVer):

- **Major (X.0.0)**: Breaking changes, new architecture
- **Minor (1.X.0)**: New features, backward compatible
- **Patch (1.0.X)**: Bug fixes, small improvements

### 3. Create Release

**Option A: Release Script**
```bash
./scripts/create-release.sh
```

**Option B: Manual Process**
```bash
# Update version
poetry version 1.0.0

# Commit version bump
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to 1.0.0"

# Create and push tag
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

### 4. Monitor Release

1. **GitHub Actions**: Monitor workflow progress
   - Go to: `https://github.com/YOUR_REPO/actions`
   - Watch the "Release" workflow

2. **Release Artifacts**: Check automated creation
   - Python packages in release assets
   - Docker images in GitHub Container Registry
   - Release notes generated automatically

### 5. Verification

**Test Docker Image:**
```bash
# Pull and test the new release
docker pull ghcr.io/makercorn/ai-prompt-manager:v1.0.0
docker run -p 7860:7860 ghcr.io/makercorn/ai-prompt-manager:v1.0.0
curl http://localhost:7860/api/health
```

**Test Python Package:**
```bash
# Test PyPI installation
pip install promptman
python -m promptman --help

# Or download and test source installation
wget https://github.com/YOUR_REPO/releases/download/v1.0.0/ai-prompt-manager-v1.0.0.tar.gz
tar -xzf ai-prompt-manager-v1.0.0.tar.gz
cd release-dist
./install.sh
```

---

## 📦 Release Artifacts

### Python Packages
- **Wheel**: `promptman-1.0.0-py3-none-any.whl`
- **Source**: `promptman-1.0.0.tar.gz`

### Docker Images
- **Registry**: `ghcr.io/makercorn/ai-prompt-manager`
- **Platforms**: `linux/amd64`, `linux/arm64`
- **Tags**: `latest`, `stable`, `v1.0.0`

### Source Archives
- **Complete Package**: `ai-prompt-manager-v1.0.0.tar.gz`
- **ZIP Archive**: `ai-prompt-manager-v1.0.0.zip`
- **Installation Script**: `install.sh`

### Documentation
- **Release Manifest**: Build information and checksums
- **Docker Manifest**: Container information and usage
- **Release Notes**: Automated GitHub release description

---

## 🛠️ Troubleshooting

### Common Issues

**❌ Release Script Fails**
```bash
# Check working directory is clean
git status

# Ensure you're on the right branch
git branch --show-current

# Verify permissions
chmod +x scripts/create-release.sh
```

**❌ GitHub Actions Fails**
- Check workflow logs in GitHub Actions tab
- Verify no syntax errors in workflow files
- Ensure GITHUB_TOKEN has required permissions

**❌ Docker Build Fails**
- Check Dockerfile syntax
- Verify all dependencies are available
- Test local Docker build: `docker build -t test .`

**❌ Docker Registry Name Error**
```
invalid reference format: repository name must be lowercase
```
- This is automatically handled by the release workflow
- Repository names are converted to lowercase (e.g., `MakerCorn/ai-prompt-manager` → `makercorn/ai-prompt-manager`)
- Test locally: `./scripts/test-docker-name.sh`

**❌ Version Conflicts**
```bash
# Check if tag already exists
git tag | grep v1.0.0

# Delete tag if needed (DANGEROUS)
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```

### Recovery Procedures

**Failed Release (Before Assets)**
```bash
# Delete tag and retry
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# Fix issues and recreate
./scripts/create-release.sh
```

**Failed Release (After Assets)**
- Use GitHub web interface to edit/delete release
- Manual cleanup may be required
- Consider creating a patch release

---

## 🔧 Advanced Configuration

### Customizing Release Notes

Edit `.github/workflows/release.yml` to modify:
- Release note templates
- Asset organization
- Additional build steps

### Custom Release Triggers

Add manual triggers for special releases:
```yaml
workflow_dispatch:
  inputs:
    version:
      description: 'Release version'
      required: true
    prerelease:
      description: 'Pre-release'
      type: boolean
```

### Environment-Specific Releases

Create environment-specific tags:
```bash
git tag staging-v1.0.0    # Staging release
git tag production-v1.0.0 # Production release
```

---

## 📚 Resources

- **GitHub Actions**: [Release Workflow](.github/workflows/release.yml)
- **Docker Registry**: [GHCR Packages](https://github.com/makercorn/ai-prompt-manager/packages)
- **Release History**: [GitHub Releases](https://github.com/makercorn/ai-prompt-manager/releases)
- **Workflow Setup**: [GITHUB_WORKFLOWS_SETUP.md](GITHUB_WORKFLOWS_SETUP.md)

---

## 🎉 Success Checklist

After a successful release, verify:

- [ ] GitHub release created with correct version
- [ ] Python packages available in release assets
- [ ] Docker images available in GHCR
- [ ] Release notes generated and accurate
- [ ] All checksums and signatures valid
- [ ] Installation scripts work correctly
- [ ] Documentation updated

---

**🚀 Happy Releasing! The automated system handles the complexity so you can focus on building great features.**
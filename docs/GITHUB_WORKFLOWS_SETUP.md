# GitHub Workflows Setup Guide

This guide covers the complete setup and configuration of GitHub Actions workflows for the AI Prompt Manager project.

## Overview

The project uses three main workflows:

- **Build and Publish Package** - Builds and tests packages on every push
- **Test and Validation** - Runs comprehensive tests (358 passing tests) after successful builds with unit test coverage
- **Release** - Handles automated releases with advanced draft and pre-release modes, Docker multi-platform builds, and Sigstore/Cosign signing

## Release Workflow Advanced Features

### Release Behavior Matrix

| Mode | Pre-release | Draft | Python Build | Docker Build | Docker Push | PyPI Push | GitHub Release |
|------|-------------|-------|--------------|--------------|-------------|-----------|----------------|
| **Draft only** | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Pre-release + Draft** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Pre-release only** | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Normal release** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |

### Manual Release Parameters

```yaml
inputs:
  version:
    description: 'Release version (e.g., v1.0.0)'
    required: true
    type: string
  prerelease:
    description: 'Pre-release'
    required: false
    type: boolean
    default: false
  draft:
    description: 'Draft mode (mock release, no PyPI push)'
    required: false
    type: boolean
    default: false
```

## Required Secrets

### Repository Secrets

```bash
# PyPI Publishing (Required for stable releases)
PYPI_API_TOKEN=pypi-...

# GitHub Token (Automatically provided)
GITHUB_TOKEN=ghp_... # Auto-generated, no setup needed
```

## Usage Examples

### 1. Draft Mode Testing
```bash
# Via GitHub UI: Actions → Release → Run workflow
- Version: v1.2.3
- Pre-release: false
- Draft: true
# Result: Only builds Python packages for testing
```

### 2. Pre-release with Docker Testing
```bash
- Version: v1.2.3-beta.1
- Pre-release: true
- Draft: true
# Result: Builds Python + Docker images, no publishing
```

### 3. Stable Release
```bash
- Version: v1.2.3
- Pre-release: false
- Draft: false
# Result: Full pipeline - PyPI + Docker + GitHub release
```

## Workflow Jobs

### Release Pipeline Jobs

1. **validate-release** - Version validation and type determination
2. **test-before-release** - Comprehensive testing suite
3. **build-python-package** - Always builds Python packages
4. **publish-to-pypi** - Only for stable releases (`!prerelease && !draft`)
5. **build-docker-image** - Conditional building and pushing
6. **create-github-release** - Creates releases when `!draft`
7. **validate-release-artifacts** - Final validation and testing

### Conditional Logic

- **Docker Build**: Skipped when `draft=true AND prerelease=false`
- **Docker Push**: Only when `draft=false`
- **PyPI Publish**: Only when `prerelease=false AND draft=false`
- **GitHub Release**: Only when `draft=false`

## Monitoring

Monitor workflows at: `https://github.com/YOUR_ORG/ai-prompt-manager/actions`

## Best Practices

1. **Test with Draft Mode**: Always test releases in draft mode first
2. **Use Pre-releases**: For beta testing and validation
3. **Version Consistency**: Keep pyproject.toml version updated
4. **Documentation**: Update CHANGELOG.md before releases
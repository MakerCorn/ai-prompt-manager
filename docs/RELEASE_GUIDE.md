# Release Guide

This guide covers how to create releases for the AI Prompt Manager project using the advanced release pipeline.

## Release Types

### 1. Draft Mode (Testing Only)
- **Purpose**: Test release process without publishing
- **Builds**: Python packages only
- **Publishes**: Nothing
- **Use Case**: Validate release process, test package building

### 2. Pre-release + Draft (Full Testing)
- **Purpose**: Test complete release including Docker builds
- **Builds**: Python packages + Docker images
- **Publishes**: Nothing (builds but doesn't push)
- **Use Case**: Validate Docker builds, test complete pipeline

### 3. Pre-release (Beta/RC)
- **Purpose**: Release beta versions for testing
- **Builds**: Python packages + Docker images
- **Publishes**: Docker images to GHCR, GitHub release
- **Skips**: PyPI publishing
- **Use Case**: Beta testing, release candidates

### 4. Stable Release
- **Purpose**: Production release
- **Builds**: Python packages + Docker images
- **Publishes**: PyPI package, Docker images, GitHub release
- **Use Case**: Production deployments

## Creating Releases

### Method 1: Manual Workflow Dispatch

1. Go to **Actions** → **Release** → **Run workflow**
2. Fill in parameters:
   - **Version**: `v1.2.3` (semantic versioning)
   - **Pre-release**: Check for beta/RC versions
   - **Draft**: Check for testing without publishing
3. Click **Run workflow**

### Method 2: Git Tag Push

```bash
# Create and push tag (triggers automatic release)
git tag v1.2.3
git push origin v1.2.3

# For pre-release versions
git tag v1.2.3-beta.1
git push origin v1.2.3-beta.1
```

### Method 3: GitHub Release Creation

1. Go to **Releases** → **Create a new release**
2. Choose tag or create new tag
3. Mark as pre-release if needed
4. Publish release (triggers workflow)

## Release Process Steps

### Pre-Release Checklist

1. **Update Version**:
   ```bash
   # Update pyproject.toml version
   poetry version 1.2.3
   ```

2. **Update Documentation**:
   - Update `CHANGELOG.md` with new version
   - Review and update `README.md` if needed
   - Update any version references

3. **Test Locally**:
   ```bash
   # Run tests
   poetry run python -m pytest tests/
   
   # Test new architecture
   poetry run python tests/integration/test_new_prompt_architecture.py
   
   # Test launcher
   poetry run python run.py --help
   ```

4. **Commit Changes**:
   ```bash
   git add .
   git commit -m "Prepare for release v1.2.3"
   git push origin main
   ```

### Release Execution

#### Option A: Test First (Recommended)

1. **Draft Mode Test**:
   - Version: `v1.2.3`
   - Pre-release: `false`
   - Draft: `true`
   - **Result**: Tests Python package building

2. **Full Pipeline Test** (if using Docker):
   - Version: `v1.2.3`
   - Pre-release: `true`
   - Draft: `true`
   - **Result**: Tests complete pipeline without publishing

3. **Actual Release**:
   - Version: `v1.2.3`
   - Pre-release: `false`
   - Draft: `false`
   - **Result**: Full production release

#### Option B: Direct Release

1. **Stable Release**:
   - Version: `v1.2.3`
   - Pre-release: `false`
   - Draft: `false`
   - **Result**: Direct to production

### Post-Release Verification

1. **Check PyPI**: https://pypi.org/project/promptman/
2. **Check Docker**: https://github.com/YOUR_ORG/ai-prompt-manager/pkgs/container/ai-prompt-manager
3. **Check GitHub Release**: https://github.com/YOUR_ORG/ai-prompt-manager/releases
4. **Test Installation**:
   ```bash
   # Test PyPI installation
   pip install promptman==1.2.3
   
   # Test Docker image
   docker run ghcr.io/YOUR_ORG/ai-prompt-manager:v1.2.3
   ```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **Major** (`1.0.0`): Breaking changes
- **Minor** (`1.1.0`): New features, backward compatible
- **Patch** (`1.0.1`): Bug fixes, backward compatible

### Pre-release Versions

- **Alpha**: `1.0.0-alpha.1` (early development)
- **Beta**: `1.0.0-beta.1` (feature complete, testing)
- **RC**: `1.0.0-rc.1` (release candidate)

## Troubleshooting

### Common Issues

1. **PyPI Publishing Fails**:
   - Check `PYPI_API_TOKEN` secret
   - Verify version doesn't already exist
   - Check package name conflicts

2. **Docker Build Fails**:
   - Review Dockerfile syntax
   - Check base image availability
   - Verify build context

3. **Version Mismatch**:
   - Ensure pyproject.toml version matches tag
   - Update version before creating release

### Recovery Steps

1. **Failed Release**:
   - Delete failed tag: `git tag -d v1.2.3 && git push origin :refs/tags/v1.2.3`
   - Fix issues and retry

2. **Partial Release**:
   - Check which components succeeded
   - Manually complete missing steps if needed

## Monitoring

- **Workflow Status**: GitHub Actions tab
- **Release Assets**: GitHub Releases page
- **Package Status**: PyPI project page
- **Docker Images**: GitHub Container Registry

## Best Practices

1. **Always Test First**: Use draft mode for testing
2. **Document Changes**: Update CHANGELOG.md
3. **Version Consistency**: Keep all version references in sync
4. **Backup Strategy**: Tag important commits
5. **Communication**: Announce releases to users
6. **Rollback Plan**: Know how to revert if needed

## Emergency Procedures

### Hotfix Release

1. Create hotfix branch from release tag
2. Apply minimal fix
3. Test thoroughly
4. Create patch release (e.g., `v1.2.4`)
5. Merge back to main

### Release Rollback

1. **PyPI**: Cannot delete, create new version
2. **Docker**: Update tags to previous version
3. **GitHub**: Mark release as pre-release or draft
4. **Communication**: Notify users of issues

This release process ensures reliable, tested releases while providing flexibility for different deployment scenarios.
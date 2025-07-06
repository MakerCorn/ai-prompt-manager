# PyPI Trusted Publishing Setup Guide

This guide explains how to configure PyPI Trusted Publishing for secure, token-free package publishing directly from GitHub Actions.

## Overview

Trusted Publishing allows GitHub Actions to publish packages to PyPI without storing API tokens as secrets. It uses OpenID Connect (OIDC) to authenticate the workflow with PyPI based on the repository, workflow, and environment configuration.

## Benefits

✅ **Enhanced Security**: No API tokens stored in GitHub secrets  
✅ **Simplified Management**: No token rotation or expiration concerns  
✅ **Audit Trail**: Better traceability of publish operations  
✅ **Zero Configuration**: No secrets to manage after initial setup  

## Prerequisites

- Repository owner or admin access to configure PyPI project
- Package already published to PyPI (for existing projects)
- GitHub repository with release workflow configured

## Setup Steps

### 1. Configure PyPI Project

1. **Log in to PyPI**: Go to [pypi.org](https://pypi.org) and sign in
2. **Navigate to Project**: Go to your project page (e.g., https://pypi.org/project/promptman/)
3. **Access Management**: Click "Manage" → "Publishing"
4. **Add Trusted Publisher**: Click "Add a new pending publisher"

### 2. Configure Publisher Details

Fill in the trusted publisher configuration:

```yaml
# Publisher Configuration
Repository owner: MakerCorn  # Your GitHub username/org
Repository name: ai-prompt-manager  # Your repository name
Workflow filename: release.yml  # Path: .github/workflows/release.yml
Environment name: pypi  # Must match workflow environment name
```

**Important**: The environment name must exactly match what's specified in your workflow file.

### 3. Verify Workflow Configuration

Ensure your GitHub workflow includes the correct configuration:

```yaml
publish-to-pypi:
  name: Publish to PyPI (Trusted Publishing)
  runs-on: ubuntu-latest
  environment: 
    name: pypi  # Must match PyPI publisher configuration
    url: https://pypi.org/p/${{ needs.build-python-package.outputs.package-name }}
  permissions:
    contents: read
    packages: write
    id-token: write  # MANDATORY for trusted publishing
  
  steps:
  - name: Publish to PyPI using Trusted Publishing
    uses: pypa/gh-action-pypi-publish@release/v1
    with:
      verbose: true
      print-hash: true
```

### 4. Repository Environment Setup

1. Go to your GitHub repository
2. Navigate to **Settings** → **Environments**
3. Create or configure the `pypi` environment
4. **Optional**: Add protection rules (recommended for production)

### 5. Required Permissions

The workflow must include these specific permissions:

```yaml
permissions:
  contents: read      # Read repository contents
  packages: write     # Publish to GitHub Packages
  id-token: write     # CRITICAL: Required for OIDC authentication
```

## Workflow Integration

### Complete Publishing Job Example

```yaml
publish-to-pypi:
  name: Publish to PyPI (Trusted Publishing)
  runs-on: ubuntu-latest
  needs: [version-bump, build-python-package]
  if: github.event.inputs.prerelease == 'false' && github.event.inputs.draft == 'false'
  environment: 
    name: pypi
    url: https://pypi.org/p/${{ needs.build-python-package.outputs.package-name }}
  permissions:
    contents: read
    packages: write
    id-token: write
  
  steps:
  - name: Download package artifacts
    uses: actions/download-artifact@v4
    with:
      name: python-packages-${{ needs.version-bump.outputs.new_version }}
      path: ./dist

  - name: Verify package contents
    run: |
      echo "📦 Built packages:"
      ls -la dist/
      python -m pip install twine
      twine check dist/*

  - name: Publish to PyPI using Trusted Publishing
    uses: pypa/gh-action-pypi-publish@release/v1
    with:
      verbose: true
      print-hash: true
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify environment name matches exactly
   - Check repository owner/name spelling
   - Ensure workflow file path is correct

2. **Missing id-token Permission**
   ```yaml
   permissions:
     id-token: write  # This is mandatory
   ```

3. **Wrong Environment Name**
   - PyPI configuration: `pypi`
   - Workflow configuration: `environment: { name: pypi }`
   - Must match exactly (case-sensitive)

4. **Workflow File Path**
   - Use relative path from `.github/workflows/`
   - Example: `release.yml` (not `.github/workflows/release.yml`)

### Validation Steps

1. **Check PyPI Configuration**: Verify trusted publisher is configured correctly
2. **Test Workflow**: Run the workflow and check for OIDC authentication success
3. **Review Logs**: Check workflow logs for detailed error messages
4. **Verify Artifacts**: Ensure packages are built correctly before publishing

## Security Considerations

### Best Practices

- **Environment Protection**: Enable environment protection rules for production
- **Branch Restrictions**: Limit publishing to main/release branches only
- **Required Reviewers**: Add required reviewers for sensitive environments
- **Deployment Rules**: Configure deployment rules for additional security

### Environment Protection Example

```yaml
# GitHub Environment Configuration
Environment: pypi
Protection Rules:
  - Required reviewers: [maintainer-team]
  - Wait timer: 0 minutes
  - Deployment branches: Selected branches [main]
```

## Migration from API Tokens

If migrating from API token authentication:

1. **Set up Trusted Publishing** (follow steps above)
2. **Test with Pre-release**: Test the configuration with a pre-release
3. **Remove API Token**: Delete `PYPI_API_TOKEN` secret after successful test
4. **Update Documentation**: Update any references to token-based publishing

## Support Resources

- [PyPI Trusted Publishing Documentation](https://docs.pypi.org/trusted-publishers/)
- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [PyPA Publish Action](https://github.com/pypa/gh-action-pypi-publish)

## Configuration Summary

| Component | Configuration | Notes |
|-----------|---------------|-------|
| **PyPI Project** | Add trusted publisher | Use repository details |
| **Workflow Environment** | `name: pypi` | Must match PyPI config |
| **Permissions** | `id-token: write` | Required for OIDC |
| **Publishing Action** | `pypa/gh-action-pypi-publish@release/v1` | Latest stable version |
| **Repository Settings** | Environment protection | Optional but recommended |

---

**✅ Setup Complete**: Once configured, your releases will automatically publish to PyPI without requiring API tokens, providing enhanced security and simplified maintenance.
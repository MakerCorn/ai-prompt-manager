# GitHub Workflows Setup Guide

Complete guide for setting up automated Docker builds and deployments using GitHub Actions for the AI Prompt Manager project.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Repository Setup](#repository-setup)
- [Workflow Configuration](#workflow-configuration)
- [Security Setup](#security-setup)
- [Testing Workflows](#testing-workflows)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

---

## 🔍 Overview

This project includes three automated GitHub workflows:

1. **🧪 Test and Validation** (`test.yml`) - Runs tests on every push and PR
2. **🐳 Docker Image Build** (`docker-image.yml`) - Builds and publishes Docker images
3. **📦 Release Management** (`release.yml`) - Creates releases and updates documentation

### Workflow Triggers

| Workflow | Trigger | Action |
|----------|---------|--------|
| **Test** | PR to `main`, Push to `main` | Run tests, validate code |
| **Docker Build** | Push to `main`, Version tags | Build and push images |
| **Release** | Version tags (`v*.*.*`) | Create GitHub release |

---

## ✅ Prerequisites

Before setting up workflows, ensure you have:

- [x] GitHub repository with admin access
- [x] Docker Hub account (optional, using GitHub Container Registry)
- [x] Basic understanding of GitHub Actions
- [x] Project files including `Dockerfile` and `pyproject.toml`

---

## 🚀 Repository Setup

### 1. **Fork or Create Repository**

```bash
# Clone the repository
git clone https://github.com/your-username/ai-prompt-manager.git
cd ai-prompt-manager

# Or create new repository and add files
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/ai-prompt-manager.git
git push -u origin main
```

### 2. **Enable GitHub Actions**

1. Navigate to your GitHub repository
2. Go to **Settings** → **Actions** → **General**
3. Under "Actions permissions", select:
   - ✅ **Allow all actions and reusable workflows**
4. Under "Workflow permissions", select:
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**

### 3. **Repository Settings**

Configure these repository settings:

**Pages (Optional):**
- Go to **Settings** → **Pages**
- Source: **Deploy from a branch**
- Branch: `main` or `gh-pages`

**Security:**
- Go to **Settings** → **Security**
- Enable **Dependency graph**
- Enable **Dependabot alerts**

---

## ⚙️ Workflow Configuration

### 1. **Create Workflow Directory**

```bash
mkdir -p .github/workflows
```

### 2. **Test Workflow (`test.yml`)**

This workflow runs comprehensive tests on every push and pull request.

<details>
<summary>📄 View complete test.yml configuration</summary>

```yaml
name: Test and Validation

on:
  pull_request:
    branches: [ "main" ]
  push:
    branches: [ "main" ]

jobs:
  test-python:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          virtualenvs-create: true
          virtualenvs-in-project: true

      - name: Load cached venv
        id: cached-poetry-dependencies
        uses: actions/cache@v3
        with:
          path: .venv
          key: venv-${{ runner.os }}-${{ steps.setup-python.outputs.python-version }}-${{ hashFiles('**/poetry.lock') }}

      - name: Install dependencies
        if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
        run: poetry install --no-interaction --no-root

      - name: Install project
        run: poetry install --no-interaction

      - name: Run LangWatch integration tests
        run: poetry run python test_langwatch_integration.py

      - name: Test standalone API
        run: |
          # Start the API in background
          poetry run python -c "
          import uvicorn
          from api_endpoints import get_api_app
          app = get_api_app()
          uvicorn.run(app, host='127.0.0.1', port=7861)
          " &
          API_PID=$!
          
          # Wait for API to start
          sleep 5
          
          # Test health endpoint
          curl -f http://127.0.0.1:7861/api/health || exit 1
          
          # Test unauthenticated endpoint (should return 403)
          curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:7861/api/prompts | grep -q "403" || exit 1
          
          # Clean up
          kill $API_PID
          
          echo "✅ API tests passed"

  test-docker:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: false
          tags: ai-prompt-manager:test
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Test Docker image
        run: |
          # Start container in background
          docker run -d -p 7860:7860 --name test-container ai-prompt-manager:test
          
          # Wait for container to be ready
          sleep 30
          
          # Test health endpoint
          for i in {1..10}; do
            if curl -f http://localhost:7860/api/health; then
              echo "✅ Health check passed"
              break
            fi
            echo "Attempt $i failed, retrying..."
            sleep 5
          done
          
          # Test web interface
          curl -f http://localhost:7860/ | grep -q "Multi-Tenant AI Prompt Manager" || exit 1
          echo "✅ Web interface accessible"
          
          # Test API documentation
          curl -f http://localhost:7860/api/docs || exit 1
          echo "✅ API documentation accessible"
          
          # Clean up
          docker stop test-container
          docker rm test-container

  lint-and-format:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install Poetry
        uses: snok/install-poetry@v1

      - name: Install dependencies
        run: poetry install --no-interaction

      - name: Check Python syntax
        run: |
          poetry run python -m py_compile *.py
          echo "✅ Python syntax check passed"

      - name: Check imports
        run: |
          poetry run python -c "
          import prompt_manager
          import prompt_data_manager
          import auth_manager
          import api_token_manager
          import api_endpoints
          import langwatch_optimizer
          print('✅ All imports successful')
          "
```

</details>

### 3. **Docker Build Workflow (`docker-image.yml`)**

This workflow builds and publishes Docker images to GitHub Container Registry.

<details>
<summary>📄 View complete docker-image.yml configuration</summary>

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ "main" ]
    tags: [ "v*.*.*" ]
  pull_request:
    branches: [ "main" ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    
    permissions:
      contents: read
      packages: write
      attestations: write
      id-token: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            # set latest tag for default branch
            type=ref,event=branch
            type=ref,event=pr
            # set version tags for releases
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=semver,pattern={{major}}
            # set edge tag for main branch
            type=edge,branch=main
            # set latest tag for main branch
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image
        id: push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64

      - name: Generate artifact attestation
        if: github.event_name != 'pull_request'
        uses: actions/attest-build-provenance@v1
        with:
          subject-name: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME}}
          subject-digest: ${{ steps.push.outputs.digest }}
          push-to-registry: true

      - name: Update README with new image tags
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          echo "📦 **Latest Build:** \`${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest\`" >> $GITHUB_STEP_SUMMARY
          echo "🏷️ **Available Tags:** ${{ steps.meta.outputs.tags }}" >> $GITHUB_STEP_SUMMARY
```

</details>

### 4. **Release Workflow (`release.yml`)**

This workflow creates GitHub releases when version tags are pushed.

<details>
<summary>📄 View complete release.yml configuration</summary>

```yaml
name: Create Release

on:
  push:
    tags:
      - 'v*.*.*'

permissions:
  contents: write
  packages: write

jobs:
  create-release:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate changelog
        id: changelog
        run: |
          # Get the previous tag
          PREVIOUS_TAG=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "")
          
          # Generate changelog
          if [ -n "$PREVIOUS_TAG" ]; then
            echo "## Changes since $PREVIOUS_TAG" > CHANGELOG.md
            git log --pretty=format:"- %s (%h)" $PREVIOUS_TAG..HEAD >> CHANGELOG.md
          else
            echo "## Initial Release" > CHANGELOG.md
            git log --pretty=format:"- %s (%h)" >> CHANGELOG.md
          fi
          
          # Set output for use in release
          echo "changelog_content=$(cat CHANGELOG.md)" >> $GITHUB_OUTPUT

      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref_name }}
          release_name: Release ${{ github.ref_name }}
          body: |
            🚀 **AI Prompt Manager ${{ github.ref_name }}**
            
            ${{ steps.changelog.outputs.changelog_content }}
            
            ## 📦 Container Images
            
            This release includes pre-built Docker images:
            
            ```bash
            # Pull the latest release
            docker pull ghcr.io/${{ github.repository }}:${{ github.ref_name }}
            
            # Run the application
            docker run -p 7860:7860 ghcr.io/${{ github.repository }}:${{ github.ref_name }}
            ```
            
            ## 🔧 Installation
            
            ```bash
            # Clone and install
            git clone https://github.com/${{ github.repository }}.git
            cd ai-prompt-manager
            git checkout ${{ github.ref_name }}
            poetry install
            
            # Run the application
            poetry run python run_mt_with_api.py
            ```
            
            ## 📚 Documentation
            
            - [Setup Guide](README.md)
            - [GitHub Workflows](GITHUB_WORKFLOWS_SETUP.md)
            - [API Documentation](http://localhost:7860/api/docs)
            
            ---
            
            **🔐 Non-Commercial License** - See [LICENSE](LICENSE) for usage terms.
          draft: false
          prerelease: false

      - name: Update documentation with release info
        run: |
          # Update README.md with latest release information
          sed -i "s|ghcr.io/OWNER/REPO:v.*|ghcr.io/${{ github.repository }}:${{ github.ref_name }}|g" README.md
          
          # Commit changes if any
          if git diff --quiet; then
            echo "No documentation updates needed"
          else
            git config --local user.email "action@github.com"
            git config --local user.name "GitHub Action"
            git add README.md
            git commit -m "docs: update release version to ${{ github.ref_name }}"
            git push origin HEAD:main
          fi
```

</details>

---

## 🔐 Security Setup

### 1. **GitHub Token Permissions**

The workflows use `GITHUB_TOKEN` which is automatically provided. Ensure your repository has these permissions:

**Settings** → **Actions** → **General** → **Workflow permissions**:
- ✅ **Read and write permissions**
- ✅ **Allow GitHub Actions to create and approve pull requests**

### 2. **Container Registry Access**

GitHub Container Registry (ghcr.io) access is automatic with `GITHUB_TOKEN`. No additional setup required.

### 3. **Optional: Docker Hub Setup**

If you prefer Docker Hub over GitHub Container Registry:

1. **Create Docker Hub Account**
2. **Generate Access Token** in Docker Hub settings
3. **Add Repository Secrets**:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Your access token

4. **Update docker-image.yml**:
```yaml
- name: Log in to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

### 4. **Repository Secrets**

Go to **Settings** → **Secrets and variables** → **Actions** and add:

| Secret Name | Purpose | Required |
|-------------|---------|----------|
| `GITHUB_TOKEN` | Automatic | ✅ Auto-provided |
| `DOCKERHUB_USERNAME` | Docker Hub login | ❌ Optional |
| `DOCKERHUB_TOKEN` | Docker Hub access | ❌ Optional |

---

## 🧪 Testing Workflows

### 1. **Test the Workflows**

**Create a test branch:**
```bash
git checkout -b test-workflows
git push origin test-workflows
```

**Create a pull request:**
- This triggers the test workflow
- Verify all tests pass

### 2. **Test Docker Build**

**Push to main branch:**
```bash
git checkout main
git merge test-workflows
git push origin main
```

**Expected results:**
- Test workflow runs
- Docker build workflow runs
- Image published to GitHub Container Registry

### 3. **Test Release Creation**

**Create and push a version tag:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

**Expected results:**
- Docker build workflow runs with version tags
- Release workflow creates GitHub release
- Multiple image tags created (v1.0.0, v1.0, v1, latest)

### 4. **Verify Published Images**

**Check GitHub Container Registry:**
1. Go to your repository on GitHub
2. Click **Packages** tab
3. Verify `ai-prompt-manager` package exists
4. Check available tags

**Test pulling the image:**
```bash
docker pull ghcr.io/your-username/ai-prompt-manager:latest
docker run -p 7860:7860 ghcr.io/your-username/ai-prompt-manager:latest
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### **1. Workflow Permission Errors**

**Error:** `Error: Resource not accessible by integration`

**Solution:**
- Go to **Settings** → **Actions** → **General**
- Set workflow permissions to "Read and write permissions"
- Enable "Allow GitHub Actions to create and approve pull requests"

#### **2. Docker Build Failures**

**Error:** `dockerfile parse error` or build failures

**Solution:**
- Verify `Dockerfile` exists in repository root
- Check Docker syntax: `docker build -t test .`
- Ensure all required files are in repository

#### **3. Container Registry Push Failures**

**Error:** `unauthorized: authentication required`

**Solution:**
- Verify `GITHUB_TOKEN` permissions
- Check repository visibility (public repos work best)
- For private repos, ensure package visibility settings

#### **4. Test Failures**

**Error:** Tests fail in CI but pass locally

**Solution:**
- Check Python version compatibility (workflow uses 3.12)
- Verify all dependencies in `pyproject.toml`
- Add missing test files to repository
- Check for environment-specific issues

#### **5. Release Creation Issues**

**Error:** Release not created for version tags

**Solution:**
- Verify tag format: `v1.0.0` (with 'v' prefix)
- Check workflow file permissions
- Ensure tag is pushed: `git push origin v1.0.0`

### **Debug Workflow Issues**

**Enable debug logging:**
Add to workflow file:
```yaml
env:
  ACTIONS_RUNNER_DEBUG: true
  ACTIONS_STEP_DEBUG: true
```

**Check workflow logs:**
1. Go to **Actions** tab in GitHub
2. Click on failed workflow run
3. Expand failed steps to see detailed logs

---

## 🚀 Advanced Configuration

### 1. **Multi-Platform Builds**

Build images for multiple architectures:

```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64,linux/arm64,linux/arm/v7
    # ... other configuration
```

### 2. **Build Optimization**

**Cache optimization:**
```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    cache-from: |
      type=gha
      type=registry,ref=ghcr.io/${{ github.repository }}:buildcache
    cache-to: |
      type=gha,mode=max
      type=registry,ref=ghcr.io/${{ github.repository }}:buildcache,mode=max
```

### 3. **Conditional Deployments**

**Deploy only on specific conditions:**
```yaml
- name: Deploy to production
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: |
    echo "Deploying to production..."
```

### 4. **Environment-Specific Builds**

**Create different images for different environments:**
```yaml
strategy:
  matrix:
    environment: [development, staging, production]
include:
  - environment: development
    dockerfile: Dockerfile.dev
  - environment: production
    dockerfile: Dockerfile.prod
```

### 5. **Custom Release Notes**

**Use conventional commits for automated changelog:**
```yaml
- name: Generate changelog
  uses: conventional-changelog/conventional-changelog-action@v3
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    output-file: "CHANGELOG.md"
```

### 6. **Notification Setup**

**Add Slack/Discord notifications:**
```yaml
- name: Notify deployment
  if: success()
  uses: 8398a7/action-slack@v3
  with:
    status: success
    channel: '#deployments'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 📚 Additional Resources

### **GitHub Actions Documentation**
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Container Registry Guide](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

### **Best Practices**
- [Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Workflow Optimization](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### **Monitoring and Alerts**
- Set up repository notifications for workflow failures
- Use GitHub Status API for integration with external systems
- Monitor container registry usage and limits

---

## ✅ Checklist

Use this checklist to verify your workflow setup:

**Repository Setup:**
- [ ] Repository created with admin access
- [ ] GitHub Actions enabled
- [ ] Workflow permissions configured (read/write)
- [ ] Branch protection rules configured (optional)

**Workflow Files:**
- [ ] `.github/workflows/test.yml` created
- [ ] `.github/workflows/docker-image.yml` created
- [ ] `.github/workflows/release.yml` created
- [ ] All workflow files have correct syntax

**Security Configuration:**
- [ ] GitHub Token permissions verified
- [ ] Container registry access configured
- [ ] Repository secrets added (if needed)
- [ ] Security scanning enabled

**Testing:**
- [ ] Test workflow runs successfully
- [ ] Docker build workflow completes
- [ ] Release workflow creates releases
- [ ] Container images published correctly
- [ ] Images can be pulled and run

**Documentation:**
- [ ] README.md updated with container registry URLs
- [ ] Workflow documentation created
- [ ] Usage instructions provided
- [ ] Troubleshooting guide available

---

**🎉 Congratulations!** Your GitHub workflows are now configured for automated testing, building, and deployment of the AI Prompt Manager.

For questions or issues, refer to the troubleshooting section or check the GitHub Actions logs for detailed error information.
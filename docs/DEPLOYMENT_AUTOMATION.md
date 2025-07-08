# 🤖 Deployment Automation

Complete guide for setting up automated deployment, CI/CD pipelines, and release automation for the AI Prompt Manager.

## Table of Contents

1. [GitHub Actions Setup](#github-actions-setup)
2. [Trusted Publishing](#trusted-publishing)
3. [Docker Automation](#docker-automation)
4. [Release System Configuration](#release-system-configuration)
5. [Monitoring & Notifications](#monitoring--notifications)

---

## GitHub Actions Setup

### Workflow Architecture

The AI Prompt Manager uses a comprehensive CI/CD pipeline with multiple workflows for different purposes:

```mermaid
graph LR
    A[Code Push] --> B[CI Workflow]
    C[Release Created] --> D[Release Workflow]
    E[Pull Request] --> F[PR Workflow]
    G[Schedule] --> H[Maintenance Workflow]
    
    B --> I[Test & Lint]
    D --> J[Build & Publish]
    F --> K[Validate Changes]
    H --> L[Security Scan]
    
    I --> M[Quality Gates]
    J --> N[PyPI & Docker]
    K --> O[PR Checks]
    L --> P[Vulnerability Reports]
```

### Core Workflows

#### 1. Continuous Integration (`.github/workflows/ci.yml`)

```yaml
name: Continuous Integration

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM

env:
  PYTHON_VERSION: '3.12'
  POETRY_VERSION: '1.7.1'

jobs:
  test:
    name: Test Suite
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12']
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: ${{ env.POETRY_VERSION }}
          virtualenvs-create: true
          virtualenvs-in-project: true
      
      - name: Load cached venv
        id: cached-poetry-dependencies
        uses: actions/cache@v3
        with:
          path: .venv
          key: venv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('**/poetry.lock') }}
      
      - name: Install dependencies
        if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
        run: poetry install --with dev,test
      
      - name: Run linting
        run: |
          poetry run black --check .
          poetry run isort --check-only .
          poetry run flake8 . --max-line-length=88 --extend-ignore=E203,W503
      
      - name: Run security scan
        run: |
          poetry run bandit -r . --skip B101,B602,B603 -f json -o bandit-report.json
          poetry run safety check --json --output safety-report.json
        continue-on-error: true
      
      - name: Run tests
        run: |
          poetry run pytest --cov=src --cov-report=xml --cov-report=html -v
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: false
      
      - name: Upload test artifacts
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-${{ matrix.os }}-${{ matrix.python-version }}
          path: |
            htmlcov/
            bandit-report.json
            safety-report.json
            pytest-report.xml
          retention-days: 30

  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: test
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: promptman_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
      
      - name: Install dependencies
        run: poetry install --with dev,test
      
      - name: Run integration tests
        env:
          POSTGRES_DSN: postgresql://postgres:postgres@localhost:5432/promptman_test
          REDIS_URL: redis://localhost:6379
        run: |
          poetry run pytest tests/integration/ -v --tb=short
      
      - name: Run API integration tests
        run: |
          poetry run python tests/integration/test_api_integration.py
          poetry run python tests/integration/test_web_interface_integration.py

  e2e-tests:
    name: End-to-End Tests
    runs-on: ubuntu-latest
    needs: integration-tests
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
      
      - name: Install dependencies
        run: poetry install --with dev,test,e2e
      
      - name: Install Playwright
        run: |
          poetry run playwright install chromium --with-deps
      
      - name: Run E2E tests
        run: |
          poetry run pytest tests/e2e/ -v --tb=short -m e2e
        env:
          E2E_HEADLESS: true
          E2E_SLOW_MO: 0
      
      - name: Upload E2E artifacts
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: e2e-artifacts
          path: |
            tests/e2e/screenshots/
            tests/e2e/videos/
          retention-days: 7

  docker-test:
    name: Docker Build Test
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          tags: ai-prompt-manager:test
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Test Docker image
        run: |
          docker run --rm -d --name test-container -p 7860:7860 ai-prompt-manager:test
          sleep 10
          curl -f http://localhost:7860/health || exit 1
          docker stop test-container
```

#### 2. Release Workflow (`.github/workflows/release.yml`)

```yaml
name: Release Pipeline

on:
  release:
    types: [published]

env:
  PYTHON_VERSION: '3.12'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  validate-release:
    name: Validate Release
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate version consistency
        run: |
          VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
          TAG_VERSION=${GITHUB_REF#refs/tags/v}
          
          if [ "$VERSION" != "$TAG_VERSION" ]; then
            echo "Version mismatch: pyproject.toml=$VERSION, tag=$TAG_VERSION"
            exit 1
          fi
          
          echo "VERSION=$VERSION" >> $GITHUB_ENV
      
      - name: Validate changelog
        run: |
          if ! grep -q "## \[${{ env.VERSION }}\]" CHANGELOG.md; then
            echo "Changelog entry missing for version ${{ env.VERSION }}"
            exit 1
          fi

  test-before-release:
    name: Pre-Release Testing
    runs-on: ubuntu-latest
    needs: validate-release
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
      
      - name: Install dependencies
        run: poetry install --with dev,test
      
      - name: Run full test suite
        run: |
          poetry run pytest --cov=src --cov-fail-under=80
          poetry run flake8 .
          poetry run black --check .
          poetry run isort --check-only .

  build-and-publish:
    name: Build & Publish to PyPI
    runs-on: ubuntu-latest
    needs: test-before-release
    environment: release
    permissions:
      id-token: write  # Required for trusted publishing
      contents: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
      
      - name: Build package
        run: |
          poetry build
          ls -la dist/
      
      - name: Verify package
        run: |
          poetry run twine check dist/*
          tar -tzf dist/*.tar.gz | head -20
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          print-hash: true
          verbose: true

  build-and-push-docker:
    name: Build & Push Docker Images
    runs-on: ubuntu-latest
    needs: test-before-release
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Container Registry
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
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=semver,pattern={{major}}
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Test Docker image
        run: |
          docker run --rm -d --name test-release -p 7860:7860 ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
          sleep 15
          curl -f http://localhost:7860/health
          docker stop test-release

  create-release-notes:
    name: Generate Release Notes
    runs-on: ubuntu-latest
    needs: [build-and-publish, build-and-push-docker]
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Generate release notes
        id: notes
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          
          # Extract changelog entry
          awk "/## \[$VERSION\]/{flag=1; next} /## \[/{flag=0} flag" CHANGELOG.md > release_notes.md
          
          # Add installation instructions
          cat >> release_notes.md << EOF
          
          ## Installation
          
          \`\`\`bash
          # Install from PyPI
          pip install promptman==$VERSION
          
          # Run the application
          python -m promptman
          \`\`\`
          
          ## Docker
          
          \`\`\`bash
          # Pull and run
          docker run -p 7860:7860 ghcr.io/makercorn/ai-prompt-manager:$VERSION
          \`\`\`
          EOF
          
          echo "RELEASE_NOTES<<EOF" >> $GITHUB_OUTPUT
          cat release_notes.md >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
      
      - name: Update release with notes
        uses: softprops/action-gh-release@v1
        with:
          body: ${{ steps.notes.outputs.RELEASE_NOTES }}
          files: |
            dist/*
```

#### 3. Pull Request Workflow (`.github/workflows/pr.yml`)

```yaml
name: Pull Request Validation

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  validate-pr:
    name: Validate Pull Request
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
      
      - name: Install dependencies
        run: poetry install --with dev,test
      
      - name: Check code formatting
        run: |
          poetry run black --check .
          poetry run isort --check-only .
      
      - name: Run linting
        run: poetry run flake8 . --max-line-length=88
      
      - name: Run tests with coverage
        run: |
          poetry run pytest --cov=src --cov-report=xml
      
      - name: Comment coverage report
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: pr-coverage
```

## Trusted Publishing

### PyPI Trusted Publishing Setup

Trusted publishing eliminates the need for PyPI API tokens by using GitHub's OIDC identity to authenticate with PyPI.

#### 1. PyPI Configuration

```bash
# 1. Create PyPI account and project
# Visit: https://pypi.org/account/register/
# Create project: https://pypi.org/manage/projects/

# 2. Configure trusted publisher
# Project Settings → Publishing → Add a new pending publisher
Publisher: GitHub
Owner: makercorn
Repository name: ai-prompt-manager
Workflow name: release.yml
Environment name: release
```

#### 2. GitHub Environment Setup

```yaml
# Repository Settings → Environments → New environment
name: release

# Protection rules:
environment_protection_rules:
  - type: required_reviewers
    reviewers: ["maintainer1", "maintainer2"]
  - type: wait_timer
    minutes: 5
  - type: deployment_branches
    branches: ["main"]

# Environment secrets:
secrets: {}  # No API tokens needed with trusted publishing
```

#### 3. Workflow Configuration

```yaml
# In .github/workflows/release.yml
jobs:
  publish:
    runs-on: ubuntu-latest
    environment: release  # Required for trusted publishing
    permissions:
      id-token: write     # Required for OIDC
      contents: read      # Required for checkout
    
    steps:
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # No API token required!
```

### Security Benefits

#### Traditional API Token vs Trusted Publishing

| Aspect | API Token | Trusted Publishing |
|--------|-----------|-------------------|
| **Secret Management** | Store in GitHub Secrets | No secrets needed |
| **Rotation** | Manual rotation required | Automatic via OIDC |
| **Scope** | Project-wide access | Repository-specific |
| **Expiration** | Manual management | Short-lived tokens |
| **Audit Trail** | Limited | Full OIDC audit |
| **Compromise Risk** | High (long-lived) | Low (ephemeral) |

#### OIDC Token Flow

```mermaid
sequenceDiagram
    participant GH as GitHub Actions
    participant OIDC as GitHub OIDC
    participant PyPI as PyPI
    
    GH->>OIDC: Request ID token
    OIDC->>GH: Return signed JWT
    GH->>PyPI: Publish with JWT
    PyPI->>OIDC: Verify token signature
    OIDC->>PyPI: Confirm authenticity
    PyPI->>GH: Allow publication
```

### Troubleshooting Trusted Publishing

#### Common Issues

1. **Environment Not Configured**
   ```
   Error: The workflow is not configured with required permissions
   ```
   **Solution**: Add `id-token: write` permission and use `environment: release`

2. **Publisher Configuration Mismatch**
   ```
   Error: No trusted publisher configured
   ```
   **Solution**: Verify repository name, workflow name, and environment match PyPI configuration

3. **Branch Protection**
   ```
   Error: Workflow cannot run on this branch
   ```
   **Solution**: Ensure environment deployment branches include the release branch

#### Debug Commands

```bash
# Check OIDC token (in GitHub Actions)
- name: Debug OIDC token
  run: |
    echo "Repository: ${{ github.repository }}"
    echo "Workflow: ${{ github.workflow }}"
    echo "Environment: ${{ github.environment }}"
    echo "Ref: ${{ github.ref }}"

# Verify PyPI project configuration
curl -s https://pypi.org/pypi/promptman/json | jq .info
```

## Docker Automation

### Multi-Platform Docker Builds

#### Dockerfile Optimization

```dockerfile
# Multi-stage build for smaller images
FROM python:3.12-slim as builder

# Install Poetry
RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --only=main --no-dev

# Production stage
FROM python:3.12-slim as production

# Copy installed packages
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application
WORKDIR /app
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:7860/health || exit 1

# Expose port and start
EXPOSE 7860
CMD ["python", "-m", "promptman"]
```

#### Build Automation

```yaml
# Multi-platform build configuration
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
  with:
    platforms: linux/amd64,linux/arm64

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    platforms: linux/amd64,linux/arm64
    push: true
    tags: |
      ghcr.io/${{ github.repository }}:latest
      ghcr.io/${{ github.repository }}:${{ github.ref_name }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Container Registry Management

#### Image Tagging Strategy

```bash
# Tag structure
ghcr.io/makercorn/ai-prompt-manager:latest          # Latest stable
ghcr.io/makercorn/ai-prompt-manager:v0.5.12         # Specific version
ghcr.io/makercorn/ai-prompt-manager:0.5             # Minor version
ghcr.io/makercorn/ai-prompt-manager:0                # Major version
ghcr.io/makercorn/ai-prompt-manager:main             # Main branch
ghcr.io/makercorn/ai-prompt-manager:pr-123           # Pull request
```

#### Cleanup Automation

```yaml
# .github/workflows/cleanup.yml
name: Container Cleanup

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly cleanup

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - name: Clean up old images
        uses: actions/github-script@v7
        with:
          script: |
            const package_name = "ai-prompt-manager";
            const keep_versions = 10;
            
            const { data: versions } = await github.rest.packages.getAllPackageVersionsForPackageOwnedByOrg({
              package_type: 'container',
              package_name: package_name,
              org: context.repo.owner,
              per_page: 100
            });
            
            // Keep latest N versions, delete older ones
            const toDelete = versions.slice(keep_versions);
            
            for (const version of toDelete) {
              await github.rest.packages.deletePackageVersionForOrg({
                package_type: 'container',
                package_name: package_name,
                org: context.repo.owner,
                package_version_id: version.id
              });
              console.log(`Deleted version ${version.name}`);
            }
```

## Release System Configuration

### Automated Release Creation

#### Release Trigger Workflow

```yaml
# .github/workflows/create-release.yml
name: Create Release

on:
  push:
    tags:
      - 'v*'

jobs:
  create-release:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Generate changelog
        id: changelog
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          
          # Extract version section from CHANGELOG.md
          awk "/## \[$VERSION\]/{flag=1; next} /## \[/{flag=0} flag" CHANGELOG.md > current_changes.md
          
          # Format for release
          echo "CHANGES<<EOF" >> $GITHUB_OUTPUT
          cat current_changes.md >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
      
      - name: Create release
        uses: softprops/action-gh-release@v1
        with:
          name: Release ${{ github.ref_name }}
          body: ${{ steps.changelog.outputs.CHANGES }}
          draft: false
          prerelease: ${{ contains(github.ref_name, 'alpha') || contains(github.ref_name, 'beta') || contains(github.ref_name, 'rc') }}
          generate_release_notes: true
```

### Release Configuration

#### Release Templates

```markdown
<!-- .github/RELEASE_TEMPLATE.md -->
## What's Changed

### ✨ New Features
- Feature 1 description
- Feature 2 description

### 🐛 Bug Fixes
- Bug fix 1 description
- Bug fix 2 description

### 🔧 Improvements
- Improvement 1 description
- Improvement 2 description

### 📖 Documentation
- Documentation update 1
- Documentation update 2

## Installation

```bash
# Install from PyPI
pip install promptman=={{VERSION}}

# Run the application  
python -m promptman
```

## Docker

```bash
# Pull and run
docker run -p 7860:7860 ghcr.io/makercorn/ai-prompt-manager:{{VERSION}}
```

## What's Next

- Upcoming feature 1
- Upcoming feature 2

**Full Changelog**: https://github.com/makercorn/ai-prompt-manager/compare/{{PREVIOUS_TAG}}...{{CURRENT_TAG}}
```

#### Version Management

```python
# scripts/version_manager.py
import subprocess
import re
from pathlib import Path

class VersionManager:
    def __init__(self):
        self.pyproject_path = Path("pyproject.toml")
        self.changelog_path = Path("CHANGELOG.md")
    
    def get_current_version(self):
        """Get current version from pyproject.toml"""
        content = self.pyproject_path.read_text()
        match = re.search(r'version = "([^"]+)"', content)
        return match.group(1) if match else None
    
    def bump_version(self, bump_type="patch"):
        """Bump version using poetry"""
        subprocess.run(["poetry", "version", bump_type], check=True)
        return self.get_current_version()
    
    def update_changelog(self, version, changes):
        """Update CHANGELOG.md with new version"""
        content = self.changelog_path.read_text()
        new_entry = f"\n## [{version}] - {datetime.now().strftime('%Y-%m-%d')}\n\n{changes}\n"
        updated = content.replace("# Changelog\n", f"# Changelog\n{new_entry}")
        self.changelog_path.write_text(updated)
    
    def create_release_commit(self, version):
        """Create release commit and tag"""
        subprocess.run(["git", "add", "pyproject.toml", "CHANGELOG.md"], check=True)
        subprocess.run(["git", "commit", "-m", f"chore: bump version to {version}"], check=True)
        subprocess.run(["git", "tag", f"v{version}"], check=True)
```

## Monitoring & Notifications

### Deployment Monitoring

#### Health Check Monitoring

```yaml
# .github/workflows/deployment-monitor.yml
name: Deployment Monitor

on:
  deployment_status:

jobs:
  monitor:
    if: github.event.deployment_status.state == 'success'
    runs-on: ubuntu-latest
    
    steps:
      - name: Health check
        run: |
          URL="${{ github.event.deployment_status.target_url }}"
          
          # Wait for deployment to be ready
          for i in {1..30}; do
            if curl -f "$URL/health"; then
              echo "Deployment healthy"
              break
            fi
            echo "Waiting for deployment... ($i/30)"
            sleep 10
          done
      
      - name: Smoke tests
        run: |
          URL="${{ github.event.deployment_status.target_url }}"
          
          # Test key endpoints
          curl -f "$URL/health"
          curl -f "$URL/api/health"
          curl -f "$URL/"
```

### Notification System

#### Slack Integration

```yaml
# .github/workflows/notifications.yml
name: Notifications

on:
  release:
    types: [published]
  workflow_run:
    workflows: ["Release Pipeline"]
    types:
      - completed

jobs:
  notify-slack:
    runs-on: ubuntu-latest
    
    steps:
      - name: Release notification
        if: github.event_name == 'release'
        uses: 8398a7/action-slack@v3
        with:
          status: success
          channel: '#releases'
          title: '🚀 New Release Published'
          message: |
            **AI Prompt Manager ${{ github.event.release.tag_name }}**
            
            📦 PyPI: https://pypi.org/project/promptman/${{ github.event.release.tag_name }}
            🐳 Docker: ghcr.io/makercorn/ai-prompt-manager:${{ github.event.release.tag_name }}
            📝 Release Notes: ${{ github.event.release.html_url }}
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
      
      - name: Failure notification
        if: github.event_name == 'workflow_run' && github.event.workflow_run.conclusion == 'failure'
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          channel: '#dev-alerts'
          title: '❌ Release Pipeline Failed'
          message: |
            **Workflow**: ${{ github.event.workflow_run.name }}
            **Branch**: ${{ github.event.workflow_run.head_branch }}
            **Commit**: ${{ github.event.workflow_run.head_sha }}
            **URL**: ${{ github.event.workflow_run.html_url }}
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

#### Email Notifications

```yaml
notify-email:
  runs-on: ubuntu-latest
  
  steps:
    - name: Send deployment notification
      uses: dawidd6/action-send-mail@v3
      with:
        server_address: smtp.gmail.com
        server_port: 587
        username: ${{ secrets.EMAIL_USERNAME }}
        password: ${{ secrets.EMAIL_PASSWORD }}
        subject: "AI Prompt Manager Deployment: ${{ github.ref_name }}"
        html_body: |
          <h2>🚀 Deployment Successful</h2>
          <p><strong>Version:</strong> ${{ github.ref_name }}</p>
          <p><strong>Environment:</strong> Production</p>
          <p><strong>Time:</strong> ${{ github.event.head_commit.timestamp }}</p>
          
          <h3>Quick Links</h3>
          <ul>
            <li><a href="https://pypi.org/project/promptman/">PyPI Package</a></li>
            <li><a href="${{ github.event.release.html_url }}">Release Notes</a></li>
            <li><a href="https://github.com/${{ github.repository }}/actions">GitHub Actions</a></li>
          </ul>
        to: team@example.com
```

### Performance Monitoring

#### Release Performance Tracking

```yaml
performance-check:
  runs-on: ubuntu-latest
  
  steps:
    - name: Performance baseline
      run: |
        # Test application startup time
        start_time=$(date +%s)
        docker run -d --name perf-test -p 7860:7860 ghcr.io/makercorn/ai-prompt-manager:latest
        
        # Wait for health check
        while ! curl -f http://localhost:7860/health; do
          sleep 1
        done
        
        end_time=$(date +%s)
        startup_time=$((end_time - start_time))
        
        echo "Startup time: ${startup_time}s"
        
        # Performance test
        curl -w "@curl-format.txt" -o /dev/null -s http://localhost:7860/
        
        docker stop perf-test
        docker rm perf-test
    
    - name: Load testing
      run: |
        # Install hey for load testing
        go install github.com/rakyll/hey@latest
        
        # Run load test
        ~/go/bin/hey -n 1000 -c 10 http://localhost:7860/health
```

---

*This deployment automation guide provides a complete CI/CD setup for the AI Prompt Manager, ensuring reliable, secure, and automated deployments.*
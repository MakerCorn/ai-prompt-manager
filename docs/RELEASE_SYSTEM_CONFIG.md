# Release Management System Configuration

The AI Prompt Manager includes a comprehensive release announcement system that can sync from multiple sources and display announcements to users.

## Environment Variables

### Core Configuration

```bash
# Enable/disable release management system
GITHUB_RELEASES_ENABLED=true          # Enable GitHub releases sync (default: true)
CHANGELOG_ENABLED=true                 # Enable local changelog parsing (default: true)

# Cache configuration
RELEASE_CACHE_DURATION=3600           # Cache duration in seconds (default: 3600 = 1 hour)
```

### GitHub Integration

```bash
# GitHub API configuration
GITHUB_TOKEN=your_github_token         # Optional: GitHub personal access token for higher rate limits
GITHUB_REPO=makercorn/ai-prompt-manager # Repository to sync releases from (default: makercorn/ai-prompt-manager)
```

### Changelog Configuration

```bash
# Local changelog file
CHANGELOG_PATH=CHANGELOG.md            # Path to changelog file (default: CHANGELOG.md)
```

## Features

### 1. GitHub Integration
- **Automatic Sync**: Fetches releases from GitHub API
- **Rate Limiting**: Respects GitHub API rate limits
- **Authentication**: Optional GitHub token for higher rate limits
- **Caching**: Caches GitHub API responses to reduce API calls

### 2. Changelog Parsing
- **Markdown Support**: Parses standard markdown changelog format
- **Version Detection**: Automatically detects version numbers and dates
- **Content Extraction**: Extracts release descriptions and changes

### 3. User Experience
- **Dashboard Integration**: Shows releases on homepage
- **Notification System**: Tracks read/unread status per user
- **Dismissal**: Users can dismiss announcements
- **Multi-tenant Support**: Proper isolation between tenants

### 4. Admin Management
- **Manual Creation**: Create releases manually via admin interface
- **Sync Control**: Manual sync from GitHub or changelog
- **Statistics**: View release statistics and user engagement
- **Bulk Operations**: Bulk sync and management operations

## API Endpoints

### User Endpoints (Authenticated)

```bash
# Get release announcements
GET /api/releases/
GET /api/releases/?limit=10&include_dismissed=false

# Get unread count
GET /api/releases/unread-count

# Mark release as viewed/dismissed
POST /api/releases/mark-viewed
{
  "release_id": "uuid",
  "is_dismissed": true
}

# Get release statistics
GET /api/releases/stats

# System health check
GET /api/releases/health
```

### Admin Endpoints (Admin Role Required)

```bash
# Create release announcement
POST /api/releases/
{
  "version": "1.2.3",
  "title": "Major Update",
  "description": "Description of changes...",
  "is_major": true,
  "is_featured": false,
  "changelog_url": "https://github.com/...",
  "download_url": "https://github.com/..."
}

# Sync from external sources
POST /api/releases/sync
{
  "source": "github",    # or "changelog"
  "force": false
}

# Admin management
GET /api/admin/releases/all
DELETE /api/admin/releases/{release_id}
POST /api/admin/releases/bulk-sync
POST /api/admin/releases/cleanup-cache
```

## Database Schema

### Release Announcements Table

```sql
CREATE TABLE release_announcements (
    id UUID PRIMARY KEY,
    version VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    release_date TIMESTAMP NOT NULL,
    is_major BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    changelog_url VARCHAR(500),
    download_url VARCHAR(500),
    github_release_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### User Release Views Table

```sql
CREATE TABLE user_release_views (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    release_id UUID REFERENCES release_announcements(id),
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_dismissed BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, release_id)
);
```

### Release Cache Table

```sql
CREATE TABLE release_cache (
    cache_key VARCHAR(100) PRIMARY KEY,
    cache_data JSONB NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Setup Instructions

### 1. Basic Setup

The release system works out-of-the-box with default configuration:

```bash
# Default configuration (no additional setup required)
GITHUB_RELEASES_ENABLED=true
CHANGELOG_ENABLED=true
```

### 2. GitHub Integration Setup

For enhanced GitHub integration:

1. **Create GitHub Personal Access Token** (optional but recommended):
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Create token with `public_repo` or `repo` scope
   - Add to environment variables:

```bash
GITHUB_TOKEN=ghp_your_token_here
```

2. **Configure Repository** (if different from default):

```bash
GITHUB_REPO=your-username/your-repo
```

### 3. Changelog Setup

1. **Create CHANGELOG.md** in project root with format:

```markdown
# Changelog

## [1.2.3] - 2024-01-15

### Added
- New feature X
- Enhancement Y

### Fixed
- Bug fix Z

## [1.2.2] - 2024-01-10

### Changed
- Updated feature A
```

2. **Configure path** (if different):

```bash
CHANGELOG_PATH=docs/CHANGELOG.md
```

### 4. Admin Access

1. **Login as admin** to access release management:
   - Default admin: `admin@localhost` / `admin123`
   - Navigate to `/admin/releases`

2. **Initial sync**:
   - Click "Sync Releases" to import from GitHub
   - Or manually create releases

## Usage Examples

### 1. Sync from GitHub

```bash
curl -X POST "http://localhost:7860/api/releases/sync" \
  -H "Authorization: Bearer your_api_token" \
  -H "Content-Type: application/json" \
  -d '{"source": "github", "force": false}'
```

### 2. Create Manual Release

```bash
curl -X POST "http://localhost:7860/api/releases/" \
  -H "Authorization: Bearer your_api_token" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "1.2.3",
    "title": "Major Feature Update",
    "description": "This release includes new AI model support and enhanced UI.",
    "is_major": true,
    "is_featured": true,
    "changelog_url": "https://github.com/makercorn/ai-prompt-manager/releases/tag/v1.2.3"
  }'
```

### 3. Get User Announcements

```bash
curl -X GET "http://localhost:7860/api/releases/?limit=5" \
  -H "Authorization: Bearer your_api_token"
```

## Troubleshooting

### GitHub Sync Issues

1. **Rate Limiting**: Add `GITHUB_TOKEN` for higher rate limits
2. **Repository Access**: Ensure repository is public or token has access
3. **API Format**: Verify repository follows GitHub releases format

### Changelog Parsing Issues

1. **Format**: Ensure changelog follows standard markdown format
2. **File Path**: Verify `CHANGELOG_PATH` is correct
3. **Permissions**: Ensure file is readable by application

### Database Issues

1. **Migrations**: Database tables are created automatically
2. **Permissions**: Ensure database user has CREATE TABLE permissions
3. **Storage**: PostgreSQL recommended for production

### Cache Issues

1. **Clear Cache**: Use `/api/admin/releases/cleanup-cache`
2. **Reduce Duration**: Lower `RELEASE_CACHE_DURATION`
3. **Force Sync**: Use `"force": true` in sync requests

## Performance Considerations

### Caching Strategy
- GitHub API responses cached for 1 hour by default
- Changelog parsing results cached until file changes
- User view tracking cached per session

### Database Optimization
- Indexes on `version`, `release_date`, `is_featured`
- Cleanup expired cache entries regularly
- Archive old user_release_views periodically

### API Rate Limits
- GitHub API: 60 requests/hour without token, 5000 with token
- Changelog parsing: No external limits
- Internal caching reduces API calls

## Security Considerations

1. **API Authentication**: All endpoints require valid API token
2. **Admin Access**: Admin endpoints restricted to admin role
3. **Token Storage**: GitHub tokens stored as environment variables
4. **Input Validation**: All inputs validated and sanitized
5. **CORS**: Proper CORS headers for web interface

## Monitoring and Maintenance

### Health Checks
- `/api/releases/health` - System health status
- Monitor GitHub API rate limit usage
- Track sync success/failure rates

### Maintenance Tasks
- Regular cache cleanup
- Archive old release views
- Monitor storage usage
- Update GitHub tokens as needed

### Logging
- Sync operations logged with results
- API errors logged with context
- User interaction events logged for analytics
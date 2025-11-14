# GitHub Actions Setup for Docker CI/CD

This guide explains how to configure GitHub Actions to automatically build and publish Docker images for lmelp.

## Overview

The CI/CD pipeline automatically:
1. Builds Docker image on push to `main` or version tags (`v*.*.*`)
2. Publishes image to GitHub Container Registry (ghcr.io)
3. Triggers Portainer webhook for auto-deployment on NAS (optional)

## Workflow Configuration

The workflow is defined in `.github/workflows/docker-publish.yml`.

### Triggers

- **Push to `main`**: Builds and tags as `latest`
- **Version tags** (`v1.0.0`, `v1.2.3`, etc.): Builds and tags with version
- **Manual**: Can be triggered manually via GitHub Actions UI

### Tags Strategy

| Git Action | Docker Tags Generated |
|------------|----------------------|
| Push to `main` | `latest`, `main` |
| Tag `v1.2.3` | `latest`, `v1.2.3`, `v1.2`, `v1`, `1.2.3`, `1.2`, `1` |
| PR #42 | `pr-42` |

## GitHub Secrets Configuration

### Required Secrets

#### `GITHUB_TOKEN` (automatic)
- **Description**: Automatically provided by GitHub Actions
- **Purpose**: Authenticate to GitHub Container Registry
- **Configuration**: None needed - automatically available

### Optional Secrets

#### `PORTAINER_WEBHOOK_URL`
- **Description**: Webhook URL from Portainer for auto-deployment
- **Purpose**: Trigger automatic deployment on NAS when new image is pushed
- **Required**: Only if you want auto-deployment on NAS

**How to configure:**

1. **Get webhook URL from Portainer:**
   - Open Portainer web UI
   - Navigate to your lmelp stack
   - Go to "Webhooks" section
   - Create a new webhook
   - Copy the webhook URL (format: `https://portainer.your-nas.com/api/webhooks/xxx`)

2. **Add to GitHub:**
   - Go to your repository: https://github.com/castorfou/lmelp
   - Click `Settings` → `Secrets and variables` → `Actions`
   - Click `New repository secret`
   - Name: `PORTAINER_WEBHOOK_URL`
   - Value: Paste the webhook URL from Portainer
   - Click `Add secret`

## Permissions

The workflow requires the following permissions (already configured):

```yaml
permissions:
  contents: read    # Read repository code
  packages: write   # Publish to GitHub Container Registry
```

## First Time Setup

### 1. Enable GitHub Container Registry

GitHub Container Registry (ghcr.io) is enabled by default for public repositories. For private repositories:

1. Go to repository `Settings` → `Packages`
2. Ensure packages are enabled

### 2. Test the Workflow

**Option A: Manual trigger**
1. Go to `Actions` tab in GitHub
2. Select `Build and Publish Docker Image`
3. Click `Run workflow`
4. Select branch `main`
5. Click `Run workflow`

**Option B: Push to main**
```bash
# Make a small change
echo "# Docker deployment" >> docs/deployment/README.md
git add docs/deployment/README.md
git commit -m "Trigger Docker build"
git push origin main
```

**Option C: Create a version tag**
```bash
git tag v0.1.0
git push origin v0.1.0
```

### 3. Monitor Build

1. Go to `Actions` tab in GitHub
2. Click on the running workflow
3. Watch the build progress
4. Estimated time: 10-15 minutes (first build with cache)

### 4. Verify Published Image

After successful build:

1. Go to repository main page
2. Click `Packages` (right sidebar)
3. You should see `lmelp` package listed
4. Click on it to see all tags

**Or via command line:**
```bash
# List available tags
docker pull ghcr.io/castorfou/lmelp:latest

# View image details
docker inspect ghcr.io/castorfou/lmelp:latest
```

## Using the Published Image

### Pull Latest Version

```bash
docker pull ghcr.io/castorfou/lmelp:latest
```

### Pull Specific Version

```bash
docker pull ghcr.io/castorfou/lmelp:v1.0.0
```

### Use in docker-compose

The `docker-compose.yml` already references the published image:

```yaml
services:
  app:
    image: ghcr.io/castorfou/lmelp:latest
```

Update to latest:
```bash
cd docker/
./scripts/update.sh
```

## Build Cache

The workflow uses GitHub Actions cache to speed up builds:

- **First build**: ~10-15 minutes (no cache)
- **Subsequent builds**: ~5-8 minutes (with cache)

Cache is automatically managed by GitHub Actions.

## Troubleshooting

### Build fails with "permission denied"

**Cause**: `GITHUB_TOKEN` doesn't have write access to packages

**Solution**:
1. Check repository settings
2. Ensure packages are enabled for the repository

### Portainer webhook not triggered

**Cause**: `PORTAINER_WEBHOOK_URL` secret not configured or incorrect

**Solution**:
1. Verify webhook URL in Portainer
2. Check secret is correctly configured in GitHub
3. Check workflow logs for webhook call errors

### Build takes too long

**Cause**: Large ML models (Whisper, Transformers) need to be downloaded

**Solution**: This is normal for first build. Subsequent builds use cache.

### Out of disk space during build

**Cause**: GitHub Actions runners have limited space

**Solution**:
- The Dockerfile uses multi-stage build to minimize size
- Clean up unnecessary files in `.dockerignore`
- If still failing, review Dockerfile for optimization

## Manual Build and Push

For testing or emergency deployments:

```bash
# Build locally
docker build -f docker/Dockerfile -t ghcr.io/castorfou/lmelp:manual .

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u castorfou --password-stdin

# Push
docker push ghcr.io/castorfou/lmelp:manual
```

## Release Process

To create a new release:

```bash
# Create and push tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# GitHub Actions will automatically:
# 1. Build image
# 2. Tag as v1.0.0, v1.0, v1, latest
# 3. Push to ghcr.io
# 4. Trigger Portainer webhook (if configured)
```

## Workflow Status Badge

Add to README.md:

```markdown
[![Docker Build](https://github.com/castorfou/lmelp/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/castorfou/lmelp/actions/workflows/docker-publish.yml)
```

## Next Steps

After CI/CD is configured:

1. [Configure Portainer on NAS](portainer-guide.md) (to be created)
2. [Setup reverse proxy](nas-deployment.md) (to be created)
3. [Configure monitoring](troubleshooting.md) (to be created)

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Build Action](https://github.com/docker/build-push-action)
- [Docker Metadata Action](https://github.com/docker/metadata-action)

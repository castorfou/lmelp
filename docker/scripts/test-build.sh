#!/bin/bash
# Test Docker image build locally before pushing
# This script helps validate the Dockerfile and build process

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=================================="
echo "lmelp Docker Build Test"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Navigate to project root
cd "$PROJECT_ROOT"

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# Check if Dockerfile exists
if [ ! -f "docker/Dockerfile" ]; then
    echo -e "${RED}❌ Error: docker/Dockerfile not found${NC}"
    exit 1
fi

# Build image
echo "🔨 Building Docker image..."
echo "This may take several minutes (downloading dependencies, ML models, etc.)"
echo ""

IMAGE_TAG="lmelp:test-$(date +%Y%m%d-%H%M%S)"

docker build \
    -f docker/Dockerfile \
    -t "$IMAGE_TAG" \
    -t lmelp:test-latest \
    .

echo ""
echo -e "${GREEN}✅ Build successful!${NC}"
echo ""

# Show image size
echo "📊 Image information:"
docker images "$IMAGE_TAG" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo ""

# Show image layers
echo "📦 Image layers:"
docker history "$IMAGE_TAG" --no-trunc=false --format "table {{.CreatedBy}}\t{{.Size}}" | head -20
echo ""

# Ask if user wants to test the image
echo ""
read -p "Do you want to test the image? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🧪 Testing image..."
    echo ""
    echo "Starting container in test mode..."
    echo "This will start the Streamlit interface on port 8501"
    echo "Press Ctrl+C to stop"
    echo ""

    # Create a minimal .env for testing
    TEMP_ENV=$(mktemp)
    cat > "$TEMP_ENV" <<EOF
DB_HOST=localhost
DB_NAME=masque_et_la_plume
DB_LOGS=true
LMELP_MODE=web
EOF

    # Run container
    docker run --rm -it \
        -p 8501:8501 \
        --env-file "$TEMP_ENV" \
        "$IMAGE_TAG"

    # Clean up
    rm "$TEMP_ENV"
else
    echo ""
    echo -e "${YELLOW}ℹ️  To test the image manually:${NC}"
    echo ""
    echo "docker run --rm -it -p 8501:8501 \\"
    echo "  -e DB_HOST=localhost \\"
    echo "  -e GEMINI_API_KEY=your_key \\"
    echo "  $IMAGE_TAG"
    echo ""
    echo "Then open: http://localhost:8501"
fi

echo ""
echo -e "${GREEN}✅ All done!${NC}"
echo ""
echo "Image tags created:"
echo "  - $IMAGE_TAG"
echo "  - lmelp:test-latest"
echo ""
echo "To remove test images:"
echo "  docker rmi $IMAGE_TAG lmelp:test-latest"

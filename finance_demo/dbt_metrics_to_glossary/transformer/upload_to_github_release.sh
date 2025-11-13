#!/bin/bash
# Script to upload wheel file to GitHub release

VERSION="0.1.7"
REPO="martyacryl/datahubdemos"
TAG="v${VERSION}-dbt-metrics-transformer"
WHEEL_FILE="dist/dbt_metrics_to_glossary_transformer-${VERSION}-py3-none-any.whl"

if [ ! -f "$WHEEL_FILE" ]; then
    echo "❌ Error: Wheel file not found at $WHEEL_FILE"
    exit 1
fi

echo "🚀 Uploading wheel file to GitHub release..."
echo "   Repository: $REPO"
echo "   Tag: $TAG"
echo "   File: $WHEEL_FILE"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed."
    echo ""
    echo "Install it with:"
    echo "  brew install gh"
    echo ""
    echo "Or manually create a release at:"
    echo "  https://github.com/$REPO/releases/new"
    echo "  Tag: $TAG"
    echo "  Title: dbt Metrics to Glossary Transformer v${VERSION}"
    echo "  Upload file: $WHEEL_FILE"
    exit 1
fi

# Check if release exists
if gh release view "$TAG" --repo "$REPO" &> /dev/null; then
    echo "✅ Release $TAG already exists. Uploading asset..."
    gh release upload "$TAG" "$WHEEL_FILE" --repo "$REPO" --clobber
else
    echo "📦 Creating new release $TAG..."
    gh release create "$TAG" \
        --repo "$REPO" \
        --title "dbt Metrics to Glossary Transformer v${VERSION}" \
        --notes "Fixed transformer to properly read metrics from manifest.json with improved logging and error handling." \
        "$WHEEL_FILE"
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Upload successful!"
    echo ""
    echo "📋 Use this URL in DataHub Cloud UI (JSON format):"
    echo ""
    echo "[\"https://github.com/$REPO/releases/download/$TAG/dbt_metrics_to_glossary_transformer-${VERSION}-py3-none-any.whl\"]"
    echo ""
    echo "Or plain URL:"
    echo "https://github.com/$REPO/releases/download/$TAG/dbt_metrics_to_glossary_transformer-${VERSION}-py3-none-any.whl"
    echo ""
    echo "Release URL:"
    echo "https://github.com/$REPO/releases/tag/$TAG"
else
    echo "❌ Upload failed. Check your GitHub authentication:"
    echo "  gh auth login"
    exit 1
fi


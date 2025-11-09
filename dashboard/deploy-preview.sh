#!/bin/bash
# Quick Deploy Script for Sports Dashboard Preview
# Run this from your LOCAL machine to get a preview URL for mobile testing

set -e

echo "🚀 Sports Dashboard - Quick Preview Deploy"
echo "=========================================="
echo ""

# Check if vercel is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

echo "✅ Vercel CLI ready"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Must run from dashboard/ directory"
    echo "Run: cd sportstatbot/dashboard && ./deploy-preview.sh"
    exit 1
fi

echo "📂 Current directory: $(pwd)"
echo ""

# Deploy preview
echo "🚀 Deploying preview..."
echo "   (This will open your browser for Vercel login if needed)"
echo ""

vercel --yes

echo ""
echo "✅ Preview deployed!"
echo ""
echo "📱 NEXT STEPS:"
echo "   1. Copy the preview URL from above"
echo "   2. Open it on your phone's browser"
echo "   3. Install as app (Add to Home Screen)"
echo ""
echo "🔄 TO UPDATE:"
echo "   Just run this script again after making changes!"
echo ""
echo "🔐 TO ADD ENVIRONMENT VARIABLES:"
echo "   vercel env add OWNER_EMAIL"
echo "   vercel env add NEXTAUTH_SECRET"
echo "   vercel env add NEXTAUTH_URL"
echo ""
echo "   Then run: vercel --prod"
echo ""

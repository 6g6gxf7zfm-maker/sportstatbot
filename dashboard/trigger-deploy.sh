#!/bin/bash
# Trigger Vercel deployment via webhook
# Get your deploy hook from: Vercel Dashboard → Project Settings → Git → Deploy Hooks

DEPLOY_HOOK_URL="YOUR_DEPLOY_HOOK_URL_HERE"

echo "🚀 Triggering Vercel deployment..."

curl -X POST "$DEPLOY_HOOK_URL"

echo ""
echo "✅ Deployment triggered!"
echo "Check status at: https://vercel.com/dashboard"

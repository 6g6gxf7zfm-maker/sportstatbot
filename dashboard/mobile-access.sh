#!/bin/bash
# Mobile Access Script for Sports Intelligence Dashboard

echo "================================"
echo "  Sports Dashboard Mobile Setup"
echo "================================"
echo ""

# Check if server is running
if ! lsof -i :3000 >/dev/null 2>&1; then
    echo "Starting Next.js server..."
    cd /home/user/sportstatbot/dashboard
    npm run dev &
    sleep 5
fi

echo "✅ Server is running on localhost:3000"
echo ""
echo "📱 TO ACCESS ON YOUR MOBILE DEVICE:"
echo ""
echo "Option 1: Use Deployment (Recommended)"
echo "  Run: cd /home/user/sportstatbot/dashboard && npx vercel"
echo "  You'll get a public HTTPS URL instantly"
echo "  Works on any device, supports PWA install"
echo ""
echo "Option 2: Local Network (if on same WiFi)"
echo "  Your computer's IP: $(hostname -I | awk '{print $1}')"
echo "  On your phone, open: http://$(hostname -I | awk '{print $1}'):3000"
echo "  Note: Needs server restarted with: npm run dev -- -H 0.0.0.0"
echo ""
echo "Option 3: ngrok (requires installation)"
echo "  Install: curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null"
echo "  Run: ngrok http 3000"
echo "  Copy the https:// URL to your phone"
echo ""
echo "================================"

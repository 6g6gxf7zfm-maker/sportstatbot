# Mobile Setup Guide

Your Sports Intelligence Dashboard is now a **Progressive Web App (PWA)** that can be installed on your mobile device!

## Features

- **Install as App**: Add to your home screen and use like a native app
- **Offline Support**: Service worker caches content for offline access
- **Mobile Responsive**: Optimized UI for phones and tablets
- **Touch Optimized**: Hamburger menu and touch-friendly controls
- **Fast Loading**: Optimized for mobile networks
- **Full Screen**: Runs in standalone mode (no browser chrome)

---

## iOS (iPhone/iPad) Installation

### 1. Open in Safari

**Important**: Must use Safari browser (not Chrome)

Open: `https://your-dashboard-url.com`

### 2. Add to Home Screen

1. Tap the **Share** button (square with arrow pointing up)
2. Scroll down and tap **"Add to Home Screen"**
3. Name it: "Sports Intel"
4. Tap **"Add"**

### 3. Open the App

Look for the "Sports Intel" icon on your home screen and tap to open!

### Features on iOS:
- ✅ Runs fullscreen (no Safari UI)
- ✅ Appears in app switcher
- ✅ Custom icon
- ✅ Splash screen
- ✅ Works offline

---

## Android Installation

### Method 1: Install Prompt (Easiest)

1. Open in Chrome/Edge/Samsung Internet
2. Wait 3 seconds after page loads
3. You'll see an **"Install App"** banner at the bottom
4. Tap **"Install"**

### Method 2: Manual Installation

1. Open: `https://your-dashboard-url.com`
2. Tap the **⋮** menu (three dots)
3. Tap **"Install app"** or **"Add to Home screen"**
4. Tap **"Install"**

### Features on Android:
- ✅ Full app experience
- ✅ Appears in app drawer
- ✅ Standalone window
- ✅ Custom icon and theme
- ✅ Push notifications (can be added)
- ✅ Works offline

---

## Desktop Installation

Works on **Chrome, Edge, and other Chromium browsers**:

1. Open the dashboard URL
2. Look for install icon (➕) in address bar
3. Click **"Install"**
4. App opens in its own window

---

## Running Locally on Mobile (Development)

### Option 1: Expose Local Server

```bash
# Start dev server on all interfaces
cd dashboard
npm run dev -- -H 0.0.0.0

# Your computer's IP (find it):
# Mac: ifconfig | grep "inet " | grep -v 127.0.0.1
# Linux: ip addr show | grep "inet " | grep -v 127.0.0.1
# Windows: ipconfig

# On mobile, open:
# http://YOUR_COMPUTER_IP:3000
```

### Option 2: ngrok (Easiest for HTTPS)

```bash
# Install ngrok
npm install -g ngrok

# In terminal 1:
cd dashboard
npm run dev

# In terminal 2:
ngrok http 3000

# Use the https:// URL on your mobile device
```

### Option 3: Deploy to Vercel

```bash
cd dashboard
npm install -g vercel
vercel

# Get instant HTTPS URL
# Access from any device
```

---

## Testing Mobile Features

### 1. Responsive Design
- Dashboard adapts to screen size
- Hamburger menu on mobile
- Touch-friendly buttons
- Optimized spacing

### 2. Install Prompt
- Appears after 3 seconds
- Can dismiss (won't show again)
- Only on mobile browsers

### 3. Offline Mode
- Service worker caches pages
- Works without internet
- Syncs when back online

### 4. PWA Features
- Custom splash screen
- Status bar theming
- Standalone display
- No browser UI

---

## Mobile-Specific Features

### Hamburger Menu
- Tap menu icon (☰) to open navigation
- Swipe or tap outside to close
- Quick access to all sections

### Install Banner
- Shows after first visit
- Can install later from settings
- Dismissible

### Touch Gestures
- Smooth scrolling
- Pull to refresh (if added)
- Swipe navigation (if added)

### Performance
- Optimized for 3G/4G
- Compressed assets
- Fast initial load
- Cached resources

---

## Customization

### Change App Name

Edit `dashboard/public/manifest.json`:
```json
{
  "name": "Your Custom Name",
  "short_name": "Custom"
}
```

### Change App Icon

Replace files in `dashboard/public/`:
- `icon-192.svg` - Small icon
- `icon-512.svg` - Large icon

Or use PNG:
```json
{
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192" },
    { "src": "/icon-512.png", "sizes": "512x512" }
  ]
}
```

### Change Theme Color

Edit `dashboard/app/layout.tsx`:
```tsx
themeColor: [
  { media: "(prefers-color-scheme: dark)", color: "#your-color" }
]
```

---

## Troubleshooting

### Install button doesn't appear (Android)
- Ensure using Chrome/Edge
- Check HTTPS is enabled
- Clear browser cache
- Wait 3 seconds after load

### Can't add to home screen (iOS)
- Must use Safari browser
- Ensure not in Private mode
- Update iOS to latest version

### App won't load offline
- Visit pages while online first
- Service worker needs to cache
- Check browser console for errors

### PWA doesn't install
- Requires HTTPS (except localhost)
- Check manifest.json is valid
- Service worker must be registered

### Clearing Cache

**iOS**: Settings > Safari > Clear History and Website Data

**Android**: App Settings > Sports Intel > Storage > Clear Cache

---

## Security on Mobile

### HTTPS Required
- PWA requires HTTPS in production
- Use Vercel/Netlify for auto-HTTPS
- localhost works for development

### Authentication
- Same owner-email restriction
- Session persists in app
- Secure token storage

### Offline Security
- Cached pages require auth first
- Sensitive data not cached
- Service worker respects auth

---

## Mobile Analytics (Optional)

Track mobile usage:

```typescript
// Add to app/layout.tsx
useEffect(() => {
  if (window.matchMedia('(display-mode: standalone)').matches) {
    // Track PWA usage
    console.log('Running as PWA');
  }
}, []);
```

---

## Next Steps

1. **Install on your phone** - Follow instructions above
2. **Test offline mode** - Turn on airplane mode
3. **Customize icons** - Replace SVG files
4. **Deploy to production** - Get HTTPS URL
5. **Share with team** - Send install link

Your dashboard is now a fully functional mobile app! 📱

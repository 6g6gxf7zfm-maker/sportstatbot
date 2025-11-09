# 🚀 Alternative Deployment Options

Having trouble with Vercel? Try these super easy alternatives!

---

## ⚡ **Option 1: Netlify (Recommended)**

### One-Click Deploy:
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/6g6gxf7zfm-maker/sportstatbot)

### Manual Deploy:
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Navigate to dashboard
cd dashboard

# Deploy
netlify deploy --prod

# Follow prompts:
# - Authorize with GitHub
# - Create new site
# - Build command: npm run build
# - Publish directory: .next
```

### Set Environment Variables:
In Netlify Dashboard → Site Settings → Environment Variables:
- `OWNER_EMAIL` = your@email.com
- `NEXTAUTH_SECRET` = (generate with: openssl rand -base64 32)
- `NEXTAUTH_URL` = https://your-site.netlify.app

---

## 🚂 **Option 2: Railway (Super Easy)**

### One-Click Deploy:
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/6g6gxf7zfm-maker/sportstatbot)

### Manual Deploy:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd dashboard
railway init

# Deploy
railway up

# Add environment variables
railway variables set OWNER_EMAIL=your@email.com
railway variables set NEXTAUTH_SECRET=$(openssl rand -base64 32)
railway variables set NEXTAUTH_URL=https://your-app.railway.app
```

### View Your App:
```bash
railway open
```

**Benefits:**
- ✅ Free tier (500 hours/month)
- ✅ Automatic HTTPS
- ✅ Easy environment variables
- ✅ PostgreSQL available (upgrade from SQLite later)

---

## 🎨 **Option 3: Render**

### One-Click Deploy:
Go to: https://render.com

1. Click **"New +"** → **"Web Service"**
2. Connect GitHub: `6g6gxf7zfm-maker/sportstatbot`
3. **Root Directory**: `dashboard`
4. **Build Command**: `npm install && npm run build`
5. **Start Command**: `npm start`
6. **Environment**: Node

### Add Environment Variables:
- `OWNER_EMAIL` = your@email.com
- `NEXTAUTH_SECRET` = (generate)
- `NEXTAUTH_URL` = https://your-app.onrender.com
- `NODE_VERSION` = 20

Click **Create Web Service**

**Benefits:**
- ✅ Free tier available
- ✅ Automatic deploys from GitHub
- ✅ PostgreSQL databases included
- ✅ Great for production apps

---

## 🐳 **Option 4: Docker + Any Platform**

### Build Docker Image:
```bash
# Create Dockerfile
cd dashboard
cat > Dockerfile << 'EOF'
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
EOF

# Build
docker build -t sports-dashboard .

# Run locally
docker run -p 3000:3000 \
  -e OWNER_EMAIL=your@email.com \
  -e NEXTAUTH_SECRET=your-secret \
  -e NEXTAUTH_URL=http://localhost:3000 \
  sports-dashboard
```

### Deploy to:
- **Fly.io**: `fly launch`
- **DigitalOcean App Platform**: Upload image
- **AWS Lightsail**: Container service
- **Google Cloud Run**: Deploy container

---

## 🌐 **Option 5: Cloudflare Pages**

```bash
# Install Wrangler
npm install -g wrangler

# Login
wrangler login

# Deploy
cd dashboard
npx @cloudflare/next-on-pages@1

# Deploy
wrangler pages deploy .vercel/output/static
```

**Note:** Cloudflare Pages requires adapter for Next.js

---

## ⚙️ **Recommended: Railway (Easiest)**

Railway is the **simplest** alternative:

1. **Install CLI**: `npm install -g @railway/cli`
2. **Login**: `railway login`
3. **Deploy**:
   ```bash
   cd dashboard
   railway init
   railway up
   ```
4. **Add env vars**:
   ```bash
   railway variables set OWNER_EMAIL=your@email.com
   railway variables set NEXTAUTH_SECRET=$(openssl rand -base64 32)
   ```
5. **Open**: `railway open`

Done! Your dashboard is live in 2 minutes! 🎉

---

## 📱 **After Deployment**

Once deployed on any platform:

1. **Get your URL** (e.g., `https://sports-dashboard.railway.app`)
2. **Open on mobile**
3. **iPhone**: Safari → Share → Add to Home Screen
4. **Android**: Chrome → Menu → Install App

---

## 🆘 **Need Help?**

**All platforms failing?**
- Check Node version is 20+
- Ensure build command runs locally: `npm run build`
- Check environment variables are set
- Look at deployment logs for errors

**Still stuck?**
- Railway has best error messages
- Render has great documentation
- Netlify has active community support

---

**Try Railway - it's the easiest!** 🚂

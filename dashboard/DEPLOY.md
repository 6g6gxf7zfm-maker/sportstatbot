# Deploy Your Sports Dashboard to Mobile

This guide shows you how to deploy your dashboard to get a **permanent public URL** you can access from your phone.

---

## 🚀 **Option 1: Vercel (Recommended - Easiest)**

### Step 1: Install Vercel CLI on your local machine

```bash
npm install -g vercel
```

### Step 2: Navigate to the dashboard folder

```bash
cd /home/user/sportstatbot/dashboard
```

### Step 3: Deploy

```bash
vercel
```

**During setup:**
- Login to Vercel (opens browser)
- Link to existing project? **No**
- Project name? (Press Enter)
- In which directory? **./` (Press Enter)
- Override settings? **No**

### Step 4: Set Environment Variables

```bash
vercel env add OWNER_EMAIL production
# Enter: your@email.com

vercel env add NEXTAUTH_SECRET production
# Generate: openssl rand -base64 32
# Paste the generated secret

vercel env add NEXTAUTH_URL production
# Enter: https://your-app.vercel.app (use the URL from step 3)
```

### Step 5: Deploy to Production

```bash
vercel --prod
```

**Your URL:** `https://your-dashboard.vercel.app`

---

## 🔷 **Option 2: Netlify**

### Step 1: Install Netlify CLI

```bash
npm install -g netlify-cli
```

### Step 2: Deploy

```bash
cd /home/user/sportstatbot/dashboard
netlify deploy --prod
```

### Step 3: Set Environment Variables

Go to: **Netlify Dashboard → Site Settings → Environment Variables**

Add:
- `OWNER_EMAIL` = your@email.com
- `NEXTAUTH_SECRET` = (generate with: `openssl rand -base64 32`)
- `NEXTAUTH_URL` = https://your-site.netlify.app

### Step 4: Redeploy

```bash
netlify deploy --prod
```

---

## 🟢 **Option 3: Railway (Free tier available)**

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Deploy

```bash
cd /home/user/sportstatbot/dashboard
railway login
railway init
railway up
```

### Step 3: Add Environment Variables

```bash
railway variables set OWNER_EMAIL=your@email.com
railway variables set NEXTAUTH_SECRET=$(openssl rand -base64 32)
railway variables set NEXTAUTH_URL=https://your-app.railway.app
```

---

## 🟣 **Option 4: Render**

### Via Web Interface:

1. Go to: https://render.com
2. Click **New → Web Service**
3. Connect your GitHub repo: `6g6gxf7zfm-maker/sportstatbot`
4. Settings:
   - **Root Directory:** `dashboard`
   - **Build Command:** `npm install && npm run build`
   - **Start Command:** `npm start`
   - **Environment:** Node

5. Add Environment Variables:
   - `OWNER_EMAIL` = your@email.com
   - `NEXTAUTH_SECRET` = (generate)
   - `NEXTAUTH_URL` = https://your-app.onrender.com

6. Click **Create Web Service**

---

## 📱 **After Deployment**

Once deployed, you'll get a URL like:
- Vercel: `https://sports-dashboard.vercel.app`
- Netlify: `https://sports-dashboard.netlify.app`
- Railway: `https://sports-dashboard.railway.app`
- Render: `https://sports-dashboard.onrender.com`

### On Your Phone:

1. Open the URL in your phone's browser
2. **iOS (Safari):** Tap Share → Add to Home Screen
3. **Android (Chrome):** Tap menu → Install App
4. The app will appear on your home screen!

---

## 🔐 **Login Credentials**

- **Email:** Whatever you set as `OWNER_EMAIL`
- **Password:** Any password (demo mode)

---

## ⚡ **Quick Deploy (If you have Git)**

### Using Vercel:

```bash
# From your local machine (not Claude Code)
cd path/to/sportstatbot/dashboard
npm install -g vercel
vercel login
vercel
# Follow prompts
vercel env add OWNER_EMAIL
vercel env add NEXTAUTH_SECRET
vercel env add NEXTAUTH_URL
vercel --prod
```

### Using Netlify:

```bash
cd path/to/sportstatbot/dashboard
npm install -g netlify-cli
netlify login
netlify init
netlify deploy --prod
# Set env vars in dashboard
```

---

## 🎯 **Recommended: Vercel**

**Why Vercel?**
- ✅ Free tier (enough for personal use)
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Zero configuration
- ✅ GitHub integration
- ✅ Instant deployments
- ✅ Perfect for Next.js

---

## 🐛 **Troubleshooting**

### Build fails on Vercel/Netlify
The app uses a mock database, so it should work. If it fails:
1. Check build logs
2. Ensure all environment variables are set
3. Try deploying again

### Can't login after deployment
1. Verify `OWNER_EMAIL` matches exactly
2. Check `NEXTAUTH_URL` is correct (must match your deployment URL)
3. Ensure `NEXTAUTH_SECRET` is set (min 32 chars)

### App not installing on mobile
1. Must use HTTPS (all these platforms provide it)
2. On iOS, use Safari browser
3. On Android, use Chrome browser
4. Wait 3 seconds for install prompt

---

## 📊 **After Deployment**

Your dashboard will be accessible:
- From any device
- Works offline (PWA)
- Installable as app
- Secure HTTPS
- Private (owner-only access)

Enjoy your mobile sports dashboard! 📱⚽🏀🏈

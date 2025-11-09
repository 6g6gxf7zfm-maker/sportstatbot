# 🚀 Quick Deploy to See on Mobile (While Still Adding Features)

Deploy a **live preview** to see how your dashboard looks on mobile. You can keep updating it as you add features!

---

## ⚡ **Option 1: One-Click Deploy to Vercel (Fastest)**

Click this button to deploy instantly:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/6g6gxf7zfm-maker/sportstatbot&project-name=sports-dashboard&repository-name=sports-dashboard&root-directory=dashboard&env=OWNER_EMAIL,NEXTAUTH_SECRET,NEXTAUTH_URL&envDescription=Required%20environment%20variables&envLink=https://github.com/6g6gxf7zfm-maker/sportstatbot/blob/main/dashboard/.env.example)

**After clicking:**
1. Login to Vercel (free)
2. Set environment variables:
   - `OWNER_EMAIL` = your@email.com
   - `NEXTAUTH_SECRET` = any-random-text-min-32-chars
   - `NEXTAUTH_URL` = (leave blank, will auto-fill)
3. Click **Deploy**
4. Wait 2 minutes
5. **You'll get a URL!** Open it on your phone!

---

## ⚡ **Option 2: Deploy from Command Line (2 minutes)**

### From your computer:

```bash
# 1. Clone the repo (if you haven't already)
git clone https://github.com/6g6gxf7zfm-maker/sportstatbot.git
cd sportstatbot/dashboard

# 2. Install Vercel CLI
npm install -g vercel

# 3. Deploy preview
vercel

# Follow prompts, then you'll get a URL like:
# https://sports-dashboard-abc123.vercel.app
```

**Environment variables** (add these after first deploy):
```bash
vercel env add OWNER_EMAIL
# Type: your@email.com

vercel env add NEXTAUTH_SECRET
# Type: test-secret-for-preview-only-min32chars

vercel env add NEXTAUTH_URL
# Type: your-preview-url-from-above
```

Then redeploy:
```bash
vercel
```

---

## ⚡ **Option 3: GitHub Pages (Static Preview)**

This won't have full functionality but you can see the UI:

```bash
cd sportstatbot/dashboard
npm run build
npm run export  # If available
```

---

## 📱 **View on Your Phone**

Once deployed, you'll get a URL like:
- **Preview:** `https://sports-dashboard-xyz123.vercel.app`

### On mobile:
1. Open URL in browser
2. See how it looks!
3. **iOS:** Safari → Share → Add to Home Screen
4. **Android:** Chrome → Menu → Install App

---

## 🔄 **Keep Adding Features**

The beauty of this setup:

1. **Deploy preview now** → Get URL to test on mobile
2. **Keep coding** → Add features in Claude Code
3. **Push to GitHub** → `git push`
4. **Auto-deploys** → Vercel auto-updates your preview!

Every time you push to GitHub, Vercel automatically redeploys. You'll always have the latest version on mobile!

---

## 🔧 **Update Your Live Preview**

As you add features:

```bash
# In Claude Code
git add .
git commit -m "Add new feature"
git push

# Vercel automatically redeploys!
# Check your preview URL in ~30 seconds
```

---

## 🎯 **Recommended Flow**

1. **Now:** Deploy preview with button above
2. **Test:** Open preview URL on phone, see how it looks
3. **Code:** Keep adding features in Claude Code
4. **Push:** Each push auto-updates your preview
5. **Launch:** When ready, deploy to production (`vercel --prod`)

---

## 📱 **Quick Test URLs**

After deployment, these will work:
- **Dashboard:** `https://your-url.vercel.app/dashboard`
- **Jobs:** `https://your-url.vercel.app/jobs`
- **Exports:** `https://your-url.vercel.app/exports`
- **Login:** `https://your-url.vercel.app/auth/signin`

---

## 🐛 **Troubleshooting**

### Can't login?
Use the email you set in `OWNER_EMAIL`, any password works in demo mode.

### Preview not updating?
Check Vercel dashboard or run `vercel --prod` to force redeploy.

### Want to remove preview?
```bash
vercel remove sports-dashboard
```

---

**Ready to see it on mobile? Click the deploy button above!** 🚀

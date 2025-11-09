# 🚀 Deploy Your Dashboard RIGHT NOW

Choose the fastest option for you:

---

## ⚡ **FASTEST: One-Click Deploy (30 seconds)**

1. **Click this link:** https://vercel.com/new/clone?repository-url=https://github.com/6g6gxf7zfm-maker/sportstatbot&project-name=sports-dashboard&root-directory=dashboard

2. **Login** to Vercel (free account)

3. Click **"Deploy"**

4. **Wait 2 minutes** ☕

5. **You'll get a URL!** Copy it and open on your phone!

---

## 💻 **From Your Computer (2 minutes)**

### Option A: One Command (No installation needed)

```bash
# Clone repo
git clone https://github.com/6g6gxf7zfm-maker/sportstatbot.git
cd sportstatbot/dashboard

# Deploy with npx (no install needed)
npx vercel
```

### Option B: Use the script

```bash
cd sportstatbot/dashboard
./deploy-preview.sh
```

---

## 🔐 **Add Your Email (After First Deploy)**

Once deployed, add your owner email:

```bash
# From dashboard directory
vercel env add OWNER_EMAIL preview
# Enter: your@email.com

vercel env add NEXTAUTH_SECRET preview
# Enter: any-random-text-at-least-32-characters-long

vercel env add NEXTAUTH_URL preview
# Enter: the-url-you-got-from-vercel

# Redeploy with new env vars
vercel
```

---

## 📱 **Open on Mobile**

Your URL will look like:
- `https://sports-dashboard-abc123.vercel.app`

**On iPhone:**
1. Open in **Safari**
2. Tap **Share** → **Add to Home Screen**
3. Done! App is on your home screen

**On Android:**
1. Open in **Chrome**
2. Tap **Menu (⋮)** → **Install App**
3. Done! App is in your app drawer

---

## 🎯 **Login**

- **Email:** The email you set in `OWNER_EMAIL`
- **Password:** Any password (demo mode)

---

## ⚠️ **Don't Have a Computer Nearby?**

### Deploy from GitHub:

1. Go to: https://github.com/6g6gxf7zfm-maker/sportstatbot
2. Fork the repository
3. Go to: https://vercel.com/new
4. Import your forked repository
5. Set root directory to: `dashboard`
6. Click Deploy!

---

## 🔄 **Auto-Deploy Setup (Optional)**

To auto-deploy when you push code:

1. Get Vercel token: https://vercel.com/account/tokens
2. Add to GitHub Secrets:
   - Go to repo → Settings → Secrets → New secret
   - Name: `VERCEL_TOKEN`
   - Value: your-token
3. GitHub Actions will auto-deploy on every push!

---

## ✅ **What You Get**

- **Live URL** accessible from anywhere
- **HTTPS** automatically configured
- **Auto-updates** on every git push (if GitHub Actions set up)
- **Mobile app** installable on iOS/Android
- **Offline support** with PWA features

---

## 🆘 **Need Help?**

**Can't deploy?**
- Check you're logged into Vercel
- Ensure Node.js 20+ is installed
- Try the one-click button above

**Can't login to dashboard?**
- Use the exact email from `OWNER_EMAIL`
- Any password works in demo mode
- Check browser console for errors

**Preview not loading?**
- Wait 2-3 minutes for first deploy
- Check Vercel dashboard for build logs
- Try accessing in incognito mode

---

**🎉 Click the link above and deploy in 30 seconds!**

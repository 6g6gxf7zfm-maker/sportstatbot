# Setup Guide

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
cd dashboard
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set **minimum required values**:

```env
OWNER_EMAIL=your@email.com
NEXTAUTH_SECRET=your-secret-here
NEXTAUTH_URL=http://localhost:3000
```

Generate `NEXTAUTH_SECRET`:
```bash
openssl rand -base64 32
```

### 3. Initialize Database

```bash
npm run db:push
```

### 4. Start Development Server

```bash
npm run dev
```

### 5. Access Dashboard

Open http://localhost:3000

**Login with**: The email you set in `OWNER_EMAIL`
**Password**: Any password (credentials provider is simplified for demo)

---

## Advanced Setup

### Google Drive Integration

**1. Create Google Cloud Project**
- Go to https://console.cloud.google.com
- Create new project
- Enable Google Drive API and Google Docs API

**2. Create Service Account**
- Go to IAM & Admin > Service Accounts
- Create service account
- Download JSON key file

**3. Share Drive Folder**
- Create a folder in Google Drive
- Share it with the service account email (found in JSON)
- Copy folder ID from URL

**4. Add to .env**
```env
GOOGLE_DRIVE_CREDENTIALS='{"type":"service_account","project_id":"...","private_key":"...","client_email":"..."}'
GOOGLE_ROOT_FOLDER_ID=your-folder-id-here
```

### Apple Notes Integration

**1. Create iOS Shortcut**
- Open Shortcuts app on Mac/iPhone
- Create new shortcut
- Add "Receive" action with JSON input
- Add "Get Dictionary Value" for title, body, folder, tags
- Add "Create Note" action
- Enable "Allow Sharing"

**2. Get Webhook URL**
- Share shortcut
- Copy the shortcut URL

**3. Add to .env**
```env
APPLE_SHORTCUT_WEBHOOK=https://www.icloud.com/shortcuts/xxxxx
```

### IP Allowlist (Optional)

Restrict access to specific IPs:

```env
IP_ALLOWLIST=203.0.113.10,198.51.100.22,192.168.1.100
```

To find your IP:
```bash
curl ifconfig.me
```

---

## Production Deployment

### Option 1: Vercel (Easiest)

1. Push code to GitHub
2. Go to https://vercel.com
3. Import repository
4. Add environment variables
5. Deploy

**Important**: Switch to PostgreSQL for production:
```env
DATABASE_URL=postgresql://user:pass@host/db
```

### Option 2: Docker

```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npx prisma generate
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t sports-dashboard .
docker run -p 3000:3000 --env-file .env sports-dashboard
```

### Option 3: PM2 (VPS)

```bash
npm install -g pm2
npm run build
pm2 start npm --name "sports-dashboard" -- start
pm2 save
pm2 startup
```

---

## Testing the Setup

### 1. Test Authentication
- Navigate to `/auth/signin`
- Enter your `OWNER_EMAIL`
- Verify you can access dashboard

### 2. Test Jobs
- Go to `/jobs`
- Select league and type
- Click "Run Job"
- Verify job appears in list

### 3. Test Exports
- Go to `/exports`
- Click "Export Now"
- Check Google Docs or Apple Notes

### 4. Test Security
- Try accessing from different email (should fail)
- Check IP allowlist (if configured)
- Verify robots.txt at `/robots.txt`

---

## Common Issues

### "Forbidden" Error
- Check `OWNER_EMAIL` matches exactly
- Verify IP is in `IP_ALLOWLIST` (if set)

### Database Errors
```bash
rm prisma/dev.db
npm run db:push
```

### NextAuth Session Issues
- Clear browser cookies
- Verify `NEXTAUTH_SECRET` is set
- Check `NEXTAUTH_URL` matches current URL

### Build Errors
```bash
rm -rf .next node_modules
npm install
npm run build
```

---

## Next Steps

1. **Customize UI**: Edit components in `/components`
2. **Add Real AI Integration**: Replace stub API calls in `/app/api`
3. **Configure Email Provider**: Switch to production email in `lib/auth.ts`
4. **Set Up Monitoring**: Add error tracking (Sentry, etc.)
5. **Enable HTTPS**: Use SSL certificate in production

---

## Support

For issues or questions:
1. Check troubleshooting in README.md
2. Review error logs: `tail -f .next/server.log`
3. Run database viewer: `npm run db:studio`

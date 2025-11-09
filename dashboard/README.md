# Sports Intelligence Dashboard

A **secure, private web application** for sports analysis AI system. This dashboard displays sports digests, features, and reports, with seamless export capabilities to Google Docs and Apple Notes.

## Features

- **Private Access**: Restricted to owner email only with NextAuth authentication
- **IP Allowlist**: Optional IP-based access control
- **Security Headers**: CSP, HSTS, X-Frame-Options, and more
- **AI Job Management**: Trigger and monitor AI pipeline jobs
- **Export Integration**: Export stories to Google Docs and Apple Notes
- **Dark Mode**: Full dark/light theme support
- **Audit Logging**: Track all user actions in SQLite database
- **📱 Mobile App (PWA)**: Install on iOS/Android as a native app
- **🔄 Offline Support**: Service worker for offline functionality
- **📲 Responsive Design**: Optimized for phones, tablets, and desktop

## Tech Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Authentication**: NextAuth
- **Database**: SQLite (via Prisma)
- **Integrations**: Google Drive API, Apple Shortcuts

## Getting Started

### Prerequisites

- Node.js 20+
- npm or yarn

### Installation

1. **Clone and navigate to the dashboard directory:**

```bash
cd dashboard
```

2. **Install dependencies:**

```bash
npm install
```

3. **Set up environment variables:**

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required variables:
- `OWNER_EMAIL`: Your email (only this email will have access)
- `NEXTAUTH_SECRET`: Generate with `openssl rand -base64 32`
- `NEXTAUTH_URL`: Your app URL (http://localhost:3000 for dev)

Optional:
- `IP_ALLOWLIST`: Comma-separated IPs to allow
- `GOOGLE_DRIVE_CREDENTIALS`: Service account JSON
- `GOOGLE_ROOT_FOLDER_ID`: Google Drive folder ID
- `APPLE_SHORTCUT_WEBHOOK`: iOS Shortcut webhook URL

4. **Initialize the database:**

```bash
npm run db:push
```

5. **Run the development server:**

```bash
npm run dev
```

6. **Open your browser:**

Navigate to [http://localhost:3000](http://localhost:3000)

## Routes

| Path | Purpose |
|------|---------|
| `/` | Redirects to dashboard |
| `/auth/signin` | Login page |
| `/dashboard` | Main view with recent digests and reports |
| `/jobs` | Trigger AI workflows |
| `/exports` | Export stories to Google Docs/Apple Notes |
| `/api/jobs/run` | API: Trigger/list jobs |
| `/api/exports/google` | API: Export to Google Docs |
| `/api/exports/apple` | API: Export to Apple Notes |

## Google Drive Setup

1. Create a Google Cloud Project
2. Enable Google Drive and Google Docs APIs
3. Create a Service Account
4. Download the credentials JSON
5. Share your target Google Drive folder with the service account email
6. Add credentials to `.env`:
   ```
   GOOGLE_DRIVE_CREDENTIALS='{"type":"service_account",...}'
   GOOGLE_ROOT_FOLDER_ID='your-folder-id'
   ```

## Apple Notes Setup

1. Create an iOS Shortcut on your Mac/iPhone
2. Add a "Get contents of URL" action
3. Parse the JSON payload (title, body, folder, tags)
4. Add "Create Note" action
5. Enable "Show in Share Sheet" and get the webhook URL
6. Add to `.env`:
   ```
   APPLE_SHORTCUT_WEBHOOK='https://your-shortcut-url'
   ```

## Security Features

### Authentication
- Email-based authentication via NextAuth
- Restricted to `OWNER_EMAIL` only
- JWT session strategy

### IP Allowlist
- Optional IP-based access control
- Configure in `.env` with `IP_ALLOWLIST`

### Security Headers
- Content-Security-Policy
- Strict-Transport-Security (HSTS)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy: no-referrer

### Private Access
- `robots.txt` set to `Disallow: /`
- All routes protected by middleware
- Only authenticated owner can access

## Database Schema

The SQLite database includes:
- `User`, `Account`, `Session`: NextAuth tables
- `Job`: AI pipeline job tracking
- `Export`: Export history
- `AuditLog`: User action logging

View database:
```bash
npm run db:studio
```

## Development Scripts

```bash
npm run dev        # Start development server
npm run build      # Build for production
npm run start      # Start production server
npm run lint       # Run ESLint
npm run db:push    # Push schema to database
npm run db:studio  # Open Prisma Studio
```

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

**Note**: For SQLite, consider switching to PostgreSQL for production (Vercel Postgres, Supabase, etc.)

### Cloudflare Pages

1. Build command: `npm run build`
2. Output directory: `.next`
3. Add environment variables

### Fly.io

1. Install flyctl
2. Run `fly launch`
3. Add environment variables
4. Deploy with `fly deploy`

## Troubleshooting

### Cannot sign in
- Verify `OWNER_EMAIL` in `.env` matches your email exactly
- Check `NEXTAUTH_SECRET` is set
- Ensure `NEXTAUTH_URL` matches your app URL

### IP blocked
- Check `IP_ALLOWLIST` includes your IP
- Remove `IP_ALLOWLIST` to disable IP filtering

### Google export fails
- Verify service account credentials are valid JSON
- Ensure folder is shared with service account email
- Check folder ID is correct

### Database errors
- Run `npm run db:push` to sync schema
- Delete `prisma/dev.db` and run `db:push` again

## License

Private use only.

# Project Structure

```
dashboard/
├── app/                          # Next.js App Router
│   ├── api/                      # API Routes
│   │   ├── auth/
│   │   │   └── [...nextauth]/    # NextAuth endpoint
│   │   │       └── route.ts
│   │   ├── jobs/
│   │   │   └── run/             # Job trigger/list endpoint
│   │   │       └── route.ts
│   │   └── exports/             # Export endpoints
│   │       ├── route.ts         # List exports
│   │       ├── google/          # Google Docs export
│   │       │   └── route.ts
│   │       └── apple/           # Apple Notes export
│   │           └── route.ts
│   ├── auth/                    # Authentication pages
│   │   ├── signin/
│   │   │   └── page.tsx
│   │   └── error/
│   │       └── page.tsx
│   ├── dashboard/               # Main dashboard
│   │   └── page.tsx
│   ├── jobs/                    # Jobs management
│   │   └── page.tsx
│   ├── exports/                 # Exports management
│   │   └── page.tsx
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page (redirects)
│   ├── providers.tsx            # Context providers
│   └── globals.css              # Global styles
│
├── components/                  # Reusable UI components
│   ├── Sidebar.tsx              # Navigation sidebar
│   ├── Header.tsx               # Page header
│   └── ThemeToggle.tsx          # Dark/light mode toggle
│
├── lib/                         # Utility libraries
│   ├── auth.ts                  # NextAuth configuration
│   ├── prisma.ts                # Prisma client
│   ├── ip-allow.ts              # IP allowlist utilities
│   ├── google.ts                # Google Drive/Docs API
│   └── apple.ts                 # Apple Notes webhook
│
├── prisma/                      # Database
│   └── schema.prisma            # Database schema
│
├── public/                      # Static files
│   └── robots.txt               # SEO/privacy
│
├── types/                       # TypeScript definitions
│   └── next-auth.d.ts           # NextAuth types
│
├── middleware.ts                # Security middleware
├── next.config.js               # Next.js configuration
├── tailwind.config.ts           # Tailwind CSS config
├── postcss.config.mjs           # PostCSS config
├── tsconfig.json                # TypeScript config
├── package.json                 # Dependencies
├── .env.example                 # Environment template
├── .eslintrc.json               # ESLint config
├── .gitignore                   # Git ignore rules
├── README.md                    # Documentation
├── SETUP.md                     # Setup guide
└── PROJECT_STRUCTURE.md         # This file
```

## Key Files

### Security
- `middleware.ts` - Auth & IP protection
- `next.config.js` - Security headers
- `lib/ip-allow.ts` - IP allowlist logic
- `public/robots.txt` - Search engine blocking

### Authentication
- `lib/auth.ts` - NextAuth setup with owner restriction
- `app/api/auth/[...nextauth]/route.ts` - Auth endpoint
- `app/auth/signin/page.tsx` - Login page
- `types/next-auth.d.ts` - Type definitions

### Database
- `prisma/schema.prisma` - Schema (User, Job, Export, AuditLog)
- `lib/prisma.ts` - Prisma client singleton

### Integrations
- `lib/google.ts` - Google Drive/Docs export
- `lib/apple.ts` - Apple Notes webhook
- `app/api/exports/google/route.ts` - Google export API
- `app/api/exports/apple/route.ts` - Apple export API

### UI
- `components/Sidebar.tsx` - Navigation with leagues
- `components/Header.tsx` - Page header with user info
- `components/ThemeToggle.tsx` - Dark/light mode
- `app/globals.css` - Global styles & Tailwind

### Pages
- `app/dashboard/page.tsx` - Main dashboard
- `app/jobs/page.tsx` - Job management
- `app/exports/page.tsx` - Export management

## Data Flow

### Job Trigger
1. User clicks "Run Job" in `/jobs`
2. POST to `/api/jobs/run`
3. Creates Job record in DB
4. Simulates AI pipeline (can be replaced with real integration)
5. Updates Job status to "completed"
6. Logs action in AuditLog

### Export to Google Docs
1. User clicks "Export to Docs" in `/exports`
2. POST to `/api/exports/google`
3. `lib/google.ts` creates folder structure: `/{LEAGUE}/{TYPE}/{DATE}/`
4. Creates Google Doc with formatted content
5. Records export in DB
6. Returns document URL
7. Logs action in AuditLog

### Export to Apple Notes
1. User clicks "Export to Notes" in `/exports`
2. POST to `/api/exports/apple`
3. `lib/apple.ts` sends payload to iOS Shortcut webhook
4. Shortcut creates note in Apple Notes
5. Records export in DB
6. Logs action in AuditLog

## Security Layers

1. **Middleware** (`middleware.ts`)
   - Checks IP allowlist (if configured)
   - Verifies NextAuth session exists
   - Confirms email matches OWNER_EMAIL

2. **API Routes**
   - Double-check session with `getServerSession()`
   - Validate email === OWNER_EMAIL
   - Log all actions to AuditLog

3. **Headers** (`next.config.js`)
   - CSP, HSTS, X-Frame-Options
   - Prevents embedding, XSS, clickjacking

4. **Private Access**
   - robots.txt blocks search engines
   - No public routes (all protected)
   - Single-user design

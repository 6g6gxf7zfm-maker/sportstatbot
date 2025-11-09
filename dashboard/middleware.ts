import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { getToken } from 'next-auth/jwt';
import { getClientIP, isIPAllowed } from './lib/ip-allow';

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // Allow public assets and Next.js internals
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api/auth') ||
    pathname.startsWith('/auth') ||
    pathname.match(/\.(png|jpg|jpeg|gif|svg|ico|css|js)$/)
  ) {
    return NextResponse.next();
  }

  // Check IP allowlist if configured
  const clientIP = getClientIP(req.headers);
  if (!isIPAllowed(clientIP)) {
    console.warn(`Blocked access from unauthorized IP: ${clientIP}`);
    return new NextResponse('Forbidden - IP not allowed', { status: 403 });
  }

  // Check authentication
  const token = await getToken({ req, secret: process.env.NEXTAUTH_SECRET });

  if (!token) {
    // Redirect to sign-in page
    const signInUrl = new URL('/auth/signin', req.url);
    signInUrl.searchParams.set('callbackUrl', pathname);
    return NextResponse.redirect(signInUrl);
  }

  // Verify it's the owner email
  if (token.email !== process.env.OWNER_EMAIL) {
    console.warn(`Unauthorized access attempt by: ${token.email}`);
    return new NextResponse('Forbidden - Unauthorized user', { status: 403 });
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico (favicon file)
     * - public files (robots.txt, etc.)
     */
    '/((?!_next/static|_next/image|favicon.ico|robots.txt).*)',
  ],
};

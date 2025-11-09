/**
 * IP Allowlist utility
 * Checks if a given IP address is in the allowlist
 */

export function isIPAllowed(clientIP: string | null): boolean {
  // If no IP allowlist is configured, allow all IPs
  const allowlist = process.env.IP_ALLOWLIST;

  if (!allowlist || allowlist.trim() === '') {
    return true;
  }

  if (!clientIP) {
    return false;
  }

  const allowedIPs = allowlist.split(',').map(ip => ip.trim());

  // Check if client IP is in the allowlist
  return allowedIPs.includes(clientIP);
}

/**
 * Extract client IP from request headers
 */
export function getClientIP(headers: Headers): string | null {
  // Try common headers in order of preference
  const forwardedFor = headers.get('x-forwarded-for');
  if (forwardedFor) {
    // x-forwarded-for can be a comma-separated list, take the first one
    return forwardedFor.split(',')[0].trim();
  }

  const realIP = headers.get('x-real-ip');
  if (realIP) {
    return realIP;
  }

  // Cloudflare
  const cfConnectingIP = headers.get('cf-connecting-ip');
  if (cfConnectingIP) {
    return cfConnectingIP;
  }

  return null;
}

import { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

export const authOptions: NextAuthOptions = {
  providers: [
    // Simple credentials provider for demo (use email provider in production)
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        // In production, verify password properly
        // This is a simplified version for demo
        if (credentials?.email === process.env.OWNER_EMAIL) {
          return {
            id: "owner",
            email: credentials.email,
          };
        }
        return null;
      }
    })
  ],
  callbacks: {
    async signIn({ user, account, profile }) {
      // Only allow the owner email to sign in
      if (user.email !== process.env.OWNER_EMAIL) {
        return false;
      }
      return true;
    },
    async jwt({ token, user, account }) {
      if (user) {
        token.email = user.email;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.email = token.email as string;
      }
      return session;
    },
  },
  pages: {
    signIn: "/auth/signin",
    error: "/auth/error",
  },
  session: {
    strategy: "jwt",
  },
  secret: process.env.NEXTAUTH_SECRET,
};

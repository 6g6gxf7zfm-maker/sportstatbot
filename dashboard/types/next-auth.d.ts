import NextAuth from "next-auth"

declare module "next-auth" {
  interface Session {
    user: {
      email: string
    }
  }

  interface User {
    email: string
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    email: string
  }
}

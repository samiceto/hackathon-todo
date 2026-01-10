/**
 * Better Auth configuration for JWT-based authentication.
 *
 * Configured with:
 * - JWT plugin for stateless authentication
 * - httpOnly cookies for secure token storage
 * - PostgreSQL database (Neon) for user management
 */

export const authConfig = {
  /**
   * Better Auth secret for JWT signing
   * Must match backend BETTER_AUTH_SECRET
   */
  secret: process.env.BETTER_AUTH_SECRET!,

  /**
   * Base URL for Better Auth
   * Used for redirect URLs and cookie domain
   */
  baseURL: process.env.BETTER_AUTH_URL || 'http://localhost:3000',

  /**
   * Database connection for user management
   * Better Auth stores user data in PostgreSQL
   */
  database: {
    provider: 'postgresql',
    url: process.env.DATABASE_URL!,
  },

  /**
   * JWT configuration
   */
  jwt: {
    /**
     * JWT expiration time (7 days)
     */
    expiresIn: '7d',

    /**
     * Algorithm for JWT signing (HS256)
     */
    algorithm: 'HS256' as const,
  },

  /**
   * Session configuration
   */
  session: {
    /**
     * Use httpOnly cookies for XSS protection
     */
    strategy: 'jwt' as const,

    /**
     * Cookie configuration
     */
    cookie: {
      name: 'auth_token',
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax' as const,
      maxAge: 60 * 60 * 24 * 7, // 7 days in seconds
    },
  },
}

export type AuthConfig = typeof authConfig

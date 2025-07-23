'use client';

import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  name?: string;
  role?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Note: This is a simplified auth provider. In production, you should:
// 1. Use proper authentication service (NextAuth.js, Auth0, Firebase Auth, etc.)
// 2. Never store sensitive data in localStorage
// 3. Use secure HTTP-only cookies for session management
// 4. Implement proper token validation and refresh
// 5. Add CSRF protection

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Check for existing session on mount
  useEffect(() => {
    const checkSession = async () => {
      try {
        // In production, this would check for a valid session token
        // For now, we'll just check sessionStorage (more secure than localStorage)
        const sessionData = sessionStorage.getItem('user_session');
        if (sessionData) {
          const parsed = JSON.parse(sessionData);
          // In production, validate the session with the server
          setUser(parsed.user);
        }
      } catch (error) {
        console.error('Failed to restore session:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkSession();
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      setIsLoading(true);
      setError(null);

      try {
        // In production, make API call to authentication endpoint
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
          throw new Error('Invalid credentials');
        }

        const data = await response.json();

        // Store session data (in production, use secure HTTP-only cookies)
        sessionStorage.setItem(
          'user_session',
          JSON.stringify({
            user: data.user,
            expiresAt: Date.now() + 1000 * 60 * 60 * 24, // 24 hours
          })
        );

        setUser(data.user);
        router.push('/dashboard');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Login failed');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [router]
  );

  const signup = useCallback(
    async (email: string, password: string, name?: string) => {
      setIsLoading(true);
      setError(null);

      try {
        // In production, make API call to registration endpoint
        const response = await fetch('/api/auth/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, name }),
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.error || 'Signup failed');
        }

        const data = await response.json();

        // Auto-login after signup
        sessionStorage.setItem(
          'user_session',
          JSON.stringify({
            user: data.user,
            expiresAt: Date.now() + 1000 * 60 * 60 * 24, // 24 hours
          })
        );

        setUser(data.user);
        router.push('/dashboard');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Signup failed');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [router]
  );

  const logout = useCallback(async () => {
    setIsLoading(true);

    try {
      // In production, call logout endpoint to invalidate session
      await fetch('/api/auth/logout', { method: 'POST' });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      sessionStorage.removeItem('user_session');
      setUser(null);
      setIsLoading(false);
      router.push('/');
    }
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        error,
        login,
        signup,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (ctx === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
}

// Protected route wrapper
export function withAuth<P extends object>(
  Component: React.ComponentType<P>
): React.ComponentType<P> {
  return function AuthenticatedComponent(props: P) {
    const { user, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!isLoading && !user) {
        router.push('/login');
      }
    }, [user, isLoading, router]);

    if (isLoading) {
      return <div>Loading...</div>;
    }

    if (!user) {
      return null;
    }

    return <Component {...props} />;
  };
}

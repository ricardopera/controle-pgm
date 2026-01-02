/**
 * Authentication context for Controle PGM.
 * Provides auth state and methods throughout the application.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { api, onUnauthorized } from './api';

/**
 * User information from authentication.
 */
export interface User {
  user_id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  must_change_password: boolean;
}

/**
 * Authentication context value type.
 */
interface AuthContextType {
  /** Current authenticated user, null if not authenticated */
  user: User | null;
  /** Whether authentication check is in progress */
  isLoading: boolean;
  /** Whether user is authenticated */
  isAuthenticated: boolean;
  /** Whether user is an admin */
  isAdmin: boolean;
  /** Login with email and password */
  login: (email: string, password: string) => Promise<void>;
  /** Logout current user */
  logout: () => Promise<void>;
  /** Refresh user data from server */
  refreshUser: () => Promise<void>;
  /** Update local user data (after password change, etc.) */
  updateUser: (updates: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

/**
 * Props for AuthProvider component.
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Authentication provider component.
 * Wraps the application to provide auth state and methods.
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check authentication status on mount
  const checkAuth = useCallback(async () => {
    try {
      const userData = await api.auth.me();
      setUser(userData);
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Listen for 401 responses (session expired)
  useEffect(() => {
    const unsubscribe = onUnauthorized(() => {
      setUser(null);
    });
    return unsubscribe;
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const userData = await api.auth.login(email, password);
    setUser(userData);
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.auth.logout();
    } finally {
      setUser(null);
    }
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const userData = await api.auth.me();
      setUser(userData);
    } catch {
      setUser(null);
    }
  }, []);

  const updateUser = useCallback((updates: Partial<User>) => {
    setUser((prev) => (prev ? { ...prev, ...updates } : null));
  }, []);

  const value = useMemo<AuthContextType>(
    () => ({
      user,
      isLoading,
      isAuthenticated: !!user,
      isAdmin: user?.role === 'admin',
      login,
      logout,
      refreshUser,
      updateUser,
    }),
    [user, isLoading, login, logout, refreshUser, updateUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to access authentication context.
 * Must be used within an AuthProvider.
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

/**
 * Hook that requires authentication.
 * Throws if user is not authenticated.
 */
export function useRequireAuth(): AuthContextType & { user: User } {
  const auth = useAuth();
  if (!auth.isAuthenticated || !auth.user) {
    throw new Error('User is not authenticated');
  }
  return auth as AuthContextType & { user: User };
}

/**
 * Hook that requires admin role.
 * Throws if user is not an admin.
 */
export function useRequireAdmin(): AuthContextType & { user: User } {
  const auth = useRequireAuth();
  if (!auth.isAdmin) {
    throw new Error('User is not an admin');
  }
  return auth;
}

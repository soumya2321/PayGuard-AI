/**
 * useAuth.tsx - React Context and custom hook managing client-side authentication state.
 * Implements session persistence and 5-attempt rate-limiting lockout.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { User, LoginCredentials, AuthContextValue, AuthState } from '../types/auth.types';
import { authApi } from '../api/authApi';
import { formatAuthErrorMessage } from '../utils/validatePassword';

const AUTH_STORAGE_KEY = 'payguard_auth_token';
const USER_STORAGE_KEY = 'payguard_auth_user';
const MAX_FAILED_ATTEMPTS = 5;
const LOCKOUT_DURATION_SECONDS = 60;

const initialAuthState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>(initialAuthState);
  const [failedAttemptCount, setFailedAttemptCount] = useState<number>(0);
  const [lockoutExpiryTimestamp, setLockoutExpiryTimestamp] = useState<number | null>(null);

  // Restore authenticated session from storage on initial mount
  useEffect(() => {
    const restoreSession = async () => {
      try {
        const storedToken = sessionStorage.getItem(AUTH_STORAGE_KEY);
        const storedUser = sessionStorage.getItem(USER_STORAGE_KEY);

        if (storedToken && storedUser) {
          const parsedUser: User = JSON.parse(storedUser);
          setAuthState({
            user: parsedUser,
            token: storedToken,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          return;
        }
      } catch {
        sessionStorage.removeItem(AUTH_STORAGE_KEY);
        sessionStorage.removeItem(USER_STORAGE_KEY);
      }

      setAuthState((prev) => ({ ...prev, isLoading: false }));
    };

    restoreSession();
  }, []);

  const clearError = useCallback(() => {
    setAuthState((prev) => ({ ...prev, error: null }));
  }, []);

  const login = useCallback(
    async (credentials: LoginCredentials): Promise<boolean> => {
      // Check if locked out due to rate limiting
      const now = Date.now();
      if (lockoutExpiryTimestamp && now < lockoutExpiryTimestamp) {
        const remainingSeconds = Math.ceil((lockoutExpiryTimestamp - now) / 1000);
        setAuthState((prev) => ({
          ...prev,
          error: `Too many failed attempts. Account locked for ${remainingSeconds} seconds.`,
          isLoading: false,
        }));
        return false;
      }

      setAuthState((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        const response = await authApi.login(credentials);

        // Reset rate limiter on successful authentication
        setFailedAttemptCount(0);
        setLockoutExpiryTimestamp(null);

        // Persist session
        sessionStorage.setItem(AUTH_STORAGE_KEY, response.token);
        sessionStorage.setItem(USER_STORAGE_KEY, JSON.stringify(response.user));

        setAuthState({
          user: response.user,
          token: response.token,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });

        return true;
      } catch (err: unknown) {
        const newFailCount = failedAttemptCount + 1;
        setFailedAttemptCount(newFailCount);

        let formattedError = formatAuthErrorMessage(err);

        if (newFailCount >= MAX_FAILED_ATTEMPTS) {
          const expiry = Date.now() + LOCKOUT_DURATION_SECONDS * 1000;
          setLockoutExpiryTimestamp(expiry);
          setFailedAttemptCount(0);
          formattedError = 'Too many failed login attempts. Account locked for 60 seconds.';
        }

        setAuthState((prev) => ({
          ...prev,
          isLoading: false,
          error: formattedError,
        }));

        return false;
      }
    },
    [failedAttemptCount, lockoutExpiryTimestamp]
  );

  const logout = useCallback(async () => {
    if (authState.token) {
      try {
        await authApi.logout(authState.token);
      } catch {
        // Continue client logout even if backend network unreachable
      }
    }

    sessionStorage.removeItem(AUTH_STORAGE_KEY);
    sessionStorage.removeItem(USER_STORAGE_KEY);

    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  }, [authState.token]);

  return (
    <AuthContext.Provider
      value={{
        ...authState,
        login,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

/**
 * authApi.ts - Dedicated API client for authentication endpoints.
 * Handles HTTP requests only with no React state or UI logic.
 */

import type { LoginCredentials, LoginResponse, User } from '../types/auth.types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * Universal JSON HTTP request helper adhering to DRY principles.
 */
async function sendAuthRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });
  } catch {
    throw new Error("Can't reach the server, please try again.");
  }

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorMessage = errorJson.detail;
      }
    } catch {
      // Fallback to status text
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }

  return (await response.json()) as T;
}

export const authApi = {
  /**
   * Submit credentials for verification and receive JWT token + user profile.
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    return sendAuthRequest<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email: credentials.email.trim(),
        password: credentials.password,
      }),
    });
  },

  /**
   * Fetch currently authenticated user using JWT bearer token.
   */
  async getCurrentUser(token: string): Promise<User> {
    return sendAuthRequest<User>('/auth/me', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  /**
   * Terminate active session.
   */
  async logout(token?: string): Promise<{ success: boolean; message: string }> {
    return sendAuthRequest<{ success: boolean; message: string }>('/auth/logout', {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
  },
};

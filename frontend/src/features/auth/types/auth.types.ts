/**
 * auth.types.ts - Strict TypeScript interfaces and domain types for authentication.
 */

export type UserRole = 'customer' | 'merchant' | 'admin';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  primaryUpiId?: string;
  createdAt?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  tokenType: string;
  user: User;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthContextValue extends AuthState {
  login: (credentials: LoginCredentials) => Promise<boolean>;
  logout: () => void;
  clearError: () => void;
}

export interface PasswordValidationCriteria {
  hasMinLength: boolean;
  hasUppercase: boolean;
  hasNumber: boolean;
  hasSpecialCharacter: boolean;
}

export interface PasswordValidationResult extends PasswordValidationCriteria {
  isValid: boolean;
  errors: string[];
}

export interface DemoUserAccount {
  name: string;
  email: string;
  password: string;
  role: UserRole;
  description: string;
}

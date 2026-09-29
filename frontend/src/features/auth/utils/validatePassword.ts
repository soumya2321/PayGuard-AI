/**
 * validatePassword.ts - Single source of truth for password validation and error formatting.
 * Enforces 8+ characters, at least 1 uppercase letter, 1 number, and 1 special symbol.
 */

import type { PasswordValidationResult } from '../types/auth.types';

export const MIN_PASSWORD_LENGTH = 8;
const UPPERCASE_REGEX = /[A-Z]/;
const NUMBER_REGEX = /[0-9]/;
const SPECIAL_CHAR_REGEX = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/;

/**
 * Validates password strength according to PayGuard AI security baseline.
 */
export function validatePasswordStrength(password: string): PasswordValidationResult {
  const hasMinLength = password.length >= MIN_PASSWORD_LENGTH;
  const hasUppercase = UPPERCASE_REGEX.test(password);
  const hasNumber = NUMBER_REGEX.test(password);
  const hasSpecialCharacter = SPECIAL_CHAR_REGEX.test(password);

  const errors: string[] = [];

  if (!hasMinLength) {
    errors.push(`Must be at least ${MIN_PASSWORD_LENGTH} characters long`);
  }
  if (!hasUppercase) {
    errors.push('Must contain at least one uppercase letter (A-Z)');
  }
  if (!hasNumber) {
    errors.push('Must contain at least one number (0-9)');
  }
  if (!hasSpecialCharacter) {
    errors.push('Must contain at least one special character (!@#$%^&*...)');
  }

  const isValid = hasMinLength && hasUppercase && hasNumber && hasSpecialCharacter;

  return {
    isValid,
    hasMinLength,
    hasUppercase,
    hasNumber,
    hasSpecialCharacter,
    errors,
  };
}

/**
 * Validates email format with basic RFC 5322 compliance.
 */
export function validateEmailAddress(email: string): boolean {
  if (!email || !email.trim()) return false;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  // Also support internal UPI handles used as identifiers (e.g. user@oksbi)
  const upiIdentifierRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+$/;
  return emailRegex.test(email.trim()) || upiIdentifierRegex.test(email.trim());
}

/**
 * Centralized error-message formatter ensuring security (no email leaking) and consistency.
 */
export function formatAuthErrorMessage(error: unknown): string {
  if (typeof error === 'string') {
    return error;
  }

  if (error instanceof Error) {
    const message = error.message.toLowerCase();

    if (
      message.includes('invalid credentials') ||
      message.includes('incorrect') ||
      message.includes('not found') ||
      message.includes('unauthorized') ||
      message.includes('401')
    ) {
      return 'Incorrect email or password.';
    }

    if (
      message.includes('rate limit') ||
      message.includes('too many') ||
      message.includes('429') ||
      message.includes('locked')
    ) {
      return 'Too many failed login attempts. Account locked for 60 seconds.';
    }

    if (
      message.includes('failed to fetch') ||
      message.includes('network') ||
      message.includes('refused') ||
      message.includes('cant reach') ||
      message.includes("can't reach")
    ) {
      return "Can't reach the server, please try again.";
    }

    return error.message;
  }

  return 'An unexpected error occurred during authentication.';
}

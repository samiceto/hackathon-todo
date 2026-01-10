/**
 * Form validation utilities
 * Provides email and password validation with helpful error messages
 */

export interface ValidationResult {
  isValid: boolean
  error?: string
}

/**
 * Validate email address (RFC 5322 compliant)
 */
export function validateEmail(email: string): ValidationResult {
  if (!email || email.trim() === '') {
    return {
      isValid: false,
      error: 'Email is required',
    }
  }

  // RFC 5322 compliant email regex
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/

  if (!emailRegex.test(email)) {
    return {
      isValid: false,
      error: 'Please enter a valid email address',
    }
  }

  return { isValid: true }
}

/**
 * Validate password with helpful error messages
 */
export function validatePassword(password: string): ValidationResult {
  if (!password || password.trim() === '') {
    return {
      isValid: false,
      error: 'Password is required',
    }
  }

  if (password.length < 8) {
    return {
      isValid: false,
      error: 'Password must be at least 8 characters',
    }
  }

  return { isValid: true }
}

/**
 * Validate password confirmation
 */
export function validatePasswordConfirmation(
  password: string,
  confirmPassword: string
): ValidationResult {
  if (!confirmPassword || confirmPassword.trim() === '') {
    return {
      isValid: false,
      error: 'Please confirm your password',
    }
  }

  if (password !== confirmPassword) {
    return {
      isValid: false,
      error: 'Passwords do not match',
    }
  }

  return { isValid: true }
}

/**
 * Validate entire signup form
 */
export function validateSignupForm(
  email: string,
  password: string,
  confirmPassword: string
): Record<string, string> {
  const errors: Record<string, string> = {}

  const emailResult = validateEmail(email)
  if (!emailResult.isValid) {
    errors.email = emailResult.error!
  }

  const passwordResult = validatePassword(password)
  if (!passwordResult.isValid) {
    errors.password = passwordResult.error!
  }

  const confirmResult = validatePasswordConfirmation(password, confirmPassword)
  if (!confirmResult.isValid) {
    errors.confirmPassword = confirmResult.error!
  }

  return errors
}

/**
 * Validate signin form
 */
export function validateSigninForm(
  email: string,
  password: string
): Record<string, string> {
  const errors: Record<string, string> = {}

  const emailResult = validateEmail(email)
  if (!emailResult.isValid) {
    errors.email = emailResult.error!
  }

  const passwordResult = validatePassword(password)
  if (!passwordResult.isValid) {
    errors.password = passwordResult.error!
  }

  return errors
}

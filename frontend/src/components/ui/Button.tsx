/**
 * Button Component - Refined Productivity Aesthetic
 *
 * Premium button with multiple variants and satisfying interactions.
 * Every click should feel intentional and rewarding.
 */

import React from 'react'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button visual variant */
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  /** Button size */
  size?: 'small' | 'medium' | 'large'
  /** Full width button */
  fullWidth?: boolean
  /** Loading state */
  isLoading?: boolean
  /** Icon to display before text */
  leftIcon?: React.ReactNode
  /** Icon to display after text */
  rightIcon?: React.ReactNode
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  isLoading = false,
  leftIcon,
  rightIcon,
  disabled,
  className = '',
  ...props
}) => {
  // Size configurations
  const sizeClasses = {
    small: 'px-4 py-2 text-sm font-semibold',
    medium: 'px-6 py-3 text-base font-bold',
    large: 'px-8 py-4 text-lg font-bold',
  }

  // Variant configurations with bold, confident styling
  const variantClasses = {
    primary: `
      bg-gradient-to-br from-primary-500 to-primary-600
      text-white
      shadow-lg shadow-primary-500/30
      hover:shadow-xl hover:shadow-primary-500/40
      hover:scale-[1.02]
      active:scale-[0.98]
      border-2 border-primary-600
    `,
    secondary: `
      bg-white
      text-gray-900
      border-2 border-gray-300
      hover:border-gray-400
      hover:bg-gray-50
      active:bg-gray-100
      shadow-md
      hover:shadow-lg
    `,
    ghost: `
      bg-transparent
      text-gray-700
      border-2 border-transparent
      hover:bg-gray-100
      hover:border-gray-200
      active:bg-gray-200
    `,
    danger: `
      bg-gradient-to-br from-red-500 to-red-600
      text-white
      shadow-lg shadow-red-500/30
      hover:shadow-xl hover:shadow-red-500/40
      hover:scale-[1.02]
      active:scale-[0.98]
      border-2 border-red-600
    `,
  }

  const baseClasses = `
    ${fullWidth ? 'w-full' : ''}
    ${sizeClasses[size]}
    ${variantClasses[variant]}
    inline-flex
    items-center
    justify-center
    gap-2.5
    rounded-2xl
    font-bold
    tracking-wide
    uppercase
    text-xs
    transition-all
    duration-200
    ease-out
    focus:outline-none
    focus:ring-4
    ${variant === 'primary' ? 'focus:ring-primary-500/30' : 'focus:ring-gray-300'}
    disabled:opacity-50
    disabled:cursor-not-allowed
    disabled:transform-none
    disabled:shadow-none
    relative
    overflow-hidden
    ${className}
  `

  return (
    <button
      className={baseClasses}
      disabled={disabled || isLoading}
      {...props}
    >
      {/* Shimmer effect on hover */}
      <div
        className={`
          absolute inset-0 opacity-0 hover:opacity-100
          bg-gradient-to-r from-transparent via-white/20 to-transparent
          -skew-x-12
          transition-all duration-700
          pointer-events-none
        `}
      />

      {/* Loading spinner */}
      {isLoading && (
        <svg
          className="animate-spin h-5 w-5"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}

      {/* Left icon */}
      {!isLoading && leftIcon && (
        <span className="inline-flex items-center justify-center">
          {leftIcon}
        </span>
      )}

      {/* Button text */}
      <span className="relative z-10">{children}</span>

      {/* Right icon */}
      {!isLoading && rightIcon && (
        <span className="inline-flex items-center justify-center">
          {rightIcon}
        </span>
      )}
    </button>
  )
}

export default Button

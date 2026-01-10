/**
 * Input Component - Refined Productivity Aesthetic
 *
 * A premium input field that feels inviting and responsive.
 * Designed to make data entry feel effortless and rewarding.
 */

import React, { forwardRef, useState } from 'react'

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement | HTMLTextAreaElement>, 'size'> {
  /** Input label */
  label?: string
  /** Error message to display */
  error?: string
  /** Helper text below input */
  helperText?: string
  /** Character count display (for title fields) */
  showCharCount?: boolean
  /** Maximum character count */
  maxCharCount?: number
  /** Full width (default: true) */
  fullWidth?: boolean
  /** Use textarea instead of input */
  multiline?: boolean
  /** Number of rows for textarea */
  rows?: number
  /** Icon to display (optional) */
  icon?: React.ReactNode
}

export const Input = forwardRef<HTMLInputElement | HTMLTextAreaElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      showCharCount = false,
      maxCharCount,
      fullWidth = true,
      multiline = false,
      rows = 4,
      icon,
      className = '',
      value,
      onChange,
      ...props
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = useState(false)
    const [currentValue, setCurrentValue] = useState(value || '')

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setCurrentValue(e.target.value)
      onChange?.(e as any)
    }

    const charCount = String(currentValue).length
    const isNearLimit = maxCharCount && charCount > maxCharCount * 0.8

    // Base input styling with editorial refinement
    const baseClasses = `
      ${fullWidth ? 'w-full' : ''}
      px-5 py-3.5
      ${icon ? 'pl-12' : ''}
      text-base
      font-normal
      bg-white
      border-2
      ${error
        ? 'border-red-400 focus:border-red-500 focus:ring-red-500/20'
        : isFocused
          ? 'border-primary-500 focus:border-primary-600 focus:ring-primary-500/20'
          : 'border-gray-200 hover:border-gray-300'
      }
      rounded-2xl
      transition-all duration-200 ease-out
      focus:outline-none
      focus:ring-4
      disabled:opacity-50
      disabled:cursor-not-allowed
      placeholder:text-gray-400
      placeholder:font-light
      ${multiline ? 'resize-none' : ''}
      ${className}
    `

    const inputElement = multiline ? (
      <textarea
        ref={ref as React.Ref<HTMLTextAreaElement>}
        rows={rows}
        className={baseClasses}
        value={value}
        onChange={handleChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? 'input-error' : helperText ? 'input-helper' : undefined}
        {...(props as React.TextareaHTMLAttributes<HTMLTextAreaElement>)}
      />
    ) : (
      <input
        ref={ref as React.Ref<HTMLInputElement>}
        className={baseClasses}
        value={value}
        onChange={handleChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? 'input-error' : helperText ? 'input-helper' : undefined}
        {...(props as React.InputHTMLAttributes<HTMLInputElement>)}
      />
    )

    return (
      <div className={`${fullWidth ? 'w-full' : ''} group`}>
        {/* Label with refined typography */}
        {label && (
          <div className="flex items-center justify-between mb-2.5">
            <label className="block text-sm font-bold tracking-wide text-gray-800 uppercase">
              {label}
              {props.required && (
                <span className="text-red-500 ml-1.5 font-normal text-base lowercase">*required</span>
              )}
            </label>

            {/* Character count indicator */}
            {showCharCount && maxCharCount && (
              <span
                className={`text-xs font-mono transition-colors ${
                  isNearLimit
                    ? 'text-amber-600 font-semibold'
                    : 'text-gray-400'
                }`}
              >
                {charCount}/{maxCharCount}
              </span>
            )}
          </div>
        )}

        {/* Input container with optional icon */}
        <div className="relative">
          {icon && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 transition-colors group-focus-within:text-primary-500">
              {icon}
            </div>
          )}

          {inputElement}

          {/* Animated focus indicator */}
          <div
            className={`
              absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-primary-500 to-primary-600
              transition-all duration-300 ease-out rounded-full
              ${isFocused ? 'opacity-100 scale-x-100' : 'opacity-0 scale-x-50'}
            `}
          />
        </div>

        {/* Error message with icon */}
        {error && (
          <div
            id="input-error"
            className="mt-3 flex items-start gap-2 text-sm text-red-600 animate-slide-up"
          >
            <svg
              className="w-4 h-4 flex-shrink-0 mt-0.5"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <span className="font-medium">{error}</span>
          </div>
        )}

        {/* Helper text with subtle styling */}
        {!error && helperText && (
          <div id="input-helper" className="mt-2.5 text-sm text-gray-500 font-light">
            {helperText}
          </div>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input

/**
 * Input Component - Dark POS Theme
 *
 * A fully accessible input component with multiple variants and states
 * designed for POS systems with a dark theme.
 *
 * Features:
 * - Variants: primary, secondary, outline
 * - Sizes: md, lg
 * - States: disabled, error, success
 * - Full keyboard accessibility (ARIA attributes)
 * - Label and helper text support
 * - Dark POS theme optimized
 */

import { InputHTMLAttributes, ReactNode, forwardRef } from 'react';
import './Input.css';

export type InputVariant = 'primary' | 'secondary' | 'outline';
export type InputSize = 'md' | 'lg';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  /** The visual style variant of the input */
  variant?: InputVariant;

  /** The size of the input */
  size?: InputSize;

  /** Label text for the input */
  label?: string;

  /** Helper text displayed below the input */
  helperText?: string;

  /** Error message (when provided, shows error state) */
  error?: string;

  /** Success message (when provided, shows success state) */
  success?: string;

  /** Icon to display on the left side of the input */
  leftIcon?: ReactNode;

  /** Icon to display on the right side of the input */
  rightIcon?: ReactNode;

  /** Whether the input is required */
  required?: boolean;

  /** Optional custom className for additional styling */
  className?: string;
}

/**
 * Input Component
 *
 * @example
 * ```tsx
 * // Basic input with label
 * <Input label="Customer Name" placeholder="Enter name..." />
 *
 * // Input with error state
 * <Input label="Email" error="Invalid email format" />
 *
 * // Input with success state
 * <Input label="Phone" success="Verified" />
 *
 * // Large input with icon
 * <Input
 *   size="lg"
 *   label="Search"
 *   leftIcon={<SearchIcon />}
 *   placeholder="Search products..."
 * />
 * ```
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      label,
      helperText,
      error,
      success,
      leftIcon,
      rightIcon,
      required = false,
      className = '',
      id,
      disabled = false,
      ...props
    },
    ref
  ) => {
    // Generate unique ID if not provided
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

    const hasError = Boolean(error);
    const hasSuccess = Boolean(success) && !hasError;

    const wrapperClassName = [
      'ui-input-wrapper',
      `ui-input-wrapper--${size}`,
      disabled && 'ui-input-wrapper--disabled',
      className,
    ]
      .filter(Boolean)
      .join(' ');

    const inputClassName = [
      'ui-input',
      `ui-input--${variant}`,
      `ui-input--${size}`,
      hasError && 'ui-input--error',
      hasSuccess && 'ui-input--success',
      leftIcon && 'ui-input--has-left-icon',
      rightIcon && 'ui-input--has-right-icon',
    ]
      .filter(Boolean)
      .join(' ');

    const messageId = hasError
      ? `${inputId}-error`
      : hasSuccess
        ? `${inputId}-success`
        : helperText
          ? `${inputId}-helper`
          : undefined;

    return (
      <div className={wrapperClassName}>
        {/* Label */}
        {label && (
          <label htmlFor={inputId} className="ui-input-label">
            {label}
            {required && <span className="ui-input-label__required" aria-label="required">*</span>}
          </label>
        )}

        {/* Input Container */}
        <div className="ui-input-container">
          {/* Left Icon */}
          {leftIcon && (
            <span className="ui-input-icon ui-input-icon--left" aria-hidden="true">
              {leftIcon}
            </span>
          )}

          {/* Input Field */}
          <input
            ref={ref}
            id={inputId}
            className={inputClassName}
            disabled={disabled}
            aria-disabled={disabled}
            aria-invalid={hasError}
            aria-describedby={messageId}
            aria-required={required}
            required={required}
            {...props}
          />

          {/* Right Icon */}
          {rightIcon && (
            <span className="ui-input-icon ui-input-icon--right" aria-hidden="true">
              {rightIcon}
            </span>
          )}
        </div>

        {/* Helper Text / Error / Success */}
        {(helperText || error || success) && (
          <div className="ui-input-message">
            {error && (
              <span id={messageId} className="ui-input-message--error" role="alert">
                {error}
              </span>
            )}
            {!error && success && (
              <span id={messageId} className="ui-input-message--success" role="status">
                {success}
              </span>
            )}
            {!error && !success && helperText && (
              <span id={messageId} className="ui-input-message--helper">
                {helperText}
              </span>
            )}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

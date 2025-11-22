/**
 * Button Component - Dark POS Theme
 *
 * A fully accessible button component with multiple variants and states
 * designed for POS systems with a dark theme.
 *
 * Features:
 * - Variants: primary, secondary, outline
 * - Sizes: md, lg
 * - States: disabled, loading
 * - Full keyboard accessibility (ARIA attributes)
 * - Dark POS theme optimized
 */

import { ButtonHTMLAttributes, ReactNode } from 'react';
import './Button.css';

export type ButtonVariant = 'primary' | 'secondary' | 'outline';
export type ButtonSize = 'md' | 'lg';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** The visual style variant of the button */
  variant?: ButtonVariant;

  /** The size of the button */
  size?: ButtonSize;

  /** Whether the button is in a loading state */
  loading?: boolean;

  /** Button content */
  children: ReactNode;

  /** Optional custom className for additional styling */
  className?: string;

  /** Whether the button is disabled */
  disabled?: boolean;
}

/**
 * Button Component
 *
 * @example
 * ```tsx
 * // Primary button
 * <Button variant="primary" size="lg">Submit Order</Button>
 *
 * // Loading state
 * <Button variant="secondary" loading>Processing...</Button>
 *
 * // Disabled state
 * <Button variant="outline" disabled>Unavailable</Button>
 * ```
 */
export const Button = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  children,
  className = '',
  disabled = false,
  type = 'button',
  ...props
}: ButtonProps) => {
  const isDisabled = disabled || loading;

  const buttonClassName = [
    'ui-button',
    `ui-button--${variant}`,
    `ui-button--${size}`,
    loading && 'ui-button--loading',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      type={type}
      className={buttonClassName}
      disabled={isDisabled}
      aria-disabled={isDisabled}
      aria-busy={loading}
      {...props}
    >
      {loading && (
        <span className="ui-button__spinner" aria-hidden="true">
          <span className="ui-button__spinner-dot"></span>
          <span className="ui-button__spinner-dot"></span>
          <span className="ui-button__spinner-dot"></span>
        </span>
      )}
      <span className={loading ? 'ui-button__content--loading' : ''}>
        {children}
      </span>
    </button>
  );
};

/**
 * Badge - Dark themed badge component
 *
 * Small status indicator with multiple color variants.
 * Perfect for tags, statuses, and notifications.
 *
 * Usage:
 *   <Badge variant="primary">New</Badge>
 *   <Badge variant="warning">Pending</Badge>
 *   <Badge variant="danger">Error</Badge>
 *   <Badge variant="neutral">Inactive</Badge>
 */

import { ReactNode, CSSProperties } from 'react';
import './Badge.css';

export type BadgeVariant = 'primary' | 'warning' | 'danger' | 'neutral';

export interface BadgeProps {
  /** Badge content */
  children: ReactNode;
  /** Color variant */
  variant?: BadgeVariant;
  /** Additional CSS classes */
  className?: string;
  /** Custom styles */
  style?: CSSProperties;
}

export const Badge = ({
  children,
  variant = 'neutral',
  className = '',
  style,
}: BadgeProps) => {
  const classes = [
    'badge-ui',
    `badge-${variant}`,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <span className={classes} style={style}>
      {children}
    </span>
  );
};

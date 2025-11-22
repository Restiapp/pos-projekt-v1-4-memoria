/**
 * Card - Dark themed card component
 *
 * A flexible container component with dark theme styling,
 * rounded corners, and shadow.
 *
 * Usage:
 *   <Card>Content here</Card>
 *   <Card padding="lg" hover>Content with custom padding and hover effect</Card>
 */

import { ReactNode, CSSProperties } from 'react';
import './Card.css';

export interface CardProps {
  /** Card content */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Padding size */
  padding?: 'sm' | 'md' | 'lg';
  /** Enable hover effect */
  hover?: boolean;
  /** Custom styles */
  style?: CSSProperties;
  /** Click handler */
  onClick?: () => void;
}

export const Card = ({
  children,
  className = '',
  padding = 'md',
  hover = false,
  style,
  onClick,
}: CardProps) => {
  const classes = [
    'card-ui',
    `card-padding-${padding}`,
    hover && 'card-hover',
    onClick && 'card-clickable',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={classes} style={style} onClick={onClick}>
      {children}
    </div>
  );
};

/**
 * Card - Generic card container component
 * Used for displaying content in a bordered, elevated container
 */

import { ReactNode } from 'react';
import './Card.css';

interface CardProps {
  children: ReactNode;
  className?: string;
  title?: string;
}

export const Card = ({ children, className = '', title }: CardProps) => {
  return (
    <div className={`card ${className}`}>
      {title && <div className="card-title">{title}</div>}
      <div className="card-content">{children}</div>
    </div>
  );
};

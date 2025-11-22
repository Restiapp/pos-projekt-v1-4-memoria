/**
 * Chip - Dark themed chip component
 *
 * Interactive tag component with selectable and removable options.
 * Perfect for filters, tags, and multi-select interfaces.
 *
 * Usage:
 *   <Chip>Basic Chip</Chip>
 *   <Chip selected>Selected Chip</Chip>
 *   <Chip onRemove={() => console.log('removed')}>Removable</Chip>
 *   <Chip onClick={() => console.log('clicked')} selected>Selectable</Chip>
 */

import { ReactNode, CSSProperties, MouseEvent } from 'react';
import './Chip.css';

export interface ChipProps {
  /** Chip content/label */
  children: ReactNode;
  /** Selected state */
  selected?: boolean;
  /** Remove handler - shows remove icon when provided */
  onRemove?: () => void;
  /** Click handler - makes chip clickable/selectable */
  onClick?: () => void;
  /** Additional CSS classes */
  className?: string;
  /** Custom styles */
  style?: CSSProperties;
  /** Disabled state */
  disabled?: boolean;
}

export const Chip = ({
  children,
  selected = false,
  onRemove,
  onClick,
  className = '',
  style,
  disabled = false,
}: ChipProps) => {
  const classes = [
    'chip-ui',
    selected && 'chip-selected',
    onClick && 'chip-clickable',
    disabled && 'chip-disabled',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  const handleRemoveClick = (e: MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    if (onRemove && !disabled) {
      onRemove();
    }
  };

  const handleChipClick = () => {
    if (onClick && !disabled) {
      onClick();
    }
  };

  return (
    <div
      className={classes}
      style={style}
      onClick={handleChipClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick && !disabled ? 0 : undefined}
    >
      <span className="chip-label">{children}</span>
      {onRemove && (
        <button
          className="chip-remove"
          onClick={handleRemoveClick}
          disabled={disabled}
          aria-label="Remove"
          type="button"
        >
          ×
        </button>
      )}
    </div>
  );
};

/**
 * Skeleton - Shimmer effect for loading states
 * Used for table rows, cards, and other content placeholders
 */

import './Skeleton.css';

interface SkeletonProps {
  variant?: 'text' | 'rectangular' | 'circular' | 'table-row' | 'card';
  width?: string | number;
  height?: string | number;
  count?: number;
  className?: string;
}

export const Skeleton = ({
  variant = 'text',
  width,
  height,
  count = 1,
  className = '',
}: SkeletonProps) => {
  const getStyle = () => {
    const style: React.CSSProperties = {};
    if (width) style.width = typeof width === 'number' ? `${width}px` : width;
    if (height) style.height = typeof height === 'number' ? `${height}px` : height;
    return style;
  };

  const renderSkeleton = () => {
    if (variant === 'table-row') {
      return (
        <tr className={`skeleton-table-row ${className}`}>
          <td colSpan={100}>
            <div className="skeleton-shimmer" style={getStyle()}></div>
          </td>
        </tr>
      );
    }

    if (variant === 'card') {
      return (
        <div className={`skeleton-card ${className}`} style={getStyle()}>
          <div className="skeleton-shimmer skeleton-card-header"></div>
          <div className="skeleton-shimmer skeleton-card-body"></div>
          <div className="skeleton-shimmer skeleton-card-footer"></div>
        </div>
      );
    }

    return (
      <div
        className={`skeleton skeleton-${variant} ${className}`}
        style={getStyle()}
      >
        <div className="skeleton-shimmer"></div>
      </div>
    );
  };

  if (count === 1) {
    return renderSkeleton();
  }

  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index}>{renderSkeleton()}</div>
      ))}
    </>
  );
};

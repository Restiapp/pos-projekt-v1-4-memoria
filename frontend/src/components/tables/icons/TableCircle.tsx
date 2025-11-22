/**
 * TableCircle - Round table icon component
 * Displays a circular table with customizable size, rotation, and status color
 */

import { Box } from '@mantine/core';

export interface TableIconProps {
  selected?: boolean;
  size?: number;
  rotation?: number;
  statusColor?: string;
  onClick?: () => void;
}

export const TableCircle = ({
  selected = false,
  size = 60,
  rotation = 0,
  statusColor = '#228be6',
  onClick,
}: TableIconProps) => {
  const strokeWidth = selected ? 3 : 2;
  const stroke = selected ? '#fd7e14' : '#495057';

  return (
    <Box
      onClick={onClick}
      style={{
        cursor: onClick ? 'pointer' : 'default',
        display: 'inline-block',
        userSelect: 'none',
      }}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        style={{
          transform: `rotate(${rotation}deg)`,
          transition: 'transform 0.2s ease',
        }}
      >
        {/* Main table circle */}
        <circle
          cx="50"
          cy="50"
          r="45"
          fill={statusColor}
          stroke={stroke}
          strokeWidth={strokeWidth}
          opacity={0.9}
        />

        {/* Inner circle detail */}
        <circle
          cx="50"
          cy="50"
          r="35"
          fill="none"
          stroke={stroke}
          strokeWidth={1}
          opacity={0.3}
        />

        {/* Center dot */}
        <circle
          cx="50"
          cy="50"
          r="3"
          fill={stroke}
          opacity={0.5}
        />
      </svg>
    </Box>
  );
};

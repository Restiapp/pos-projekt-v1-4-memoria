/**
 * TableSquare - Square table icon component
 * Displays a square/rectangular table with customizable size, rotation, and status color
 */

import { Box } from '@mantine/core';
import type { TableIconProps } from './TableCircle';

export const TableSquare = ({
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
        {/* Main table rectangle */}
        <rect
          x="10"
          y="10"
          width="80"
          height="80"
          rx="4"
          fill={statusColor}
          stroke={stroke}
          strokeWidth={strokeWidth}
          opacity={0.9}
        />

        {/* Inner rectangle detail */}
        <rect
          x="20"
          y="20"
          width="60"
          height="60"
          rx="2"
          fill="none"
          stroke={stroke}
          strokeWidth={1}
          opacity={0.3}
        />

        {/* Center cross pattern */}
        <line
          x1="50"
          y1="30"
          x2="50"
          y2="70"
          stroke={stroke}
          strokeWidth={1}
          opacity={0.2}
        />
        <line
          x1="30"
          y1="50"
          x2="70"
          y2="50"
          stroke={stroke}
          strokeWidth={1}
          opacity={0.2}
        />
      </svg>
    </Box>
  );
};

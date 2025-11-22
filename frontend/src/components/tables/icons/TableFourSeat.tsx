/**
 * TableFourSeat - Four-seat table icon component
 * Displays a square table with 4 chair indicators (one on each side)
 */

import { Box } from '@mantine/core';
import type { TableIconProps } from './TableCircle';

export const TableFourSeat = ({
  selected = false,
  size = 80,
  rotation = 0,
  statusColor = '#228be6',
  onClick,
}: TableIconProps) => {
  const strokeWidth = selected ? 3 : 2;
  const stroke = selected ? '#fd7e14' : '#495057';
  const chairColor = '#868e96';

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
        viewBox="0 0 120 120"
        style={{
          transform: `rotate(${rotation}deg)`,
          transition: 'transform 0.2s ease',
        }}
      >
        {/* Chair - Top */}
        <rect
          x="52"
          y="10"
          width="16"
          height="12"
          rx="2"
          fill={chairColor}
          stroke={stroke}
          strokeWidth={1}
          opacity={0.8}
        />

        {/* Chair - Right */}
        <rect
          x="98"
          y="52"
          width="12"
          height="16"
          rx="2"
          fill={chairColor}
          stroke={stroke}
          strokeWidth={1}
          opacity={0.8}
        />

        {/* Chair - Bottom */}
        <rect
          x="52"
          y="98"
          width="16"
          height="12"
          rx="2"
          fill={chairColor}
          stroke={stroke}
          strokeWidth={1}
          opacity={0.8}
        />

        {/* Chair - Left */}
        <rect
          x="10"
          y="52"
          width="12"
          height="16"
          rx="2"
          fill={chairColor}
          stroke={stroke}
          strokeWidth={1}
          opacity={0.8}
        />

        {/* Main table */}
        <rect
          x="35"
          y="35"
          width="50"
          height="50"
          rx="4"
          fill={statusColor}
          stroke={stroke}
          strokeWidth={strokeWidth}
          opacity={0.9}
        />

        {/* Inner detail */}
        <rect
          x="42"
          y="42"
          width="36"
          height="36"
          rx="2"
          fill="none"
          stroke={stroke}
          strokeWidth={1}
          opacity={0.3}
        />
      </svg>
    </Box>
  );
};

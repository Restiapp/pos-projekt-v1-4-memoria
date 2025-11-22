/**
 * TableSixSeat - Six-seat table icon component
 * Displays a rectangular table with 6 chair indicators (2 on long sides, 1 on each short side)
 */

import { Box } from '@mantine/core';
import type { TableIconProps } from './TableCircle';

export const TableSixSeat = ({
  selected = false,
  size = 90,
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
        height={size * 0.75}
        viewBox="0 0 140 105"
        style={{
          transform: `rotate(${rotation}deg)`,
          transition: 'transform 0.2s ease',
        }}
      >
        {/* Chair - Top Left */}
        <rect
          x="35"
          y="8"
          width="16"
          height="10"
          rx="2"
          fill={chairColor}
          stroke={stroke}
          strokeWidth={1}
          opacity={0.8}
        />

        {/* Chair - Top Right */}
        <rect
          x="89"
          y="8"
          width="16"
          height="10"
          rx="2"
          fill={chairColor}
          stroke={stroke}
          strokeWidth={1}
          opacity={0.8}
        />

        {/* Chair - Right Top */}
        <rect
          x="122"
          y="32"
          width="10"
          height="16"
          rx="2"
          fill={chairColor}
          stroke={stroke}
          strokeWidth={1}
          opacity={0.8}
        />

        {/* Chair - Right Bottom */}
        <rect
          x="122"
          y="57"
          width="10"
          height="16"
          rx="2"
          fill={chairColor}
          stroke={stroke}
          strokeWidth={1}
          opacity={0.8}
        />

        {/* Chair - Bottom Left */}
        <rect
          x="35"
          y="87"
          width="16"
          height="10"
          rx="2"
          fill={chairColor}
          stroke={stroke}
          strokeWidth={1}
          opacity={0.8}
        />

        {/* Chair - Bottom Right */}
        <rect
          x="89"
          y="87"
          width="16"
          height="10"
          rx="2"
          fill={chairColor}
          stroke={stroke}
          strokeWidth={1}
          opacity={0.8}
        />

        {/* Chair - Left Top */}
        <rect
          x="8"
          y="32"
          width="10"
          height="16"
          rx="2"
          fill={chairColor}
          stroke={stroke}
          strokeWidth={1}
          opacity={0.8}
        />

        {/* Chair - Left Bottom */}
        <rect
          x="8"
          y="57"
          width="10"
          height="16"
          rx="2"
          fill={chairColor}
          stroke={stroke}
          strokeWidth={1}
          opacity={0.8}
        />

        {/* Main table - rectangular */}
        <rect
          x="28"
          y="28"
          width="84"
          height="49"
          rx="4"
          fill={statusColor}
          stroke={stroke}
          strokeWidth={strokeWidth}
          opacity={0.9}
        />

        {/* Inner detail */}
        <rect
          x="35"
          y="35"
          width="70"
          height="35"
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

import React from 'react';
import { Badge, Group, Tooltip } from '@mantine/core';
import { TableMetrics } from '@/api/guestOrderApi';

interface MetricsDisplayProps {
  metrics?: TableMetrics;
}

export const MetricsDisplay: React.FC<MetricsDisplayProps> = ({ metrics }) => {
  if (!metrics || !metrics.active) return null;

  const colorMap = {
    green: 'green',
    yellow: 'yellow',
    red: 'red'
  };

  return (
    <Group>
      <Tooltip label="Eltelt idő a rendelés nyitása óta">
        <Badge
          size="lg"
          variant="filled"
          color={colorMap[metrics.color]}
        >
          {metrics.minutes_since_start} perc
        </Badge>
      </Tooltip>
      {/* Could add Last Round time here if provided by API */}
    </Group>
  );
};

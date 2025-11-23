import React from 'react';
import { Paper, Text, Badge, Group, ActionIcon, Stack, ThemeIcon } from '@mantine/core';
import { IconFlame, IconChefHat } from '@tabler/icons-react'; // Assuming tabler icons are available or need verify
import { OrderItem } from '@/api/guestOrderApi';

interface OrderItemRowProps {
  item: OrderItem;
  onToggleUrgent: (itemId: number, currentStatus: boolean) => void;
}

export const OrderItemRow: React.FC<OrderItemRowProps> = ({ item, onToggleUrgent }) => {
  const isUrgent = item.metadata_json?.is_urgent;
  const courseTag = item.metadata_json?.course_tag;
  const notes = item.metadata_json?.notes;

  return (
    <Paper withBorder p="sm" mb="xs" style={{
      borderColor: isUrgent ? 'var(--mantine-color-red-5)' : undefined,
      backgroundColor: isUrgent ? 'var(--mantine-color-red-0)' : undefined
    }}>
      <Group justify="space-between">
        <Group gap="sm">
          <Badge circle size="lg" variant="filled" color="blue">{item.quantity}</Badge>
          <Stack gap={0}>
            <Text fw={500}>{item.name || `Product #${item.product_id}`}</Text>
            {notes && <Text size="xs" c="dimmed" fs="italic">{notes}</Text>}
          </Stack>
        </Group>

        <Group>
          {courseTag && (
            <Badge variant="dot" color="gray" size="sm">{courseTag}</Badge>
          )}

          <ActionIcon
            variant={isUrgent ? "filled" : "light"}
            color="red"
            onClick={() => onToggleUrgent(item.id, !!isUrgent)}
            title="Toggle Urgent"
          >
             U
          </ActionIcon>

          <Badge variant="outline" color={getKdsStatusColor(item.kds_status)}>
            {item.kds_status || 'NEW'}
          </Badge>
        </Group>
      </Group>
    </Paper>
  );
};

function getKdsStatusColor(status?: string) {
  switch (status) {
    case 'KÉSZ': return 'green';
    case 'KÉSZÜL': return 'yellow';
    case 'VÁRAKOZIK': return 'orange';
    default: return 'gray';
  }
}

import { ActionIcon, Alert, Group, Skeleton, Tabs, Text, Tooltip } from '@mantine/core';
import { IconAlertTriangle, IconRefresh } from '@tabler/icons-react';
import type { Room } from '@/types/room';
import './RoomNavigation.css';

interface RoomNavigationProps {
  rooms: Room[];
  selectedRoomId: number | null;
  onRoomChange: (roomId: number | null) => void;
  loading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
}

export const RoomNavigation = ({
  rooms,
  selectedRoomId,
  onRoomChange,
  loading = false,
  error,
  onRefresh,
}: RoomNavigationProps) => {
  if (loading && rooms.length === 0) {
    return <Skeleton height={44} radius="md" />;
  }

  return (
    <div className="room-navigation">
      <Group justify="space-between" align="center" mb="xs">
        <Text fw={700}>Termek</Text>
        <Group gap={6}>
          {onRefresh && (
            <Tooltip label="Frissítés" withArrow>
              <ActionIcon
                size="md"
                variant="light"
                color="blue"
                onClick={onRefresh}
                loading={loading}
              >
                <IconRefresh size={16} />
              </ActionIcon>
            </Tooltip>
          )}
        </Group>
      </Group>

      {error && (
        <Alert
          icon={<IconAlertTriangle size={18} />}
          color="red"
          title="Nem sikerült betölteni a termeket"
          radius="md"
          mb="sm"
        >
          {error}
        </Alert>
      )}

      {rooms.length === 0 ? (
        <Alert color="gray" radius="md" title="Nincs elérhető terem">
          Adj hozzá legalább egy termet az alaprajzhoz.
        </Alert>
      ) : (
        <Tabs
          value={selectedRoomId ? String(selectedRoomId) : null}
          onChange={(value) => onRoomChange(value ? Number(value) : null)}
          variant="pills"
          radius="md"
          classNames={{ list: 'room-navigation-tabs' }}
        >
          <Tabs.List>
            {rooms.map((room) => (
              <Tabs.Tab key={room.id} value={String(room.id)}>
                <div className="room-tab-content">
                  <span className="room-name">{room.name}</span>
                  <span className="room-meta">
                    {room.type === 'outdoor' ? 'Kültér' : 'Beltér'} · {room.width}×{room.height}
                  </span>
                </div>
              </Tabs.Tab>
            ))}
          </Tabs.List>
        </Tabs>
      )}
    </div>
  );
};

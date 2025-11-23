import { useEffect, useMemo, useState } from 'react';
import {
  ActionIcon,
  Alert,
  Badge,
  Button,
  Center,
  Group,
  Loader,
  Paper,
  ScrollArea,
  Skeleton,
  Stack,
  Text,
  Tooltip,
} from '@mantine/core';
import { IconAlertTriangle, IconRefresh } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { getTables } from '@/services/tableService';
import type { Room } from '@/types/room';
import type { Table, TableShape, TableStatus } from '@/types/table';
import './TableMap.css';

interface TableMapProps {
  activeRoomId: number | null;
  rooms: Room[];
  onTableSelect?: (table: Table) => void;
}

const statusColors: Record<TableStatus, { bg: string; text: string; border: string }> = {
  FREE: { bg: '#2fb344', text: '#f4fff6', border: '#38d357' },
  ORDERING: { bg: '#228be6', text: '#eef7ff', border: '#3b9aff' },
  IN_PROGRESS: { bg: '#f08c00', text: '#fff8e1', border: '#f7a400' },
  PAYING: { bg: '#e03131', text: '#ffecec', border: '#ff4d4f' },
  RESERVED: { bg: '#adb5bd', text: '#f8f9fa', border: '#ced4da' },
  INACTIVE: { bg: '#868e96', text: '#f1f3f5', border: '#adb5bd' },
};

const statusLabels: Record<TableStatus, string> = {
  FREE: 'Szabad',
  ORDERING: 'Rendelés alatt',
  IN_PROGRESS: 'Folyamatban',
  PAYING: 'Fizetés',
  RESERVED: 'Foglalt',
  INACTIVE: 'Inaktív',
};

const shapeVariant = (shape?: TableShape): 'round' | 'square' | 'rect' => {
  if (shape === 'ROUND') return 'round';
  if (shape === 'SQUARE') return 'square';
  return 'rect'; // RECTANGLE -> rect for visual rendering
};

const deriveStatus = (table: Table): TableStatus => {
  const metaStatus = (table.metadata_json as Record<string, unknown> | null | undefined)?.status as
    | TableStatus
    | undefined;
  return table.status ?? metaStatus ?? 'FREE';
};

export const TableMap = ({ activeRoomId, rooms, onTableSelect }: TableMapProps) => {
  const navigate = useNavigate();
  const [tables, setTables] = useState<Table[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const activeRoom = useMemo(
    () => rooms.find((room) => room.id === activeRoomId) ?? null,
    [activeRoomId, rooms]
  );

  const fetchTables = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getTables();
      setTables(data);
    } catch (err) {
      console.error('Failed to load tables', err);
      setError('Nem sikerült betölteni az asztalokat.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTables();
  }, []);

  const filteredTables = useMemo(() => {
    if (!activeRoomId) return tables;
    return tables.filter((table) => table.room_id === activeRoomId);
  }, [tables, activeRoomId]);

  const handleTableClick = (table: Table) => {
    if (onTableSelect) {
      onTableSelect(table);
    } else {
      navigate(`/orders/new?table_id=${table.id}`);
    }
  };

  const renderContent = () => {
    if (error) {
      return (
        <Center className="table-map-empty">
          <Alert
            color="red"
            icon={<IconAlertTriangle size={18} />}
            title="Hiba történt"
            radius="md"
          >
            <Stack gap="xs">
              <Text size="sm">{error}</Text>
              <Button variant="light" color="red" onClick={fetchTables}>
                Újra
              </Button>
            </Stack>
          </Alert>
        </Center>
      );
    }

    if (isLoading && filteredTables.length === 0) {
      return (
        <div className="table-map-skeleton">
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} height={120} radius="md" />
          ))}
        </div>
      );
    }

    if (filteredTables.length === 0) {
      return (
        <Center className="table-map-empty">
          <Stack gap={4} align="center">
            <Text fw={600}>Nincs megjeleníthető asztal</Text>
            <Text size="sm" c="dimmed">
              Adj hozzá asztalokat ehhez a teremhez az admin felületen.
            </Text>
          </Stack>
        </Center>
      );
    }

    const width = activeRoom?.width ?? 1200;
    const height = activeRoom?.height ?? 720;

    return (
      <>
        <ScrollArea>
          <div
            className="table-map-canvas"
            style={{
              width,
              height,
            }}
          >
            {filteredTables.map((table) => {
              const status = deriveStatus(table);
              const palette = statusColors[status] ?? statusColors.FREE;
              const tableWidth = table.width ?? 96;
              const tableHeight = table.height ?? 96;
              const variant = shapeVariant(table.shape);
              const computedHeight = variant === 'square' ? tableWidth : tableHeight ?? 96;

              return (
                <button
                  key={table.id}
                  className={`table-map-node table-shape-${variant}`}
                  style={{
                    left: table.position_x ?? 0,
                    top: table.position_y ?? 0,
                    width: tableWidth,
                    height: variant === 'round' ? tableWidth : computedHeight,
                    backgroundColor: palette.bg,
                    color: palette.text,
                    borderColor: palette.border,
                    transform: `rotate(${table.rotation ?? 0}deg)`,
                  }}
                  onClick={() => handleTableClick(table)}
                >
                  <div className="table-node-header">
                    <Text fw={700} size="lg">
                      {table.table_number}
                    </Text>
                    <Badge
                      size="xs"
                      variant="light"
                      color="dark"
                      className="table-status-badge"
                    >
                      {statusLabels[status]}
                    </Badge>
                  </div>
                  <Text size="sm" fw={600}>
                    {table.capacity ?? '-'} fő
                  </Text>
                  <Text size="xs" className="table-meta">
                    {table.shape === 'ROUND' ? 'Kör' : table.shape === 'SQUARE' ? 'Négyzet' : 'Téglalap'}
                  </Text>
                </button>
              );
            })}
          </div>
        </ScrollArea>

        <Group gap="md" mt="md" wrap="wrap" className="table-map-legend">
          {(Object.keys(statusColors) as TableStatus[]).map((statusKey) => {
            const palette = statusColors[statusKey];
            return (
              <Group key={statusKey} gap={8}>
                <span
                  className="status-dot"
                  style={{ backgroundColor: palette.bg, borderColor: palette.border }}
                />
                <Text size="xs" c="dimmed">
                  {statusLabels[statusKey]}
                </Text>
              </Group>
            );
          })}
        </Group>
      </>
    );
  };

  return (
    <Paper withBorder radius="lg" p="md" className="table-map-card">
      <Group justify="space-between" align="center" mb="md">
        <div>
          <Text fw={700}>Alaprajz</Text>
          <Text size="sm" c="dimmed">
            {activeRoom
              ? `${activeRoom.name} · ${filteredTables.length} asztal`
              : 'Válassz termet a fenti navigációval'}
          </Text>
        </div>
        <Tooltip label="Frissítés" withArrow>
          <ActionIcon
            variant="light"
            color="blue"
            onClick={fetchTables}
            loading={isLoading}
            aria-label="Asztalok frissítése"
          >
            {isLoading ? <Loader size="sm" /> : <IconRefresh size={16} />}
          </ActionIcon>
        </Tooltip>
      </Group>
      {renderContent()}
    </Paper>
  );
};

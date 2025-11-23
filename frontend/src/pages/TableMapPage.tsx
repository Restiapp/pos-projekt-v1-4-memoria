import { useEffect, useState } from 'react';
import { Container, Stack, Text } from '@mantine/core';
import { MobileAppShell } from '@/components/layout/MobileAppShell';
import { RoomNavigation } from '@/components/rooms/RoomNavigation';
import { TableMap } from '@/components/table-map/TableMap';
import { TableOrderPanel } from '@/components/waiter/TableOrderPanel';
import { getRooms } from '@/services/roomService';
import { getTables } from '@/services/tableService';
import type { Room } from '@/types/room';
import type { Table } from '@/types/table';
import { useToast } from '@/components/common/Toast';
import './TableMapPage.css';

export const TableMapPage = () => {
  const { showToast } = useToast();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [tables, setTables] = useState<Table[]>([]);
  const [activeRoomId, setActiveRoomId] = useState<number | null>(null);
  const [selectedTable, setSelectedTable] = useState<Table | null>(null);
  const [loadingRooms, setLoadingRooms] = useState<boolean>(false);
  const [roomsError, setRoomsError] = useState<string | null>(null);

  const loadRooms = async () => {
    setLoadingRooms(true);
    setRoomsError(null);
    try {
      const data = await getRooms();
      setRooms(data);
      if (!activeRoomId && data.length > 0) {
        setActiveRoomId(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load rooms', err);
      setRoomsError('Nem sikerült betölteni a termeket.');
      showToast('Nem sikerült betölteni a termeket', 'error');
    } finally {
      setLoadingRooms(false);
    }
  };

  const loadTables = async () => {
    try {
      const data = await getTables();
      setTables(data);
    } catch (err) {
      console.error('Failed to load tables', err);
    }
  };

  const handleTableSelect = (tableId: number) => {
    const table = tables.find(t => t.id === tableId);
    if (table) {
      setSelectedTable(table);
    }
  };

  useEffect(() => {
    loadRooms();
    loadTables();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Auto-refresh when user returns to the page (e.g., from admin editor)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        console.log('🔄 Page became visible, refreshing rooms...');
        loadRooms();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <MobileAppShell>
      <div className={`table-map-page ${selectedTable ? 'with-panel' : ''}`}>
        <div className="table-map-page__main">
          <Container size="lg" className="table-map-page__container">
            <Stack gap="md">
              <div className="table-map-page__header">
                <Text fw={700} size="xl">
                  Asztaltérkép
                </Text>
                <Text size="sm" c="dimmed">
                  Válaszd ki a termet, majd koppints egy asztalra a rendelés kezeléséhez.
                </Text>
              </div>

              <RoomNavigation
                rooms={rooms}
                selectedRoomId={activeRoomId}
                onRoomChange={setActiveRoomId}
                loading={loadingRooms}
                error={roomsError}
                onRefresh={loadRooms}
              />

              <TableMap
                activeRoomId={activeRoomId}
                rooms={rooms}
                onTableSelect={handleTableSelect}
                selectedTableId={selectedTable?.id}
              />
            </Stack>
          </Container>
        </div>

        {selectedTable && (
          <div className="table-map-page__panel">
            <TableOrderPanel
              table={selectedTable}
              onClose={() => setSelectedTable(null)}
            />
          </div>
        )}
      </div>
    </MobileAppShell>
  );
};

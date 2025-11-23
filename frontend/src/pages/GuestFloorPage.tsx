import { useEffect, useState } from 'react';
import { Container, Paper, Stack, Text } from '@mantine/core';
import { MobileAppShell } from '@/components/layout/MobileAppShell';
import { RoomNavigation } from '@/components/rooms/RoomNavigation';
import { TableMap } from '@/components/table-map/TableMap';
import { getRooms } from '@/services/roomService';
import type { Room } from '@/types/room';
import type { Table } from '@/types/table';
import { useToast } from '@/components/common/Toast';
import './GuestFloorPage.css';

export const GuestFloorPage = () => {
  const { showToast } = useToast();
  const [rooms, setRooms] = useState<Room[]>([]);
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

  useEffect(() => {
    loadRooms();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleTableSelect = (table: Table) => {
    setSelectedTable(table);
  };

  return (
    <MobileAppShell>
      <div className="guest-floor-page">
        <Container size="xl" className="guest-floor-container">
          <Stack gap="md">
            <div className="guest-floor-header">
              <Text fw={700} size="xl">
                Vendégtér - Pincér Felület
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
          </Stack>
        </Container>

        <div className="guest-floor-workspace">
          <div className="guest-floor-map-area">
            <Container size="xl">
              <TableMap
                activeRoomId={activeRoomId}
                rooms={rooms}
                onTableSelect={handleTableSelect}
              />
            </Container>
          </div>

          <aside className="guest-floor-panel">
            <Paper withBorder radius="lg" p="lg" className="order-panel">
              {selectedTable ? (
                <Stack gap="md">
                  <div>
                    <Text fw={700} size="lg">
                      {selectedTable.table_number}
                    </Text>
                    <Text size="sm" c="dimmed">
                      Kapacitás: {selectedTable.capacity ?? '-'} fő
                    </Text>
                  </div>
                  <Text size="sm" c="dimmed">
                    A rendelési panel a következő lépésekben kerül implementálásra (FE-2, FE-3, FE-4).
                  </Text>
                </Stack>
              ) : (
                <Stack gap="md" align="center" justify="center" style={{ minHeight: '200px' }}>
                  <Text size="sm" c="dimmed" ta="center">
                    Válassz egy asztalt a részletek megtekintéséhez.
                  </Text>
                </Stack>
              )}
            </Paper>
          </aside>
        </div>
      </div>
    </MobileAppShell>
  );
};

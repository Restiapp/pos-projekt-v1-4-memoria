/**
 * GuestFloorPage - Guest-facing floor plan with order panel
 * FE-2: Implements table selection and basic order management
 */

import { useEffect, useState, useMemo, useCallback } from 'react';
import { RoomNavigation } from '@/components/rooms/RoomNavigation';
import { TableOrderPanel } from '@/components/orders/TableOrderPanel';
import { getRooms } from '@/services/roomService';
import { getTables } from '@/services/tableService';
import { useToast } from '@/hooks/useToast';
import type { Room } from '@/types/room';
import type { Table, TableShape, TableStatus } from '@/types/table';
import type { Order } from '@/types/order';
import { Spinner } from '@/components/ui/Spinner';
import './GuestFloorPage.css';

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
  return 'rect';
};

const deriveStatus = (table: Table): TableStatus => {
  const metaStatus = (table.metadata_json as Record<string, unknown> | null | undefined)?.status as
    | TableStatus
    | undefined;
  return table.status ?? metaStatus ?? 'FREE';
};

export const GuestFloorPage = () => {
  const toast = useToast();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [activeRoomId, setActiveRoomId] = useState<number | null>(null);
  const [loadingRooms, setLoadingRooms] = useState<boolean>(false);
  const [roomsError, setRoomsError] = useState<string | null>(null);

  const [tables, setTables] = useState<Table[]>([]);
  const [selectedTable, setSelectedTable] = useState<Table | null>(null);
  const [isLoadingTables, setIsLoadingTables] = useState<boolean>(false);
  const [tablesError, setTablesError] = useState<string | null>(null);

  const activeRoom = useMemo(
    () => rooms.find((room) => room.id === activeRoomId) ?? null,
    [activeRoomId, rooms]
  );

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
      toast.error('Nem sikerült betölteni a termeket');
    } finally {
      setLoadingRooms(false);
    }
  };

  const fetchTables = async () => {
    setIsLoadingTables(true);
    setTablesError(null);
    try {
      const data = await getTables();
      setTables(data);
    } catch (err) {
      console.error('Failed to load tables', err);
      setTablesError('Nem sikerült betölteni az asztalokat.');
      toast.error('Nem sikerült betölteni az asztalokat');
    } finally {
      setIsLoadingTables(false);
    }
  };

  useEffect(() => {
    loadRooms();
  }, []);

  useEffect(() => {
    fetchTables();
  }, []);

  const filteredTables = useMemo(() => {
    if (!activeRoomId) return tables;
    return tables.filter((table) => table.room_id === activeRoomId);
  }, [tables, activeRoomId]);

  const handleTableClick = useCallback((table: Table) => {
    setSelectedTable(table);
  }, []);

  const handleOrderUpdated = useCallback((order: Order) => {
    // Future: Update table status based on order
    console.log('Order updated:', order);
  }, []);

  const renderTableMap = () => {
    if (tablesError) {
      return (
        <div className="guest-floor-error">
          <p className="guest-floor-error-text">{tablesError}</p>
        </div>
      );
    }

    if (isLoadingTables && filteredTables.length === 0) {
      return (
        <div className="guest-floor-loading">
          <Spinner size="medium" />
          <p>Asztalok betöltése...</p>
        </div>
      );
    }

    if (filteredTables.length === 0) {
      return (
        <div className="guest-floor-empty">
          <p>Nincs megjeleníthető asztal</p>
          <p className="guest-floor-empty-hint">
            Adj hozzá asztalokat ehhez a teremhez az admin felületen.
          </p>
        </div>
      );
    }

    const width = activeRoom?.width ?? 1200;
    const height = activeRoom?.height ?? 720;

    return (
      <div className="guest-floor-canvas-wrapper">
        <div
          className="guest-floor-canvas"
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
            const isSelected = selectedTable?.id === table.id;

            return (
              <button
                key={table.id}
                className={`guest-floor-table guest-floor-table-${variant} ${
                  isSelected ? 'guest-floor-table-selected' : ''
                }`}
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
                <div className="guest-floor-table-content">
                  <span className="guest-floor-table-number">{table.table_number}</span>
                  <span className="guest-floor-table-status">{statusLabels[status]}</span>
                  <span className="guest-floor-table-capacity">{table.capacity ?? '-'} fő</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Legend */}
        <div className="guest-floor-legend">
          {(Object.keys(statusColors) as TableStatus[]).map((statusKey) => {
            const palette = statusColors[statusKey];
            return (
              <div key={statusKey} className="guest-floor-legend-item">
                <span
                  className="guest-floor-legend-dot"
                  style={{ backgroundColor: palette.bg, borderColor: palette.border }}
                />
                <span className="guest-floor-legend-label">{statusLabels[statusKey]}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="guest-floor-page">
      {/* Left Panel: Room Navigation + Table Map */}
      <div className="guest-floor-left">
        <div className="guest-floor-header">
          <h1 className="guest-floor-title">Terem Alaprajz</h1>
          <p className="guest-floor-subtitle">Válassz egy asztalt a rendelés megkezdéséhez</p>
        </div>

        <RoomNavigation
          rooms={rooms}
          selectedRoomId={activeRoomId}
          onRoomChange={setActiveRoomId}
          loading={loadingRooms}
          error={roomsError}
          onRefresh={loadRooms}
        />

        <div className="guest-floor-map-container">
          <div className="guest-floor-map-header">
            <h2 className="guest-floor-map-title">
              {activeRoom
                ? `${activeRoom.name} · ${filteredTables.length} asztal`
                : 'Válassz termet'}
            </h2>
          </div>
          {renderTableMap()}
        </div>
      </div>

      {/* Right Panel: Order Panel */}
      <div className="guest-floor-right">
        <TableOrderPanel table={selectedTable} onOrderUpdated={handleOrderUpdated} />
      </div>
    </div>
  );
};

/**
 * TableMap - Főkomponens: Asztaltérkép megjelenítése
 * Fetch-eli az összes termet és asztalokat és vizuális layout-ban jeleníti meg
 */

import { useState, useEffect } from 'react';
import { getTables, getRooms } from '@/services/tableService';
import type { Table, Room } from '@/types/table';
import { useAuthStore } from '@/stores/authStore';
import { notify } from '@/utils/notifications';
import './TableMap.css';

export const TableMap = () => {
  const { isAuthenticated } = useAuthStore();

  const [rooms, setRooms] = useState<Room[]>([]);
  const [tables, setTables] = useState<Table[]>([]);
  const [activeRoomId, setActiveRoomId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Termek és asztalok betöltése
  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('[TableMap] Fetching rooms and tables...');
        setLoading(true);
        const [roomsData, tablesData] = await Promise.all([
          getRooms(),
          getTables(),
        ]);
        console.log('[TableMap] ✅ Data loaded:', roomsData.length, 'rooms,', tablesData.length, 'tables');
        setRooms(roomsData);
        setTables(tablesData);
        if (roomsData.length > 0 && !activeRoomId) {
          setActiveRoomId(roomsData[0].id);
        }
        setError(null);
      } catch (err: any) {
        console.error('[TableMap] ❌ Failed to fetch data:', err);
        let errorMessage = 'Nem sikerült betölteni az asztalokat.';

        if (err.response?.status === 401) {
          errorMessage = '❌ Nincs bejelentkezve. Kérjük jelentkezzen be újra.';
        } else if (err.response?.status === 403) {
          errorMessage = '❌ Nincs jogosultsága az asztalok megtekintéséhez. Szükséges jogosultság: orders:manage';
        } else if (err.response?.data?.detail) {
          errorMessage = `❌ ${err.response.data.detail}`;
        } else if (err.message) {
          errorMessage = `❌ ${err.message}`;
        }

        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated) {
      fetchData();
    }
  }, [isAuthenticated]);

  // Asztal kattintás kezelése
  const handleTableClick = (table: Table) => {
    console.log('Asztal kiválasztva:', table);
    // TODO: Navigáció a rendelés oldalra vagy részletek megjelenítése
    notify.info(`Asztal: ${table.table_number} (ID: ${table.id})`);
  };

  if (loading) {
    return (
      <div className="table-map-loading">
        <p>Asztalok betöltése...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="table-map-error">
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Újrapróbálás</button>
      </div>
    );
  }

  if (tables.length === 0) {
    return (
      <div className="table-map-empty">
        <p>Nincs elérhető asztal.</p>
      </div>
    );
  }

  const activeRoom = rooms.find((r) => r.id === activeRoomId);
  const roomTables = tables.filter((t) => t.room_id === activeRoomId);

  // Determine table availability (green = available, red = occupied)
  const isTableAvailable = (table: Table): boolean => {
    // TODO: Check actual orders/reservations
    // For now, all tables are available (green)
    return true;
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Room Tabs Header */}
      <div className="bg-white border-b px-6 py-4 flex justify-between items-center shadow-sm">
        <h1 className="text-2xl font-bold text-gray-800">Asztalok</h1>

        <div className="flex items-center space-x-4">
          {/* Room Tabs */}
          <div className="flex bg-gray-100 rounded-lg p-1 gap-1">
            {rooms.map((room) => (
              <button
                key={room.id}
                onClick={() => setActiveRoomId(room.id)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeRoomId === room.id
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {room.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Canvas Area - Read-only Floor Plan View */}
      <div className="flex-1 p-8 overflow-auto flex justify-center">
        {activeRoom ? (
          <div className="relative overflow-auto bg-gray-100 p-8 rounded-lg shadow-inner min-h-[600px]">
            <div
              className="relative bg-white shadow-lg mx-auto"
              style={{
                width: `${activeRoom.width}px`,
                height: `${activeRoom.height}px`,
                backgroundImage: 'radial-gradient(#ddd 1px, transparent 1px)',
                backgroundSize: '20px 20px',
              }}
            >
              {roomTables.map((table) => {
                const isAvailable = isTableAvailable(table);
                return (
                  <div
                    key={table.id}
                    style={{
                      width: `${table.width}px`,
                      height: `${table.height}px`,
                      position: 'absolute',
                      left: `${table.x}px`,
                      top: `${table.y}px`,
                      backgroundColor: isAvailable ? '#F0FDF4' : '#FEE2E2',
                      border: isAvailable ? '2px solid #16A34A' : '2px solid #DC2626',
                      boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
                      transform: `rotate(${table.rotation}deg)`,
                      transformOrigin: 'center',
                      borderRadius: table.shape === 'CIRCLE' ? '50%' : '4px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      userSelect: 'none',
                      transition: 'all 0.2s ease',
                    }}
                    onClick={() => handleTableClick(table)}
                    className="hover:opacity-80"
                  >
                    <div className="flex flex-col items-center pointer-events-none">
                      <span className="font-bold text-sm">{table.table_number}</span>
                      <span className="text-xs text-gray-600">{table.capacity} fő</span>
                      <span className="text-xs font-medium mt-1" style={{ color: isAvailable ? '#16A34A' : '#DC2626' }}>
                        {isAvailable ? 'Szabad' : 'Foglalt'}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="text-gray-500">Nincs kiválasztott helyiség</div>
        )}
      </div>
    </div>
  );
};

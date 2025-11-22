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

                // Render chairs function (same logic as DraggableTable)
                const renderChairs = () => {
                  if (!table.capacity) return null;

                  const chairs = [];
                  const chairSize = 16;
                  const chairDistance = table.shape === 'CIRCLE' ? 10 : 8;

                  if (table.shape === 'CIRCLE') {
                    // Circular arrangement for round tables
                    const radius = (Math.max(table.width, table.height) / 2) + chairDistance;
                    for (let i = 0; i < table.capacity; i++) {
                      const angle = (i * 360) / table.capacity;
                      const radian = (angle * Math.PI) / 180;
                      const x = Math.cos(radian) * radius;
                      const y = Math.sin(radian) * radius;

                      chairs.push(
                        <div
                          key={i}
                          style={{
                            position: 'absolute',
                            width: `${chairSize}px`,
                            height: `${chairSize}px`,
                            borderRadius: '50%',
                            backgroundColor: '#8B4513',
                            border: '2px solid #654321',
                            left: `calc(50% + ${x}px - ${chairSize / 2}px)`,
                            top: `calc(50% + ${y}px - ${chairSize / 2}px)`,
                            boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
                          }}
                        />
                      );
                    }
                  } else {
                    // Rectangle: distribute chairs along edges
                    const perSide = Math.ceil(table.capacity / 4);
                    const longSideChairs = table.width > table.height ? perSide : Math.floor(perSide / 2) || 1;
                    const shortSideChairs = table.width > table.height ? Math.floor(perSide / 2) || 1 : perSide;

                    let chairIndex = 0;

                    // Top side
                    for (let i = 0; i < longSideChairs && chairIndex < table.capacity; i++) {
                      const x = ((i + 1) * table.width) / (longSideChairs + 1);
                      chairs.push(
                        <div
                          key={chairIndex++}
                          style={{
                            position: 'absolute',
                            width: `${chairSize}px`,
                            height: `${chairSize}px`,
                            borderRadius: '50%',
                            backgroundColor: '#8B4513',
                            border: '2px solid #654321',
                            left: `${x - chairSize / 2}px`,
                            top: `-${chairDistance + chairSize}px`,
                            boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
                          }}
                        />
                      );
                    }

                    // Right side
                    for (let i = 0; i < shortSideChairs && chairIndex < table.capacity; i++) {
                      const y = ((i + 1) * table.height) / (shortSideChairs + 1);
                      chairs.push(
                        <div
                          key={chairIndex++}
                          style={{
                            position: 'absolute',
                            width: `${chairSize}px`,
                            height: `${chairSize}px`,
                            borderRadius: '50%',
                            backgroundColor: '#8B4513',
                            border: '2px solid #654321',
                            right: `-${chairDistance + chairSize}px`,
                            top: `${y - chairSize / 2}px`,
                            boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
                          }}
                        />
                      );
                    }

                    // Bottom side
                    for (let i = 0; i < longSideChairs && chairIndex < table.capacity; i++) {
                      const x = ((i + 1) * table.width) / (longSideChairs + 1);
                      chairs.push(
                        <div
                          key={chairIndex++}
                          style={{
                            position: 'absolute',
                            width: `${chairSize}px`,
                            height: `${chairSize}px`,
                            borderRadius: '50%',
                            backgroundColor: '#8B4513',
                            border: '2px solid #654321',
                            left: `${x - chairSize / 2}px`,
                            bottom: `-${chairDistance + chairSize}px`,
                            boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
                          }}
                        />
                      );
                    }

                    // Left side
                    for (let i = 0; i < shortSideChairs && chairIndex < table.capacity; i++) {
                      const y = ((i + 1) * table.height) / (shortSideChairs + 1);
                      chairs.push(
                        <div
                          key={chairIndex++}
                          style={{
                            position: 'absolute',
                            width: `${chairSize}px`,
                            height: `${chairSize}px`,
                            borderRadius: '50%',
                            backgroundColor: '#8B4513',
                            border: '2px solid #654321',
                            left: `-${chairDistance + chairSize}px`,
                            top: `${y - chairSize / 2}px`,
                            boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
                          }}
                        />
                      );
                    }
                  }

                  return chairs;
                };

                return (
                  <div
                    key={table.id}
                    style={{
                      width: `${table.width}px`,
                      height: `${table.height}px`,
                      position: 'absolute',
                      left: `${table.x}px`,
                      top: `${table.y}px`,
                      // Furniture look with availability colors
                      background: isAvailable
                        ? 'linear-gradient(135deg, #D4F4DD 0%, #A7F3D0 100%)'
                        : 'linear-gradient(135deg, #FECACA 0%, #FCA5A5 100%)',
                      border: isAvailable ? '2px solid #16A34A' : '2px solid #DC2626',
                      boxShadow: '0 3px 8px rgba(0,0,0,0.25)',
                      transform: `rotate(${table.rotation}deg)`,
                      transformOrigin: 'center',
                      borderRadius: table.shape === 'CIRCLE' ? '50%' : '8px',
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
                    {/* Chairs */}
                    {renderChairs()}

                    {/* Table Label */}
                    <div className="flex flex-col items-center pointer-events-none">
                      <span className="font-bold text-sm text-gray-800">{table.table_number}</span>
                      <span className="text-xs text-gray-700">{table.capacity} fő</span>
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

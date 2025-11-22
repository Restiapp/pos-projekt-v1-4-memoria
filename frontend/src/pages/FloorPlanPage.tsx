import React, { useEffect, useState } from 'react';
import type { Room, Table, TableCreate } from '@/types/table';
import {
  getRooms,
  getTables,
  createTable,
  updateTable,
  deleteTable,
  createRoom,
  updateRoom,
  deleteRoom,
} from '@/services/tableService';
import RoomEditor from '@/components/table-map/RoomEditor';
import TablePropertiesPanel from '@/components/table-map/TablePropertiesPanel';

const FloorPlanPage: React.FC = () => {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [tables, setTables] = useState<Table[]>([]);
  const [activeRoomId, setActiveRoomId] = useState<number | null>(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [editingRoomId, setEditingRoomId] = useState<number | null>(null);
  const [editingRoomName, setEditingRoomName] = useState('');
  const [selectedTable, setSelectedTable] = useState<Table | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [roomsData, tablesData] = await Promise.all([
        getRooms(),
        getTables(),
      ]);
      setRooms(roomsData);
      setTables(tablesData);
      if (roomsData.length > 0 && !activeRoomId) {
        setActiveRoomId(roomsData[0].id);
      }
    } catch (error) {
      console.error('Failed to load floor plan data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTableMove = async (id: number, x: number, y: number) => {
    try {
      // Round to integers (backend expects int, not float)
      const roundedX = Math.round(x);
      const roundedY = Math.round(y);

      // Optimistic update
      setTables((prev) =>
        prev.map((t) => (t.id === id ? { ...t, x: roundedX, y: roundedY } : t))
      );

      // Update selected table if it's the one being moved
      if (selectedTable?.id === id) {
        setSelectedTable((prev) => prev ? { ...prev, x: roundedX, y: roundedY } : null);
      }

      await updateTable(id, { x: roundedX, y: roundedY });
    } catch (error) {
      console.error('Failed to update table position:', error);
      // Revert on error
      loadData();
    }
  };

  const handleTableClick = (table: Table) => {
    setSelectedTable(table);
  };

  const handleTablePropertyUpdate = async (id: number, updates: Partial<Table>) => {
    try {
      // Optimistic update
      setTables((prev) =>
        prev.map((t) => (t.id === id ? { ...t, ...updates } : t))
      );

      // Update selected table
      if (selectedTable?.id === id) {
        setSelectedTable((prev) => prev ? { ...prev, ...updates } : null);
      }

      // Backend update
      await updateTable(id, updates);
    } catch (error) {
      console.error('Failed to update table properties:', error);
      loadData();
    }
  };

  const handleDeleteTable = async (id: number) => {
    try {
      // Optimistic removal
      setTables((prev) => prev.filter((t) => t.id !== id));

      // Close properties panel if deleting selected table
      if (selectedTable?.id === id) {
        setSelectedTable(null);
      }

      // Backend delete
      await deleteTable(id);
    } catch (error) {
      console.error('Failed to delete table:', error);
      alert('Nem sikerült törölni az asztalt.');
      loadData();
    }
  };

  const handleAddTable = async (shape: 'RECTANGLE' | 'CIRCLE', capacity: number) => {
    if (!activeRoomId) return;

    // Calculate dimensions based on shape and capacity
    let width = 80;
    let height = 80;

    if (shape === 'CIRCLE') {
      // Circles: diameter based on capacity
      if (capacity === 2) { width = 60; height = 60; }
      else if (capacity === 4) { width = 80; height = 80; }
      else if (capacity === 6) { width = 100; height = 100; }
    } else {
      // Rectangles
      if (capacity === 2) { width = 60; height = 60; }
      else if (capacity === 4) { width = 80; height = 80; }
      else if (capacity === 6) { width = 120; height = 60; }
      else if (capacity === 8) { width = 160; height = 60; }
    }

    const newTableData: TableCreate = {
      table_number: `T${tables.length + 1}`,
      room_id: activeRoomId,
      x: 50,
      y: 50,
      width,
      height,
      rotation: 0,
      shape,
      capacity,
    };

    try {
      const newTable = await createTable(newTableData);
      setTables((prev) => [...prev, newTable]);
    } catch (error) {
      console.error('Failed to create table:', error);
    }
  };

  const handleCreateRoom = async () => {
    const roomName = prompt('Adja meg az új terem nevét:');
    if (!roomName || !roomName.trim()) return;

    try {
      const newRoom = await createRoom({
        name: roomName.trim(),
        width: 800,
        height: 600,
        is_active: true,
      });
      setRooms((prev) => [...prev, newRoom]);
      setActiveRoomId(newRoom.id);
    } catch (error) {
      console.error('Failed to create room:', error);
      alert('Nem sikerült létrehozni a termet. Lehet, hogy már létezik ilyen névvel.');
    }
  };

  const handleStartRenameRoom = (roomId: number, currentName: string) => {
    setEditingRoomId(roomId);
    setEditingRoomName(currentName);
  };

  const handleSaveRoomName = async () => {
    if (!editingRoomId || !editingRoomName.trim()) {
      setEditingRoomId(null);
      return;
    }

    try {
      await updateRoom(editingRoomId, { name: editingRoomName.trim() });
      setRooms((prev) =>
        prev.map((r) => (r.id === editingRoomId ? { ...r, name: editingRoomName.trim() } : r))
      );
      setEditingRoomId(null);
    } catch (error) {
      console.error('Failed to rename room:', error);
      alert('Nem sikerült átnevezni a termet. Lehet, hogy már létezik ilyen névvel.');
      setEditingRoomId(null);
    }
  };

  const handleDeleteRoom = async (roomId: number) => {
    const room = rooms.find((r) => r.id === roomId);
    if (!room) return;

    if (!confirm(`Biztosan törli a(z) "${room.name}" termet? Ez a művelet nem visszavonható!`)) {
      return;
    }

    try {
      await deleteRoom(roomId);
      setRooms((prev) => prev.filter((r) => r.id !== roomId));

      // Ha az aktív termet töröljük, váltsunk másikra
      if (activeRoomId === roomId) {
        const remainingRooms = rooms.filter((r) => r.id !== roomId);
        setActiveRoomId(remainingRooms.length > 0 ? remainingRooms[0].id : null);
      }
    } catch (error) {
      console.error('Failed to delete room:', error);
      alert('Nem sikerült törölni a termet.');
    }
  };

  const activeRoom = rooms.find((r) => r.id === activeRoomId);
  const roomTables = tables.filter((t) => t.room_id === activeRoomId);

  if (isLoading) {
    return <div className="p-8 text-center">Betöltés...</div>;
  }

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header & Toolbar */}
      <div className="bg-white border-b px-6 py-4 flex justify-between items-center shadow-sm">
        <h1 className="text-2xl font-bold text-gray-800">Alaprajz Szerkesztő</h1>

        <div className="flex items-center space-x-4">
          {/* Room Tabs */}
          <div className="flex bg-gray-100 rounded-lg p-1 gap-1">
            {rooms.map((room) => (
              <div key={room.id} className="flex items-center group">
                {editingRoomId === room.id ? (
                  <input
                    type="text"
                    value={editingRoomName}
                    onChange={(e) => setEditingRoomName(e.target.value)}
                    onBlur={handleSaveRoomName}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleSaveRoomName();
                      if (e.key === 'Escape') setEditingRoomId(null);
                    }}
                    autoFocus
                    className="px-3 py-2 rounded-md text-sm font-medium border border-blue-500 outline-none w-32"
                  />
                ) : (
                  <button
                    onClick={() => setActiveRoomId(room.id)}
                    onDoubleClick={() => handleStartRenameRoom(room.id, room.name)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      activeRoomId === room.id
                        ? 'bg-white text-blue-600 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    {room.name}
                  </button>
                )}
                {rooms.length > 1 && (
                  <button
                    onClick={() => handleDeleteRoom(room.id)}
                    className="ml-1 opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 transition-opacity"
                    title="Terem törlése"
                  >
                    ×
                  </button>
                )}
              </div>
            ))}

            {/* Add Room Button */}
            <button
              onClick={handleCreateRoom}
              className="px-3 py-2 rounded-md text-sm font-medium text-green-600 hover:bg-green-50 transition-colors"
              title="Új terem létrehozása"
            >
              + Új Terem
            </button>
          </div>

          <div className="h-6 w-px bg-gray-300 mx-2" />

          <button
            onClick={() => setIsEditMode(!isEditMode)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              isEditMode
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {isEditMode ? 'Szerkesztés Kész' : 'Szerkesztés'}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Toolbox (Only in Edit Mode) */}
        {isEditMode && (
          <div className="w-64 bg-white border-r p-4 flex flex-col gap-4 shadow-sm z-10 overflow-y-auto">
            <h3 className="font-semibold text-gray-700">Eszköztár</h3>

            {/* Kör asztalok */}
            <div className="space-y-2">
              <p className="text-xs text-gray-500 uppercase font-bold">Kör Asztalok</p>

              <button
                onClick={() => handleAddTable('CIRCLE', 2)}
                className="w-full flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="w-8 h-8 border-2 border-gray-600 rounded-full bg-white" />
                <div className="text-left">
                  <div className="text-sm font-medium">Kicsi kör</div>
                  <div className="text-xs text-gray-500">2 fő</div>
                </div>
              </button>

              <button
                onClick={() => handleAddTable('CIRCLE', 4)}
                className="w-full flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="w-10 h-10 border-2 border-gray-600 rounded-full bg-white" />
                <div className="text-left">
                  <div className="text-sm font-medium">Közepes kör</div>
                  <div className="text-xs text-gray-500">4 fő</div>
                </div>
              </button>

              <button
                onClick={() => handleAddTable('CIRCLE', 6)}
                className="w-full flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="w-12 h-12 border-2 border-gray-600 rounded-full bg-white" />
                <div className="text-left">
                  <div className="text-sm font-medium">Nagy kör</div>
                  <div className="text-xs text-gray-500">6 fő</div>
                </div>
              </button>
            </div>

            {/* Négyzet asztalok */}
            <div className="space-y-2">
              <p className="text-xs text-gray-500 uppercase font-bold">Négyzet Asztalok</p>

              <button
                onClick={() => handleAddTable('RECTANGLE', 2)}
                className="w-full flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="w-8 h-8 border-2 border-gray-600 rounded bg-white" />
                <div className="text-left">
                  <div className="text-sm font-medium">Kicsi négyzet</div>
                  <div className="text-xs text-gray-500">2 fő</div>
                </div>
              </button>

              <button
                onClick={() => handleAddTable('RECTANGLE', 4)}
                className="w-full flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="w-10 h-10 border-2 border-gray-600 rounded bg-white" />
                <div className="text-left">
                  <div className="text-sm font-medium">Nagy négyzet</div>
                  <div className="text-xs text-gray-500">4 fő</div>
                </div>
              </button>
            </div>

            {/* Téglalap asztalok */}
            <div className="space-y-2">
              <p className="text-xs text-gray-500 uppercase font-bold">Téglalap Asztalok</p>

              <button
                onClick={() => handleAddTable('RECTANGLE', 6)}
                className="w-full flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="w-12 h-8 border-2 border-gray-600 rounded bg-white" />
                <div className="text-left">
                  <div className="text-sm font-medium">Téglalap 6 fő</div>
                  <div className="text-xs text-gray-500">6 fő</div>
                </div>
              </button>

              <button
                onClick={() => handleAddTable('RECTANGLE', 8)}
                className="w-full flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="w-16 h-8 border-2 border-gray-600 rounded bg-white" />
                <div className="text-left">
                  <div className="text-sm font-medium">Téglalap 8 fő</div>
                  <div className="text-xs text-gray-500">8 fő</div>
                </div>
              </button>
            </div>
          </div>
        )}

        {/* Canvas Area */}
        <div className="flex-1 p-8 overflow-auto flex justify-center">
          {activeRoom ? (
            <RoomEditor
              room={activeRoom}
              tables={roomTables}
              isEditMode={isEditMode}
              selectedTableId={selectedTable?.id}
              onTableMove={handleTableMove}
              onTableClick={handleTableClick}
            />
          ) : (
            <div className="text-gray-500">Nincs kiválasztott helyiség</div>
          )}
        </div>

        {/* Table Properties Panel */}
        {selectedTable && isEditMode && (
          <TablePropertiesPanel
            table={selectedTable}
            onUpdate={handleTablePropertyUpdate}
            onDelete={handleDeleteTable}
            onClose={() => setSelectedTable(null)}
          />
        )}
      </div>
    </div>
  );
};

export default FloorPlanPage;

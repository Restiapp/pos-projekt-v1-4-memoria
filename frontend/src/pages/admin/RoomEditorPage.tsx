/**
 * RoomEditorPage - Helyiségek (Rooms) kezelése
 *
 * Funkciók:
 *   - Helyiségek listázása
 *   - Új helyiség létrehozása
 *   - Helyiség átnevezése
 *   - Drag & Drop átrendezés
 *   - Aktiválás/Deaktiválás
 */

import { useState, useEffect } from 'react';
import { Button, TextInput, Modal, Switch } from '@mantine/core';
import { useForm } from '@mantine/form';
import { getRooms, createRoom, updateRoom, toggleRoomActive, reorderRooms } from '@/services/roomService';
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import type { Room, RoomCreate } from '@/types/room';
import './RoomEditorPage.css';

export const RoomEditorPage = () => {
  const { showToast } = useToast();
  const { showConfirm } = useConfirm();

  const [rooms, setRooms] = useState<Room[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);
  const [draggedRoomId, setDraggedRoomId] = useState<number | null>(null);

  // Mantine form for room creation/editing
  const form = useForm<RoomCreate>({
    initialValues: {
      name: '',
      type: 'indoor',
      width: 800,
      height: 600,
      is_active: true,
      display_order: 0,
    },
    validate: {
      name: (value) => (value.trim().length === 0 ? 'A név megadása kötelező' : null),
      width: (value) => (value && value > 0 ? null : 'A szélesség pozitív szám kell legyen'),
      height: (value) => (value && value > 0 ? null : 'A magasság pozitív szám kell legyen'),
    },
  });

  // Fetch rooms
  const fetchRooms = async () => {
    try {
      setIsLoading(true);
      const data = await getRooms();
      setRooms(data);
    } catch (error) {
      console.error('Hiba a helyiségek betöltésekor:', error);
      showToast('Nem sikerült betölteni a helyiségeket!', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRooms();
  }, []);

  // Create new room
  const handleCreate = () => {
    form.reset();
    setEditingRoom(null);
    setIsModalOpen(true);
  };

  // Edit existing room
  const handleEdit = (room: Room) => {
    setEditingRoom(room);
    form.setValues({
      name: room.name,
      type: room.type,
      width: room.width,
      height: room.height,
      is_active: room.is_active,
      display_order: room.display_order,
    });
    setIsModalOpen(true);
  };

  // Submit form (create or update)
  const handleSubmit = async (values: RoomCreate) => {
    try {
      if (editingRoom) {
        await updateRoom(editingRoom.id, values);
        showToast('Helyiség sikeresen frissítve!', 'success');
      } else {
        await createRoom(values);
        showToast('Helyiség sikeresen létrehozva!', 'success');
      }
      setIsModalOpen(false);
      fetchRooms();
    } catch (error) {
      console.error('Hiba a helyiség mentésekor:', error);
      showToast('Nem sikerült menteni a helyiséget!', 'error');
    }
  };

  // Toggle active/inactive
  const handleToggleActive = async (room: Room) => {
    const action = room.is_active ? 'deaktiválni' : 'aktiválni';
    const confirmed = await showConfirm(
      `Biztosan szeretnéd ${action} ezt a helyiséget?`,
      `Helyiség: ${room.name}`
    );

    if (!confirmed) return;

    try {
      await toggleRoomActive(room.id);
      showToast(`Helyiség sikeresen ${room.is_active ? 'deaktiválva' : 'aktiválva'}!`, 'success');
      fetchRooms();
    } catch (error) {
      console.error('Hiba a helyiség állapotának váltásakor:', error);
      showToast('Nem sikerült módosítani a helyiséget!', 'error');
    }
  };

  // Drag and Drop handlers
  const handleDragStart = (e: React.DragEvent, roomId: number) => {
    setDraggedRoomId(roomId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = async (e: React.DragEvent, targetRoomId: number) => {
    e.preventDefault();

    if (draggedRoomId === null || draggedRoomId === targetRoomId) {
      setDraggedRoomId(null);
      return;
    }

    const draggedIndex = rooms.findIndex((r) => r.id === draggedRoomId);
    const targetIndex = rooms.findIndex((r) => r.id === targetRoomId);

    if (draggedIndex === -1 || targetIndex === -1) {
      setDraggedRoomId(null);
      return;
    }

    // Create new order
    const newRooms = [...rooms];
    const [draggedRoom] = newRooms.splice(draggedIndex, 1);
    newRooms.splice(targetIndex, 0, draggedRoom);

    // Update local state immediately for better UX
    setRooms(newRooms);

    // Send to backend
    try {
      const roomIds = newRooms.map((r) => r.id);
      await reorderRooms(roomIds);
      showToast('Helyiségek sorrendje frissítve!', 'success');
    } catch (error) {
      console.error('Hiba a helyiségek átrendezésekor:', error);
      showToast('Nem sikerült átrendezni a helyiségeket!', 'error');
      // Revert to original order
      fetchRooms();
    } finally {
      setDraggedRoomId(null);
    }
  };

  const handleDragEnd = () => {
    setDraggedRoomId(null);
  };

  return (
    <div className="room-editor-page">
      <div className="page-header">
        <h1>🏠 Helyiségek kezelése</h1>
        <div className="header-actions">
          <Button onClick={fetchRooms} variant="outline">
            🔄 Frissítés
          </Button>
          <Button onClick={handleCreate} variant="filled">
            ➕ Új helyiség
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="loading-state">Betöltés...</div>
      ) : rooms.length === 0 ? (
        <div className="empty-state">
          <p>Még nincsenek helyiségek. Hozz létre egyet!</p>
        </div>
      ) : (
        <div className="rooms-list">
          {rooms.map((room) => (
            <div
              key={room.id}
              className={`room-card ${draggedRoomId === room.id ? 'dragging' : ''} ${
                !room.is_active ? 'inactive' : ''
              }`}
              draggable
              onDragStart={(e) => handleDragStart(e, room.id)}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, room.id)}
              onDragEnd={handleDragEnd}
            >
              <div className="drag-handle">⋮⋮</div>
              <div className="room-info">
                <h3 className="room-name">{room.name}</h3>
                <div className="room-details">
                  <span className="room-type">
                    {room.type === 'indoor' ? '🏠 Belső' : '🌳 Kültéri'}
                  </span>
                  <span className="room-dimensions">
                    {room.width}x{room.height}px
                  </span>
                </div>
              </div>
              <div className="room-actions">
                <Switch
                  checked={room.is_active}
                  onChange={() => handleToggleActive(room)}
                  label={room.is_active ? 'Aktív' : 'Inaktív'}
                  color={room.is_active ? 'green' : 'gray'}
                />
                <Button onClick={() => handleEdit(room)} variant="light" size="sm">
                  ✏️ Szerkesztés
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        opened={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingRoom ? 'Helyiség szerkesztése' : 'Új helyiség létrehozása'}
        size="md"
      >
        <form onSubmit={form.onSubmit(handleSubmit)} className="room-form">
          <TextInput
            label="Név"
            placeholder="pl. Terasz, Nagyterem"
            required
            {...form.getInputProps('name')}
          />

          <div className="form-row">
            <TextInput
              label="Típus"
              placeholder="indoor / outdoor"
              {...form.getInputProps('type')}
            />
          </div>

          <div className="form-row">
            <TextInput
              label="Szélesség (px)"
              type="number"
              placeholder="800"
              {...form.getInputProps('width')}
            />
            <TextInput
              label="Magasság (px)"
              type="number"
              placeholder="600"
              {...form.getInputProps('height')}
            />
          </div>

          <Switch
            label="Aktív helyiség"
            {...form.getInputProps('is_active', { type: 'checkbox' })}
          />

          <div className="modal-actions">
            <Button variant="subtle" onClick={() => setIsModalOpen(false)}>
              Mégse
            </Button>
            <Button type="submit" variant="filled">
              {editingRoom ? 'Mentés' : 'Létrehozás'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

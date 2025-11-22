/**
 * MoveOrderModal - Modal for moving orders between different locations
 *
 * Features:
 * - Move order between TAKEAWAY ↔ BAR ↔ TABLE
 * - Fetch dynamic room list from GET /rooms
 * - Fetch tables for selected room from GET /tables
 * - Validate VAT changes (27% takeaway → 5% dine-in)
 * - Show confirmation dialog before moving
 *
 * UI: Mantine Modal + Select + Button
 * Error handling: Mantine notifications
 */

import { useState, useEffect } from 'react';
import { Modal, Select, Button, Stack, Text, Alert } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import type { Order, OrderUpdate } from '@/types/order';
import type { Room } from '@/types/room';
import type { Table } from '@/types/table';
import { getRooms, getTables } from '@/services/tableService';
import { updateOrder } from '@/services/orderService';
import { useConfirm } from '@/components/common/ConfirmDialog';

interface MoveOrderModalProps {
  order: Order;
  opened: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

type MoveDestination = 'TAKEAWAY' | 'BAR' | 'TABLE';

export const MoveOrderModal = ({
  order,
  opened,
  onClose,
  onSuccess,
}: MoveOrderModalProps) => {
  const { showConfirm } = useConfirm();

  // State
  const [destination, setDestination] = useState<MoveDestination | null>(null);
  const [selectedRoomId, setSelectedRoomId] = useState<string | null>(null);
  const [selectedTableId, setSelectedTableId] = useState<string | null>(null);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [tables, setTables] = useState<Table[]>([]);
  const [isLoadingRooms, setIsLoadingRooms] = useState(false);
  const [isLoadingTables, setIsLoadingTables] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch rooms on mount
  useEffect(() => {
    if (opened) {
      fetchRooms();
    }
  }, [opened]);

  // Fetch tables when room is selected
  useEffect(() => {
    if (selectedRoomId && destination === 'TABLE') {
      fetchTablesForRoom(Number(selectedRoomId));
    } else {
      setTables([]);
      setSelectedTableId(null);
    }
  }, [selectedRoomId, destination]);

  // Reset state when modal opens/closes
  useEffect(() => {
    if (!opened) {
      resetState();
    }
  }, [opened]);

  const resetState = () => {
    setDestination(null);
    setSelectedRoomId(null);
    setSelectedTableId(null);
    setTables([]);
  };

  const fetchRooms = async () => {
    try {
      setIsLoadingRooms(true);
      const roomsData = await getRooms();
      setRooms(roomsData);
    } catch (error: any) {
      console.error('Error fetching rooms:', error);
      notifications.show({
        title: 'Hiba',
        message: 'Nem sikerült betölteni a termeket',
        color: 'red',
      });
    } finally {
      setIsLoadingRooms(false);
    }
  };

  const fetchTablesForRoom = async (roomId: number) => {
    try {
      setIsLoadingTables(true);
      const allTables = await getTables();
      // Filter tables by room_id
      const filteredTables = allTables.filter((table) => table.room_id === roomId);
      setTables(filteredTables);
    } catch (error: any) {
      console.error('Error fetching tables:', error);
      notifications.show({
        title: 'Hiba',
        message: 'Nem sikerült betölteni az asztalokat',
        color: 'red',
      });
    } finally {
      setIsLoadingTables(false);
    }
  };

  const getCurrentLocation = (): string => {
    if (order.order_type === 'Elvitel') {
      return 'TAKEAWAY (Elvitel)';
    } else if (order.order_type === 'Helyben') {
      if (order.table_id) {
        return `TABLE (Asztal #${order.table_id})`;
      }
      return 'BAR (Helyben)';
    } else if (order.order_type === 'Kiszállítás') {
      return 'DELIVERY (Kiszállítás)';
    }
    return 'Ismeretlen';
  };

  const getVATChangeWarning = (): string | null => {
    const currentType = order.order_type;
    const currentVAT = order.final_vat_rate;

    // TAKEAWAY (Elvitel 27%) → BAR/TABLE (Helyben 5%)
    if (currentType === 'Elvitel' && (destination === 'BAR' || destination === 'TABLE')) {
      return `⚠️ ÁFA változás: ${currentVAT}% → 5% (Elvitel → Helyben fogyasztás)`;
    }

    // BAR/TABLE (Helyben 5%) → TAKEAWAY (Elvitel 27%)
    if (currentType === 'Helyben' && destination === 'TAKEAWAY') {
      return `⚠️ ÁFA változás: ${currentVAT}% → 27% (Helyben fogyasztás → Elvitel)`;
    }

    return null;
  };

  const handleMove = async () => {
    if (!destination) {
      notifications.show({
        title: 'Hiba',
        message: 'Kérjük, válassz célállomást!',
        color: 'red',
      });
      return;
    }

    if (destination === 'TABLE' && !selectedTableId) {
      notifications.show({
        title: 'Hiba',
        message: 'Kérjük, válassz asztalt!',
        color: 'red',
      });
      return;
    }

    // Build confirmation message
    let confirmMessage = `Biztosan át akarod helyezni a rendelést?\n\n`;
    confirmMessage += `Jelenlegi hely: ${getCurrentLocation()}\n`;
    confirmMessage += `Új hely: ${destination}`;

    if (destination === 'TABLE' && selectedTableId) {
      const selectedTable = tables.find((t) => t.id === Number(selectedTableId));
      if (selectedTable) {
        confirmMessage += ` (Asztal: ${selectedTable.table_number})`;
      }
    }

    const vatWarning = getVATChangeWarning();
    if (vatWarning) {
      confirmMessage += `\n\n${vatWarning}`;
    }

    const confirmed = await showConfirm(confirmMessage);
    if (!confirmed) return;

    // Prepare update data
    const updateData: any = {};

    if (destination === 'TAKEAWAY') {
      // Move to takeaway (Elvitel)
      updateData.order_type = 'Elvitel';
      updateData.table_id = null;
      updateData.final_vat_rate = 27.0;
    } else if (destination === 'BAR') {
      // Move to BAR (Helyben without specific table)
      updateData.order_type = 'Helyben';
      updateData.table_id = null;
      updateData.final_vat_rate = 5.0;
    } else if (destination === 'TABLE') {
      // Move to specific table (Helyben with table)
      updateData.order_type = 'Helyben';
      updateData.table_id = Number(selectedTableId);
      updateData.final_vat_rate = 5.0;
    }

    try {
      setIsSubmitting(true);
      await updateOrder(order.id, updateData);

      notifications.show({
        title: 'Siker',
        message: 'Rendelés sikeresen áthelyezve!',
        color: 'green',
      });

      onSuccess();
      onClose();
    } catch (error: any) {
      console.error('Error moving order:', error);
      const errorMsg = error.response?.data?.detail || 'Hiba történt a rendelés áthelyezése közben!';
      notifications.show({
        title: 'Hiba',
        message: errorMsg,
        color: 'red',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const destinationOptions = [
    { value: 'TAKEAWAY', label: 'TAKEAWAY (Elvitel)' },
    { value: 'BAR', label: 'BAR (Helyben - pult)' },
    { value: 'TABLE', label: 'TABLE (Helyben - asztal)' },
  ];

  const roomOptions = rooms.map((room) => ({
    value: String(room.id),
    label: room.name,
  }));

  const tableOptions = tables.map((table) => ({
    value: String(table.id),
    label: `Asztal ${table.table_number}`,
  }));

  const vatWarning = getVATChangeWarning();
  const canSubmit = destination && (destination !== 'TABLE' || selectedTableId) && !isSubmitting;

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={`Rendelés áthelyezése - #${order.id}`}
      size="lg"
      centered
    >
      <Stack gap="md">
        {/* Current location */}
        <Alert color="blue" title="Jelenlegi hely">
          {getCurrentLocation()}
        </Alert>

        {/* Destination selector */}
        <Select
          label="Új hely"
          placeholder="Válassz célállomást"
          data={destinationOptions}
          value={destination}
          onChange={(value) => setDestination(value as MoveDestination)}
          disabled={isSubmitting}
          required
        />

        {/* Room selector (only for TABLE destination) */}
        {destination === 'TABLE' && (
          <Select
            label="Terem"
            placeholder="Válassz termet"
            data={roomOptions}
            value={selectedRoomId}
            onChange={setSelectedRoomId}
            disabled={isSubmitting || isLoadingRooms}
            required
          />
        )}

        {/* Table selector (only for TABLE destination and after room selected) */}
        {destination === 'TABLE' && selectedRoomId && (
          <Select
            label="Asztal"
            placeholder="Válassz asztalt"
            data={tableOptions}
            value={selectedTableId}
            onChange={setSelectedTableId}
            disabled={isSubmitting || isLoadingTables}
            required
          />
        )}

        {/* VAT warning */}
        {vatWarning && (
          <Alert color="yellow" title="ÁFA figyelmeztetés">
            {vatWarning}
          </Alert>
        )}

        {/* Action buttons */}
        <Stack gap="sm" mt="md">
          <Button
            onClick={handleMove}
            disabled={!canSubmit}
            loading={isSubmitting}
            fullWidth
            color="blue"
          >
            Áthelyezés
          </Button>
          <Button
            onClick={onClose}
            disabled={isSubmitting}
            variant="outline"
            fullWidth
          >
            Mégse
          </Button>
        </Stack>
      </Stack>
    </Modal>
  );
};

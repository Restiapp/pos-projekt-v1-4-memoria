/**
 * TakeawayOrders - Elviteles rendelések kezelése
 *
 * Funkciók:
 *   - Elviteles rendelések listázása
 *   - Időalapú színkódolás (<15 perc = normál, >15 perc = sárga, >60 perc = piros villogó)
 *   - Átmozgatás funkció:
 *     - Pultra mozgatás
 *     - Asztalra mozgatás (modal room+table választóval)
 */

import { useState, useEffect } from 'react';
import { Table, Select, Button, Modal, Group, Text } from '@mantine/core';
import { getOrders, updateOrder } from '@/services/orderService';
import { getTables } from '@/services/tableService';
import { getRooms } from '@/services/roomService';
import type { Order } from '@/types/order';
import type { Table as TableType } from '@/types/table';
import type { Room } from '@/types/room';
import './TakeawayOrders.css';

interface TakeawayOrder extends Order {
  elapsedMinutes?: number;
}

export const TakeawayOrders = () => {
  const [orders, setOrders] = useState<TakeawayOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [tables, setTables] = useState<TableType[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);

  // Modal state for table selection
  const [isTableModalOpen, setIsTableModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [selectedRoomId, setSelectedRoomId] = useState<string | null>(null);
  const [selectedTableId, setSelectedTableId] = useState<string | null>(null);

  // Fetch takeaway orders
  const fetchOrders = async () => {
    try {
      setIsLoading(true);
      const response = await getOrders(1, 100, 'Elvitel', 'NYITOTT');

      // Calculate elapsed time for each order
      const ordersWithTime = response.items.map((order) => {
        const createdAt = new Date(order.created_at);
        const now = new Date();
        const elapsedMinutes = Math.floor((now.getTime() - createdAt.getTime()) / (1000 * 60));
        return { ...order, elapsedMinutes };
      });

      setOrders(ordersWithTime);
    } catch (error) {
      console.error('Hiba az elviteles rendelések betöltésekor:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch tables and rooms
  const fetchTablesAndRooms = async () => {
    try {
      const [tablesData, roomsData] = await Promise.all([
        getTables(),
        getRooms(),
      ]);
      setTables(tablesData);
      setRooms(roomsData);
    } catch (error) {
      console.error('Hiba az asztalok/termek betöltésekor:', error);
    }
  };

  useEffect(() => {
    fetchOrders();
    fetchTablesAndRooms();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchOrders, 30000);
    return () => clearInterval(interval);
  }, []);

  // Get row color class based on elapsed time
  const getRowColorClass = (minutes: number = 0): string => {
    if (minutes > 60) return 'row-red-blink';
    if (minutes > 15) return 'row-yellow';
    return '';
  };

  // Handle move action selection
  const handleMoveAction = async (order: Order, action: string) => {
    if (action === 'bar') {
      // Move to bar counter - change type to "Helyben" and assign to bar table
      try {
        await updateOrder(order.id, {
          order_type: 'Helyben',
          table_id: undefined, // Bar counter has no specific table
          notes: `${order.notes || ''}\n[Átmozgatva pultra]`.trim(),
        });
        fetchOrders();
      } catch (error) {
        console.error('Hiba a pultra mozgatáskor:', error);
        alert('Nem sikerült átmozgatni a rendelést a pultra!');
      }
    } else if (action === 'table') {
      // Open modal for table selection
      setSelectedOrder(order);
      setSelectedRoomId(null);
      setSelectedTableId(null);
      setIsTableModalOpen(true);
    }
  };

  // Handle move to table
  const handleMoveToTable = async () => {
    if (!selectedOrder || !selectedTableId) {
      alert('Kérlek válassz asztalt!');
      return;
    }

    try {
      await updateOrder(selectedOrder.id, {
        order_type: 'Helyben',
        table_id: parseInt(selectedTableId),
        notes: `${selectedOrder.notes || ''}\n[Átmozgatva asztalra: ${selectedTableId}]`.trim(),
      });
      setIsTableModalOpen(false);
      setSelectedOrder(null);
      fetchOrders();
    } catch (error) {
      console.error('Hiba az asztalra mozgatáskor:', error);
      alert('Nem sikerült átmozgatni a rendelést az asztalra!');
    }
  };

  // Get tables for selected room
  const getTablesForRoom = (): TableType[] => {
    if (!selectedRoomId) return [];
    return tables.filter((table) => table.room_id === parseInt(selectedRoomId));
  };

  // Format date/time
  const formatTime = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit' });
  };

  // Get expected pickup time (created + 30 min estimate)
  const getExpectedPickupTime = (createdAt: string): string => {
    const date = new Date(createdAt);
    date.setMinutes(date.getMinutes() + 30); // Assume 30 min prep time
    return formatTime(date.toISOString());
  };

  // Get customer name from order (placeholder - could be enhanced with customer lookup)
  const getCustomerName = (order: Order): string => {
    // Try to extract from notes or use customer_id
    if (order.notes) {
      const nameMatch = order.notes.match(/Név:\s*([^\n]+)/i);
      if (nameMatch) return nameMatch[1];
    }
    return order.customer_id ? `Vendég #${order.customer_id}` : 'Vendég';
  };

  const rows = orders.map((order) => (
    <Table.Tr key={order.id} className={getRowColorClass(order.elapsedMinutes)}>
      <Table.Td>{order.id}</Table.Td>
      <Table.Td>{getCustomerName(order)}</Table.Td>
      <Table.Td>{getExpectedPickupTime(order.created_at)}</Table.Td>
      <Table.Td>
        <span className={`status-badge status-${order.status.toLowerCase()}`}>
          {order.status}
        </span>
      </Table.Td>
      <Table.Td>
        <span className="elapsed-time">
          {order.elapsedMinutes} perc
        </span>
      </Table.Td>
      <Table.Td>
        <Select
          placeholder="Átmozgatás..."
          data={[
            { value: 'bar', label: 'Pultra mozgatás' },
            { value: 'table', label: 'Asztalra mozgatás' },
          ]}
          onChange={(value) => value && handleMoveAction(order, value)}
          clearable
          size="xs"
        />
      </Table.Td>
    </Table.Tr>
  ));

  return (
    <div className="takeaway-orders">
      {/* Header */}
      <header className="orders-header">
        <h1>🛍️ Elviteles Rendelések</h1>
        <Button onClick={fetchOrders} loading={isLoading} variant="light">
          🔄 Frissítés
        </Button>
      </header>

      {/* Orders Table */}
      <div className="table-wrapper">
        {isLoading && orders.length === 0 ? (
          <div className="loading-state">Betöltés...</div>
        ) : orders.length === 0 ? (
          <div className="empty-state">
            <p>✨ Nincs elviteles rendelés</p>
          </div>
        ) : (
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Sorszám</Table.Th>
                <Table.Th>Név</Table.Th>
                <Table.Th>Várható elvitel</Table.Th>
                <Table.Th>Státusz</Table.Th>
                <Table.Th>Várakozási idő</Table.Th>
                <Table.Th>Átmozgatás</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>{rows}</Table.Tbody>
          </Table>
        )}
      </div>

      {/* Table Selection Modal */}
      <Modal
        opened={isTableModalOpen}
        onClose={() => setIsTableModalOpen(false)}
        title="Asztal kiválasztása"
        size="md"
      >
        <div className="table-selection-modal">
          <Select
            label="Terem"
            placeholder="Válassz termet..."
            data={rooms.map((room) => ({
              value: room.id.toString(),
              label: room.name,
            }))}
            value={selectedRoomId}
            onChange={setSelectedRoomId}
            mb="md"
          />

          {selectedRoomId && (
            <Select
              label="Asztal"
              placeholder="Válassz asztalt..."
              data={getTablesForRoom().map((table) => ({
                value: table.id.toString(),
                label: `Asztal ${table.table_number}`,
              }))}
              value={selectedTableId}
              onChange={setSelectedTableId}
              mb="md"
            />
          )}

          <Group justify="flex-end" mt="xl">
            <Button variant="subtle" onClick={() => setIsTableModalOpen(false)}>
              Mégse
            </Button>
            <Button
              onClick={handleMoveToTable}
              disabled={!selectedTableId}
            >
              Átmozgatás
            </Button>
          </Group>
        </div>
      </Modal>
    </div>
  );
};

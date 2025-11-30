import React, { useEffect, useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Title, Group, Button, LoadingOverlay, Stack, Card, Text } from '@mantine/core';
import { guestOrderApi } from '@/api/guestOrderApi';
import type { OrderWithMetrics, TableMetrics, OrderItem } from '@/api/guestOrderApi';
import { RoundList } from './components/RoundList';
import { AddItemModal } from './components/AddItemModal';
import { MetricsDisplay } from './components/MetricsDisplay';
import { TableActions } from './components/TableActions';
import { WaveSelectionModal } from './components/WaveSelectionModal';

export const TableOrderPage: React.FC = () => {
  const { tableId } = useParams<{ tableId: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<OrderWithMetrics | null>(null);
  const [metrics, setMetrics] = useState<TableMetrics | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [addItemModalOpen, setAddItemModalOpen] = useState(false);
  const [waveModalOpen, setWaveModalOpen] = useState(false);

  // Load initial data
  const loadOrder = async () => {
    if (!tableId) return;
    try {
      setLoading(true);
      const orderData = await guestOrderApi.openOrder(parseInt(tableId));
      setOrder(orderData);

      const metricsData = await guestOrderApi.getMetrics(parseInt(tableId));
      setMetrics(metricsData);
    } catch (error) {
      console.error("Failed to load order", error);
    } finally {
      setLoading(false);
    }
  };

  // Poll for updates (metrics & order state)
  useEffect(() => {
    loadOrder();
    const interval = setInterval(async () => {
        if (!tableId) return;
        // Silent update
        const m = await guestOrderApi.getMetrics(parseInt(tableId));
        setMetrics(m);
    }, 5000);
    return () => clearInterval(interval);
  }, [tableId]);

  // Group items by round
  const rounds = useMemo(() => {
    if (!order) return {};
    const grouped: Record<number, OrderItem[]> = {};
    order.items.forEach(item => {
      const r = item.round_number || 1;
      if (!grouped[r]) grouped[r] = [];
      grouped[r].push(item);
    });
    return grouped;
  }, [order]);

  // Determine items that are "unsent" (Status VÁRAKOZIK or null)
  const unsentItems = useMemo(() => {
    if (!order) return [];
    return order.items.filter(i => !i.kds_status || i.kds_status === 'VÁRAKOZIK');
  }, [order]);

  const handleAddItem = async (itemData: { productId: number; quantity: number; courseTag: string; isUrgent: boolean; notes: string }) => {
    if (!order) return;
    // D5: Add items with default round 1 (or current unsent round).
    // The Wave Selector will re-assign rounds before sending.
    try {
        await guestOrderApi.addItems(order.id, 1, [{
            product_id: itemData.productId,
            quantity: itemData.quantity,
            course_tag: itemData.courseTag,
            is_urgent: itemData.isUrgent,
            notes: itemData.notes
        }]);
        loadOrder(); // Refresh
    } catch (e) {
        console.error(e);
    }
  };

  const handleToggleUrgent = async (itemId: number, currentStatus: boolean) => {
    try {
        await guestOrderApi.updateItemFlags(itemId, { is_urgent: !currentStatus });
        loadOrder();
    } catch (e) {
        console.error(e);
    }
  };

  const handleSendToKds = async (roundNumber: number) => {
    if (!order) return;
    try {
        await guestOrderApi.sendRoundToKds(order.id, roundNumber);
        loadOrder();
    } catch (e) {
        console.error(e);
    }
  };

  // D5: Logic for Wave Confirmation
  const handleWaveConfirm = async (waves: Record<number, number>) => {
    if (!order) return;
    setLoading(true);
    try {
      // 1. Update round_number for all items
      // In a real app, we'd want a bulk update endpoint. For now, loop parallel.
      const updatePromises = Object.entries(waves).map(([itemIdStr, roundNum]) =>
        guestOrderApi.updateItemRound(parseInt(itemIdStr), roundNum)
      );
      await Promise.all(updatePromises);

      // 2. Trigger Send for Round 1 (Red)
      // The prompt implies: "First send: Red goes out".
      // We check if there are any Round 1 items in the selection.
      const hasRound1 = Object.values(waves).includes(1);

      if (hasRound1) {
        await guestOrderApi.sendRoundToKds(order.id, 1);
      } else {
        console.log("No Round 1 items to send immediately.");
      }

      // Refresh
      await loadOrder();
    } catch (e) {
      console.error("Wave processing failed", e);
      alert("Hiba a rendelés küldésekor!");
    } finally {
      setLoading(false);
    }
  };

  const handleMoveTable = async (targetTableId: number) => {
    if (!order) return;
    try {
        await guestOrderApi.moveOrder(order.id, targetTableId);
        navigate(`/guest/table/${targetTableId}`);
    } catch (e) {
        alert("Hiba az asztal átmozgatásakor (pl. foglalt a cél asztal).");
    }
  };

  // Only show "Send to Kitchen" if there are unsent items
  const showSendButton = unsentItems.length > 0;

  if (loading && !order) return <LoadingOverlay visible />;

  return (
    <Container size="md" py="xl">
      <Card shadow="sm" p="lg" radius="md" withBorder mb="lg">
        <Group justify="space-between" mb="md">
          <Group>
             <Title order={2}>Asztal {tableId}</Title>
             <MetricsDisplay metrics={metrics} />
          </Group>
          <TableActions onMoveTable={handleMoveTable} />
        </Group>

        <Group mb="xl">
          <Button size="lg" onClick={() => setAddItemModalOpen(true)}>+ Tétel Hozzáadása</Button>

          {showSendButton && (
            <Button
              size="lg"
              color="orange"
              onClick={() => setWaveModalOpen(true)}
            >
              Rendelés Küldése (Hullámok)
            </Button>
          )}
        </Group>
      </Card>

      <RoundList
        rounds={rounds}
        onToggleUrgent={handleToggleUrgent}
        onSendToKds={handleSendToKds}
      />

      <AddItemModal
        opened={addItemModalOpen}
        onClose={() => setAddItemModalOpen(false)}
        onAdd={handleAddItem}
      />

      {order && (
        <WaveSelectionModal
          opened={waveModalOpen}
          onClose={() => setWaveModalOpen(false)}
          items={unsentItems}
          onConfirm={handleWaveConfirm}
        />
      )}
    </Container>
  );
};

/**
 * TableOrderPanel - Rounds-based order management for table orders
 *
 * Features:
 * - Display rounds grouped by round_number
 * - Add new rounds
 * - Add items to specific rounds
 * - Send rounds to kitchen (KDS)
 * - Status tracking for each round
 */

import { useState, useEffect, useMemo } from 'react';
import { Button, Paper, Stack, Text, Group, Badge, Divider } from '@mantine/core';
import { IconPlus, IconChefHat } from '@tabler/icons-react';
import { getOrderWithItems, sendRoundToKds } from '@/services/orderService';
import { useToast } from '@/components/common/Toast';
import type { OrderWithItems, Round, OrderItem } from '@/types/order';
import { AddItemModal } from './AddItemModal';
import './TableOrderPanel.css';

interface TableOrderPanelProps {
  orderId: number;
  onOrderUpdated?: () => void;
}

export const TableOrderPanel = ({ orderId, onOrderUpdated }: TableOrderPanelProps) => {
  const { showToast } = useToast();
  const [order, setOrder] = useState<OrderWithItems | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [addItemModalOpen, setAddItemModalOpen] = useState<boolean>(false);
  const [selectedRound, setSelectedRound] = useState<number | null>(null);
  const [sendingRounds, setSendingRounds] = useState<Set<number>>(new Set());

  // Derive rounds from order items
  const rounds = useMemo<Round[]>(() => {
    if (!order?.items) return [];

    // Group items by round_number
    const roundsMap = new Map<number, OrderItem[]>();

    order.items.forEach((item) => {
      // Default to round 1 if no round_number is set
      const roundNum = item.round_number ?? 1;
      if (!roundsMap.has(roundNum)) {
        roundsMap.set(roundNum, []);
      }
      roundsMap.get(roundNum)!.push(item);
    });

    // Convert to Round objects and sort by round_number
    const roundsArray: Round[] = Array.from(roundsMap.entries())
      .map(([roundNumber, items]) => ({
        round_number: roundNumber,
        items,
        status: 'OPEN' as const, // TODO: derive from backend when available
      }))
      .sort((a, b) => a.round_number - b.round_number);

    return roundsArray;
  }, [order]);

  const loadOrder = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const orderData = await getOrderWithItems(orderId);
      setOrder(orderData);
    } catch (err) {
      console.error('Failed to load order', err);
      setError('Nem sikerült betölteni a rendelést.');
      showToast('Nem sikerült betölteni a rendelést', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadOrder();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderId]);

  const handleAddNewRound = () => {
    // Find the highest round number and add 1
    const maxRound = rounds.length > 0
      ? Math.max(...rounds.map((r) => r.round_number))
      : 0;
    const newRoundNumber = maxRound + 1;

    // Open modal to add items to the new round
    setSelectedRound(newRoundNumber);
    setAddItemModalOpen(true);
  };

  const handleAddItemsToRound = (roundNumber: number) => {
    setSelectedRound(roundNumber);
    setAddItemModalOpen(true);
  };

  const handleSendRoundToKds = async (roundNumber: number) => {
    setSendingRounds((prev) => new Set(prev).add(roundNumber));
    try {
      const result = await sendRoundToKds(orderId, roundNumber);
      if (result.success) {
        showToast(result.message || `Kör ${roundNumber} elküldve a konyhának`, 'success');
        await loadOrder();
        onOrderUpdated?.();
      } else {
        showToast('Nem sikerült elküldeni a kört', 'error');
      }
    } catch (err) {
      console.error('Failed to send round to KDS', err);
      showToast('Hiba történt a kör küldésekor', 'error');
    } finally {
      setSendingRounds((prev) => {
        const next = new Set(prev);
        next.delete(roundNumber);
        return next;
      });
    }
  };

  const handleItemsAdded = async () => {
    setAddItemModalOpen(false);
    setSelectedRound(null);
    await loadOrder();
    onOrderUpdated?.();
    showToast('Tételek hozzáadva', 'success');
  };

  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const getStatusBadgeColor = (status?: string): string => {
    switch (status) {
      case 'SENT_TO_KDS':
        return 'blue';
      case 'READY':
        return 'green';
      default:
        return 'gray';
    }
  };

  const getStatusLabel = (status?: string): string => {
    switch (status) {
      case 'SENT_TO_KDS':
        return 'KONYHÁNAK KÜLDVE';
      case 'READY':
        return 'KÉSZ';
      default:
        return 'NYITOTT';
    }
  };

  if (isLoading) {
    return (
      <Paper withBorder radius="md" p="md" className="table-order-panel">
        <Text>Betöltés...</Text>
      </Paper>
    );
  }

  if (error || !order) {
    return (
      <Paper withBorder radius="md" p="md" className="table-order-panel">
        <Text c="red">{error || 'Nem sikerült betölteni a rendelést'}</Text>
        <Button onClick={loadOrder} mt="sm">
          Újrapróbálás
        </Button>
      </Paper>
    );
  }

  return (
    <>
      <Paper withBorder radius="md" p="md" className="table-order-panel">
        <Stack gap="md">
          {/* Header */}
          <Group justify="space-between" align="center">
            <div>
              <Text fw={700} size="lg">
                Rendelés #{order.id}
              </Text>
              <Text size="sm" c="dimmed">
                Asztal #{order.table_id} · {order.order_type}
              </Text>
            </div>
            <Badge color={order.status === 'NYITOTT' ? 'green' : 'gray'}>
              {order.status}
            </Badge>
          </Group>

          <Divider />

          {/* Rounds */}
          {rounds.length === 0 ? (
            <Text c="dimmed" ta="center" py="xl">
              Nincs még tétel ebben a rendelésben
            </Text>
          ) : (
            <Stack gap="lg">
              {rounds.map((round) => (
                <Paper key={round.round_number} withBorder p="sm" className="round-section">
                  <Stack gap="sm">
                    {/* Round Header */}
                    <Group justify="space-between" align="center">
                      <Group gap="xs">
                        <Text fw={600} size="md">
                          {round.round_number}. kör
                        </Text>
                        <Badge size="sm" color={getStatusBadgeColor(round.status)}>
                          {getStatusLabel(round.status)}
                        </Badge>
                      </Group>
                      <Group gap="xs">
                        <Button
                          size="xs"
                          variant="light"
                          leftSection={<IconPlus size={14} />}
                          onClick={() => handleAddItemsToRound(round.round_number)}
                        >
                          Tétel hozzáadása
                        </Button>
                        <Button
                          size="xs"
                          variant="filled"
                          color="orange"
                          leftSection={<IconChefHat size={14} />}
                          onClick={() => handleSendRoundToKds(round.round_number)}
                          loading={sendingRounds.has(round.round_number)}
                        >
                          Kör küldése konyhának
                        </Button>
                      </Group>
                    </Group>

                    {/* Round Items */}
                    <Stack gap="xs">
                      {round.items.map((item) => (
                        <Group key={item.id} justify="space-between" className="round-item">
                          <Group gap="sm">
                            <Text fw={500}>{item.quantity}x</Text>
                            <Text>{item.product_name || `Termék #${item.product_id}`}</Text>
                          </Group>
                          <Group gap="sm">
                            {item.kds_status && (
                              <Badge size="xs" variant="dot">
                                {item.kds_status}
                              </Badge>
                            )}
                            <Text size="sm" c="dimmed">
                              {formatPrice(item.unit_price * item.quantity)}
                            </Text>
                          </Group>
                        </Group>
                      ))}
                    </Stack>
                  </Stack>
                </Paper>
              ))}
            </Stack>
          )}

          {/* Add New Round Button */}
          <Button
            variant="outline"
            leftSection={<IconPlus size={16} />}
            onClick={handleAddNewRound}
          >
            Új kör
          </Button>
        </Stack>
      </Paper>

      {/* Add Item Modal */}
      {addItemModalOpen && selectedRound !== null && (
        <AddItemModal
          isOpen={addItemModalOpen}
          onClose={() => {
            setAddItemModalOpen(false);
            setSelectedRound(null);
          }}
          orderId={orderId}
          roundNumber={selectedRound}
          onItemsAdded={handleItemsAdded}
        />
      )}
    </>
  );
};

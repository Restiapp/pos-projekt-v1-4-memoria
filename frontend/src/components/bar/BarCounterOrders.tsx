/**
 * BarCounterOrders - Display active bar counter orders
 * Fetches and displays orders for guests consuming at the bar
 * Features: real-time polling, status color coding, time tracking
 */

import { useState, useEffect } from 'react';
import { Card, Text, Badge, Group, Stack, Skeleton } from '@mantine/core';
import apiClient from '@/services/api';
import './BarCounterOrders.css';

// =====================================================
// TYPES
// =====================================================

type BarOrderStatus = 'NEW' | 'DRINK_READY' | 'IN_PROGRESS' | 'COMPLETED';

interface BarCounterOrder {
  id: number;
  orderNumber: string;
  guestName?: string;
  createdAt: string; // ISO datetime string
  itemCount: number;
  status: BarOrderStatus;
}

interface BarOrdersResponse {
  items: BarCounterOrder[];
  total: number;
}

// =====================================================
// CONSTANTS
// =====================================================

const POLLING_INTERVAL = 5000; // 5 seconds
const DELAYED_THRESHOLD_MS = 20 * 60 * 1000; // 20 minutes in milliseconds

// =====================================================
// COMPONENT
// =====================================================

export const BarCounterOrders = () => {
  const [orders, setOrders] = useState<BarCounterOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Fetch bar counter orders from backend
  const fetchBarOrders = async () => {
    try {
      const response = await apiClient.get<BarOrdersResponse>('/api/orders/bar');
      setOrders(response.data.items);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      console.error('Error fetching bar orders:', err);
      setError('Hiba történt a pult rendelések betöltése során');
    } finally {
      setIsLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchBarOrders();
  }, []);

  // Polling with 5-second interval
  useEffect(() => {
    const interval = setInterval(() => {
      fetchBarOrders();
    }, POLLING_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  // Calculate time since order was created
  const getTimeSince = (createdAt: string): string => {
    const now = new Date();
    const created = new Date(createdAt);
    const diffMs = now.getTime() - created.getTime();
    const diffMinutes = Math.floor(diffMs / 60000);

    if (diffMinutes < 1) {
      return 'most';
    } else if (diffMinutes === 1) {
      return '1 perce';
    } else if (diffMinutes < 60) {
      return `${diffMinutes} perce`;
    } else {
      const hours = Math.floor(diffMinutes / 60);
      const minutes = diffMinutes % 60;
      return `${hours}ó ${minutes}p`;
    }
  };

  // Check if order is delayed (>20 minutes)
  const isDelayed = (createdAt: string): boolean => {
    const now = new Date();
    const created = new Date(createdAt);
    return (now.getTime() - created.getTime()) > DELAYED_THRESHOLD_MS;
  };

  // Get status color and label
  const getStatusDisplay = (order: BarCounterOrder) => {
    // Check if delayed first (overrides status color)
    if (isDelayed(order.createdAt)) {
      return {
        color: 'yellow' as const,
        label: 'KÉSIK',
      };
    }

    switch (order.status) {
      case 'NEW':
        return { color: 'blue' as const, label: 'ÚJ' };
      case 'DRINK_READY':
        return { color: 'green' as const, label: 'KÉSZ' };
      case 'IN_PROGRESS':
        return { color: 'cyan' as const, label: 'KÉSZÜL' };
      case 'COMPLETED':
        return { color: 'gray' as const, label: 'KÉSZ' };
      default:
        return { color: 'gray' as const, label: order.status };
    }
  };

  // Loading skeleton
  if (isLoading) {
    return (
      <div className="bar-counter-orders">
        <h2 className="bar-orders-title">🍺 Pult Rendelések</h2>
        <Stack gap="md">
          {[1, 2, 3].map((i) => (
            <Card key={i} shadow="sm" padding="lg" radius="md" withBorder>
              <Skeleton height={20} width="60%" mb="sm" />
              <Skeleton height={16} width="80%" mb="xs" />
              <Skeleton height={16} width="40%" />
            </Card>
          ))}
        </Stack>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bar-counter-orders">
        <h2 className="bar-orders-title">🍺 Pult Rendelések</h2>
        <Card shadow="sm" padding="lg" radius="md" withBorder className="error-card">
          <Text c="red" size="sm">⚠️ {error}</Text>
        </Card>
      </div>
    );
  }

  // Empty state
  if (orders.length === 0) {
    return (
      <div className="bar-counter-orders">
        <h2 className="bar-orders-title">🍺 Pult Rendelések</h2>
        <Card shadow="sm" padding="lg" radius="md" withBorder className="empty-state-card">
          <Text c="dimmed" ta="center" size="sm">
            ✨ Nincs aktív pult rendelés
          </Text>
        </Card>
      </div>
    );
  }

  return (
    <div className="bar-counter-orders">
      {/* Header */}
      <Group justify="space-between" mb="md" className="bar-orders-header">
        <h2 className="bar-orders-title">🍺 Pult Rendelések</h2>
        {lastUpdate && (
          <Text size="xs" c="dimmed">
            Frissítve: {lastUpdate.toLocaleTimeString('hu-HU')}
          </Text>
        )}
      </Group>

      {/* Orders List */}
      <Stack gap="md">
        {orders.map((order) => {
          const statusDisplay = getStatusDisplay(order);
          const timeSince = getTimeSince(order.createdAt);

          return (
            <Card
              key={order.id}
              shadow="sm"
              padding="lg"
              radius="md"
              withBorder
              className={`bar-order-card status-${statusDisplay.color}`}
            >
              {/* Order Number + Status Badge */}
              <Group justify="space-between" mb="xs">
                <Text fw={700} size="lg">
                  #{order.orderNumber}
                </Text>
                <Badge color={statusDisplay.color} variant="filled">
                  {statusDisplay.label}
                </Badge>
              </Group>

              {/* Guest Name */}
              <Text size="sm" c="dimmed" mb="xs">
                👤 {order.guestName || 'Névtelen'}
              </Text>

              {/* Time Since + Item Count */}
              <Group justify="space-between">
                <Text size="xs" c="dimmed">
                  🕐 {timeSince}
                </Text>
                <Text size="xs" c="dimmed">
                  📦 {order.itemCount} tétel
                </Text>
              </Group>
            </Card>
          );
        })}
      </Stack>
    </div>
  );
};

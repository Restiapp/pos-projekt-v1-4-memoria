/**
 * DrinkKdsQueue - Bar KDS Queue Display
 *
 * Displays drink orders in a queue with:
 * - Order number
 * - Item name and quantity
 * - Urgent flag (red highlight for items waiting > 5 minutes)
 * - Timer showing time in queue
 * - Grey styling for completed items (status=ready)
 */

import { useEffect, useState } from 'react';
import { Card, Grid, Badge, Text, Group, Stack, Loader, Center } from '@mantine/core';
import { getDrinkItems, type DrinkItem } from '@/services/kdsService';

const DrinkKdsQueue = () => {
  const [drinks, setDrinks] = useState<DrinkItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(Date.now());

  // Fetch drink items
  const fetchDrinks = async () => {
    try {
      setLoading(true);
      const items = await getDrinkItems();
      setDrinks(items);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch drink items:', err);
      setError('Failed to load drink orders');
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch and polling
  useEffect(() => {
    fetchDrinks();

    // Poll every 10 seconds for new drinks
    const pollInterval = setInterval(fetchDrinks, 10000);

    return () => clearInterval(pollInterval);
  }, []);

  // Update timer every second
  useEffect(() => {
    const timerInterval = setInterval(() => {
      setCurrentTime(Date.now());
    }, 1000);

    return () => clearInterval(timerInterval);
  }, []);

  // Calculate current time in queue
  const getTimeInQueue = (createdAt: string): string => {
    const created = new Date(createdAt).getTime();
    const diff = Math.floor((currentTime - created) / 1000); // seconds

    const minutes = Math.floor(diff / 60);
    const seconds = diff % 60;

    if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    }
    return `${seconds}s`;
  };

  // Determine card border color
  const getCardStyle = (drink: DrinkItem) => {
    const isReady = drink.status === 'READY' || drink.status === 'KÉSZ';
    const isUrgent = drink.urgent;

    if (isReady) {
      return {
        borderColor: '#adb5bd',
        backgroundColor: '#f8f9fa',
        opacity: 0.7
      };
    }

    if (isUrgent) {
      return {
        borderColor: '#fa5252',
        borderWidth: '3px',
        backgroundColor: '#fff5f5'
      };
    }

    return {
      borderColor: '#339af0',
      borderWidth: '2px'
    };
  };

  // Render loading state
  if (loading && drinks.length === 0) {
    return (
      <Center style={{ minHeight: '400px' }}>
        <Loader size="xl" />
      </Center>
    );
  }

  // Render error state
  if (error) {
    return (
      <Center style={{ minHeight: '400px' }}>
        <Text c="red" size="lg">{error}</Text>
      </Center>
    );
  }

  // Render empty state
  if (drinks.length === 0) {
    return (
      <Center style={{ minHeight: '400px' }}>
        <Text size="xl" c="dimmed">No drinks in queue</Text>
      </Center>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <Group justify="space-between" mb="xl">
        <Text size="xl" fw={700}>Bar Queue - Drink Orders</Text>
        <Badge size="lg" color="blue">
          {drinks.length} {drinks.length === 1 ? 'drink' : 'drinks'}
        </Badge>
      </Group>

      <Grid gutter="md">
        {drinks.map((drink) => {
          const cardStyle = getCardStyle(drink);
          const isReady = drink.status === 'READY' || drink.status === 'KÉSZ';

          return (
            <Grid.Col key={drink.id} span={{ base: 12, sm: 6, md: 4, lg: 3 }}>
              <Card
                shadow="sm"
                padding="lg"
                radius="md"
                withBorder
                style={{
                  borderColor: cardStyle.borderColor,
                  borderWidth: cardStyle.borderWidth || '1px',
                  backgroundColor: cardStyle.backgroundColor || '#ffffff',
                  opacity: cardStyle.opacity || 1,
                  transition: 'all 0.3s ease'
                }}
              >
                <Stack gap="xs">
                  {/* Order number and status badges */}
                  <Group justify="space-between">
                    <Badge size="lg" color="dark" variant="filled">
                      Order #{drink.orderNumber}
                    </Badge>
                    {drink.urgent && !isReady && (
                      <Badge size="sm" color="red" variant="filled">
                        URGENT
                      </Badge>
                    )}
                    {isReady && (
                      <Badge size="sm" color="gray" variant="filled">
                        READY
                      </Badge>
                    )}
                  </Group>

                  {/* Item name */}
                  <Text size="xl" fw={700} style={{ marginTop: '8px' }}>
                    {drink.itemName}
                  </Text>

                  {/* Quantity */}
                  <Text size="md" c="dimmed">
                    Quantity: {drink.quantity}x
                  </Text>

                  {/* Notes */}
                  {drink.notes && (
                    <Text size="sm" c="dimmed" style={{ fontStyle: 'italic' }}>
                      📝 {drink.notes}
                    </Text>
                  )}

                  {/* Time in queue */}
                  <Group justify="space-between" mt="md">
                    <Text size="sm" fw={500} c={drink.urgent ? 'red' : 'blue'}>
                      ⏱️ {getTimeInQueue(drink.createdAt)}
                    </Text>
                    <Text size="xs" c="dimmed">
                      {drink.minutesWaiting} min ago
                    </Text>
                  </Group>
                </Stack>
              </Card>
            </Grid.Col>
          );
        })}
      </Grid>
    </div>
  );
};

export default DrinkKdsQueue;

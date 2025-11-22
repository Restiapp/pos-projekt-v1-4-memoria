/**
 * BarPage - Bárpultos nézet (Bar View)
 *
 * Split-screen layout:
 *   LEFT: Active bar orders (Bárpult)
 *   RIGHT: Bar drink queue (Italos KDS)
 *
 * Sprint 1: Base layout implementation
 * - No business logic yet (mock only)
 * - Skeleton loaders for both panels
 * - Error boundary wrapper
 */

import { useState, useEffect } from 'react';
import { Flex, Paper, Stack, Title, Text, Skeleton, ScrollArea } from '@mantine/core';
import { GlobalHeader } from '@/components/layout/GlobalHeader';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import styles from './BarPage.module.scss';

// Mock data types for future implementation
interface BarOrder {
  id: number;
  tableNumber: string;
  status: 'pending' | 'preparing' | 'ready';
  items: string[];
}

interface DrinkQueueItem {
  id: number;
  orderNumber: string;
  drinkName: string;
  quantity: number;
  priority: 'normal' | 'urgent';
}

export const BarPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [barOrders] = useState<BarOrder[]>([]);
  const [drinkQueue] = useState<DrinkQueueItem[]>([]);

  // Simulate initial data loading
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <ErrorBoundary>
      <div className={styles.barPage}>
        {/* Global navigation header */}
        <GlobalHeader currentPage="bar" />

        {/* Main content: Split-screen layout */}
        <main className={styles.mainContent}>
          <Flex
            gap="md"
            className={styles.splitContainer}
            direction={{ base: 'column', md: 'row' }}
          >
            {/* LEFT PANEL: Bárpult (Active Bar Orders) */}
            <div className={styles.leftPanel}>
              <Paper shadow="sm" p="md" className={styles.panel}>
                <Stack gap="md">
                  <Title order={2} className={styles.panelTitle}>
                    🍸 Bárpult
                  </Title>

                  <Text size="sm" c="dimmed">
                    Aktív rendelések a bárpultról
                  </Text>

                  <ScrollArea className={styles.scrollArea}>
                    {isLoading ? (
                      // Skeleton loaders for active orders
                      <Stack gap="sm">
                        {Array.from({ length: 5 }).map((_, index) => (
                          <Paper key={index} shadow="xs" p="md" withBorder>
                            <Stack gap="xs">
                              <Skeleton height={20} width="40%" />
                              <Skeleton height={16} width="60%" />
                              <Skeleton height={16} width="80%" />
                              <Skeleton height={14} mt="xs" width="30%" />
                            </Stack>
                          </Paper>
                        ))}
                      </Stack>
                    ) : barOrders.length === 0 ? (
                      // Empty state
                      <Paper shadow="xs" p="xl" withBorder className={styles.emptyState}>
                        <Stack align="center" gap="sm">
                          <Text size="xl" c="dimmed">
                            📋
                          </Text>
                          <Text size="sm" c="dimmed" ta="center">
                            Nincs aktív rendelés
                          </Text>
                        </Stack>
                      </Paper>
                    ) : (
                      // Future: Render actual bar orders
                      <Stack gap="sm">
                        {barOrders.map((order) => (
                          <Paper key={order.id} shadow="xs" p="md" withBorder>
                            <Text fw={500}>Asztal {order.tableNumber}</Text>
                            <Text size="sm" c="dimmed">
                              {order.items.join(', ')}
                            </Text>
                          </Paper>
                        ))}
                      </Stack>
                    )}
                  </ScrollArea>
                </Stack>
              </Paper>
            </div>

            {/* RIGHT PANEL: Italos KDS (Bar Drink Queue) */}
            <div className={styles.rightPanel}>
              <Paper shadow="sm" p="md" className={styles.panel}>
                <Stack gap="md">
                  <Title order={2} className={styles.panelTitle}>
                    🥤 Italos KDS
                  </Title>

                  <Text size="sm" c="dimmed">
                    Ital előkészítési sor
                  </Text>

                  <ScrollArea className={styles.scrollArea}>
                    {isLoading ? (
                      // Skeleton loaders for drink queue
                      <Stack gap="sm">
                        {Array.from({ length: 6 }).map((_, index) => (
                          <Paper key={index} shadow="xs" p="md" withBorder>
                            <Stack gap="xs">
                              <Skeleton height={18} width="50%" />
                              <Skeleton height={14} width="70%" />
                              <Skeleton height={12} mt="xs" width="40%" />
                            </Stack>
                          </Paper>
                        ))}
                      </Stack>
                    ) : drinkQueue.length === 0 ? (
                      // Empty state
                      <Paper shadow="xs" p="xl" withBorder className={styles.emptyState}>
                        <Stack align="center" gap="sm">
                          <Text size="xl" c="dimmed">
                            ✅
                          </Text>
                          <Text size="sm" c="dimmed" ta="center">
                            Nincs várakozó ital
                          </Text>
                        </Stack>
                      </Paper>
                    ) : (
                      // Future: Render actual drink queue
                      <Stack gap="sm">
                        {drinkQueue.map((item) => (
                          <Paper key={item.id} shadow="xs" p="md" withBorder>
                            <Text fw={500}>{item.drinkName}</Text>
                            <Text size="sm" c="dimmed">
                              Rendelés: {item.orderNumber} | Mennyiség: {item.quantity}
                            </Text>
                          </Paper>
                        ))}
                      </Stack>
                    )}
                  </ScrollArea>
                </Stack>
              </Paper>
            </div>
          </Flex>
        </main>
      </div>
    </ErrorBoundary>
  );
};

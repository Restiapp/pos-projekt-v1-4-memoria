/**
 * GuestFloorPage - Guest-facing order management page
 *
 * This page demonstrates the TableOrderPanel component usage.
 * In production, this would be integrated with the table selection flow.
 *
 * Usage:
 *   /guest-floor?order_id=123
 */

import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Container, Stack, Text, Button, Group, Alert } from '@mantine/core';
import { IconArrowLeft } from '@tabler/icons-react';
import { MobileAppShell } from '@/components/layout/MobileAppShell';
import { TableOrderPanel } from '@/components/orders';
import './GuestFloorPage.css';

export const GuestFloorPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const orderIdParam = searchParams.get('order_id');
  const orderId = orderIdParam ? parseInt(orderIdParam) : null;

  if (!orderId) {
    return (
      <MobileAppShell>
        <Container size="lg" py="xl">
          <Alert color="red" title="Hiányzó rendelés azonosító">
            <Stack gap="sm">
              <Text>Nem található order_id paraméter az URL-ben.</Text>
              <Text size="sm">
                Példa: /guest-floor?order_id=123
              </Text>
              <Button
                variant="light"
                onClick={() => navigate('/tables')}
                leftSection={<IconArrowLeft size={16} />}
              >
                Vissza az asztaltérképre
              </Button>
            </Stack>
          </Alert>
        </Container>
      </MobileAppShell>
    );
  }

  return (
    <MobileAppShell>
      <Container size="lg" className="guest-floor-page">
        <Stack gap="md">
          <Group justify="space-between" align="center">
            <div>
              <Text fw={700} size="xl">
                Rendelés kezelése
              </Text>
              <Text size="sm" c="dimmed">
                Köröket kezelhetsz és tételeket adhatsz hozzá a rendeléshez
              </Text>
            </div>
            <Button
              variant="light"
              onClick={() => navigate('/tables')}
              leftSection={<IconArrowLeft size={16} />}
            >
              Vissza
            </Button>
          </Group>

          <TableOrderPanel orderId={orderId} />
        </Stack>
      </Container>
    </MobileAppShell>
  );
};

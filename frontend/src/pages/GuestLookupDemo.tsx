/**
 * GuestLookupDemo - Demo page for Guest Lookup + CRM feature
 * Module 9: Guest Lookup functionality showcase
 */

import { useState } from 'react';
import { Container, Title, Text, Stack, Alert } from '@mantine/core';
import { IconInfoCircle } from '@tabler/icons-react';
import { GuestLookup } from '@/components/crm/GuestLookup';
import { GlobalHeader } from '@/components/layout/GlobalHeader';
import type { Customer } from '@/types/customer';

export const GuestLookupDemo = () => {
  const [selectedGuest, setSelectedGuest] = useState<Customer | null>(null);
  const [isAnonymous, setIsAnonymous] = useState(false);

  const handleGuestSelected = (guest: Customer | null) => {
    setSelectedGuest(guest);
    setIsAnonymous(false);
    console.log('Guest selected:', guest);
  };

  const handleAnonymousGuest = () => {
    setSelectedGuest(null);
    setIsAnonymous(true);
    console.log('Anonymous guest (Guest = 0)');
  };

  return (
    <div>
      <GlobalHeader currentPage="operator" />

      <Container size="md" py="xl">
        <Stack gap="xl">
          <div>
            <Title order={1}>👤 Guest Lookup + CRM Demo</Title>
            <Text c="dimmed" size="sm">
              Module 9: Vendég keresése vendégszám alapján Mantine UI-val
            </Text>
          </div>

          <Alert icon={<IconInfoCircle />} title="Használat" color="blue">
            <Stack gap="xs">
              <Text size="sm">
                • Add meg a vendégszámot (customer_uid) pl. <strong>CUST-123456</strong>
              </Text>
              <Text size="sm">
                • Ha a vendég megtalálható: vendég adatok megjelennek (autofill)
              </Text>
              <Text size="sm">
                • Ha nincs találat: rendszer névtelen vendégként (Guest = 0) kezeli
              </Text>
              <Text size="sm">
                • Mantine UI komponensekkel beautified felület
              </Text>
            </Stack>
          </Alert>

          <GuestLookup
            onGuestSelected={handleGuestSelected}
            onAnonymousGuest={handleAnonymousGuest}
          />

          {/* Debug info */}
          {selectedGuest && (
            <Alert color="green" title="Vendég kiválasztva">
              <Text size="sm">
                Vendég ID: {selectedGuest.id}<br />
                Név: {selectedGuest.first_name} {selectedGuest.last_name}<br />
                Email: {selectedGuest.email}
              </Text>
            </Alert>
          )}

          {isAnonymous && (
            <Alert color="gray" title="Névtelen vendég">
              <Text size="sm">
                Guest = 0 (Anonymous)<br />
                A rendelés névtelen vendégként kerül rögzítésre.
              </Text>
            </Alert>
          )}
        </Stack>
      </Container>
    </div>
  );
};

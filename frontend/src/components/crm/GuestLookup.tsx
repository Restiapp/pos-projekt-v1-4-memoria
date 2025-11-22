/**
 * GuestLookup - Vendég keresése vendégszám (customer_uid) alapján
 *
 * Funkciók:
 *   - Vendégszám (sequence_id / customer_uid) alapján keresés
 *   - Találat esetén: vendég adatok megjelenítése és autofill
 *   - Nincs találat esetén: Anonymous guest (Guest = 0) kezelés
 *   - Mantine UI komponensekkel beautified felület
 */

import { useState } from 'react';
import {
  TextInput,
  Button,
  Card,
  Badge,
  Group,
  Stack,
  Text,
  Loader,
  Paper,
  Title,
  Divider,
} from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { IconSearch, IconUser, IconUserOff, IconMail, IconPhone, IconId } from '@tabler/icons-react';
import { getCustomerByUid } from '@/services/crmService';
import type { Customer } from '@/types/customer';

interface GuestLookupProps {
  onGuestSelected?: (guest: Customer | null) => void;
  onAnonymousGuest?: () => void;
}

export const GuestLookup = ({ onGuestSelected, onAnonymousGuest }: GuestLookupProps) => {
  const [guestNumber, setGuestNumber] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [foundGuest, setFoundGuest] = useState<Customer | null>(null);
  const [isAnonymous, setIsAnonymous] = useState(false);

  const handleLookup = async () => {
    if (!guestNumber.trim()) {
      notifications.show({
        title: 'Hiányzó adat',
        message: 'Kérlek add meg a vendégszámot!',
        color: 'yellow',
        icon: <IconUserOff size={18} />,
      });
      return;
    }

    try {
      setIsSearching(true);
      setIsAnonymous(false);
      setFoundGuest(null);

      const guest = await getCustomerByUid(guestNumber.trim());

      if (guest) {
        // Guest found - autofill
        setFoundGuest(guest);
        setIsAnonymous(false);
        notifications.show({
          title: 'Vendég megtalálva',
          message: `${guest.first_name} ${guest.last_name} - ${guest.email}`,
          color: 'green',
          icon: <IconUser size={18} />,
        });
        onGuestSelected?.(guest);
      } else {
        // Guest not found - anonymous (guest = 0)
        setFoundGuest(null);
        setIsAnonymous(true);
        notifications.show({
          title: 'Vendég nem található',
          message: 'A rendszer névtelen vendégként (Guest = 0) kezeli a rendelést.',
          color: 'blue',
          icon: <IconUserOff size={18} />,
        });
        onAnonymousGuest?.();
      }
    } catch (error) {
      console.error('Hiba a vendég keresésekor:', error);
      notifications.show({
        title: 'Hiba',
        message: 'Nem sikerült megkeresni a vendéget!',
        color: 'red',
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handleClear = () => {
    setGuestNumber('');
    setFoundGuest(null);
    setIsAnonymous(false);
  };

  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  return (
    <Stack gap="md">
      <Title order={3}>🔍 Vendég keresése</Title>

      {/* Search Input */}
      <Group align="flex-end">
        <TextInput
          label="Vendégszám (Customer UID)"
          placeholder="pl. CUST-123456"
          value={guestNumber}
          onChange={(e) => setGuestNumber(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleLookup()}
          leftSection={<IconId size={16} />}
          style={{ flex: 1 }}
          disabled={isSearching}
        />
        <Button
          onClick={handleLookup}
          loading={isSearching}
          leftSection={<IconSearch size={16} />}
          variant="filled"
        >
          Keresés
        </Button>
        {(foundGuest || isAnonymous) && (
          <Button onClick={handleClear} variant="light" color="gray">
            Törlés
          </Button>
        )}
      </Group>

      {/* Found Guest Card */}
      {foundGuest && (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Group justify="space-between" mb="xs">
            <Group>
              <IconUser size={24} />
              <Text fw={500} size="lg">
                {foundGuest.first_name} {foundGuest.last_name}
              </Text>
            </Group>
            <Group gap="xs">
              {foundGuest.tags && foundGuest.tags.map((tag, idx) => (
                <Badge key={idx} color="blue" variant="light">
                  {tag}
                </Badge>
              ))}
              {foundGuest.is_active ? (
                <Badge color="green">Aktív</Badge>
              ) : (
                <Badge color="red">Inaktív</Badge>
              )}
            </Group>
          </Group>

          <Divider my="sm" />

          <Stack gap="xs">
            <Group>
              <IconId size={16} />
              <Text size="sm" c="dimmed">Vendégszám:</Text>
              <Text size="sm" fw={500}>{foundGuest.customer_uid}</Text>
            </Group>

            <Group>
              <IconMail size={16} />
              <Text size="sm" c="dimmed">Email:</Text>
              <Text size="sm">{foundGuest.email}</Text>
            </Group>

            {foundGuest.phone && (
              <Group>
                <IconPhone size={16} />
                <Text size="sm" c="dimmed">Telefon:</Text>
                <Text size="sm">{foundGuest.phone}</Text>
              </Group>
            )}

            {foundGuest.birth_date && (
              <Group>
                <Text size="sm" c="dimmed">🎂 Születési dátum:</Text>
                <Text size="sm">
                  {new Date(foundGuest.birth_date).toLocaleDateString('hu-HU')}
                </Text>
              </Group>
            )}
          </Stack>

          <Divider my="sm" />

          <Group justify="space-around">
            <Paper p="xs" radius="md" withBorder style={{ flex: 1, textAlign: 'center' }}>
              <Text size="xs" c="dimmed">Hűségpontok</Text>
              <Text size="lg" fw={700} c="blue">
                {foundGuest.loyalty_points} pt
              </Text>
            </Paper>
            <Paper p="xs" radius="md" withBorder style={{ flex: 1, textAlign: 'center' }}>
              <Text size="xs" c="dimmed">Össz. költés</Text>
              <Text size="lg" fw={700} c="green">
                {formatPrice(foundGuest.total_spent)}
              </Text>
            </Paper>
            <Paper p="xs" radius="md" withBorder style={{ flex: 1, textAlign: 'center' }}>
              <Text size="xs" c="dimmed">Rendelések</Text>
              <Text size="lg" fw={700} c="orange">
                {foundGuest.total_orders}
              </Text>
            </Paper>
          </Group>

          {foundGuest.notes && (
            <>
              <Divider my="sm" />
              <Text size="sm" c="dimmed">📝 Jegyzetek:</Text>
              <Text size="sm">{foundGuest.notes}</Text>
            </>
          )}
        </Card>
      )}

      {/* Anonymous Guest Notice */}
      {isAnonymous && (
        <Card shadow="sm" padding="lg" radius="md" withBorder bg="blue.0">
          <Group>
            <IconUserOff size={32} color="gray" />
            <Stack gap={4} style={{ flex: 1 }}>
              <Text fw={500} size="lg">
                Névtelen vendég (Guest = 0)
              </Text>
              <Text size="sm" c="dimmed">
                A vendégszám nem található a rendszerben. A rendelés névtelen vendégként kerül rögzítésre.
              </Text>
            </Stack>
          </Group>
        </Card>
      )}

      {/* Loading State */}
      {isSearching && (
        <Group justify="center" p="xl">
          <Loader size="lg" />
          <Text size="sm" c="dimmed">
            Vendég keresése...
          </Text>
        </Group>
      )}
    </Stack>
  );
};

import React, { useState } from 'react';
import { Modal, Button, Group, Stack, Text, Badge, ScrollArea } from '@mantine/core';
import { OrderItem } from '@/api/guestOrderApi';

interface WaveSelectionModalProps {
  opened: boolean;
  onClose: () => void;
  items: OrderItem[];
  onConfirm: (waves: Record<number, number>) => void; // itemId -> roundNumber
}

export const WaveSelectionModal: React.FC<WaveSelectionModalProps> = ({ opened, onClose, items, onConfirm }) => {
  // Local state for waves: 1=Red, 2=Yellow, 3=Unmarked/Grey
  // Default to 3 (Unmarked)
  const [waves, setWaves] = useState<Record<number, number>>({});

  // Cycle: 3 (Grey) -> 1 (Red) -> 2 (Yellow) -> 3 (Grey)
  const toggleWave = (itemId: number) => {
    setWaves(prev => {
      const current = prev[itemId] || 3;
      let next = 3;
      if (current === 3) next = 1;
      else if (current === 1) next = 2;
      else next = 3;
      return { ...prev, [itemId]: next };
    });
  };

  const getWaveColor = (wave: number) => {
    switch (wave) {
      case 1: return 'red';
      case 2: return 'yellow';
      default: return 'gray';
    }
  };

  const getWaveLabel = (wave: number) => {
    switch (wave) {
      case 1: return '1. KÖR (AZONNAL)';
      case 2: return '2. KÖR (KÖVETKEZŐ)';
      default: return '3. KÖR (VÉGÉN)';
    }
  };

  const handleConfirm = () => {
    // Fill in defaults for untouched items
    const finalWaves: Record<number, number> = {};
    items.forEach(item => {
      finalWaves[item.id] = waves[item.id] || 3;
    });
    onConfirm(finalWaves);
    onClose();
  };

  return (
    <Modal opened={opened} onClose={onClose} title="Küldés a konyhára - Hullámok kiválasztása" size="lg">
      <Stack>
        <Text size="sm" c="dimmed">
          Kattints a tételekre a sorrend beállításához: Piros (1.) - Sárga (2.) - Szürke (3.)
        </Text>

        <ScrollArea h={400}>
          <Stack gap="xs">
            {items.map(item => {
              const wave = waves[item.id] || 3;
              return (
                <Group
                  key={item.id}
                  justify="space-between"
                  p="sm"
                  style={{
                    border: '1px solid var(--mantine-color-gray-3)',
                    borderRadius: 'var(--mantine-radius-md)',
                    cursor: 'pointer',
                    backgroundColor: wave === 1 ? 'var(--mantine-color-red-0)' :
                                     wave === 2 ? 'var(--mantine-color-yellow-0)' : 'transparent'
                  }}
                  onClick={() => toggleWave(item.id)}
                >
                  <Group>
                    <Badge circle>{item.quantity}</Badge>
                    <Text fw={500}>{item.name || `Termék #${item.product_id}`}</Text>
                  </Group>
                  <Badge color={getWaveColor(wave)} variant="filled" size="lg">
                    {getWaveLabel(wave)}
                  </Badge>
                </Group>
              );
            })}
          </Stack>
        </ScrollArea>

        <Group justify="flex-end" mt="md">
          <Button variant="default" onClick={onClose}>Mégse</Button>
          <Button onClick={handleConfirm} color="green">Kiválasztottak Küldése</Button>
        </Group>
      </Stack>
    </Modal>
  );
};

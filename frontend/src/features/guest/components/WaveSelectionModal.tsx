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
  // Defaults to 1 (Red/Immediate) for simplified waiter flow
  const [waves, setWaves] = useState<Record<number, number>>({});

  // Cycle: 1 (Red) -> 2 (Yellow) -> 3 (Grey) -> 1 (Red)
  const toggleWave = (itemId: number, currentRound: number) => {
    setWaves(prev => {
      const current = prev[itemId] || currentRound;
      let next = 1;
      if (current === 1) next = 2;
      else if (current === 2) next = 3;
      else next = 1;
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
    // Fill in defaults for untouched items using their existing round or defaulting to 1
    const finalWaves: Record<number, number> = {};
    items.forEach(item => {
      finalWaves[item.id] = waves[item.id] || item.round_number || 1;
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
              // Determine display wave: local state -> item prop -> default (1)
              const wave = waves[item.id] || item.round_number || 1;

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
                  onClick={() => toggleWave(item.id, wave)}
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

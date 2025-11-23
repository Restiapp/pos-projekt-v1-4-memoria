import React, { useState } from 'react';
import { Accordion, Button, Group, Text, Box } from '@mantine/core';
import type { OrderItem } from '@/api/guestOrderApi';
import { OrderItemRow } from './OrderItemRow';

interface RoundListProps {
  rounds: Record<number, OrderItem[]>;
  onToggleUrgent: (itemId: number, currentStatus: boolean) => void;
  onSendToKds: (roundNumber: number) => void;
}

export const RoundList: React.FC<RoundListProps> = ({ rounds, onToggleUrgent, onSendToKds }) => {
  // Sort rounds descending (newest first)
  const sortedRoundNumbers = Object.keys(rounds).map(Number).sort((a, b) => b - a);
  const [openItems, setOpenItems] = useState<string[]>(sortedRoundNumbers.map(String));

  return (
    <Accordion multiple value={openItems} onChange={setOpenItems} variant="separated">
      {sortedRoundNumbers.map((roundNum) => {
        const items = rounds[roundNum];
        // Check if any items in this round are still "VÁRAKOZIK" (Waiting) to enable Send button
        const canSend = items.some(i => !i.kds_status || i.kds_status === 'VÁRAKOZIK');

        return (
          <Accordion.Item key={roundNum} value={String(roundNum)}>
            <Accordion.Control>
              <Group justify="space-between">
                <Text fw={700} size="lg">{roundNum}. Kör</Text>
                <Text size="sm" c="dimmed">{items.length} tétel</Text>
              </Group>
            </Accordion.Control>
            <Accordion.Panel>
              <Box mb="md">
                {items.map(item => (
                  <OrderItemRow key={item.id} item={item} onToggleUrgent={onToggleUrgent} />
                ))}
              </Box>

              {canSend && (
                <Button
                  fullWidth
                  color="orange"
                  onClick={() => onSendToKds(roundNum)}
                >
                  Küldés a Konyhára (KDS)
                </Button>
              )}
            </Accordion.Panel>
          </Accordion.Item>
        );
      })}
    </Accordion>
  );
};

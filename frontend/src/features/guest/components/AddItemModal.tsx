import React from 'react';
import { Modal, NumberInput, Select, Switch, TextInput, Button, Group, Stack, Text } from '@mantine/core';

interface AddItemModalProps {
  opened: boolean;
  onClose: () => void;
  onAdd: (item: { productId: number; quantity: number; courseTag: string; isUrgent: boolean; notes: string }) => void;
}

// Mock products for Sprint 0/D3 since we don't have full Menu API connected yet
const MOCK_PRODUCTS = [
  { value: '1', label: 'Gulyásleves' },
  { value: '2', label: 'Bécsi szelet' },
  { value: '3', label: 'Somlói galuska' },
  { value: '4', label: 'Coca Cola' },
  { value: '5', label: 'Ásványvíz' },
];

export const AddItemModal: React.FC<AddItemModalProps> = ({ opened, onClose, onAdd }) => {
  const [productId, setProductId] = React.useState<string | null>(null);
  const [quantity, setQuantity] = React.useState<number>(1);
  // D5: "Nem használunk többé course_tag alapú logikát" - hidden from UI, default null
  const [isUrgent, setIsUrgent] = React.useState(false);
  const [notes, setNotes] = React.useState('');

  const handleAdd = () => {
    if (productId) {
      onAdd({
        productId: parseInt(productId),
        quantity,
        courseTag: '', // Deprecated for D5 waiter flow
        isUrgent,
        notes
      });
      // Reset form
      setProductId(null);
      setQuantity(1);
      setNotes('');
      onClose();
    }
  };

  return (
    <Modal opened={opened} onClose={onClose} title="Új tétel hozzáadása">
      <Stack>
        <Select
          label="Termék"
          placeholder="Válassz terméket"
          data={MOCK_PRODUCTS}
          value={productId}
          onChange={setProductId}
          searchable
        />

        <NumberInput
          label="Mennyiség"
          value={quantity}
          onChange={(val) => setQuantity(Number(val))}
          min={1}
        />

        {/* D5: Course Tag Removed from UI */}

        <Switch
          label="Sürgős (Urgent)"
          checked={isUrgent}
          onChange={(event) => setIsUrgent(event.currentTarget.checked)}
          color="red"
        />

        <TextInput
          label="Megjegyzés"
          placeholder="pl. Gluténmentes, Nincs hagyma..."
          value={notes}
          onChange={(e) => setNotes(e.currentTarget.value)}
        />

        <Group justify="flex-end" mt="md">
          <Button variant="default" onClick={onClose}>Mégse</Button>
          <Button onClick={handleAdd} disabled={!productId}>Hozzáadás</Button>
        </Group>
      </Stack>
    </Modal>
  );
};

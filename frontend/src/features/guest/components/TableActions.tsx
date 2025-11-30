import React, { useState } from 'react';
import { Button, Group, Menu, Modal, NumberInput } from '@mantine/core';

interface TableActionsProps {
  onMoveTable: (targetTableId: number) => void;
}

export const TableActions: React.FC<TableActionsProps> = ({ onMoveTable }) => {
  const [moveModalOpen, setMoveModalOpen] = useState(false);
  const [targetTableId, setTargetTableId] = useState<number | ''>('');

  const handleMove = () => {
    if (typeof targetTableId === 'number') {
      onMoveTable(targetTableId);
      setMoveModalOpen(false);
    }
  };

  return (
    <>
      <Menu shadow="md" width={200}>
        <Menu.Target>
          <Button variant="outline">Műveletek</Button>
        </Menu.Target>

        <Menu.Dropdown>
          <Menu.Item onClick={() => setMoveModalOpen(true)}>
            Asztal átmozgatása (Move)
          </Menu.Item>
          <Menu.Item disabled>Számla szétbontása (Split) - WIP</Menu.Item>
          <Menu.Item disabled>Asztal összevonás (Merge) - WIP</Menu.Item>
        </Menu.Dropdown>
      </Menu>

      <Modal opened={moveModalOpen} onClose={() => setMoveModalOpen(false)} title="Asztal Átmozgatása">
        <NumberInput
          label="Cél asztal száma (ID)"
          placeholder="pl. 12"
          value={targetTableId}
          onChange={(val) => setTargetTableId(Number(val))}
          mb="md"
        />
        <Button fullWidth onClick={handleMove} disabled={targetTableId === ''}>
          Átmozgatás
        </Button>
      </Modal>
    </>
  );
};

import React from 'react';
import { DndContext, DragOverlay } from '@dnd-kit/core';
import type { DragEndEvent } from '@dnd-kit/core';
import { restrictToParentElement } from '@dnd-kit/modifiers';
import type { Room, Table } from '@/types/table';
import DraggableTable from './DraggableTable';

interface RoomEditorProps {
  room: Room;
  tables: Table[];
  isEditMode: boolean;
  selectedTableId?: number | null;
  onTableMove: (id: number, x: number, y: number) => void;
  onTableClick: (table: Table) => void;
}

const RoomEditor: React.FC<RoomEditorProps> = ({
  room,
  tables,
  isEditMode,
  selectedTableId,
  onTableMove,
  onTableClick,
}) => {
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, delta } = event;

    if (!active.data.current) return;

    const table = active.data.current.table as Table;

    // Calculate new position based on delta
    const newX = table.x + delta.x;
    const newY = table.y + delta.y;

    // Call parent callback with new position
    onTableMove(table.id, newX, newY);
  };

  return (
    <DndContext
      onDragEnd={handleDragEnd}
      modifiers={[restrictToParentElement]}
    >
      <div className="relative overflow-auto bg-gray-100 p-8 rounded-lg shadow-inner min-h-[600px]">
        <div
          className="relative bg-white shadow-lg mx-auto transition-all duration-300"
          style={{
            width: `${room.width}px`,
            height: `${room.height}px`,
            backgroundImage: 'radial-gradient(#ddd 1px, transparent 1px)',
            backgroundSize: '20px 20px',
          }}
        >
          {tables.map((table) => (
            <DraggableTable
              key={table.id}
              table={table}
              isEditMode={isEditMode}
              isSelected={selectedTableId === table.id}
              onClick={onTableClick}
            />
          ))}
        </div>
      </div>
      <DragOverlay>
        {/* Optional: Custom drag overlay */}
      </DragOverlay>
    </DndContext>
  );
};

export default RoomEditor;

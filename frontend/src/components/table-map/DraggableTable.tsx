import React from 'react';
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import type { Table } from '@/types/table';

interface DraggableTableProps {
  table: Table;
  isEditMode: boolean;
  isSelected?: boolean;
  onClick: (table: Table) => void;
}

const DraggableTable: React.FC<DraggableTableProps> = ({
  table,
  isEditMode,
  isSelected = false,
  onClick,
}) => {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: `table-${table.id}`,
    disabled: !isEditMode,
    data: {
      table,
    },
  });

  const style: React.CSSProperties = {
    width: `${table.width}px`,
    height: `${table.height}px`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: isEditMode ? 'move' : 'pointer',
    position: 'absolute',
    left: `${table.x}px`,
    top: `${table.y}px`,
    backgroundColor: isSelected ? '#EBF8FF' : '#fff',
    border: isSelected ? '3px solid #3B82F6' : '2px solid #333',
    boxShadow: isDragging
      ? '0 8px 15px rgba(0,0,0,0.3)'
      : isSelected
        ? '0 0 0 3px rgba(59, 130, 246, 0.3)'
        : '0 2px 5px rgba(0,0,0,0.2)',
    userSelect: 'none',
    transform: `${CSS.Translate.toString(transform)} rotate(${table.rotation}deg)`,
    transformOrigin: 'center',
    transition: isDragging ? 'none' : 'all 0.2s ease',
    zIndex: isDragging ? 1000 : isSelected ? 100 : 1,
    borderRadius: table.shape === 'CIRCLE' ? '50%' : '4px',
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      onClick={() => !isDragging && onClick(table)}
      className="hover:bg-gray-50 transition-colors"
    >
      <div className="flex flex-col items-center pointer-events-none">
        <span className="font-bold text-sm">{table.table_number}</span>
        <span className="text-xs text-gray-500">
          {table.capacity} fő
        </span>
      </div>
    </div>
  );
};

export default DraggableTable;

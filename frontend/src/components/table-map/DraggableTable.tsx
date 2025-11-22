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

  // Calculate chair positions based on table shape and capacity
  const renderChairs = () => {
    if (!table.capacity) return null;

    const chairs = [];
    const chairSize = 16;
    const chairDistance = table.shape === 'CIRCLE' ? 10 : 8;

    if (table.shape === 'CIRCLE') {
      // Circular arrangement for round tables
      const radius = (Math.max(table.width, table.height) / 2) + chairDistance;
      for (let i = 0; i < table.capacity; i++) {
        const angle = (i * 360) / table.capacity;
        const radian = (angle * Math.PI) / 180;
        const x = Math.cos(radian) * radius;
        const y = Math.sin(radian) * radius;

        chairs.push(
          <div
            key={i}
            style={{
              position: 'absolute',
              width: `${chairSize}px`,
              height: `${chairSize}px`,
              borderRadius: '50%',
              backgroundColor: '#8B4513',
              border: '2px solid #654321',
              left: `calc(50% + ${x}px - ${chairSize / 2}px)`,
              top: `calc(50% + ${y}px - ${chairSize / 2}px)`,
              boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
            }}
          />
        );
      }
    } else {
      // Rectangle: distribute chairs along edges
      const perSide = Math.ceil(table.capacity / 4);
      const longSideChairs = table.width > table.height ? perSide : Math.floor(perSide / 2) || 1;
      const shortSideChairs = table.width > table.height ? Math.floor(perSide / 2) || 1 : perSide;

      let chairIndex = 0;

      // Top side
      for (let i = 0; i < longSideChairs && chairIndex < table.capacity; i++) {
        const x = ((i + 1) * table.width) / (longSideChairs + 1);
        chairs.push(
          <div
            key={chairIndex++}
            style={{
              position: 'absolute',
              width: `${chairSize}px`,
              height: `${chairSize}px`,
              borderRadius: '50%',
              backgroundColor: '#8B4513',
              border: '2px solid #654321',
              left: `${x - chairSize / 2}px`,
              top: `-${chairDistance + chairSize}px`,
              boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
            }}
          />
        );
      }

      // Right side
      for (let i = 0; i < shortSideChairs && chairIndex < table.capacity; i++) {
        const y = ((i + 1) * table.height) / (shortSideChairs + 1);
        chairs.push(
          <div
            key={chairIndex++}
            style={{
              position: 'absolute',
              width: `${chairSize}px`,
              height: `${chairSize}px`,
              borderRadius: '50%',
              backgroundColor: '#8B4513',
              border: '2px solid #654321',
              right: `-${chairDistance + chairSize}px`,
              top: `${y - chairSize / 2}px`,
              boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
            }}
          />
        );
      }

      // Bottom side
      for (let i = 0; i < longSideChairs && chairIndex < table.capacity; i++) {
        const x = ((i + 1) * table.width) / (longSideChairs + 1);
        chairs.push(
          <div
            key={chairIndex++}
            style={{
              position: 'absolute',
              width: `${chairSize}px`,
              height: `${chairSize}px`,
              borderRadius: '50%',
              backgroundColor: '#8B4513',
              border: '2px solid #654321',
              left: `${x - chairSize / 2}px`,
              bottom: `-${chairDistance + chairSize}px`,
              boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
            }}
          />
        );
      }

      // Left side
      for (let i = 0; i < shortSideChairs && chairIndex < table.capacity; i++) {
        const y = ((i + 1) * table.height) / (shortSideChairs + 1);
        chairs.push(
          <div
            key={chairIndex++}
            style={{
              position: 'absolute',
              width: `${chairSize}px`,
              height: `${chairSize}px`,
              borderRadius: '50%',
              backgroundColor: '#8B4513',
              border: '2px solid #654321',
              left: `-${chairDistance + chairSize}px`,
              top: `${y - chairSize / 2}px`,
              boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
            }}
          />
        );
      }
    }

    return chairs;
  };

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
    // Modern furniture look: wood grain or elegant color
    background: isSelected
      ? 'linear-gradient(135deg, #EBF8FF 0%, #DBEAFE 100%)'
      : 'linear-gradient(135deg, #D4A574 0%, #C19A6B 100%)',
    border: isSelected ? '3px solid #3B82F6' : '2px solid #8B6F47',
    boxShadow: isDragging
      ? '0 8px 15px rgba(0,0,0,0.3)'
      : isSelected
        ? '0 0 0 3px rgba(59, 130, 246, 0.3)'
        : '0 3px 8px rgba(0,0,0,0.25)',
    userSelect: 'none',
    transform: `${CSS.Translate.toString(transform)} rotate(${table.rotation}deg)`,
    transformOrigin: 'center',
    transition: isDragging ? 'none' : 'all 0.2s ease',
    zIndex: isDragging ? 1000 : isSelected ? 100 : 1,
    borderRadius: table.shape === 'CIRCLE' ? '50%' : '8px',
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      onClick={() => !isDragging && onClick(table)}
      className="hover:opacity-90 transition-opacity"
    >
      {/* Chairs */}
      {renderChairs()}

      {/* Table Label */}
      <div className="flex flex-col items-center pointer-events-none">
        <span className="font-bold text-sm text-gray-800">{table.table_number}</span>
        <span className="text-xs text-gray-700">
          {table.capacity} fő
        </span>
      </div>
    </div>
  );
};

export default DraggableTable;

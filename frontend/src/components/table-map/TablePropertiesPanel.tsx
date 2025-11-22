import React, { useState, useEffect } from 'react';
import type { Table } from '@/types/table';

interface TablePropertiesPanelProps {
  table: Table | null;
  onUpdate: (id: number, updates: Partial<Table>) => void;
  onDelete: (id: number) => void;
  onClose: () => void;
}

const TablePropertiesPanel: React.FC<TablePropertiesPanelProps> = ({
  table,
  onUpdate,
  onDelete,
  onClose,
}) => {
  const [tableNumber, setTableNumber] = useState('');
  const [capacity, setCapacity] = useState<number>(4);
  const [width, setWidth] = useState<number>(80);
  const [height, setHeight] = useState<number>(80);
  const [rotation, setRotation] = useState<number>(0);
  const [shape, setShape] = useState<'RECTANGLE' | 'CIRCLE'>('RECTANGLE');

  useEffect(() => {
    if (table) {
      setTableNumber(table.table_number);
      setCapacity(table.capacity || 4);
      setWidth(table.width);
      setHeight(table.height);
      setRotation(table.rotation);
      setShape(table.shape as 'RECTANGLE' | 'CIRCLE');
    }
  }, [table]);

  if (!table) return null;

  const handleUpdate = (field: keyof Table, value: any) => {
    onUpdate(table.id, { [field]: value });
  };

  return (
    <div className="w-80 bg-white border-l p-6 flex flex-col shadow-lg overflow-y-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold text-gray-800">Asztal tulajdonságok</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
        >
          ×
        </button>
      </div>

      {/* Properties Form */}
      <div className="space-y-4">
        {/* Table Number/Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Asztal Név/Szám
          </label>
          <input
            type="text"
            value={tableNumber}
            onChange={(e) => {
              setTableNumber(e.target.value);
              handleUpdate('table_number', e.target.value);
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="pl. T-12, Terasz-A"
          />
        </div>

        {/* Capacity */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Férőhely (fő)
          </label>
          <input
            type="number"
            min="1"
            max="20"
            value={capacity}
            onChange={(e) => {
              const value = parseInt(e.target.value) || 1;
              setCapacity(value);
              handleUpdate('capacity', value);
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Shape */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Forma
          </label>
          <div className="flex gap-2">
            <button
              onClick={() => {
                setShape('RECTANGLE');
                handleUpdate('shape', 'RECTANGLE');
              }}
              className={`flex-1 py-2 px-4 rounded-md border-2 transition-colors ${
                shape === 'RECTANGLE'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-300 hover:bg-gray-50'
              }`}
            >
              Téglalap
            </button>
            <button
              onClick={() => {
                setShape('CIRCLE');
                handleUpdate('shape', 'CIRCLE');
              }}
              className={`flex-1 py-2 px-4 rounded-md border-2 transition-colors ${
                shape === 'CIRCLE'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-300 hover:bg-gray-50'
              }`}
            >
              Kör
            </button>
          </div>
        </div>

        {/* Width */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Szélesség: {width}px
          </label>
          <input
            type="range"
            min="40"
            max="200"
            step="10"
            value={width}
            onChange={(e) => {
              const value = parseInt(e.target.value);
              setWidth(value);
              handleUpdate('width', value);
            }}
            className="w-full"
          />
        </div>

        {/* Height */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Magasság: {height}px
          </label>
          <input
            type="range"
            min="40"
            max="200"
            step="10"
            value={height}
            onChange={(e) => {
              const value = parseInt(e.target.value);
              setHeight(value);
              handleUpdate('height', value);
            }}
            className="w-full"
          />
        </div>

        {/* Rotation */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Forgatás: {rotation}°
          </label>
          <input
            type="range"
            min="0"
            max="360"
            step="15"
            value={rotation}
            onChange={(e) => {
              const value = parseInt(e.target.value);
              setRotation(value);
              handleUpdate('rotation', value);
            }}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0°</span>
            <span>90°</span>
            <span>180°</span>
            <span>270°</span>
            <span>360°</span>
          </div>
        </div>

        {/* Position Info (Read-only) */}
        <div className="pt-4 border-t">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Pozíció
          </label>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="bg-gray-50 px-3 py-2 rounded">
              <span className="text-gray-600">X:</span>{' '}
              <span className="font-mono">{table.x}px</span>
            </div>
            <div className="bg-gray-50 px-3 py-2 rounded">
              <span className="text-gray-600">Y:</span>{' '}
              <span className="font-mono">{table.y}px</span>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Húzd az asztalt az elrendezés megváltoztatásához
          </p>
        </div>
      </div>

      {/* Preview */}
      <div className="mt-6 pt-6 border-t">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Előnézet
        </label>
        <div className="bg-gray-100 rounded-lg p-4 flex items-center justify-center h-32">
          <div
            style={{
              width: `${Math.min(width, 100)}px`,
              height: `${Math.min(height, 100)}px`,
              transform: `rotate(${rotation}deg)`,
              borderRadius: shape === 'CIRCLE' ? '50%' : '4px',
            }}
            className="border-2 border-gray-600 bg-white flex items-center justify-center shadow-md transition-all"
          >
            <div className="text-center">
              <div className="font-bold text-xs">{tableNumber}</div>
              <div className="text-xs text-gray-500">{capacity} fő</div>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Button */}
      <div className="mt-6 pt-6 border-t">
        <button
          onClick={() => {
            if (confirm(`Biztosan törli a(z) "${tableNumber}" asztalt?`)) {
              onDelete(table.id);
              onClose();
            }
          }}
          className="w-full px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
        >
          Asztal törlése
        </button>
      </div>
    </div>
  );
};

export default TablePropertiesPanel;

/**
 * TableMap - Runtime Table Map Component
 * Module 5: Displays tables for a specific room with status colors
 *
 * Features:
 * - Loads tables from GET /rooms/{id}/tables
 * - Renders using TableIcon component (Module 3)
 * - Click handler to open order start modal
 * - Status colors: green/blue/yellow/red/grey
 * - Skeleton loading state
 */

import { useState, useEffect } from 'react';
import { TableIcon, type TableStatus } from './TableIcon';
import { Skeleton } from '@/components/ui/Skeleton';
import { getRoomTables } from '@/services/roomService';
import type { Table } from '@/types/table';
import './TableMap.css';

interface TableMapProps {
  roomId: number;
  onTableClick?: (table: Table) => void;
}

export const TableMap = ({ roomId, onTableClick }: TableMapProps) => {
  const [tables, setTables] = useState<Table[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTables();
  }, [roomId]);

  const loadTables = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getRoomTables(roomId);
      setTables(data);
    } catch (err) {
      console.error('Failed to load tables:', err);
      setError('Failed to load tables. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTableClick = (table: Table) => {
    if (onTableClick) {
      onTableClick(table);
    } else {
      // TODO: Open order start modal
      console.log('Table clicked:', table.table_number);
    }
  };

  const getTableStatus = (table: Table): TableStatus => {
    // TODO: Determine status based on active orders, reservations, etc.
    // For now, return 'available' as default
    // This will be enhanced when order system is integrated
    return 'available';
  };

  if (loading) {
    return (
      <div className="table-map-container">
        <div className="table-grid">
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton
              key={index}
              variant="rectangular"
              width={120}
              height={120}
            />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="table-map-container">
        <div className="table-map-error">
          <p>{error}</p>
          <button onClick={loadTables}>Retry</button>
        </div>
      </div>
    );
  }

  if (tables.length === 0) {
    return (
      <div className="table-map-container">
        <div className="table-map-empty">
          <p>No tables found in this room.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="table-map-container">
      <div className="table-grid">
        {tables.map((table) => (
          <TableIcon
            key={table.id}
            table={table}
            status={getTableStatus(table)}
            onClick={handleTableClick}
          />
        ))}
      </div>
    </div>
  );
};

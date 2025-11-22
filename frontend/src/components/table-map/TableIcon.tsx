/**
 * TableIcon - Egyetlen asztal komponens
 * Megjeleníti az asztalt (szám, kapacitás, státusz)
 *
 * Status colors:
 * - available (green): No active orders
 * - occupied (blue): Has active orders
 * - reserved (yellow): Reserved for future
 * - needs-cleaning (red): Needs cleaning
 * - inactive (grey): Disabled/Inactive
 */

import type { Table } from '@/types/table';
import './TableIcon.css';

export type TableStatus = 'available' | 'occupied' | 'reserved' | 'needs-cleaning' | 'inactive';

interface TableIconProps {
  table: Table;
  status?: TableStatus;
  onClick?: (table: Table) => void;
}

const STATUS_LABELS: Record<TableStatus, string> = {
  available: 'Szabad',
  occupied: 'Foglalt',
  reserved: 'Foglalva',
  'needs-cleaning': 'Takarítandó',
  inactive: 'Inaktív',
};

export const TableIcon = ({ table, status = 'available', onClick }: TableIconProps) => {
  const handleClick = () => {
    if (onClick && status !== 'inactive') {
      onClick(table);
    }
  };

  return (
    <div
      className={`table-icon ${status}`}
      onClick={handleClick}
      role="button"
      tabIndex={status === 'inactive' ? -1 : 0}
      onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      style={{ cursor: status === 'inactive' ? 'not-allowed' : 'pointer' }}
    >
      <div className="table-number">{table.table_number}</div>
      <div className="table-info">
        {table.capacity && <span className="capacity">👥 {table.capacity}</span>}
      </div>
      <div className="table-status">{STATUS_LABELS[status]}</div>
    </div>
  );
};

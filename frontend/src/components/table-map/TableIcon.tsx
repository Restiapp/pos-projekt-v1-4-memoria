/**
 * TableIcon - Egyetlen asztal komponens
 * Megjeleníti az asztalt (szám, kapacitás, státusz)
 */

import type { Table } from '@/types/table';
import './TableIcon.css';

interface TableIconProps {
  table: Table;
  occupiedSeats?: number; // Foglalt ülések száma (opcionális, később rendelések alapján)
  onClick?: (table: Table) => void;
}

export const TableIcon = ({ table, occupiedSeats = 0, onClick }: TableIconProps) => {
  const isAvailable = occupiedSeats === 0;
  const statusClass = isAvailable ? 'available' : 'occupied';

  const handleClick = () => {
    if (onClick) {
      onClick(table);
    }
  };

  return (
    <div
      className={`table-icon ${statusClass}`}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && handleClick()}
    >
      <div className="table-number">{table.table_number}</div>
      <div className="table-info">
        {table.capacity && <span className="capacity">👥 {table.capacity}</span>}
      </div>
      <div className="table-status">{isAvailable ? 'Szabad' : 'Foglalt'}</div>
    </div>
  );
};

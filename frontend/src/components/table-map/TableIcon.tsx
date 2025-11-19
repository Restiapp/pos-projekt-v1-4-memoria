/**
 * TableIcon - Egyetlen asztal komponens
 * Megjeleníti az asztalt (szám, kapacitás, státusz)
 * Frissítve: Támogatja a 4 státuszt (free, occupied, payment, cleaning)
 */

import type { Table, TableStatus } from '@/types/table';
import './TableIcon.css';

interface TableIconProps {
  table: Table;
  occupiedSeats?: number; // Foglalt ülések száma (opcionális, később rendelések alapján)
  onClick?: (table: Table) => void;
}

// Státusz címkék magyarul
const STATUS_LABELS: Record<TableStatus, string> = {
  free: 'Szabad',
  occupied: 'Foglalt',
  payment: 'Fizetés',
  cleaning: 'Takarítás',
};

export const TableIcon = ({ table, occupiedSeats = 0, onClick }: TableIconProps) => {
  // Státusz meghatározása: ha nincs explicit status, akkor occupiedSeats alapján
  const status: TableStatus = table.status || (occupiedSeats === 0 ? 'free' : 'occupied');
  const statusClass = `status-${status}`;

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
      aria-label={`Asztal ${table.table_number}, ${STATUS_LABELS[status]}, Kapacitás: ${table.capacity || 'N/A'}`}
    >
      <div className="table-number">{table.table_number}</div>
      <div className="table-info">
        {table.capacity && <span className="capacity">👥 {table.capacity}</span>}
      </div>
      <div className="table-status">{STATUS_LABELS[status]}</div>
    </div>
  );
};

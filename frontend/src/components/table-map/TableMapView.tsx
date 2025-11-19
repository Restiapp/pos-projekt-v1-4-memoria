/**
 * TableMapView - Vendégtér vizuális reprezentációja
 * Szekció választóval és állapot alapú megjelenítéssel
 * Task A9: Vendégtér UI (Asztaltérkép)
 */

import { useState } from 'react';
import { TableIcon } from './TableIcon';
import type { Table, TableSection, TableStatus } from '@/types/table';
import './TableMapView.css';

// Dummy adatok - a backend (Task A1) fejlesztése alatt
const DUMMY_TABLES: Table[] = [
  // Terasz szekció
  { id: 1, table_number: 'T1', capacity: 4, section: 'Terasz', status: 'free', position_x: 0, position_y: 0 },
  { id: 2, table_number: 'T2', capacity: 2, section: 'Terasz', status: 'occupied', position_x: 1, position_y: 0 },
  { id: 3, table_number: 'T3', capacity: 6, section: 'Terasz', status: 'payment', position_x: 2, position_y: 0 },
  { id: 4, table_number: 'T4', capacity: 4, section: 'Terasz', status: 'cleaning', position_x: 0, position_y: 1 },
  { id: 5, table_number: 'T5', capacity: 2, section: 'Terasz', status: 'free', position_x: 1, position_y: 1 },
  { id: 6, table_number: 'T6', capacity: 4, section: 'Terasz', status: 'occupied', position_x: 2, position_y: 1 },

  // Galéria szekció
  { id: 7, table_number: 'G1', capacity: 2, section: 'Galéria', status: 'free', position_x: 0, position_y: 0 },
  { id: 8, table_number: 'G2', capacity: 4, section: 'Galéria', status: 'occupied', position_x: 1, position_y: 0 },
  { id: 9, table_number: 'G3', capacity: 4, section: 'Galéria', status: 'free', position_x: 2, position_y: 0 },
  { id: 10, table_number: 'G4', capacity: 6, section: 'Galéria', status: 'payment', position_x: 0, position_y: 1 },
  { id: 11, table_number: 'G5', capacity: 2, section: 'Galéria', status: 'free', position_x: 1, position_y: 1 },

  // Kert szekció
  { id: 12, table_number: 'K1', capacity: 4, section: 'Kert', status: 'free', position_x: 0, position_y: 0 },
  { id: 13, table_number: 'K2', capacity: 8, section: 'Kert', status: 'occupied', position_x: 1, position_y: 0 },
  { id: 14, table_number: 'K3', capacity: 4, section: 'Kert', status: 'cleaning', position_x: 2, position_y: 0 },
  { id: 15, table_number: 'K4', capacity: 6, section: 'Kert', status: 'free', position_x: 0, position_y: 1 },
  { id: 16, table_number: 'K5', capacity: 4, section: 'Kert', status: 'occupied', position_x: 1, position_y: 1 },
];

// Szekciók lista
const SECTIONS: TableSection[] = ['Terasz', 'Galéria', 'Kert'];

// Státusz leírások magyarul
const STATUS_LABELS: Record<TableStatus, string> = {
  free: 'Szabad',
  occupied: 'Foglalt',
  payment: 'Fizetés alatt',
  cleaning: 'Takarítás',
};

export const TableMapView = () => {
  const [selectedSection, setSelectedSection] = useState<TableSection>('Terasz');

  // Kiválasztott szekcióhoz tartozó asztalok szűrése
  const filteredTables = DUMMY_TABLES.filter(
    (table) => table.section === selectedSection
  );

  // Asztal kattintás kezelése
  const handleTableClick = (table: Table) => {
    console.log('Asztal kiválasztva:', table);

    // Ha szabad az asztal, navigálás rendelésfelvételhez
    if (table.status === 'free') {
      console.log(`→ Navigálás rendelésfelvételre: Asztal ${table.table_number}`);
      // TODO: React Router navigáció implementálása
      // navigate(`/order/${table.id}`);
    } else {
      console.log(`→ Asztal részletek megjelenítése: ${table.table_number} (${STATUS_LABELS[table.status || 'free']})`);
      // TODO: Modal vagy oldal részletek megjelenítéséhez
    }
  };

  // Összesítő statisztikák a szekcióhoz
  const stats = {
    total: filteredTables.length,
    free: filteredTables.filter(t => t.status === 'free').length,
    occupied: filteredTables.filter(t => t.status === 'occupied').length,
    payment: filteredTables.filter(t => t.status === 'payment').length,
    cleaning: filteredTables.filter(t => t.status === 'cleaning').length,
  };

  return (
    <div className="table-map-view">
      {/* Fejléc és szekció választó */}
      <header className="map-header">
        <h1 className="map-title">Asztaltérkép</h1>

        {/* Szekció fülek */}
        <div className="section-tabs">
          {SECTIONS.map((section) => (
            <button
              key={section}
              className={`section-tab ${selectedSection === section ? 'active' : ''}`}
              onClick={() => setSelectedSection(section)}
            >
              {section}
            </button>
          ))}
        </div>

        {/* Statisztikák */}
        <div className="section-stats">
          <span className="stat stat-total">Összes: {stats.total}</span>
          <span className="stat stat-free">Szabad: {stats.free}</span>
          <span className="stat stat-occupied">Foglalt: {stats.occupied}</span>
          {stats.payment > 0 && <span className="stat stat-payment">Fizetés: {stats.payment}</span>}
          {stats.cleaning > 0 && <span className="stat stat-cleaning">Takarítás: {stats.cleaning}</span>}
        </div>
      </header>

      {/* Asztalok rács */}
      <main className="map-content">
        {filteredTables.length === 0 ? (
          <div className="empty-section">
            <p>Nincs asztal ebben a szekcióban.</p>
          </div>
        ) : (
          <div className="table-grid">
            {filteredTables.map((table) => (
              <TableIcon
                key={table.id}
                table={table}
                onClick={handleTableClick}
              />
            ))}
          </div>
        )}
      </main>

      {/* Jelmagyarázat */}
      <footer className="map-legend">
        <h3>Jelmagyarázat:</h3>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-color status-free"></span>
            <span>Szabad</span>
          </div>
          <div className="legend-item">
            <span className="legend-color status-occupied"></span>
            <span>Foglalt</span>
          </div>
          <div className="legend-item">
            <span className="legend-color status-payment"></span>
            <span>Fizetés alatt</span>
          </div>
          <div className="legend-item">
            <span className="legend-color status-cleaning"></span>
            <span>Takarításra vár</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

/**
 * TableMapPage - Asztaltérkép oldal (wrapper + header)
 * V3.0 Fázis 5: GlobalHeader integrálva
 */

import { GlobalHeader } from '@/components/layout/GlobalHeader';
import { TableMap } from '@/components/table-map/TableMap';
import './TableMapPage.css';

export const TableMapPage = () => {
  return (
    <div className="table-map-page">
      {/* Globális navigációs header */}
      <GlobalHeader currentPage="tables" />

      {/* Fő tartalom */}
      <main className="page-content">
        <TableMap />
      </main>
    </div>
  );
};

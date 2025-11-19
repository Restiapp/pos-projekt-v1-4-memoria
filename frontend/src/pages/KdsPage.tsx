/**
 * KdsPage - Konyhai Kijelző Oldal
 * V2: Feladat B2 implementáció - KdsBoard komponens használata
 * - Állomásváltó fülek
 * - Csempés nézet
 * - Valós idejű frissítés
 */

import { GlobalHeader } from '@/components/layout/GlobalHeader';
import { KdsBoard } from '@/components/kds/KdsBoard';
import './KdsPage.css';

export const KdsPage = () => {
  return (
    <div className="kds-page">
      {/* Globális navigációs header */}
      <GlobalHeader currentPage="kds" />

      {/* KDS Board komponens a füles állomásváltással */}
      <KdsBoard />
    </div>
  );
};

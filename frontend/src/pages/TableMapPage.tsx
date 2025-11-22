import { MobileAppShell } from '@/components/layout/MobileAppShell';
import { TableMap } from '@/components/table-map/TableMap';
import { RoomNavigation } from '@/components/rooms/RoomNavigation';
import { useState } from 'react';
import './TableMapPage.css';

export const TableMapPage = () => {
    // Active room ID from RoomNavigation
    const [activeRoomId, setActiveRoomId] = useState<number | null>(null);

    return (
        <MobileAppShell>
             {/* Room Switcher - Sprint 1 Module 1 */}
             <RoomNavigation
                activeRoomId={activeRoomId}
                onChange={setActiveRoomId}
             />

            {/* The actual Floor Plan Canvas */}
            <div style={{
                height: 'calc(100vh - 180px)', // Adjust for header/footer/tabs
                border: '1px solid var(--mantine-color-dark-4)',
                borderRadius: '8px',
                overflow: 'hidden',
                position: 'relative',
                marginTop: '1rem'
            }}>
                 <TableMap activeRoom={activeRoomId?.toString() ?? null} />
            </div>
        </MobileAppShell>
    );
};

import { MobileAppShell } from '@/components/layout/MobileAppShell';
import { TableMap } from '@/components/table-map/TableMap';
import { TableStatusLegend } from '@/components/table-map/TableStatusLegend';
import { Tabs } from '@mantine/core';
import { useState } from 'react';
import './TableMapPage.css';

export const TableMapPage = () => {
    // Mock Rooms for now - will come from API later
    const [activeRoom, setActiveRoom] = useState<string | null>('terasz');

    return (
        <MobileAppShell>
             {/* Room Switcher Tabs at the top of the content area */}
             <Tabs value={activeRoom} onChange={setActiveRoom} variant="pills" radius="md" mb="md">
                <Tabs.List justify="center">
                    <Tabs.Tab value="terasz">Terasz</Tabs.Tab>
                    <Tabs.Tab value="belso">Belső Terem</Tabs.Tab>
                    <Tabs.Tab value="vip">VIP Szoba</Tabs.Tab>
                </Tabs.List>
             </Tabs>

            {/* The actual Floor Plan Canvas */}
            <div style={{
                height: 'calc(100vh - 180px)', // Adjust for header/footer/tabs
                border: '1px solid var(--mantine-color-dark-4)',
                borderRadius: '8px',
                overflow: 'hidden',
                position: 'relative'
            }}>
                 <TableMap activeRoom={activeRoom} />
                 <TableStatusLegend />
            </div>
        </MobileAppShell>
    );
};

import { MobileAppShell } from '@/components/layout/MobileAppShell';
import { TableMap } from '@/components/table-map/TableMap';
import { Tabs, Alert } from '@mantine/core';
import { useState, useEffect } from 'react';
import { getRooms } from '@/services/roomService';
import { useUserRole } from '@/hooks/useUserRole';
import type { Room } from '@/types/room';
import './TableMapPage.css';

export const TableMapPage = () => {
    const { filterRoomsByRole, getDefaultRoom, isAdmin } = useUserRole();
    const [rooms, setRooms] = useState<Room[]>([]);
    const [filteredRooms, setFilteredRooms] = useState<Room[]>([]);
    const [activeRoom, setActiveRoom] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch rooms from API on mount
    useEffect(() => {
        const fetchRooms = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const data = await getRooms();
                console.log('[TableMapPage] Rooms fetched:', data);
                setRooms(data);

                // Filter rooms based on user role
                const filtered = filterRoomsByRole(data);
                console.log('[TableMapPage] Filtered rooms:', filtered);
                setFilteredRooms(filtered);

                // Set default active room
                if (filtered.length > 0) {
                    // Try to use the role's default room if it exists in filtered rooms
                    const defaultRoomIdentifier = getDefaultRoom();
                    const defaultRoom = filtered.find(
                        (room) => room.name.toLowerCase().includes(defaultRoomIdentifier || '')
                    );
                    setActiveRoom(defaultRoom ? String(defaultRoom.id) : String(filtered[0].id));
                }
            } catch (err) {
                console.error('[TableMapPage] Error fetching rooms:', err);
                setError('Hiba történt a termek betöltésekor.');
            } finally {
                setIsLoading(false);
            }
        };

        fetchRooms();
    }, [filterRoomsByRole, getDefaultRoom]);

    if (isLoading) {
        return (
            <MobileAppShell>
                <div className="flex items-center justify-center h-96">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                        <p className="text-gray-600">Termek betöltése...</p>
                    </div>
                </div>
            </MobileAppShell>
        );
    }

    if (error) {
        return (
            <MobileAppShell>
                <Alert color="red" title="Hiba">
                    {error}
                </Alert>
            </MobileAppShell>
        );
    }

    if (filteredRooms.length === 0) {
        return (
            <MobileAppShell>
                <Alert color="yellow" title="Nincs elérhető terem">
                    Nincs olyan terem, amelyhez hozzáféréssel rendelkezel.
                </Alert>
            </MobileAppShell>
        );
    }

    return (
        <MobileAppShell>
             {/* Room Switcher Tabs - Only show rooms user has access to */}
             <Tabs value={activeRoom} onChange={setActiveRoom} variant="pills" radius="md" mb="md">
                <Tabs.List justify="center">
                    {filteredRooms.map((room) => (
                        <Tabs.Tab key={room.id} value={String(room.id)}>
                            {room.name}
                        </Tabs.Tab>
                    ))}
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
            </div>
        </MobileAppShell>
    );
};

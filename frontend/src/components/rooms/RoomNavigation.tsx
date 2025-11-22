/**
 * RoomNavigation - Top navigation bar for room selection
 * Sprint 1 - Module 1
 *
 * Features:
 * - Fetches rooms from API (GET /rooms)
 * - Renders tabs using Mantine Tabs component
 * - Highlights active room
 * - Emits onChange(room_id) callback
 * - Supports role-based filtering (bar/waiter/dispatcher)
 * - Skeleton loaders during fetch
 * - Error toast on API failure
 */

import { useEffect, useState } from 'react';
import { Tabs, Skeleton, Box } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { useAuth } from '@/hooks/useAuth';
import { getRooms } from '@/services/roomService';
import type { Room } from '@/types/room';

interface RoomNavigationProps {
  /** Currently active room ID */
  activeRoomId?: number | null;
  /** Callback when room is changed */
  onChange?: (roomId: number) => void;
  /** Optional className for custom styling */
  className?: string;
}

/**
 * Role-based room filtering configuration
 * Maps role names to allowed room names/types
 */
const ROLE_ROOM_FILTERS: Record<string, string[]> = {
  bar: ['BAR', 'Bar Counter'],
  waiter: ['Guest Area', 'Terrace'],
  dispatcher: ['VIP', 'Delivery'],
  // admin sees all rooms (no filter)
};

export const RoomNavigation = ({
  activeRoomId,
  onChange,
  className = '',
}: RoomNavigationProps) => {
  const { user, hasRole } = useAuth();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRooms = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getRooms();

        // Apply role-based filtering
        let filteredRooms = data;

        if (user && !hasRole('admin')) {
          // Check which filter applies to this user
          for (const [roleName, allowedRooms] of Object.entries(ROLE_ROOM_FILTERS)) {
            if (hasRole(roleName)) {
              filteredRooms = data.filter((room) =>
                allowedRooms.some((allowed) =>
                  room.name.toLowerCase().includes(allowed.toLowerCase())
                )
              );
              break;
            }
          }
        }

        setRooms(filteredRooms);

        // Auto-select first room if none selected and onChange is provided
        if (filteredRooms.length > 0 && !activeRoomId && onChange) {
          onChange(filteredRooms[0].id);
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load rooms';
        setError(errorMessage);

        notifications.show({
          title: 'Error',
          message: 'Failed to load rooms. Please try again.',
          color: 'red',
          autoClose: 5000,
        });

        console.error('Error fetching rooms:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRooms();
  }, [user, hasRole, activeRoomId, onChange]);

  const handleTabChange = (value: string | null) => {
    if (value && onChange) {
      const roomId = parseInt(value, 10);
      if (!isNaN(roomId)) {
        onChange(roomId);
      }
    }
  };

  // Loading state with skeleton
  if (loading) {
    return (
      <Box className={className} style={{ padding: '0.5rem 1rem' }}>
        <Skeleton height={40} width="100%" radius="md" />
      </Box>
    );
  }

  // Error state (still show component but with error logged)
  if (error || rooms.length === 0) {
    return (
      <Box className={className} style={{ padding: '0.5rem 1rem', color: '#888' }}>
        {error ? 'Error loading rooms' : 'No rooms available'}
      </Box>
    );
  }

  // Main render with Mantine Tabs
  return (
    <Tabs
      value={activeRoomId?.toString() ?? null}
      onChange={handleTabChange}
      className={className}
      variant="default"
      style={{
        borderBottom: '1px solid var(--mantine-color-dark-4)',
      }}
    >
      <Tabs.List>
        {rooms.map((room) => (
          <Tabs.Tab
            key={room.id}
            value={room.id.toString()}
            style={{
              fontSize: '0.95rem',
              fontWeight: 500,
              padding: '0.75rem 1.5rem',
            }}
          >
            {room.name}
          </Tabs.Tab>
        ))}
      </Tabs.List>
    </Tabs>
  );
};

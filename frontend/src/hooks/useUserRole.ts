/**
 * useUserRole Hook - Role-based UI filtering and navigation
 *
 * Provides utilities for:
 * - Role detection (bar, waiter, dispatcher, admin)
 * - Default route per role
 * - Room filtering based on role
 */

import { useAuth } from './useAuth';

// Role constants
export const ROLES = {
  ADMIN: 'admin',
  BAR: 'bar',
  WAITER: 'waiter',
  DISPATCHER: 'dispatcher',
  KITCHEN: 'kitchen',
} as const;

// Room identifiers (match backend room names/types)
export const ROOMS = {
  BAR_COUNTER: 'bar',
  GUEST_AREA: 'guest', // streetfood + á la carte merged
  TERRACE_SMOKING: 'terrace_smoking',
  TERRACE_NON_SMOKING: 'terrace_non_smoking',
  VIP: 'vip',
  DELIVERY: 'delivery',
} as const;

// Default routes per role
const ROLE_DEFAULT_ROUTES: Record<string, string> = {
  [ROLES.BAR]: '/tables', // Will filter to BAR counter
  [ROLES.WAITER]: '/tables', // Will filter to Guest Area
  [ROLES.DISPATCHER]: '/tables', // Will filter to VIP + Delivery
  [ROLES.ADMIN]: '/admin', // Access to all rooms
  [ROLES.KITCHEN]: '/kds', // Kitchen Display System
};

// Room access mapping per role
const ROLE_ROOM_ACCESS: Record<string, string[]> = {
  [ROLES.BAR]: [ROOMS.BAR_COUNTER],
  [ROLES.WAITER]: [ROOMS.GUEST_AREA, ROOMS.TERRACE_SMOKING, ROOMS.TERRACE_NON_SMOKING],
  [ROLES.DISPATCHER]: [ROOMS.VIP, ROOMS.DELIVERY],
  [ROLES.ADMIN]: Object.values(ROOMS), // All rooms
};

export const useUserRole = () => {
  const { user, hasRole } = useAuth();

  /**
   * Get the primary role of the user
   * Returns the first role or null if no roles
   */
  const getPrimaryRole = (): string | null => {
    if (!user || !user.roles || user.roles.length === 0) {
      return null;
    }
    return user.roles[0].name;
  };

  /**
   * Check if user has a specific role
   */
  const isRole = (roleName: string): boolean => {
    return hasRole(roleName);
  };

  /**
   * Role-specific checks
   */
  const isBar = () => isRole(ROLES.BAR);
  const isWaiter = () => isRole(ROLES.WAITER);
  const isDispatcher = () => isRole(ROLES.DISPATCHER);
  const isAdmin = () => isRole(ROLES.ADMIN);
  const isKitchen = () => isRole(ROLES.KITCHEN);

  /**
   * Get default route for the user's primary role
   * Falls back to /tables if role not found
   */
  const getDefaultRoute = (): string => {
    const primaryRole = getPrimaryRole();
    if (!primaryRole) {
      return '/tables';
    }
    return ROLE_DEFAULT_ROUTES[primaryRole] || '/tables';
  };

  /**
   * Get allowed room identifiers for the user's role(s)
   * Returns all rooms for admin, specific rooms for other roles
   */
  const getAllowedRooms = (): string[] => {
    if (!user || !user.roles || user.roles.length === 0) {
      return [];
    }

    // Admin gets all rooms
    if (isAdmin()) {
      return Object.values(ROOMS);
    }

    // Collect all allowed rooms from all user roles
    const allowedRooms = new Set<string>();
    user.roles.forEach((role) => {
      const rooms = ROLE_ROOM_ACCESS[role.name] || [];
      rooms.forEach((room) => allowedRooms.add(room));
    });

    return Array.from(allowedRooms);
  };

  /**
   * Check if user can access a specific room
   */
  const canAccessRoom = (roomIdentifier: string): boolean => {
    const allowedRooms = getAllowedRooms();
    return allowedRooms.includes(roomIdentifier);
  };

  /**
   * Filter rooms based on user's role
   * This can be used to filter a list of rooms from the API
   */
  const filterRoomsByRole = <T extends { name: string; type?: string }>(
    rooms: T[]
  ): T[] => {
    if (!user || isAdmin()) {
      return rooms; // Admin sees all rooms
    }

    const allowedRooms = getAllowedRooms();
    return rooms.filter((room) => {
      // Match by room name (case-insensitive) or type
      const roomIdentifier = room.name.toLowerCase();
      return allowedRooms.some(
        (allowed) => roomIdentifier.includes(allowed) || room.type === allowed
      );
    });
  };

  /**
   * Get the default room for the user's role
   * Returns the first allowed room or null
   */
  const getDefaultRoom = (): string | null => {
    const allowedRooms = getAllowedRooms();
    return allowedRooms.length > 0 ? allowedRooms[0] : null;
  };

  return {
    // Role detection
    getPrimaryRole,
    isRole,
    isBar,
    isWaiter,
    isDispatcher,
    isAdmin,
    isKitchen,

    // Navigation
    getDefaultRoute,
    getDefaultRoom,

    // Room filtering
    getAllowedRooms,
    canAccessRoom,
    filterRoomsByRole,

    // Constants
    ROLES,
    ROOMS,
  };
};

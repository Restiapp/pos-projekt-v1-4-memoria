# Role-Based UI Filtering - Documentation

## Overview

The POS system implements a comprehensive role-based UI filtering system that controls:
1. **Default navigation** - Users are redirected to their role-specific default page
2. **Room visibility** - Users only see rooms they have access to
3. **Route protection** - Routes are protected by role and permission checks

## Architecture

### Components

#### 1. `useUserRole()` Hook
Location: `frontend/src/hooks/useUserRole.ts`

A custom hook that provides role-based utilities:

```typescript
const {
  // Role detection
  getPrimaryRole,    // Get user's primary role
  isRole,            // Check if user has a specific role
  isBar,             // Check if user is a bartender
  isWaiter,          // Check if user is a waiter
  isDispatcher,      // Check if user is a dispatcher
  isAdmin,           // Check if user is an admin
  isKitchen,         // Check if user is kitchen staff

  // Navigation
  getDefaultRoute,   // Get default route for user's role
  getDefaultRoom,    // Get default room for user's role

  // Room filtering
  getAllowedRooms,   // Get list of allowed room identifiers
  canAccessRoom,     // Check if user can access a specific room
  filterRoomsByRole, // Filter array of rooms based on user's role

  // Constants
  ROLES,             // Role constants (ADMIN, BAR, WAITER, etc.)
  ROOMS,             // Room identifier constants
} = useUserRole();
```

#### 2. `RoleBasedRedirect` Component
Location: `frontend/src/components/auth/RoleBasedRedirect.tsx`

A component that redirects users to their default route based on their role.

Usage:
```typescript
<Route path="/" element={<RoleBasedRedirect />} />
```

#### 3. Enhanced `ProtectedRoute` Component
Location: `frontend/src/components/auth/ProtectedRoute.tsx`

The ProtectedRoute component now supports three types of access control:

```typescript
// Permission-based (existing)
<ProtectedRoute requiredPermission="orders:manage">
  <OrdersPage />
</ProtectedRoute>

// Role-based (new) - exact role match
<ProtectedRoute requiredRole="admin">
  <AdminDashboard />
</ProtectedRoute>

// Role-based (new) - any of the allowed roles
<ProtectedRoute allowedRoles={["admin", "waiter"]}>
  <TablesPage />
</ProtectedRoute>
```

## Role Configuration

### Role Constants
Defined in `useUserRole.ts`:

```typescript
export const ROLES = {
  ADMIN: 'admin',
  BAR: 'bar',
  WAITER: 'waiter',
  DISPATCHER: 'dispatcher',
  KITCHEN: 'kitchen',
} as const;
```

### Room Access Mapping

Each role has access to specific rooms:

| Role        | Allowed Rooms                                           | Default Route |
|-------------|--------------------------------------------------------|---------------|
| `bar`       | BAR counter only                                       | `/tables`     |
| `waiter`    | Guest Area, Terrace (smoking), Terrace (non-smoking) | `/tables`     |
| `dispatcher`| VIP, Delivery                                          | `/tables`     |
| `admin`     | All rooms                                              | `/admin`      |
| `kitchen`   | N/A (KDS only)                                        | `/kds`        |

### Room Identifiers

```typescript
export const ROOMS = {
  BAR_COUNTER: 'bar',
  GUEST_AREA: 'guest',
  TERRACE_SMOKING: 'terrace_smoking',
  TERRACE_NON_SMOKING: 'terrace_non_smoking',
  VIP: 'vip',
  DELIVERY: 'delivery',
} as const;
```

## Usage Examples

### Example 1: Filter Rooms in a Component

```typescript
import { useUserRole } from '@/hooks/useUserRole';
import { getRooms } from '@/services/roomService';

const MyComponent = () => {
  const { filterRoomsByRole } = useUserRole();
  const [rooms, setRooms] = useState([]);

  useEffect(() => {
    const fetchRooms = async () => {
      const allRooms = await getRooms();
      const filteredRooms = filterRoomsByRole(allRooms);
      setRooms(filteredRooms);
    };
    fetchRooms();
  }, []);

  return (
    <div>
      {rooms.map(room => (
        <RoomTab key={room.id} room={room} />
      ))}
    </div>
  );
};
```

### Example 2: Check Access to a Specific Room

```typescript
import { useUserRole } from '@/hooks/useUserRole';

const RoomSelector = ({ roomId }) => {
  const { canAccessRoom, ROOMS } = useUserRole();

  if (!canAccessRoom(ROOMS.VIP)) {
    return <div>No access to VIP room</div>;
  }

  return <div>Welcome to VIP</div>;
};
```

### Example 3: Conditional Rendering Based on Role

```typescript
import { useUserRole } from '@/hooks/useUserRole';

const Navigation = () => {
  const { isAdmin, isWaiter } = useUserRole();

  return (
    <nav>
      {isAdmin() && <Link to="/admin">Admin Dashboard</Link>}
      {isWaiter() && <Link to="/tables">Tables</Link>}
    </nav>
  );
};
```

### Example 4: Protect Routes with Roles

```typescript
// In App.tsx
<Route
  path="/admin"
  element={
    <ProtectedRoute requiredRole="admin">
      <AdminPage />
    </ProtectedRoute>
  }
/>

// Multiple roles allowed
<Route
  path="/tables"
  element={
    <ProtectedRoute allowedRoles={["admin", "waiter", "bar"]}>
      <TableMapPage />
    </ProtectedRoute>
  }
/>
```

## Implementation in TableMapPage

The `TableMapPage` component demonstrates the complete implementation:

1. **Fetch all rooms** from the API
2. **Filter rooms** based on user's role
3. **Set default active room** based on user's role
4. **Display only allowed rooms** in the tab navigation

```typescript
const { filterRoomsByRole, getDefaultRoom } = useUserRole();

useEffect(() => {
  const fetchRooms = async () => {
    const data = await getRooms();
    const filtered = filterRoomsByRole(data);
    setFilteredRooms(filtered);

    // Set default active room
    if (filtered.length > 0) {
      const defaultRoomIdentifier = getDefaultRoom();
      const defaultRoom = filtered.find(
        (room) => room.name.toLowerCase().includes(defaultRoomIdentifier || '')
      );
      setActiveRoom(defaultRoom ? String(defaultRoom.id) : String(filtered[0].id));
    }
  };
  fetchRooms();
}, []);
```

## Backend Integration

### User Role Response

The backend must return roles in the user object:

```json
{
  "id": 1,
  "username": "john_waiter",
  "name": "John Doe",
  "roles": [
    {
      "id": 2,
      "name": "waiter",
      "description": "Waiter role"
    }
  ],
  "permissions": ["orders:view", "orders:create"]
}
```

### Room Response

Rooms should be returned with identifiable names or types:

```json
[
  {
    "id": 1,
    "name": "Bar Counter",
    "type": "indoor",
    "width": 800,
    "height": 600
  },
  {
    "id": 2,
    "name": "Guest Area",
    "type": "indoor",
    "width": 1200,
    "height": 800
  }
]
```

## Testing

### Manual Testing Checklist

1. **Login as different roles** and verify:
   - [ ] Default redirect goes to correct page
   - [ ] Only allowed rooms are visible in TableMapPage
   - [ ] Unauthorized routes redirect to /unauthorized

2. **Role-specific tests**:
   - [ ] Bar role: See only BAR counter
   - [ ] Waiter role: See Guest Area and Terrace rooms
   - [ ] Dispatcher role: See VIP and Delivery rooms
   - [ ] Admin role: See all rooms
   - [ ] Kitchen role: Redirected to /kds

3. **Navigation tests**:
   - [ ] Direct access to unauthorized routes redirects properly
   - [ ] Role-based redirect on login works correctly

## Security Considerations

1. **Backend validation**: Always validate roles and permissions on the backend. Frontend filtering is for UX only.
2. **API protection**: Ensure all API endpoints check user roles/permissions server-side.
3. **Token validation**: Frontend role checks rely on the JWT token, which should be validated by the backend.

## Future Enhancements

1. **Dynamic role configuration**: Load role-room mappings from backend
2. **Role hierarchy**: Support parent-child role relationships
3. **Time-based access**: Roles with time restrictions (e.g., night shift)
4. **Multi-tenant support**: Different role configurations per restaurant location

## Troubleshooting

### Issue: User sees all rooms despite role restrictions

**Solution**: Check that:
1. User roles are correctly set in the backend
2. Room names match the identifiers in `ROOMS` constants
3. `filterRoomsByRole` is being called with the correct data

### Issue: Default redirect doesn't work

**Solution**: Verify:
1. `RoleBasedRedirect` is used in App.tsx for "/" route
2. User has a valid role in their profile
3. Auth state is loaded before redirect (check `isLoading`)

### Issue: Protected routes allow unauthorized access

**Solution**: Ensure:
1. `ProtectedRoute` is wrapping the component
2. `requiredRole` or `allowedRoles` prop is set correctly
3. User has the required role in their profile

## Contact

For questions or issues with role-based filtering:
- Check the codebase documentation
- Review existing implementations in `TableMapPage.tsx`
- Consult the `useUserRole.ts` hook for available utilities

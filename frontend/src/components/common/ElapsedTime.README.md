# ElapsedTime Component

## Overview
A reusable React component that displays the elapsed time since a given timestamp with automatic updates and color-coded visual feedback.

## Features
- **Auto-refresh**: Updates every 1 second
- **Color-coded display**:
  - **Gray**: < 10 minutes (normal)
  - **Yellow**: 10-20 minutes (attention needed)
  - **Red**: > 20 minutes (urgent)
- **Hungarian format**: "X perc / Y másodperce"

## Usage

### Basic Example
```tsx
import { ElapsedTime } from '@/components/common/ElapsedTime';

function MyComponent() {
  const orderTimestamp = "2025-11-22T10:30:00Z";

  return (
    <div>
      <ElapsedTime timestamp={orderTimestamp} />
    </div>
  );
}
```

### With Custom Styling
```tsx
<ElapsedTime
  timestamp={order.created_at}
  className="my-custom-class"
/>
```

## Integration Examples

### DrinkKdsQueue Component (Future)
```tsx
export const DrinkKdsQueue = () => {
  const [drinkOrders, setDrinkOrders] = useState<Order[]>([]);

  return (
    <div className="drink-kds-queue">
      {drinkOrders.map(order => (
        <div key={order.id} className="drink-order-card">
          <h3>{order.product_name}</h3>
          <ElapsedTime timestamp={order.created_at} />
        </div>
      ))}
    </div>
  );
};
```

### BarCounterOrders Component (Future)
```tsx
export const BarCounterOrders = () => {
  const [barOrders, setBarOrders] = useState<Order[]>([]);

  return (
    <div className="bar-counter-orders">
      {barOrders.map(order => (
        <div key={order.id} className="bar-order">
          <div className="order-header">
            <span>Rendelés #{order.id}</span>
            <ElapsedTime timestamp={order.created_at} />
          </div>
          <div className="order-items">
            {/* Order items */}
          </div>
        </div>
      ))}
    </div>
  );
};
```

### TakeawayOrders Component (Future)
```tsx
export const TakeawayOrders = () => {
  const [takeawayOrders, setTakeawayOrders] = useState<Order[]>([]);

  return (
    <div className="takeaway-orders">
      {takeawayOrders.map(order => (
        <div key={order.id} className="takeaway-order-card">
          <div className="order-info">
            <span className="customer-name">{order.customer_name}</span>
            <ElapsedTime timestamp={order.created_at} />
          </div>
          <div className="order-status">
            {order.status}
          </div>
        </div>
      ))}
    </div>
  );
};
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `timestamp` | `string` | Yes | ISO datetime string (e.g., "2025-11-22T10:30:00Z") |
| `className` | `string` | No | Additional CSS class names |

## Color Thresholds

The component automatically applies color classes based on elapsed time:

- **0-9 minutes**: `.elapsed-time-gray` - Subtle gray background
- **10-19 minutes**: `.elapsed-time-yellow` - Yellow background with warning color
- **20+ minutes**: `.elapsed-time-red` - Red background with pulsing animation

## Styling

The component uses CSS classes that can be customized in `ElapsedTime.css`:
- `.elapsed-time` - Base styles
- `.elapsed-time-gray` - Normal state
- `.elapsed-time-yellow` - Attention state
- `.elapsed-time-red` - Urgent state with pulse animation

## Performance

- Uses React hooks (`useState`, `useEffect`) for efficient updates
- Automatically cleans up intervals on component unmount
- Minimal re-renders (only updates the elapsed time state)

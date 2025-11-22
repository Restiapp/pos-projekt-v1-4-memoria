# StartOrderModal Component

Modal component for starting a new order with sequence number management.

## Features

- ✅ Manual sequence number input
- ✅ Auto-generate sequence number via API (`POST /order-sequence/next`)
- ✅ Continue button to create order with sequence
- ✅ Cancel button to close modal
- ✅ Form validation
- ✅ Loading states
- ✅ Toast notifications
- ✅ Keyboard support (Enter to submit)
- ✅ Responsive design

## Usage

```tsx
import { useState } from 'react';
import { StartOrderModal } from '@/components/orders/StartOrderModal';

function MyComponent() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleStartOrder = (orderData: { sequence_number: number }) => {
    console.log('Starting order with sequence:', orderData.sequence_number);

    // TODO: Create the order with the sequence number
    // Example:
    // const newOrder = await createOrder({
    //   sequence_number: orderData.sequence_number,
    //   order_type: 'Helyben',
    //   // ... other order fields
    // });

    setIsModalOpen(false);
  };

  return (
    <div>
      <button onClick={() => setIsModalOpen(true)}>
        Start New Order
      </button>

      <StartOrderModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onStart={handleStartOrder}
      />
    </div>
  );
}
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `isOpen` | `boolean` | Yes | Controls modal visibility |
| `onClose` | `() => void` | Yes | Callback when modal is closed |
| `onStart` | `(orderData: { sequence_number: number }) => void` | Yes | Callback when user clicks Continue with valid sequence number |

## API Integration

The component calls the following API endpoint:

- `POST /api/order-sequence/next` - Generate next order sequence number
  - Response: `{ sequence_number: number }`

This endpoint is proxied through Vite to `http://localhost:8002/api/v1/order-sequence/next`

## Backend Requirements

The backend service (service_orders) must implement the following endpoint:

```python
@router.post("/order-sequence/next")
async def get_next_order_sequence():
    """Generate and return the next order sequence number"""
    # Implementation details:
    # - Maintain a counter in the database
    # - Ensure thread-safe increment
    # - Return the new sequence number
    return {"sequence_number": next_seq}
```

## Validation

- Sequence number must be a positive integer
- Empty input shows error toast
- Invalid input (negative, zero, non-numeric) shows error toast

## Accessibility

- Full keyboard navigation support
- ESC key closes modal
- Enter key submits form
- Proper ARIA labels
- Focus management

## Styling

The component uses `StartOrderModal.css` for styling. All styles are scoped to the component and follow the existing design system.

## Dependencies

- `@/components/ui/Modal` - Base modal component
- `@/hooks/useToast` - Toast notifications
- `@/services/orderService` - API service for order operations

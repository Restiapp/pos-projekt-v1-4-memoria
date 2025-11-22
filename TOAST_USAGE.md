# Toast Notification System - Usage Guide

Complete implementation of a toast notification system with TypeScript support, multiple variants, auto-dismiss, and smooth animations.

## 📁 Files Created

- `frontend/src/components/ui/Toast.tsx` - Individual toast component
- `frontend/src/components/ui/Toast.css` - Toast component styles
- `frontend/src/components/ui/ToastProvider.tsx` - Toast provider/container
- `frontend/src/components/ui/ToastProvider.css` - Toast container styles
- `frontend/src/hooks/useToast.ts` - Hook to trigger toasts

## 🚀 Setup

### 1. Wrap your application with ToastProvider

Update `frontend/src/main.tsx`:

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { ToastProvider } from '@/components/ui/ToastProvider';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ToastProvider>
      <App />
    </ToastProvider>
  </React.StrictMode>
);
```

## 📖 Basic Usage

### Import the hook

```tsx
import { useToast } from '@/hooks/useToast';
```

### Use in your components

```tsx
function MyComponent() {
  const toast = useToast();

  const handleSuccess = () => {
    toast.success('Operation completed successfully!');
  };

  const handleError = () => {
    toast.error('Something went wrong!');
  };

  const handleWarning = () => {
    toast.warning('Please check your input');
  };

  const handleInfo = () => {
    toast.info('New features available');
  };

  return (
    <div>
      <button onClick={handleSuccess}>Show Success</button>
      <button onClick={handleError}>Show Error</button>
      <button onClick={handleWarning}>Show Warning</button>
      <button onClick={handleInfo}>Show Info</button>
    </div>
  );
}
```

## 🎨 Features

### ✅ Variants

- **success** - Green theme for successful operations
- **error** - Red theme for errors and failures
- **warning** - Orange theme for warnings
- **info** - Blue theme for informational messages

### ⏱️ Auto-dismiss

- Default: 4 seconds
- Customizable per toast
- Smooth exit animation

### 📚 Queue Management

- Multiple toasts stack vertically
- New toasts appear at the bottom
- Auto-removes after duration

### 📍 Position

- Fixed at top-right
- Responsive on mobile (full-width)
- High z-index (9999) to stay on top

### ✨ Animations

- Smooth slide-in from right (300ms)
- Smooth slide-out to right (300ms)
- CSS-based animations for performance

### 🔒 TypeScript

- Full type safety
- IntelliSense support
- Type-safe variant names

## 🔧 Advanced Usage

### Custom Duration

```tsx
const toast = useToast();

// Show for 2 seconds instead of default 4
toast.success('Quick message!', 2000);

// Show for 8 seconds
toast.error('Important error message', 8000);
```

### Real-world Examples

#### Form Submission

```tsx
function FormComponent() {
  const toast = useToast();

  const handleSubmit = async (data: FormData) => {
    try {
      await submitForm(data);
      toast.success('Form submitted successfully!');
    } catch (error) {
      toast.error('Failed to submit form. Please try again.');
    }
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

#### API Calls

```tsx
function DataComponent() {
  const toast = useToast();

  const fetchData = async () => {
    try {
      const response = await api.getData();
      toast.success('Data loaded successfully');
      return response;
    } catch (error) {
      toast.error('Failed to load data');
      throw error;
    }
  };

  return <button onClick={fetchData}>Load Data</button>;
}
```

#### Delete Confirmation

```tsx
function DeleteButton({ itemId }: { itemId: string }) {
  const toast = useToast();

  const handleDelete = async () => {
    try {
      await deleteItem(itemId);
      toast.success('Item deleted successfully');
    } catch (error) {
      toast.error('Failed to delete item');
    }
  };

  return <button onClick={handleDelete}>Delete</button>;
}
```

#### Input Validation

```tsx
function InputComponent() {
  const toast = useToast();

  const handleValidation = (value: string) => {
    if (value.length < 3) {
      toast.warning('Input must be at least 3 characters');
      return false;
    }
    return true;
  };

  return <input onBlur={(e) => handleValidation(e.target.value)} />;
}
```

#### Information Updates

```tsx
function NotificationComponent() {
  const toast = useToast();

  useEffect(() => {
    const unsubscribe = subscribeToUpdates((message) => {
      toast.info(message);
    });

    return () => unsubscribe();
  }, []);

  return null;
}
```

## 🎯 API Reference

### `useToast()` Hook

Returns an object with the following methods:

#### `success(message: string, duration?: number): void`

Shows a success toast (green theme).

#### `error(message: string, duration?: number): void`

Shows an error toast (red theme).

#### `warning(message: string, duration?: number): void`

Shows a warning toast (orange theme).

#### `info(message: string, duration?: number): void`

Shows an info toast (blue theme).

#### `addToast(message: string, variant: ToastVariant, duration?: number): void`

Generic method to add any toast.

#### `removeToast(id: string): void`

Manually remove a toast by ID.

### TypeScript Types

```typescript
type ToastVariant = 'success' | 'error' | 'warning' | 'info';

interface ToastData {
  id: string;
  message: string;
  variant: ToastVariant;
  duration?: number;
}

interface ToastContextValue {
  addToast: (message: string, variant: ToastVariant, duration?: number) => void;
  removeToast: (id: string) => void;
  success: (message: string, duration?: number) => void;
  error: (message: string, duration?: number) => void;
  warning: (message: string, duration?: number) => void;
  info: (message: string, duration?: number) => void;
}
```

## 🎨 Customization

### Modify Colors

Edit `frontend/src/components/ui/Toast.css`:

```css
/* Change success color */
.toast-success {
  border-left: 4px solid #your-color;
}

.toast-success .toast-icon-wrapper {
  color: #your-color;
}
```

### Modify Position

Edit `frontend/src/components/ui/ToastProvider.css`:

```css
/* Change to top-left */
.toast-container {
  top: 1rem;
  left: 1rem; /* changed from right */
  align-items: flex-start; /* changed from flex-end */
}
```

### Modify Duration

Change default in `ToastProvider.tsx`:

```typescript
const addToast = useCallback((message: string, variant: ToastVariant, duration = 6000) => {
  // Changed from 4000 to 6000
  // ...
});
```

## 📱 Responsive Behavior

- **Desktop**: Fixed width (300-500px) at top-right
- **Mobile**: Full width with side margins (0.5rem)

## ♿ Accessibility

- `role="alert"` on toast elements
- `aria-label` on close button
- Keyboard accessible close button
- High contrast icon colors

## 🔍 Browser Support

Works in all modern browsers:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## 📝 Notes

- Toasts auto-dismiss after 4 seconds by default
- Multiple toasts queue vertically
- Toasts can be manually closed by clicking the X button
- Maximum stack is unlimited (adjust CSS if needed)
- Each toast has a unique ID for tracking

## 🐛 Troubleshooting

### Toast not appearing?

1. Ensure `ToastProvider` wraps your app in `main.tsx`
2. Check that you're calling `useToast()` inside a component
3. Verify CSS files are imported

### TypeScript errors?

1. Ensure `@/` path alias is configured in `tsconfig.json`
2. Check that all imports use the correct paths

### Styling issues?

1. Check that CSS files are imported in the component files
2. Verify z-index isn't being overridden by other elements
3. Check browser console for CSS loading errors

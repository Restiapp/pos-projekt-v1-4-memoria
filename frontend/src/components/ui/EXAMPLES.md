# Modal & ConfirmDialog - Usage Examples

## Modal Component

### Basic Modal

```tsx
import { useState } from 'react';
import { Modal } from '@/components/ui';

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsOpen(true)}>Open Modal</button>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="My Modal Title"
      >
        <p>This is the modal content.</p>
        <button onClick={() => setIsOpen(false)}>Close</button>
      </Modal>
    </>
  );
}
```

### Modal with Custom Width

```tsx
<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Wide Modal"
  maxWidth="800px"
>
  <p>This modal has a custom max-width.</p>
</Modal>
```

### Modal without Close Button

```tsx
<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="No Close Button"
  showCloseButton={false}
  closeOnOverlayClick={false}
  closeOnEsc={false}
>
  <p>This modal can only be closed programmatically.</p>
  <button onClick={() => setIsOpen(false)}>Done</button>
</Modal>
```

### Modal with Custom ARIA Labels

```tsx
<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  ariaLabelledBy="custom-title"
  ariaDescribedBy="custom-description"
  showCloseButton={true}
>
  <h2 id="custom-title">Custom Title</h2>
  <p id="custom-description">Custom description for screen readers.</p>
</Modal>
```

## ConfirmDialog Component

### Basic Confirmation Dialog

```tsx
import { useState } from 'react';
import { ConfirmDialog } from '@/components/ui';

function DeleteButton() {
  const [showConfirm, setShowConfirm] = useState(false);

  const handleDelete = () => {
    console.log('Item deleted!');
    // Perform delete operation
  };

  return (
    <>
      <button onClick={() => setShowConfirm(true)}>Delete Item</button>

      <ConfirmDialog
        isOpen={showConfirm}
        onClose={() => setShowConfirm(false)}
        onConfirm={handleDelete}
        title="Delete Item?"
        description="Are you sure you want to delete this item? This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        confirmVariant="danger"
      />
    </>
  );
}
```

### Success Confirmation

```tsx
<ConfirmDialog
  isOpen={showConfirm}
  onClose={() => setShowConfirm(false)}
  onConfirm={handleSubmit}
  title="Submit Order?"
  description="Your order is ready to be submitted. Continue?"
  confirmLabel="Submit Order"
  cancelLabel="Go Back"
  confirmVariant="success"
/>
```

### With Processing State

```tsx
import { useState } from 'react';
import { ConfirmDialog } from '@/components/ui';

function SaveButton() {
  const [showConfirm, setShowConfirm] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSave = async () => {
    setIsProcessing(true);
    try {
      await saveData();
      setShowConfirm(false);
    } catch (error) {
      console.error(error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <>
      <button onClick={() => setShowConfirm(true)}>Save Changes</button>

      <ConfirmDialog
        isOpen={showConfirm}
        onClose={() => setShowConfirm(false)}
        onConfirm={handleSave}
        title="Save Changes?"
        description="Do you want to save your changes?"
        confirmLabel="Save"
        cancelLabel="Cancel"
        confirmVariant="primary"
        isProcessing={isProcessing}
      />
    </>
  );
}
```

## Replacing window.confirm()

### Before (Blocking Browser Dialog)

```tsx
const handleCloseOrder = () => {
  const confirmed = window.confirm(
    'Are you sure you want to close this order? This action cannot be undone.'
  );
  if (!confirmed) return;

  closeOrder();
};
```

### After (Accessible ConfirmDialog)

```tsx
const [showCloseConfirm, setShowCloseConfirm] = useState(false);

const handleCloseOrder = () => {
  setShowCloseConfirm(true);
};

const confirmCloseOrder = () => {
  closeOrder();
};

return (
  <>
    <button onClick={handleCloseOrder}>Close Order</button>

    <ConfirmDialog
      isOpen={showCloseConfirm}
      onClose={() => setShowCloseConfirm(false)}
      onConfirm={confirmCloseOrder}
      title="Close Order?"
      description="Are you sure you want to close this order? This action cannot be undone."
      confirmLabel="Close Order"
      cancelLabel="Cancel"
      confirmVariant="danger"
    />
  </>
);
```

## Accessibility Features

Both components include:

- **role="dialog"** and **aria-modal="true"** for screen readers
- **aria-labelledby** and **aria-describedby** for proper labeling
- **ESC key** closes the modal (can be disabled)
- **Focus trap** - keeps focus within modal
- **Focus restoration** - returns focus to triggering element on close
- **Body scroll lock** - prevents background scrolling
- **Keyboard navigation** - full keyboard support

## Styling Customization

Both components use separate CSS files that can be customized:

- `Modal.css` - Base modal styles
- `ConfirmDialog.css` - Confirmation dialog styles

You can override these styles in your own CSS files or modify them directly.

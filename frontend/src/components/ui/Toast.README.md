# Toast Notification System

A production-grade toast notification system with glassmorphism effects, smooth animations, and accessibility features.

## Features

- ✨ **Beautiful Design**: Glassmorphism with backdrop blur and gradient accents
- 🎭 **4 Variants**: Success, Error, Warning, Info
- ⏱️ **Auto-dismiss**: Configurable duration with visual progress bar
- ⏸️ **Pause on Hover**: Hover to pause auto-dismiss countdown
- 📚 **Multiple Toasts**: Stacking support with proper spacing
- ♿ **Accessible**: ARIA labels, keyboard support, screen reader friendly
- 🎨 **Smooth Animations**: Slide + fade entrance/exit animations
- 📱 **Responsive**: Works on all screen sizes

## Usage

### Basic Example

```tsx
'use client'

import { useToast } from '@/lib/hooks/useToast'

export default function MyComponent() {
  const toast = useToast()

  const handleSuccess = () => {
    toast.success('Task completed successfully!')
  }

  const handleError = () => {
    toast.error('Failed to save task. Please try again.')
  }

  const handleWarning = () => {
    toast.warning('Your session will expire in 5 minutes.')
  }

  const handleInfo = () => {
    toast.info('New feature available! Check it out.')
  }

  return (
    <div>
      <button onClick={handleSuccess}>Show Success</button>
      <button onClick={handleError}>Show Error</button>
      <button onClick={handleWarning}>Show Warning</button>
      <button onClick={handleInfo}>Show Info</button>
    </div>
  )
}
```

### Custom Duration

```tsx
// Auto-dismiss after 3 seconds
toast.success('Quick message!', 3000)

// Auto-dismiss after 10 seconds
toast.error('Important error message', 10000)

// Never auto-dismiss (requires manual close)
toast.info('Manual dismiss only', Infinity)
```

### Advanced Usage

```tsx
import { useToast } from '@/lib/hooks/useToast'

export default function TaskActions() {
  const toast = useToast()

  const createTask = async () => {
    try {
      await api.createTask(taskData)
      toast.success('Task created successfully!')
    } catch (error) {
      toast.error('Failed to create task. Please try again.')
    }
  }

  const deleteTask = async (id: number) => {
    try {
      await api.deleteTask(id)
      toast.success('Task deleted successfully!')
    } catch (error) {
      toast.error('Failed to delete task.')
    }
  }

  return (
    // Your component JSX
  )
}
```

### Manual Dismiss

```tsx
const toast = useToast()

// Show a toast and get its ID
const toastId = toast.info('Processing...', Infinity)

// Later, dismiss it manually
toast.dismiss(toastId)
```

## API Reference

### `useToast()` Hook

Returns an object with the following methods:

#### `success(message: string, duration?: number)`
Shows a success toast (green theme).

#### `error(message: string, duration?: number)`
Shows an error toast (red theme).

#### `warning(message: string, duration?: number)`
Shows a warning toast (amber theme).

#### `info(message: string, duration?: number)`
Shows an info toast (blue theme).

#### `showToast(options: ShowToastOptions)`
Shows a toast with custom options:
```tsx
toast.showToast({
  message: 'Custom toast',
  variant: 'success',
  duration: 5000
})
```

#### `dismiss(id: string)`
Manually dismisses a toast by its ID.

#### `toasts`
Array of currently active toasts (readonly).

## Design Details

### Color Palette

- **Success**: Emerald/Green gradients
- **Error**: Red/Rose gradients
- **Warning**: Amber/Orange gradients
- **Info**: Blue/Indigo gradients

### Animations

- **Entrance**: Slide from right + fade in (300ms)
- **Exit**: Scale down + fade out + slide right (300ms)
- **Progress Bar**: Smooth linear countdown
- **Hover**: Scale up slightly (1.02x)

### Accessibility

- ARIA `role="status"` with `aria-live="polite"`
- Keyboard accessible (ESC to dismiss)
- Screen reader announcements
- Focus management
- High contrast colors

## Customization

To customize the toast appearance, edit `/mnt/d/Quarter-4/spec_kit_plus/hackathon-todo/frontend/src/components/ui/Toast.tsx`:

```tsx
const variantStyles = {
  success: {
    gradient: 'from-emerald-500 to-green-600',
    bg: 'bg-emerald-50/95',
    // ... customize colors
  },
  // ... other variants
}
```

## Examples in Codebase

See these components for real-world usage examples:
- `/src/app/tasks/page.tsx` - Task CRUD operations
- `/src/components/auth/SigninForm.tsx` - Authentication feedback
- `/src/components/tasks/TaskForm.tsx` - Form submission feedback

## Dependencies

- React 18+
- Next.js 16+ (App Router)
- Tailwind CSS 3+
- TypeScript 5+

No external toast libraries required - fully custom implementation!

import { Toaster, toast } from 'react-hot-toast';
import {
  CheckCircleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/solid';

// ─── Toaster Provider ─────────────────────────────────────────────────────────

export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      gutter={8}
      toastOptions={{
        duration: 4000,
        style: {
          background: '#1f2937',
          color: '#f3f4f6',
          border: '1px solid #374151',
          borderRadius: '0.75rem',
          fontSize: '0.875rem',
          fontFamily: 'Inter, system-ui, sans-serif',
          maxWidth: '380px',
          padding: '12px 16px',
        },
        success: {
          iconTheme: { primary: '#22c55e', secondary: '#1f2937' },
        },
        error: {
          iconTheme: { primary: '#ef4444', secondary: '#1f2937' },
          duration: 5000,
        },
      }}
    />
  );
}

// ─── Typed toast helpers ──────────────────────────────────────────────────────

export const showToast = {
  success: (message: string) =>
    toast.success(message, {
      icon: <CheckCircleIcon className="h-5 w-5 text-green-400" />,
    }),

  error: (message: string) =>
    toast.error(message, {
      icon: <XCircleIcon className="h-5 w-5 text-red-400" />,
    }),

  info: (message: string) =>
    toast(message, {
      icon: <InformationCircleIcon className="h-5 w-5 text-blue-400" />,
    }),

  warning: (message: string) =>
    toast(message, {
      icon: <ExclamationCircleIcon className="h-5 w-5 text-yellow-400" />,
      style: {
        background: '#1f2937',
        color: '#f3f4f6',
        border: '1px solid #374151',
        borderRadius: '0.75rem',
      },
    }),

  loading: (message: string) => toast.loading(message),

  dismiss: (id?: string) => toast.dismiss(id),

  promise: (
    promise: Promise<unknown>,
    messages: { loading: string; success: string; error: string },
  ) =>
    toast.promise(promise, {
      loading: messages.loading,
      success: messages.success,
      error: messages.error,
    }),
};

export { toast };

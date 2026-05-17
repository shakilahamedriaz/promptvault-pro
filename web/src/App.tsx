import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, Suspense, lazy } from 'react';
import { ToastProvider } from '@/components/Toast';
import { Layout } from '@/components/Layout';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { useAuthStore } from '@/store/authStore';
import { useThemeStore } from '@/store/themeStore';
import { tokenStore } from '@/api/client';

// ─── Lazy-loaded routes ───────────────────────────────────────────────────────
const LoginPage          = lazy(() => import('@/features/auth/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage       = lazy(() => import('@/features/auth/RegisterPage').then(m => ({ default: m.RegisterPage })));
const GoogleCallbackPage = lazy(() => import('@/features/auth/GoogleCallbackPage').then(m => ({ default: m.GoogleCallbackPage })));
const HomePage           = lazy(() => import('@/features/home/HomePage').then(m => ({ default: m.HomePage })));
const LibraryPage        = lazy(() => import('@/features/library/LibraryPage').then(m => ({ default: m.LibraryPage })));
const RefinerPage        = lazy(() => import('@/features/refiner/RefinerPage').then(m => ({ default: m.RefinerPage })));
const HistoryPage        = lazy(() => import('@/features/history/HistoryPage').then(m => ({ default: m.HistoryPage })));
const AnalyticsPage      = lazy(() => import('@/features/analytics/AnalyticsPage').then(m => ({ default: m.AnalyticsPage })));
const SettingsPage       = lazy(() => import('@/features/settings/SettingsPage').then(m => ({ default: m.SettingsPage })));
const MarketplacePage    = lazy(() => import('@/features/marketplace/MarketplacePage').then(m => ({ default: m.MarketplacePage })));
const CreatorProfilePage = lazy(() => import('@/features/creators/CreatorProfilePage').then(m => ({ default: m.CreatorProfilePage })));
const EarningsDashboard  = lazy(() => import('@/features/earnings/EarningsDashboard').then(m => ({ default: m.EarningsDashboard })));

function LoadingFallback() {
  return (
    <div className="flex min-h-screen items-center justify-center" style={{ background: 'var(--color-bg)' }}>
      <div className="text-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-brand-600 border-t-transparent mx-auto mb-4" />
        <p className="text-sm" style={{ color: 'var(--color-text-muted)' }}>Loading…</p>
      </div>
    </div>
  );
}

export default function App() {
  const { logout } = useAuthStore();
  const { theme } = useThemeStore();

  // Apply theme class — supports light, dark, and auto (system preference)
  useEffect(() => {
    const root = document.documentElement;

    if (theme === 'auto') {
      const mq = window.matchMedia('(prefers-color-scheme: dark)');
      const apply = (dark: boolean) => {
        root.classList.toggle('dark', dark);
        root.classList.toggle('light', !dark);
      };
      apply(mq.matches);
      mq.addEventListener('change', (e) => apply(e.matches));
      return () => mq.removeEventListener('change', (e) => apply(e.matches));
    }

    root.classList.toggle('dark', theme === 'dark');
    root.classList.toggle('light', theme === 'light');
  }, [theme]);

  // Handle global auth:logout events from the axios interceptor
  useEffect(() => {
    const handler = () => {
      tokenStore.clear();
      logout();
    };
    window.addEventListener('auth:logout', handler);
    return () => window.removeEventListener('auth:logout', handler);
  }, [logout]);

  return (
    <Suspense fallback={<LoadingFallback />}>
      <BrowserRouter>
        <ToastProvider />
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/auth/callback" element={<GoogleCallbackPage />} />

          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<HomePage />} />
            <Route path="library" element={<LibraryPage />} />
            <Route path="refiner" element={<RefinerPage />} />
            <Route path="history" element={<HistoryPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="marketplace" element={<MarketplacePage />} />
            <Route path="creators/:userId" element={<CreatorProfilePage />} />
            <Route path="earnings" element={<EarningsDashboard />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </Suspense>
  );
}

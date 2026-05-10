import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { clsx } from 'clsx';
import {
  BookOpenIcon,
  SparklesIcon,
  ClockIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  SunIcon,
  MoonIcon,
  CommandLineIcon,
} from '@heroicons/react/24/outline';
import { useAuthStore } from '@/store/authStore';
import { useTheme } from '@/hooks/useTheme';

// ─── Nav Items ────────────────────────────────────────────────────────────────

const navItems = [
  { to: '/library', label: 'Library', icon: BookOpenIcon },
  { to: '/refiner', label: 'AI Refiner', icon: SparklesIcon },
  { to: '/history', label: 'History', icon: ClockIcon },
  { to: '/analytics', label: 'Analytics', icon: ChartBarIcon },
  { to: '/settings', label: 'Settings', icon: Cog6ToothIcon },
];

// ─── Component ────────────────────────────────────────────────────────────────

export function Layout() {
  const { user, logout } = useAuthStore();
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  return (
    <div className="flex h-screen overflow-hidden bg-gray-950 dark:bg-gray-950 light:bg-gray-50">
      {/* ── Sidebar ─────────────────────────────────────────────────────── */}
      <aside className="flex w-64 shrink-0 flex-col border-r border-gray-800 bg-gray-900 dark:bg-gray-900 dark:border-gray-800">
        {/* Logo */}
        <div className="flex items-center gap-3 border-b border-gray-800 px-5 py-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600">
            <CommandLineIcon className="h-5 w-5 text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-white">PromptVault</p>
            <p className="text-xs text-brand-400">Pro</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <ul className="space-y-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  className={({ isActive }) =>
                    clsx(
                      'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-brand-600/20 text-brand-400'
                        : 'text-gray-400 hover:bg-gray-800 hover:text-white',
                    )
                  }
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  {label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* Bottom section */}
        <div className="border-t border-gray-800 p-3 space-y-1">
          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-400 hover:bg-gray-800 hover:text-white transition-colors"
          >
            {isDark ? (
              <>
                <SunIcon className="h-5 w-5" />
                Light Mode
              </>
            ) : (
              <>
                <MoonIcon className="h-5 w-5" />
                Dark Mode
              </>
            )}
          </button>

          {/* User info */}
          {user && (
            <div className="flex items-center gap-3 rounded-lg px-3 py-2">
              <div className="h-8 w-8 shrink-0 rounded-full bg-brand-700 flex items-center justify-center overflow-hidden">
                {user.avatar_url ? (
                  <img src={user.avatar_url} alt={user.display_name} className="h-full w-full object-cover" />
                ) : (
                  <span className="text-xs font-bold text-brand-200">
                    {user.display_name.charAt(0).toUpperCase()}
                  </span>
                )}
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-medium text-white">{user.display_name}</p>
                <p className="truncate text-xs text-gray-500">{user.email}</p>
              </div>
            </div>
          )}

          {/* Logout */}
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-400 hover:bg-red-900/30 hover:text-red-400 transition-colors"
          >
            <ArrowRightOnRectangleIcon className="h-5 w-5" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* ── Main Content ─────────────────────────────────────────────────── */}
      <main className="flex flex-1 flex-col overflow-hidden bg-gray-950 dark:bg-gray-950">
        <div className="flex-1 overflow-y-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

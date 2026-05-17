import { useState, useRef, ChangeEvent } from 'react';
import {
  UserCircleIcon,
  ArrowDownTrayIcon,
  ArrowUpTrayIcon,
  SunIcon,
  MoonIcon,
  ComputerDesktopIcon,
  TrashIcon,
  CheckIcon,
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { useAuthStore } from '@/store/authStore';
import { useTheme } from '@/hooks/useTheme';
import { api } from '@/api/client';
import { showToast } from '@/components/Toast';

// ─── Section wrapper ──────────────────────────────────────────────────────────

function Section({ title, description, children, className = '' }: { title: string; description?: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={clsx("rounded-lg border bg-white p-4 shadow-sm", className)} style={{ borderColor: 'var(--color-border)' }}>
      <div className="mb-4 border-b pb-3" style={{ borderColor: 'var(--color-border)' }}>
        <h2 className="text-sm font-semibold text-gray-900">{title}</h2>
        {description && <p className="mt-0.5 text-xs text-gray-500">{description}</p>}
      </div>
      {children}
    </div>
  );
}

// ─── Settings Page ────────────────────────────────────────────────────────────

export function SettingsPage() {
  const { user, updateUser } = useAuthStore();
  const { theme, setTheme } = useTheme();

  const [displayName, setDisplayName] = useState(user?.display_name || '');
  const [isSavingProfile, setIsSavingProfile] = useState(false);

  const [isExporting, setIsExporting] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [deleteAccountOpen, setDeleteAccountOpen] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');

  const importFileRef = useRef<HTMLInputElement>(null);

  const handleSaveProfile = async () => {
    if (!displayName.trim()) return;
    setIsSavingProfile(true);
    try {
      const updated = await api.put<typeof user>('/auth/me', { display_name: displayName.trim() });
      updateUser(updated as Partial<typeof user> & object);
      showToast.success('Profile updated!');
    } catch {
      showToast.error('Failed to update profile.');
    } finally {
      setIsSavingProfile(false);
    }
  };

  const handleExport = async (format: 'json' | 'csv') => {
    setIsExporting(true);
    try {
      const response = await api.get<Blob>(`/prompts/export?format=${format}`, {
        responseType: 'blob',
      });
      const url = URL.createObjectURL(response as unknown as Blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `prompt-verse-export-${new Date().toISOString().slice(0, 10)}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
      showToast.success(`Exported as ${format.toUpperCase()}!`);
    } catch {
      showToast.error('Export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const handleImport = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsImporting(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const result = await api.post<{ imported: number; skipped: number }>(
        '/prompts/import',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } },
      );
      showToast.success(`Imported ${result.imported} prompts (${result.skipped} skipped).`);
    } catch {
      showToast.error('Import failed. Check file format.');
    } finally {
      setIsImporting(false);
      if (importFileRef.current) importFileRef.current.value = '';
    }
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== 'DELETE') return;
    try {
      await api.delete('/auth/account');
      showToast.success('Account deleted. Redirecting…');
      setTimeout(() => (window.location.href = '/login'), 1500);
    } catch {
      showToast.error('Failed to delete account.');
    }
  };

  return (
    <div className="flex h-full flex-col">
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="border-b bg-white px-5 py-3" style={{ borderColor: 'var(--color-border)' }}>
        <h1 className="text-base font-bold tracking-tight text-gray-900">Settings</h1>
        <p className="text-xs text-gray-500 mt-0.5">Manage your account and preferences</p>
      </div>

      {/* ── Body ────────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto p-5" style={{ background: 'var(--color-bg)' }}>
        <div className="mx-auto max-w-7xl space-y-4">

          {/* Top Row: Appearance + Quick Account */}
          <div className="grid grid-cols-2 gap-4">
            {/* Appearance */}
            <Section title="Appearance" description="Color theme">
              <div className="flex gap-2">
                {([
                  { value: 'light', label: 'Light', icon: SunIcon },
                  { value: 'dark',  label: 'Dark',  icon: MoonIcon },
                  { value: 'auto',  label: 'Auto',  icon: ComputerDesktopIcon },
                ] as const).map(({ value: t, label, icon: Icon }) => (
                  <button
                    key={t}
                    onClick={() => setTheme(t)}
                    aria-pressed={theme === t}
                    className={clsx(
                      'flex-1 flex items-center justify-center gap-1.5 rounded-lg border py-2 text-xs font-medium transition-colors',
                      theme === t
                        ? 'border-brand-400 bg-brand-50 text-brand-700'
                        : 'border-gray-200 bg-white text-gray-500 hover:border-gray-300',
                    )}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {label}
                    {theme === t && <CheckIcon className="h-3 w-3" />}
                  </button>
                ))}
              </div>
            </Section>

            {/* Quick Account */}
            <Section title="Account" description="Profile info">
              <div className="flex items-center gap-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-100 overflow-hidden flex-shrink-0">
                  {user?.avatar_url ? (
                    <img src={user.avatar_url} alt="Avatar" className="h-full w-full object-cover" />
                  ) : (
                    <span className="text-xs font-bold text-brand-600">
                      {user?.display_name?.charAt(0).toUpperCase() || '?'}
                    </span>
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-gray-900 truncate">{user?.display_name}</p>
                  <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                  <span className={clsx(
                    'inline-flex rounded px-1.5 py-0.5 text-xs font-medium mt-0.5',
                    user?.plan === 'pro' ? 'bg-brand-100 text-brand-700' : 'bg-gray-100 text-gray-600',
                  )}>
                    {(user?.plan || 'free').toUpperCase()}
                  </span>
                </div>
              </div>
            </Section>
          </div>

          {/* Account Info Grid */}
          <div className="grid grid-cols-2 gap-4">
            {/* Display Name */}
            <Section title="Display Name" description="Your profile name">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="flex-1 rounded-lg border bg-white px-2.5 py-2 text-xs text-gray-800 focus:border-brand-400 focus:outline-none transition-colors" style={{ borderColor: 'var(--color-border)' }}
                />
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleSaveProfile}
                  isLoading={isSavingProfile}
                  disabled={displayName === user?.display_name}
                >
                  Save
                </Button>
              </div>
            </Section>

            {/* Email (read-only) */}
            <Section title="Email Address" description="Account email">
              <div className="flex items-center gap-2">
                <input
                  type="email"
                  value={user?.email || ''}
                  readOnly
                  className="flex-1 rounded-lg border border-gray-200 bg-gray-50 px-2.5 py-2 text-xs text-gray-400 cursor-default"
                />
                <UserCircleIcon className="h-3.5 w-3.5 text-gray-300 flex-shrink-0" />
              </div>
            </Section>
          </div>

          {/* Export / Import */}
          <div className="grid grid-cols-2 gap-4">
            {/* Export */}
            <Section title="Export" description="Backup your data">
              <div className="space-y-2">
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={<ArrowDownTrayIcon className="h-3.5 w-3.5" />}
                    onClick={() => handleExport('json')}
                    isLoading={isExporting}
                    className="flex-1"
                  >
                    JSON
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={<ArrowDownTrayIcon className="h-3.5 w-3.5" />}
                    onClick={() => handleExport('csv')}
                    isLoading={isExporting}
                    className="flex-1"
                  >
                    CSV
                  </Button>
                </div>
                <p className="text-xs text-gray-400">
                  Download all prompts
                </p>
              </div>
            </Section>

            {/* Import */}
            <Section title="Import" description="Load data">
              <div className="space-y-2">
                <input
                  ref={importFileRef}
                  type="file"
                  accept=".json,.csv"
                  onChange={handleImport}
                  className="hidden"
                  id="import-file"
                />
                <Button
                  variant="outline"
                  size="sm"
                  leftIcon={<ArrowUpTrayIcon className="h-3.5 w-3.5" />}
                  isLoading={isImporting}
                  onClick={() => importFileRef.current?.click()}
                  className="w-full"
                >
                  Upload File
                </Button>
                <p className="text-xs text-gray-400">
                  JSON or CSV format
                </p>
              </div>
            </Section>
          </div>

          {/* Danger Zone */}
          <Section title="Danger Zone" className="border-red-100 bg-red-50">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs font-medium text-red-700">Delete Account</p>
                <p className="mt-0.5 text-xs text-red-600">
                  Permanently delete your account and all data.
                </p>
              </div>
              <Button
                variant="danger"
                size="sm"
                leftIcon={<TrashIcon className="h-3.5 w-3.5" />}
                onClick={() => setDeleteAccountOpen(true)}
              >
                Delete
              </Button>
            </div>
          </Section>
        </div>
      </div>

      {/* ── Delete Account Modal ─────────────────────────────────────────── */}
      <Modal
        isOpen={deleteAccountOpen}
        onClose={() => { setDeleteAccountOpen(false); setDeleteConfirmText(''); }}
        title="Delete Account"
        size="sm"
        footer={
          <>
            <Button variant="ghost" onClick={() => { setDeleteAccountOpen(false); setDeleteConfirmText(''); }} size="sm">
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleDeleteAccount}
              disabled={deleteConfirmText !== 'DELETE'}
              size="sm"
            >
              Delete
            </Button>
          </>
        }
      >
        <div className="space-y-3">
          <p className="text-xs text-gray-600">
            This will permanently delete your account, all prompts, history, and settings.
            <span className="font-semibold text-gray-900"> This cannot be undone.</span>
          </p>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Type <span className="font-mono font-bold text-red-600">DELETE</span> to confirm
            </label>
            <input
              type="text"
              value={deleteConfirmText}
              onChange={(e) => setDeleteConfirmText(e.target.value)}
              placeholder="DELETE"
              className="block w-full rounded-lg border border-red-200 bg-red-50 px-2.5 py-2 text-xs text-gray-900 placeholder-gray-400 focus:border-red-400 focus:outline-none focus:ring-1 focus:ring-red-200"
            />
          </div>
        </div>
      </Modal>
    </div>
  );
}

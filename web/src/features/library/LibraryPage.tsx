import { useState, useCallback } from 'react';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  StarIcon,
  TrashIcon,
  PencilIcon,
  FunnelIcon,
  ArrowsUpDownIcon,
  DocumentDuplicateIcon,
} from '@heroicons/react/24/outline';
import { StarIcon as StarSolid } from '@heroicons/react/24/solid';
import { clsx } from 'clsx';
import { formatDistanceToNow } from 'date-fns';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { usePrompts, type Prompt, type SortOption } from '@/hooks/usePrompts';
import { PromptEditor } from './PromptEditor';
import { showToast } from '@/components/Toast';

// ─── Constants ────────────────────────────────────────────────────────────────

const CATEGORIES = ['All', 'General', 'Writing', 'Coding', 'Analysis', 'Creative', 'Research', 'Business', 'Education', 'Marketing', 'Other'];

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'recent', label: 'Most Recent' },
  { value: 'alpha', label: 'Alphabetical' },
  { value: 'most_used', label: 'Most Used' },
];

// ─── Prompt Card ──────────────────────────────────────────────────────────────

interface PromptCardProps {
  prompt: Prompt;
  onEdit: (p: Prompt) => void;
  onDelete: (p: Prompt) => void;
  onToggleFavorite: (id: string) => void;
  onCopy: (body: string) => void;
}

function PromptCard({ prompt, onEdit, onDelete, onToggleFavorite, onCopy }: PromptCardProps) {
  const scoreColor =
    prompt.quality_score === null
      ? 'text-gray-500'
      : prompt.quality_score >= 70
        ? 'text-green-400'
        : prompt.quality_score >= 40
          ? 'text-yellow-400'
          : 'text-red-400';

  return (
    <article className="group relative rounded-xl border border-gray-800 bg-gray-900 p-5 hover:border-gray-700 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-sm font-semibold text-white">{prompt.title}</h3>
          <div className="mt-1 flex items-center gap-2 flex-wrap">
            <span className="rounded-full bg-gray-800 px-2 py-0.5 text-xs text-gray-400">
              {prompt.category || 'General'}
            </span>
            {prompt.quality_score !== null && (
              <span className={clsx('text-xs font-medium', scoreColor)}>
                Score: {prompt.quality_score}
              </span>
            )}
            <span className="text-xs text-gray-600">
              Used {prompt.use_count}×
            </span>
          </div>
        </div>

        {/* Favorite star */}
        <button
          onClick={() => onToggleFavorite(prompt.id)}
          className="shrink-0 text-gray-600 hover:text-yellow-400 transition-colors"
          aria-label={prompt.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
        >
          {prompt.is_favorite ? (
            <StarSolid className="h-5 w-5 text-yellow-400" />
          ) : (
            <StarIcon className="h-5 w-5" />
          )}
        </button>
      </div>

      {/* Body preview */}
      <p className="text-xs text-gray-500 line-clamp-3 font-mono leading-relaxed mb-3">
        {prompt.body}
      </p>

      {/* Tags */}
      {prompt.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {prompt.tags.slice(0, 4).map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-brand-600/10 px-2 py-0.5 text-xs text-brand-400"
            >
              #{tag}
            </span>
          ))}
          {prompt.tags.length > 4 && (
            <span className="text-xs text-gray-600">+{prompt.tags.length - 4} more</span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-600">
          {formatDistanceToNow(new Date(prompt.updated_at), { addSuffix: true })}
        </span>

        {/* Actions — visible on hover */}
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onCopy(prompt.body)}
            className="rounded p-1.5 text-gray-500 hover:bg-gray-800 hover:text-gray-200 transition-colors"
            title="Copy prompt"
          >
            <DocumentDuplicateIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => onEdit(prompt)}
            className="rounded p-1.5 text-gray-500 hover:bg-gray-800 hover:text-gray-200 transition-colors"
            title="Edit prompt"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => onDelete(prompt)}
            className="rounded p-1.5 text-gray-500 hover:bg-red-900/30 hover:text-red-400 transition-colors"
            title="Delete prompt"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      </div>
    </article>
  );
}

// ─── Library Page ─────────────────────────────────────────────────────────────

export function LibraryPage() {
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [category, setCategory] = useState('');
  const [sort, setSort] = useState<SortOption>('recent');
  const [page, setPage] = useState(1);
  const [editorOpen, setEditorOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Prompt | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Debounce search
  const handleSearchChange = useCallback((value: string) => {
    setSearch(value);
    const timer = setTimeout(() => {
      setDebouncedSearch(value);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, []);

  const {
    prompts,
    total,
    isLoading,
    error,
    createPrompt,
    updatePrompt,
    deletePrompt,
    toggleFavorite,
    getVersions,
  } = usePrompts({ search: debouncedSearch, category: category === 'All' ? '' : category, sort, page });

  const totalPages = Math.ceil(total / 20);

  const handleCreate = () => {
    setEditingPrompt(null);
    setEditorOpen(true);
  };

  const handleEdit = (prompt: Prompt) => {
    setEditingPrompt(prompt);
    setEditorOpen(true);
  };

  const handleSave = async (payload: Parameters<typeof createPrompt>[0]) => {
    setIsSaving(true);
    try {
      if (editingPrompt) {
        await updatePrompt(editingPrompt.id, payload);
      } else {
        await createPrompt(payload);
      }
    } catch {
      showToast.error('Failed to save prompt.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    try {
      await deletePrompt(deleteTarget.id);
    } catch {
      showToast.error('Failed to delete prompt.');
    } finally {
      setDeleteTarget(null);
    }
  };

  const handleCopy = (body: string) => {
    navigator.clipboard.writeText(body);
    showToast.success('Copied to clipboard!');
  };

  return (
    <div className="flex h-full flex-col">
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="border-b border-gray-800 bg-gray-900 px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-xl font-bold text-white">Prompt Library</h1>
            <p className="text-sm text-gray-400">{total.toLocaleString()} prompts</p>
          </div>
          <Button variant="primary" leftIcon={<PlusIcon className="h-4 w-4" />} onClick={handleCreate}>
            New Prompt
          </Button>
        </div>

        {/* Search + Controls */}
        <div className="flex items-center gap-3">
          <div className="relative flex-1 max-w-md">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
            <input
              type="search"
              value={search}
              onChange={(e) => handleSearchChange(e.target.value)}
              placeholder="Search prompts…"
              className="block w-full rounded-lg border border-gray-700 bg-gray-800 pl-9 pr-3 py-2 text-sm text-white placeholder-gray-500 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <button
            onClick={() => setShowFilters((v) => !v)}
            className={clsx(
              'flex items-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors',
              showFilters
                ? 'border-brand-500 bg-brand-600/20 text-brand-400'
                : 'border-gray-700 bg-gray-800 text-gray-400 hover:border-gray-600 hover:text-white',
            )}
          >
            <FunnelIcon className="h-4 w-4" />
            Filters
          </button>

          {/* Sort */}
          <div className="relative">
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value as SortOption)}
              className="appearance-none rounded-lg border border-gray-700 bg-gray-800 pl-3 pr-8 py-2 text-sm text-gray-300 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              {SORT_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
            <ArrowsUpDownIcon className="pointer-events-none absolute right-2 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
          </div>
        </div>

        {/* Category filter pills */}
        {showFilters && (
          <div className="mt-3 flex flex-wrap gap-2 animate-slide-in">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => { setCategory(cat === 'All' ? '' : cat); setPage(1); }}
                className={clsx(
                  'rounded-full px-3 py-1 text-xs font-medium transition-colors',
                  (category === cat || (cat === 'All' && !category))
                    ? 'bg-brand-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white',
                )}
              >
                {cat}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* ── Body ────────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto p-6">
        {error && (
          <div className="rounded-lg bg-red-900/30 border border-red-800 px-4 py-3 text-sm text-red-300 mb-4">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-44 rounded-xl bg-gray-800 animate-pulse" />
            ))}
          </div>
        ) : prompts.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-800">
              <DocumentDuplicateIcon className="h-8 w-8 text-gray-600" />
            </div>
            <p className="text-lg font-medium text-gray-300">
              {debouncedSearch || category ? 'No prompts match your filters' : 'No prompts yet'}
            </p>
            <p className="mt-1 text-sm text-gray-500">
              {debouncedSearch || category
                ? 'Try adjusting your search or filters.'
                : 'Create your first prompt to get started.'}
            </p>
            {!debouncedSearch && !category && (
              <Button variant="primary" className="mt-4" onClick={handleCreate}>
                Create Prompt
              </Button>
            )}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {prompts.map((prompt) => (
                <PromptCard
                  key={prompt.id}
                  prompt={prompt}
                  onEdit={handleEdit}
                  onDelete={setDeleteTarget}
                  onToggleFavorite={toggleFavorite}
                  onCopy={handleCopy}
                />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-6 flex items-center justify-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={page === 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  Previous
                </Button>
                <span className="text-sm text-gray-400">
                  Page {page} of {totalPages}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={page === totalPages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                </Button>
              </div>
            )}
          </>
        )}
      </div>

      {/* ── Prompt Editor Modal ──────────────────────────────────────────── */}
      <PromptEditor
        isOpen={editorOpen}
        onClose={() => setEditorOpen(false)}
        prompt={editingPrompt}
        onSave={handleSave}
        getVersions={getVersions}
        isSaving={isSaving}
      />

      {/* ── Delete Confirm Modal ─────────────────────────────────────────── */}
      <Modal
        isOpen={Boolean(deleteTarget)}
        onClose={() => setDeleteTarget(null)}
        title="Delete Prompt"
        size="sm"
        footer={
          <>
            <Button variant="ghost" onClick={() => setDeleteTarget(null)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDeleteConfirm}>
              Delete
            </Button>
          </>
        }
      >
        <p className="text-sm text-gray-300">
          Are you sure you want to delete{' '}
          <span className="font-semibold text-white">&ldquo;{deleteTarget?.title}&rdquo;</span>?
          This action cannot be undone.
        </p>
      </Modal>
    </div>
  );
}

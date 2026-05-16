import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  PlusIcon,
  SparklesIcon,
  GlobeAltIcon,
  ArrowRightIcon,
  FireIcon,
  CircleStackIcon,
  ArrowTrendingUpIcon,
  DocumentDuplicateIcon,
  ChartBarIcon,
  StarIcon,
} from '@heroicons/react/24/outline';
import { StarIcon as StarSolid } from '@heroicons/react/24/solid';
import { clsx } from 'clsx';
import { formatDistanceToNow, format } from 'date-fns';
import { api } from '@/api/client';
import { useAuthStore } from '@/store/authStore';
import { showToast } from '@/components/Toast';

// ─── Helpers ──────────────────────────────────────────────────────────────────

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
}

function firstName(displayName?: string) {
  if (!displayName) return 'there';
  return displayName.split(' ')[0];
}

// ─── Types ────────────────────────────────────────────────────────────────────

interface Summary {
  total_prompts: number;
  total_uses: number;
  total_refinements: number;
  avg_quality_score: number;
  prompts_this_week: number;
  uses_this_week: number;
}

interface RecentPrompt {
  id: string;
  title: string;
  category: string;
  body: string;
  use_count: number;
  quality_score: number | null;
  updated_at: string;
  is_favorite: boolean;
}

// ─── Static trending (replace with real API in Phase 2) ───────────────────────

const TRENDING = [
  { id: 't1', title: 'Senior Code Reviewer',      category: 'Coding',    downloads: 1240, rating: 4.9, price: 0    },
  { id: 't2', title: 'SEO Blog Post Writer',       category: 'Writing',   downloads: 987,  rating: 4.7, price: 4.99 },
  { id: 't3', title: 'Cold Email Outreach',        category: 'Marketing', downloads: 843,  rating: 4.8, price: 2.99 },
  { id: 't4', title: 'Executive Summary Generator',category: 'Business',  downloads: 712,  rating: 4.6, price: 1.99 },
];

// ─── Quick Actions ─────────────────────────────────────────────────────────────

const ACTIONS = [
  {
    icon: PlusIcon,
    label: 'New Prompt',
    desc: 'Start from scratch or pick a template',
    to: '/library',
    iconBg: 'rgba(99,102,241,0.08)',
    iconBorder: 'rgba(99,102,241,0.18)',
    iconColor: '#6366f1',
  },
  {
    icon: SparklesIcon,
    label: 'AI Refiner',
    desc: 'Improve any prompt with AI in seconds',
    to: '/refiner',
    iconBg: 'rgba(124,58,237,0.08)',
    iconBorder: 'rgba(124,58,237,0.18)',
    iconColor: '#7c3aed',
  },
  {
    icon: GlobeAltIcon,
    label: 'Explore',
    desc: 'Discover prompts from the community',
    to: '/marketplace',
    iconBg: 'rgba(5,150,105,0.08)',
    iconBorder: 'rgba(5,150,105,0.18)',
    iconColor: '#059669',
  },
];

// ─── Stat definitions ─────────────────────────────────────────────────────────

function buildStats(s: Summary) {
  return [
    {
      label: 'My Prompts',
      value: s.total_prompts,
      delta: s.prompts_this_week > 0 ? `+${s.prompts_this_week} this week` : null,
      icon: CircleStackIcon,
      iconBg: 'bg-indigo-50',
      iconBorder: 'border-indigo-100',
      iconColor: 'text-indigo-600',
      trend: s.prompts_this_week > 0 ? 1 : 0,
    },
    {
      label: 'Total Uses',
      value: s.total_uses,
      delta: s.uses_this_week > 0 ? `+${s.uses_this_week} this week` : null,
      icon: ArrowTrendingUpIcon,
      iconBg: 'bg-emerald-50',
      iconBorder: 'border-emerald-100',
      iconColor: 'text-emerald-600',
      trend: s.uses_this_week > 0 ? 1 : 0,
    },
    {
      label: 'AI Refinements',
      value: s.total_refinements,
      delta: null,
      icon: SparklesIcon,
      iconBg: 'bg-violet-50',
      iconBorder: 'border-violet-100',
      iconColor: 'text-violet-600',
      trend: 0,
    },
    {
      label: 'Avg Quality Score',
      value: s.avg_quality_score ? `${s.avg_quality_score}/100` : '—',
      delta: null,
      icon: ChartBarIcon,
      iconBg: 'bg-amber-50',
      iconBorder: 'border-amber-100',
      iconColor: 'text-amber-600',
      trend: 0,
    },
  ];
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function SkeletonCard() {
  return <div className="h-28 rounded-[14px] bg-gray-100 animate-pulse" />;
}

function StatCard({ stat }: { stat: ReturnType<typeof buildStats>[number] }) {
  const Icon = stat.icon;
  return (
    <div
      className="rounded-[14px] border bg-white p-5 shadow-card flex flex-col gap-3"
      style={{ borderColor: 'var(--color-border)' }}
    >
      <div className="flex items-center justify-between">
        <div className={clsx('flex h-10 w-10 items-center justify-center rounded-xl border', stat.iconBg, stat.iconBorder)}>
          <Icon className={clsx('h-5 w-5', stat.iconColor)} />
        </div>
        {stat.trend > 0 && (
          <span className="text-[11px] font-semibold text-emerald-600 bg-emerald-50 border border-emerald-100 px-2 py-0.5 rounded-full">
            ↑ up
          </span>
        )}
      </div>
      <div>
        <p className="text-[24px] font-bold tracking-tight text-gray-900 leading-none">
          {typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}
        </p>
        <p className="text-[12px] font-medium text-gray-500 mt-1">{stat.label}</p>
        {stat.delta && (
          <p className="text-[11px] text-emerald-600 mt-0.5 font-medium">{stat.delta}</p>
        )}
      </div>
    </div>
  );
}

function QuickActionCard({ action }: { action: typeof ACTIONS[number] }) {
  const Icon = action.icon;
  return (
    <Link
      to={action.to}
      className="group flex items-center gap-4 rounded-[14px] border bg-white p-5 shadow-card transition-all duration-150 hover:shadow-card-hover hover:border-brand-300"
      style={{ borderColor: 'var(--color-border)' }}
    >
      <div
        className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border"
        style={{ background: action.iconBg, borderColor: action.iconBorder }}
      >
        <Icon className="h-5 w-5" style={{ color: action.iconColor }} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[14px] font-semibold text-gray-900 leading-tight">{action.label}</p>
        <p className="text-[12px] text-gray-400 mt-0.5">{action.desc}</p>
      </div>
      <ArrowRightIcon className="h-4 w-4 shrink-0 text-gray-300 group-hover:text-brand-500 group-hover:translate-x-0.5 transition-all duration-150" />
    </Link>
  );
}

function QualityBadge({ score }: { score: number | null }) {
  if (score === null) return null;
  const color =
    score >= 80 ? 'text-emerald-600 bg-emerald-50 border-emerald-100' :
    score >= 60 ? 'text-amber-600 bg-amber-50 border-amber-100' :
                 'text-red-500 bg-red-50 border-red-100';
  return (
    <span className={clsx('text-[10px] font-bold border rounded-full px-1.5 py-0.5', color)}>
      {score}
    </span>
  );
}

function RecentPromptRow({ prompt, onCopy }: { prompt: RecentPrompt; onCopy: (body: string) => void }) {
  return (
    <div
      className="group flex items-center gap-3 px-5 py-3.5 border-b last:border-0 hover:bg-gray-50/70 transition-colors"
      style={{ borderColor: 'var(--color-border)' }}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-[13px] font-semibold text-gray-900 truncate">{prompt.title}</p>
          <span className="shrink-0 rounded-full bg-brand-50 border border-brand-100 px-2 py-0.5 text-[10px] font-medium text-brand-600">
            {prompt.category || 'General'}
          </span>
          <QualityBadge score={prompt.quality_score} />
        </div>
        <div className="flex items-center gap-3 mt-0.5">
          <span className="text-[11px] text-gray-400">Used {prompt.use_count}×</span>
          <span className="text-[11px] text-gray-300">·</span>
          <span className="text-[11px] text-gray-400">
            {formatDistanceToNow(new Date(prompt.updated_at), { addSuffix: true })}
          </span>
        </div>
      </div>
      <button
        onClick={() => onCopy(prompt.body)}
        title="Copy prompt"
        className="opacity-0 group-hover:opacity-100 rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-all duration-150"
      >
        <DocumentDuplicateIcon className="h-4 w-4" />
      </button>
    </div>
  );
}

function TrendingRow({ item }: { item: typeof TRENDING[number] }) {
  return (
    <Link
      to="/marketplace"
      className="group flex items-center gap-3 px-5 py-3.5 border-b last:border-0 hover:bg-gray-50/70 transition-colors"
      style={{ borderColor: 'var(--color-border)' }}
    >
      <div className="flex-1 min-w-0">
        <p className="text-[13px] font-semibold text-gray-900 truncate group-hover:text-brand-600 transition-colors">
          {item.title}
        </p>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="text-[11px] text-gray-400">{item.category}</span>
          <span className="text-[11px] text-gray-300">·</span>
          <span className="flex items-center gap-0.5 text-[11px] text-amber-500 font-medium">
            <StarSolid className="h-2.5 w-2.5" />
            {item.rating}
          </span>
          <span className="text-[11px] text-gray-300">·</span>
          <span className="text-[11px] text-gray-400">{item.downloads.toLocaleString()} downloads</span>
        </div>
      </div>
      <span className={clsx(
        'shrink-0 text-[11px] font-bold rounded-full px-2.5 py-1',
        item.price === 0
          ? 'bg-emerald-50 border border-emerald-100 text-emerald-600'
          : 'bg-gray-50 border border-gray-100 text-gray-600'
      )}>
        {item.price === 0 ? 'Free' : `$${item.price}`}
      </span>
    </Link>
  );
}

// ─── Home Page ────────────────────────────────────────────────────────────────

export function HomePage() {
  const { user } = useAuthStore();
  const [summary, setSummary] = useState<Summary | null>(null);
  const [recent, setRecent] = useState<RecentPrompt[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      try {
        const [summaryData, promptsData] = await Promise.all([
          api.get<Summary>('/analytics/summary'),
          api.get<{ prompts: RecentPrompt[] }>('/prompts?sort=recent&limit=4'),
        ]);
        setSummary(summaryData);
        setRecent(promptsData.prompts ?? []);
      } catch {
        // silently degrade — page still renders with empty states
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  const handleCopy = (body: string) => {
    navigator.clipboard.writeText(body);
    showToast.success('Copied to clipboard!');
  };

  const stats = summary ? buildStats(summary) : null;

  return (
    <div className="flex h-full flex-col">

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div
        className="shrink-0 border-b bg-white px-8 py-6"
        style={{ borderColor: 'var(--color-border)' }}
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-[22px] font-bold tracking-tight text-gray-900 leading-tight">
              {getGreeting()},{' '}
              <span style={{
                background: 'linear-gradient(120deg, #6d28d9, #6366f1)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}>
                {firstName(user?.display_name)}
              </span>
            </h1>
            <p className="text-[13px] text-gray-400 mt-1">
              {format(new Date(), "EEEE, MMMM d")}
              <span className="mx-2 text-gray-200">·</span>
              Here's your workspace overview
            </p>
          </div>

          <Link
            to="/library"
            className="flex items-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-[13px] font-bold text-white shadow-sm hover:bg-brand-700 active:scale-[0.98] transition-all duration-150"
          >
            <PlusIcon className="h-4 w-4" />
            New Prompt
          </Link>
        </div>
      </div>

      {/* ── Body ────────────────────────────────────────────────────────── */}
      <div
        className="flex-1 overflow-y-auto p-6 space-y-5"
        style={{ background: 'var(--color-bg)' }}
      >

        {/* ── Stat Cards ──────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {isLoading
            ? Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
            : stats?.map(s => <StatCard key={s.label} stat={s} />)
          }
        </div>

        {/* ── Quick Actions ────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {ACTIONS.map(a => <QuickActionCard key={a.to} action={a} />)}
        </div>

        {/* ── Recent + Trending ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-5">

          {/* Recent Prompts — wider col */}
          <div
            className="lg:col-span-3 rounded-[14px] border bg-white shadow-card overflow-hidden"
            style={{ borderColor: 'var(--color-border)' }}
          >
            <div
              className="flex items-center justify-between px-5 py-4 border-b"
              style={{ borderColor: 'var(--color-border)' }}
            >
              <div className="flex items-center gap-2">
                <div className="h-6 w-6 rounded-lg bg-brand-50 border border-brand-100 flex items-center justify-center">
                  <DocumentDuplicateIcon className="h-3.5 w-3.5 text-brand-600" />
                </div>
                <h2 className="text-[13px] font-semibold text-gray-800">Recent Prompts</h2>
              </div>
              <Link
                to="/library"
                className="text-[12px] font-medium text-brand-600 hover:text-brand-700 flex items-center gap-1 transition-colors"
              >
                View all <ArrowRightIcon className="h-3 w-3" />
              </Link>
            </div>

            {isLoading ? (
              <div className="p-5 space-y-3">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="h-12 rounded-xl bg-gray-100 animate-pulse" />
                ))}
              </div>
            ) : recent.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-14 px-6 text-center">
                <div className="h-12 w-12 rounded-2xl bg-brand-50 border border-brand-100 flex items-center justify-center mb-3">
                  <DocumentDuplicateIcon className="h-6 w-6 text-brand-400" />
                </div>
                <p className="text-[14px] font-semibold text-gray-700">No prompts yet</p>
                <p className="text-[12px] text-gray-400 mt-1">Create your first prompt to get started.</p>
                <Link
                  to="/library"
                  className="mt-4 flex items-center gap-1.5 rounded-xl bg-brand-600 px-4 py-2 text-[12px] font-bold text-white hover:bg-brand-700 transition-colors"
                >
                  <PlusIcon className="h-3.5 w-3.5" /> Create Prompt
                </Link>
              </div>
            ) : (
              <div>
                {recent.map(p => (
                  <RecentPromptRow key={p.id} prompt={p} onCopy={handleCopy} />
                ))}
              </div>
            )}
          </div>

          {/* Trending in Explore — narrower col */}
          <div
            className="lg:col-span-2 rounded-[14px] border bg-white shadow-card overflow-hidden"
            style={{ borderColor: 'var(--color-border)' }}
          >
            <div
              className="flex items-center justify-between px-5 py-4 border-b"
              style={{ borderColor: 'var(--color-border)' }}
            >
              <div className="flex items-center gap-2">
                <div className="h-6 w-6 rounded-lg bg-orange-50 border border-orange-100 flex items-center justify-center">
                  <FireIcon className="h-3.5 w-3.5 text-orange-500" />
                </div>
                <h2 className="text-[13px] font-semibold text-gray-800">Trending in Explore</h2>
              </div>
              <Link
                to="/marketplace"
                className="text-[12px] font-medium text-brand-600 hover:text-brand-700 flex items-center gap-1 transition-colors"
              >
                Browse <ArrowRightIcon className="h-3 w-3" />
              </Link>
            </div>

            <div>
              {TRENDING.map(item => (
                <TrendingRow key={item.id} item={item} />
              ))}
            </div>

            {/* Marketplace teaser footer */}
            <div
              className="px-5 py-3.5 border-t"
              style={{
                borderColor: 'var(--color-border)',
                background: 'linear-gradient(to right, rgba(109,40,217,0.03), rgba(99,102,241,0.05))',
              }}
            >
              <p className="text-[11px] text-gray-400 leading-relaxed">
                Marketplace launching soon —{' '}
                <Link to="/marketplace" className="text-brand-500 font-medium hover:text-brand-700 transition-colors">
                  explore community prompts
                </Link>
              </p>
            </div>
          </div>
        </div>

        {/* ── AI Refiner Banner ────────────────────────────────────────── */}
        <div
          className="rounded-[14px] p-6 flex items-center gap-5"
          style={{
            background: 'linear-gradient(135deg, #6366f1 0%, #7c3aed 55%, #6d28d9 100%)',
            boxShadow: '0 8px 32px rgba(99,102,241,0.22)',
          }}
        >
          <div
            className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl"
            style={{ background: 'rgba(255,255,255,0.12)', border: '1px solid rgba(255,255,255,0.2)' }}
          >
            <SparklesIcon className="h-6 w-6 text-white" />
          </div>

          <div className="flex-1 min-w-0">
            <p className="text-[15px] font-bold text-white leading-tight">
              Supercharge your prompts with AI
            </p>
            <p className="text-[12.5px] mt-1 leading-relaxed" style={{ color: 'rgba(255,255,255,0.72)' }}>
              The AI Refiner analyzes and improves your prompts in seconds. Average quality boost: +23 points.
            </p>
          </div>

          <Link
            to="/refiner"
            className="shrink-0 flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-[13px] font-bold text-brand-700 hover:bg-brand-50 active:scale-[0.98] transition-all duration-150 shadow-sm"
          >
            Try Refiner
            <ArrowRightIcon className="h-4 w-4" />
          </Link>
        </div>

      </div>
    </div>
  );
}

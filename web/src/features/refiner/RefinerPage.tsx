import { useState } from 'react';
import {
  SparklesIcon,
  HandThumbUpIcon,
  HandThumbDownIcon,
  ArrowPathIcon,
  BookmarkIcon,
  ClipboardDocumentIcon,
} from '@heroicons/react/24/outline';
import { HandThumbUpIcon as ThumbUpSolid, HandThumbDownIcon as ThumbDownSolid } from '@heroicons/react/24/solid';
import ReactDiffViewer, { DiffMethod } from 'react-diff-viewer-continued';
import { clsx } from 'clsx';
import { Button } from '@/components/Button';
import { api } from '@/api/client';
import { showToast } from '@/components/Toast';

// ─── Types ────────────────────────────────────────────────────────────────────

type RefineStyle = 'Professional' | 'Creative' | 'Technical' | 'Concise';

interface RefineResponse {
  refined_body: string;
  explanation: string;
  score_before: number;
  score_after: number;
  refinement_id: string;
}

// ─── Style options ────────────────────────────────────────────────────────────

const STYLES: { value: RefineStyle; label: string; description: string; color: string }[] = [
  {
    value: 'Professional',
    label: 'Professional',
    description: 'Formal, business-ready tone',
    color: 'blue',
  },
  {
    value: 'Creative',
    label: 'Creative',
    description: 'Imaginative, expressive language',
    color: 'purple',
  },
  {
    value: 'Technical',
    label: 'Technical',
    description: 'Precise, developer-focused',
    color: 'green',
  },
  {
    value: 'Concise',
    label: 'Concise',
    description: 'Short, direct, no fluff',
    color: 'orange',
  },
];

const styleColorClasses: Record<string, string> = {
  blue: 'border-blue-500 bg-blue-500/10 text-blue-400',
  purple: 'border-purple-500 bg-purple-500/10 text-purple-400',
  green: 'border-green-500 bg-green-500/10 text-green-400',
  orange: 'border-orange-500 bg-orange-500/10 text-orange-400',
};

// ─── Quality Score Ring ───────────────────────────────────────────────────────

function ScoreRing({ score, label }: { score: number; label: string }) {
  const color = score >= 70 ? '#22c55e' : score >= 40 ? '#f59e0b' : '#ef4444';
  const circumference = 2 * Math.PI * 18;
  const dash = (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width="48" height="48" viewBox="0 0 48 48" aria-label={`${label}: ${score}`}>
        <circle cx="24" cy="24" r="18" fill="none" stroke="#374151" strokeWidth="4" />
        <circle
          cx="24"
          cy="24"
          r="18"
          fill="none"
          stroke={color}
          strokeWidth="4"
          strokeDasharray={`${dash} ${circumference}`}
          strokeLinecap="round"
          transform="rotate(-90 24 24)"
          style={{ transition: 'stroke-dasharray 0.6s ease' }}
        />
        <text
          x="24"
          y="28"
          textAnchor="middle"
          fontSize="11"
          fontWeight="600"
          fill={color}
        >
          {score}
        </text>
      </svg>
      <span className="text-xs text-gray-500">{label}</span>
    </div>
  );
}

// ─── Component ────────────────────────────────────────────────────────────────

export function RefinerPage() {
  const [inputPrompt, setInputPrompt] = useState('');
  const [style, setStyle] = useState<RefineStyle>('Professional');
  const [result, setResult] = useState<RefineResponse | null>(null);
  const [isRefining, setIsRefining] = useState(false);
  const [viewMode, setViewMode] = useState<'diff' | 'side-by-side'>('diff');
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const handleRefine = async () => {
    if (!inputPrompt.trim()) {
      showToast.warning('Please enter a prompt to refine.');
      return;
    }
    setIsRefining(true);
    setResult(null);
    setFeedback(null);
    try {
      const data = await api.post<RefineResponse>('/ai/refine', {
        body: inputPrompt.trim(),
        style: style.toLowerCase(),
      });
      setResult(data);
    } catch {
      showToast.error('Refinement failed. Please try again.');
    } finally {
      setIsRefining(false);
    }
  };

  const handleFeedback = async (rating: 'up' | 'down') => {
    if (!result) return;
    setFeedback(rating);
    try {
      await api.post('/ai/feedback', {
        refinement_id: result.refinement_id,
        rating: rating === 'up' ? 1 : -1,
      });
      showToast.success('Thank you for your feedback!');
    } catch {
      showToast.error('Could not submit feedback.');
    }
  };

  const handleSaveRefined = async () => {
    if (!result) return;
    setIsSaving(true);
    try {
      await api.post('/prompts', {
        title: `Refined: ${inputPrompt.slice(0, 60)}…`,
        body: result.refined_body,
        category: 'General',
        tags: ['refined', style.toLowerCase()],
      });
      showToast.success('Refined prompt saved to Library!');
    } catch {
      showToast.error('Failed to save to Library.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCopyRefined = () => {
    if (!result) return;
    navigator.clipboard.writeText(result.refined_body);
    showToast.success('Copied to clipboard!');
  };

  const handleReset = () => {
    setResult(null);
    setFeedback(null);
  };

  return (
    <div className="flex h-full flex-col">
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="border-b border-gray-800 bg-gray-900 px-6 py-4">
        <div className="flex items-center gap-3">
          <SparklesIcon className="h-6 w-6 text-brand-400" />
          <div>
            <h1 className="text-xl font-bold text-white">AI Refiner</h1>
            <p className="text-sm text-gray-400">Enhance your prompts with AI-powered refinement</p>
          </div>
        </div>
      </div>

      {/* ── Body ────────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-5xl space-y-6">
          {/* Input Section */}
          <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
            <h2 className="mb-4 text-sm font-semibold text-gray-300">Your Prompt</h2>
            <textarea
              value={inputPrompt}
              onChange={(e) => setInputPrompt(e.target.value)}
              placeholder="Paste or type your prompt here…"
              rows={6}
              className="block w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-3 text-sm text-white placeholder-gray-500 font-mono focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 resize-y"
            />
            <div className="mt-2 flex items-center justify-between">
              <span className="text-xs text-gray-600">{inputPrompt.length.toLocaleString()} characters</span>
            </div>

            {/* Style selector */}
            <div className="mt-4">
              <p className="mb-3 text-sm font-medium text-gray-300">Refinement Style</p>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                {STYLES.map((s) => (
                  <button
                    key={s.value}
                    onClick={() => setStyle(s.value)}
                    className={clsx(
                      'rounded-lg border p-3 text-left transition-colors',
                      style === s.value
                        ? styleColorClasses[s.color]
                        : 'border-gray-700 bg-gray-800 text-gray-400 hover:border-gray-600 hover:text-white',
                    )}
                  >
                    <p className="text-sm font-semibold">{s.label}</p>
                    <p className="mt-0.5 text-xs opacity-70">{s.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Refine button */}
            <div className="mt-5 flex items-center gap-3">
              <Button
                variant="primary"
                leftIcon={<SparklesIcon className="h-4 w-4" />}
                onClick={handleRefine}
                isLoading={isRefining}
                disabled={!inputPrompt.trim()}
              >
                {isRefining ? 'Refining…' : 'Refine with AI'}
              </Button>
              {result && (
                <Button variant="ghost" leftIcon={<ArrowPathIcon className="h-4 w-4" />} onClick={handleReset}>
                  Reset
                </Button>
              )}
            </div>
          </div>

          {/* Results Section */}
          {isRefining && (
            <div className="rounded-xl border border-gray-800 bg-gray-900 p-8 flex flex-col items-center gap-4">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
              <p className="text-sm text-gray-400">AI is refining your prompt…</p>
            </div>
          )}

          {result && !isRefining && (
            <>
              {/* Quality scores */}
              <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
                <h2 className="mb-4 text-sm font-semibold text-gray-300">Quality Scores</h2>
                <div className="flex items-center gap-8">
                  <ScoreRing score={result.score_before} label="Before" />
                  <div className="flex-1 text-center">
                    <div className="inline-flex items-center gap-2 rounded-full bg-green-500/10 px-3 py-1 text-xs text-green-400">
                      <span>▲</span>
                      <span>+{result.score_after - result.score_before} points</span>
                    </div>
                  </div>
                  <ScoreRing score={result.score_after} label="After" />
                </div>

                {result.explanation && (
                  <div className="mt-4 rounded-lg bg-gray-800 px-4 py-3">
                    <p className="text-xs font-medium text-gray-400 mb-1">AI Explanation</p>
                    <p className="text-sm text-gray-300">{result.explanation}</p>
                  </div>
                )}
              </div>

              {/* Diff Viewer */}
              <div className="rounded-xl border border-gray-800 bg-gray-900 overflow-hidden">
                <div className="flex items-center justify-between border-b border-gray-800 px-6 py-3">
                  <h2 className="text-sm font-semibold text-gray-300">Comparison</h2>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setViewMode('diff')}
                      className={clsx(
                        'rounded px-3 py-1 text-xs font-medium transition-colors',
                        viewMode === 'diff'
                          ? 'bg-brand-600 text-white'
                          : 'text-gray-400 hover:text-white',
                      )}
                    >
                      Unified
                    </button>
                    <button
                      onClick={() => setViewMode('side-by-side')}
                      className={clsx(
                        'rounded px-3 py-1 text-xs font-medium transition-colors',
                        viewMode === 'side-by-side'
                          ? 'bg-brand-600 text-white'
                          : 'text-gray-400 hover:text-white',
                      )}
                    >
                      Side by Side
                    </button>
                  </div>
                </div>
                <div className="overflow-x-auto text-sm">
                  <ReactDiffViewer
                    oldValue={inputPrompt}
                    newValue={result.refined_body}
                    splitView={viewMode === 'side-by-side'}
                    compareMethod={DiffMethod.WORDS}
                    useDarkTheme
                    leftTitle="Original"
                    rightTitle="Refined"
                    styles={{
                      variables: {
                        dark: {
                          diffViewerBackground: '#111827',
                          addedBackground: '#14532d33',
                          addedColor: '#86efac',
                          removedBackground: '#7f1d1d33',
                          removedColor: '#fca5a5',
                          wordAddedBackground: '#14532d66',
                          wordRemovedBackground: '#7f1d1d66',
                          addedGutterBackground: '#14532d22',
                          removedGutterBackground: '#7f1d1d22',
                          gutterBackground: '#111827',
                          gutterColor: '#6b7280',
                          emptyLineBackground: '#111827',
                          highlightBackground: '#1f2937',
                          highlightGutterBackground: '#1f2937',
                        },
                      },
                    }}
                  />
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between rounded-xl border border-gray-800 bg-gray-900 px-6 py-4">
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-400">Was this helpful?</span>
                  <button
                    onClick={() => handleFeedback('up')}
                    className={clsx(
                      'rounded-lg p-2 transition-colors',
                      feedback === 'up'
                        ? 'bg-green-500/10 text-green-400'
                        : 'text-gray-500 hover:bg-gray-800 hover:text-green-400',
                    )}
                    aria-label="Thumbs up"
                  >
                    {feedback === 'up' ? (
                      <ThumbUpSolid className="h-5 w-5" />
                    ) : (
                      <HandThumbUpIcon className="h-5 w-5" />
                    )}
                  </button>
                  <button
                    onClick={() => handleFeedback('down')}
                    className={clsx(
                      'rounded-lg p-2 transition-colors',
                      feedback === 'down'
                        ? 'bg-red-500/10 text-red-400'
                        : 'text-gray-500 hover:bg-gray-800 hover:text-red-400',
                    )}
                    aria-label="Thumbs down"
                  >
                    {feedback === 'down' ? (
                      <ThumbDownSolid className="h-5 w-5" />
                    ) : (
                      <HandThumbDownIcon className="h-5 w-5" />
                    )}
                  </button>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={<ClipboardDocumentIcon className="h-4 w-4" />}
                    onClick={handleCopyRefined}
                  >
                    Copy Refined
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    leftIcon={<BookmarkIcon className="h-4 w-4" />}
                    onClick={handleSaveRefined}
                    isLoading={isSaving}
                  >
                    Save to Library
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

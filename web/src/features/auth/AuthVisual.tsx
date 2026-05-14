import React from 'react';
import { SparklesIcon } from '@heroicons/react/24/outline';

// ── Node map ──────────────────────────────────────────────────────────────────
const NODES = {
  i1: { x: 12,  y: 22,  label: 'write a blog post…',  layer: 'input'  },
  i2: { x: 12,  y: 50,  label: 'explain quantum…',     layer: 'input'  },
  i3: { x: 12,  y: 78,  label: 'summarize this doc…',  layer: 'input'  },
  h1: { x: 38,  y: 15,  label: null,                   layer: 'hidden' },
  h2: { x: 42,  y: 38,  label: null,                   layer: 'hidden' },
  h3: { x: 38,  y: 62,  label: null,                   layer: 'hidden' },
  h4: { x: 42,  y: 84,  label: null,                   layer: 'hidden' },
  c1: { x: 62,  y: 30,  label: null,                   layer: 'core'   },
  c2: { x: 62,  y: 70,  label: null,                   layer: 'core'   },
  o1: { x: 86,  y: 20,  label: 'Structured prompt',    layer: 'output' },
  o2: { x: 86,  y: 50,  label: 'Expert persona set',   layer: 'output' },
  o3: { x: 86,  y: 80,  label: 'Context enriched',     layer: 'output' },
} as const;

type NodeId = keyof typeof NODES;

const EDGES: [NodeId, NodeId, number][] = [
  ['i1','h1',1.4], ['i1','h2',2.1], ['i1','h3',2.8],
  ['i2','h1',1.8], ['i2','h2',1.2], ['i2','h4',2.4],
  ['i3','h2',3.0], ['i3','h3',1.6], ['i3','h4',1.0],
  ['h1','c1',1.5], ['h2','c1',2.0], ['h2','c2',2.5],
  ['h3','c1',3.2], ['h3','c2',1.3], ['h4','c2',1.8],
  ['c1','o1',1.6], ['c1','o2',2.2], ['c1','o3',3.0],
  ['c2','o1',2.8], ['c2','o2',1.4], ['c2','o3',1.9],
];

// Stable staggered delays — never use Math.random() in JSX render
const NODE_IDS = Object.keys(NODES) as NodeId[];
const NODE_DELAYS: Record<string, number> = Object.fromEntries(
  NODE_IDS.map((id, i) => [id, i * 0.07])
);

const LAYER_COLORS: Record<string, string> = {
  input:  'rgba(99,102,241,0.9)',
  hidden: 'rgba(139,92,246,0.7)',
  core:   'rgba(167,139,250,1)',
  output: 'rgba(52,211,153,0.9)',
};

const LAYER_GLOW: Record<string, string> = {
  input:  'rgba(99,102,241,0.3)',
  hidden: 'rgba(139,92,246,0.25)',
  core:   'rgba(167,139,250,0.4)',
  output: 'rgba(52,211,153,0.3)',
};

function NeuralNetwork() {
  return (
    <svg
      viewBox="0 0 100 100"
      className="absolute inset-0 w-full h-full"
      style={{ opacity: 0.75 }}
      aria-hidden="true"
    >
      <defs>
        <filter id="node-blur">
          <feGaussianBlur stdDeviation="0.8" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      {EDGES.map(([a, b], i) => {
        const na = NODES[a]; const nb = NODES[b];
        const isOutput = nb.layer === 'output' || na.layer === 'core';
        return (
          <line
            key={i}
            x1={na.x} y1={na.y} x2={nb.x} y2={nb.y}
            stroke={isOutput ? 'rgba(52,211,153,0.2)' : 'rgba(139,92,246,0.18)'}
            strokeWidth="0.3"
          />
        );
      })}

      {EDGES.filter((_, i) => i % 3 === 0).map(([a, b, delay], i) => {
        const na = NODES[a]; const nb = NODES[b];
        const isOutput = nb.layer === 'output';
        return (
          <line
            key={`flow-${i}`}
            x1={na.x} y1={na.y} x2={nb.x} y2={nb.y}
            stroke={isOutput ? 'rgba(52,211,153,0.6)' : 'rgba(167,139,250,0.5)'}
            strokeWidth="0.4"
            strokeDasharray="4 196"
            strokeLinecap="round"
            style={{
              animation: `neural-flow ${2 + delay * 0.4}s linear infinite`,
              animationDelay: `${delay * 0.3}s`,
            }}
          />
        );
      })}

      {NODE_IDS.map(id => {
        const n = NODES[id];
        const color = LAYER_COLORS[n.layer];
        const glow  = LAYER_GLOW[n.layer];
        const r     = n.layer === 'core' ? 2.2 : n.layer === 'input' || n.layer === 'output' ? 1.6 : 1.2;
        return (
          <g key={id} style={{ animation: `auth-node-enter 0.5s ease-out both`, animationDelay: `${NODE_DELAYS[id]}s` }}>
            <circle cx={n.x} cy={n.y} r={r + 1.5} fill={glow} />
            <circle cx={n.x} cy={n.y} r={r} fill={color} filter="url(#node-blur)" />
            {n.layer === 'core' && (
              <circle
                cx={n.x} cy={n.y} r={r + 0.5}
                fill="none"
                stroke="rgba(167,139,250,0.5)"
                strokeWidth="0.3"
                style={{ animation: 'auth-ping 2.5s ease-out infinite', transformOrigin: `${n.x}px ${n.y}px` }}
              />
            )}
          </g>
        );
      })}
    </svg>
  );
}

// All 6 platforms to match the "6 AI platforms" stat
const CHIPS = [
  { label: 'GPT-4o',      bg: 'rgba(16,163,127,0.12)',  border: 'rgba(16,163,127,0.28)',  text: '#6EE7B7' },
  { label: 'Claude',      bg: 'rgba(210,162,70,0.12)',   border: 'rgba(210,162,70,0.28)',  text: '#FCD34D' },
  { label: 'Gemini',      bg: 'rgba(66,133,244,0.12)',   border: 'rgba(66,133,244,0.28)',  text: '#93C5FD' },
  { label: 'Llama',       bg: 'rgba(139,92,246,0.12)',   border: 'rgba(139,92,246,0.28)',  text: '#C4B5FD' },
  { label: 'Perplexity',  bg: 'rgba(20,184,166,0.12)',   border: 'rgba(20,184,166,0.28)',  text: '#5EEAD4' },
  { label: 'Grok',        bg: 'rgba(148,163,184,0.12)',  border: 'rgba(148,163,184,0.28)', text: '#CBD5E1' },
];

function OutputCard() {
  return (
    <div
      className="w-[228px] rounded-xl p-3.5"
      style={{
        background: 'rgba(255,255,255,0.06)',
        border: '1px solid rgba(139,92,246,0.28)',
        backdropFilter: 'blur(12px)',
        boxShadow: '0 20px 48px rgba(0,0,0,0.45)',
        animation: 'auth-node-enter 0.6s ease-out both',
        animationDelay: '0.4s',
      }}
    >
      <div className="flex items-center gap-1.5 mb-2.5">
        <div
          className="h-1.5 w-1.5 rounded-full"
          style={{ background: '#34D399', animation: 'auth-glow-pulse 2s ease-in-out infinite' }}
        />
        <span className="text-[10px] font-bold tracking-widest" style={{ color: '#34D399', letterSpacing: '0.1em' }}>
          REFINED
        </span>
      </div>
      <p className="text-[11px] leading-relaxed" style={{ color: '#CBD5E1', fontFamily: 'ui-monospace, monospace' }}>
        <span style={{ color: '#C4B5FD' }}>You are a senior writer.</span>
        {' '}Write a structured explainer on AI for tech-curious readers with 3 real-world examples.
      </p>
      <div className="mt-3 flex items-center justify-between">
        <span className="text-[10px]" style={{ color: '#94A3B8' }}>Quality score</span>
        <span className="text-[11px] font-bold" style={{ color: '#34D399' }}>91 / 100</span>
      </div>
      <div className="mt-1.5 h-1 rounded-full" style={{ background: 'rgba(255,255,255,0.08)' }}>
        <div className="h-full rounded-full" style={{ width: '91%', background: 'linear-gradient(90deg, #7c3aed, #34d399)' }} />
      </div>
    </div>
  );
}

export function AuthVisual() {
  return (
    <div
      className="relative flex h-full w-full flex-col overflow-hidden select-none"
      style={{ background: '#0b1020' }}
      aria-hidden="true"
    >
      {/* Background orbs */}
      <div className="absolute inset-0 pointer-events-none" style={{
        background:
          'radial-gradient(ellipse 60% 50% at 20% 25%, rgba(99,102,241,0.12) 0%, transparent 65%), ' +
          'radial-gradient(ellipse 50% 40% at 80% 75%, rgba(52,211,153,0.07) 0%, transparent 65%), ' +
          'radial-gradient(ellipse 40% 60% at 65% 20%, rgba(139,92,246,0.08) 0%, transparent 60%)',
      }} />

      {/* Dot grid */}
      <div className="absolute inset-0 pointer-events-none" style={{
        backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.04) 1px, transparent 1px)',
        backgroundSize: '28px 28px',
        maskImage: 'radial-gradient(ellipse 90% 90% at 50% 50%, black 30%, transparent 100%)',
      }} />

      {/* Neural network fills the whole panel as background */}
      <NeuralNetwork />

      {/* ── Top: branding, headline, stats ──────────────────────────── */}
      <div className="relative z-10 shrink-0 px-10 pt-10">

        {/* Logo */}
        <div className="flex items-center gap-2.5 mb-9">
          <div
            className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg"
            style={{ background: 'rgba(139,92,246,0.2)', border: '1px solid rgba(139,92,246,0.35)' }}
          >
            <SparklesIcon className="h-3.5 w-3.5 text-violet-400" />
          </div>
          <span className="text-[13px] font-semibold" style={{ color: '#A78BFA', letterSpacing: '-0.01em' }}>
            PromptVault Pro
          </span>
        </div>

        {/* Headline */}
        <h2
          className="font-extrabold leading-tight mb-3"
          style={{
            fontSize: 'clamp(24px, 2.6vw, 32px)',
            letterSpacing: '-0.03em',
            color: '#F1F5F9',
            textWrap: 'balance',
          } as React.CSSProperties}
        >
          Raw prompts,<br />
          <span style={{ color: '#A78BFA' }}>refined into results.</span>
        </h2>

        <p className="text-[13px] mb-8" style={{ color: '#94A3B8', lineHeight: '1.65', maxWidth: 248 }}>
          Save, organize, and refine prompts across every AI platform.
        </p>

        {/* Stats — placed directly under the pitch where users will read them */}
        <div className="flex items-start gap-8">
          {[
            { value: '50k+', label: 'Prompts refined' },
            { value: '6',    label: 'AI platforms'    },
            { value: '4.9★', label: 'User rating'     },
          ].map(s => (
            <div key={s.label}>
              <p
                className="text-[15px] font-bold"
                style={{ color: '#E2E8F0', letterSpacing: '-0.02em', fontVariantNumeric: 'tabular-nums' }}
              >
                {s.value}
              </p>
              <p className="text-[11px] mt-0.5" style={{ color: '#94A3B8' }}>
                {s.label}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Middle: grows, OutputCard anchored to bottom-right ──────── */}
      <div className="relative z-10 flex-1 flex items-end justify-end px-6 pb-5">
        <OutputCard />
      </div>

      {/* ── Bottom: platform chips ───────────────────────────────────── */}
      <div className="relative z-10 shrink-0 px-10 pb-9">
        <div className="flex flex-wrap gap-2">
          {CHIPS.map(c => (
            <div
              key={c.label}
              className="rounded-full px-2.5 py-1 text-[10px] font-semibold"
              style={{ background: c.bg, border: `1px solid ${c.border}`, color: c.text }}
            >
              {c.label}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

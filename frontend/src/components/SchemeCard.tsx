import React from 'react';
import { Calendar, Building2, ArrowRight, Clock } from 'lucide-react';

export interface SchemeData {
  id: number;
  name: string;
  launching_authority: string;
  category?: string;
  launch_date?: string;
  budget_allocated?: number;
  description?: string;
  source_url?: string;
  average_impact_score?: number;
  created_at: string;
}

interface SchemeCardProps {
  scheme: SchemeData;
  onSelect: (scheme: SchemeData) => void;
}

export const SchemeCard: React.FC<SchemeCardProps> = ({ scheme, onSelect }) => {
  const score = scheme.average_impact_score ?? 0;
  
  const getBadgeClass = (s: number) => {
    if (s >= 70) return 'score-badge-high';
    if (s >= 50) return 'score-badge-mid';
    return 'score-badge-low';
  };

  const formatCurrency = (val?: number) => {
    if (!val) return 'N/A';
    return `₹${(val / 10000000).toFixed(2)} Cr`;
  };

  const getCardGlowClass = (s: number) => {
    if (s >= 70) return 'glow-accent-emerald';
    if (s >= 50) return 'glow-accent-amber';
    return 'glow-accent-rose';
  };

  return (
    <div className={`glass-card ${getCardGlowClass(score)}`} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', marginBottom: '0.75rem' }}>
          <div>
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: '#38bdf8',
              background: 'rgba(56, 189, 248, 0.1)',
              padding: '0.2rem 0.6rem',
              borderRadius: '6px',
              border: '1px solid rgba(56, 189, 248, 0.2)'
            }}>
              {scheme.category || 'General'}
            </span>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem', lineHeight: '1.3' }}>
              {scheme.name}
            </h3>
          </div>

          <div className={getBadgeClass(score)} style={{
            padding: '0.5rem 0.85rem',
            borderRadius: '12px',
            textAlign: 'center',
            minWidth: '75px',
            flexShrink: 0
          }}>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, lineHeight: '1' }}>
              {score > 0 ? score.toFixed(1) : 'N/A'}
            </div>
            <div style={{ fontSize: '0.65rem', fontWeight: 600, textTransform: 'uppercase', marginTop: '0.15rem' }}>
              Impact Score
            </div>
          </div>
        </div>

        <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '1rem', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
          {scheme.description}
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.8rem', color: '#cbd5e1', background: 'rgba(15, 23, 42, 0.4)', padding: '0.75rem', borderRadius: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Building2 size={14} color="#94a3b8" />
            <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {scheme.launching_authority}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Calendar size={14} color="#94a3b8" />
            <span>Budget: {formatCurrency(scheme.budget_allocated)}</span>
          </div>
        </div>
      </div>

      <div style={{ paddingTop: '0.75rem', borderTop: '1px solid rgba(255, 255, 255, 0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.7rem', color: '#64748b' }}>
          <Clock size={12} />
          <span>Src: Official Portal ({new Date(scheme.created_at).toLocaleDateString()})</span>
        </div>

        <button
          onClick={() => onSelect(scheme)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            background: 'none',
            border: 'none',
            color: '#38bdf8',
            fontWeight: 700,
            fontSize: '0.85rem',
            cursor: 'pointer'
          }}
        >
          View Score Breakdown
          <ArrowRight size={14} />
        </button>
      </div>
    </div>
  );
};

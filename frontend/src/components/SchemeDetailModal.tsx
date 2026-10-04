import React, { useEffect, useState } from 'react';
import { X, ExternalLink, Activity, MessageSquare, HelpCircle } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { API_BASE } from '../api';

interface ImpactScoreDetail {
  id: number;
  district_name: string;
  score: number;
  reach_component: number;
  sentiment_component: number;
  adoption_component: number;
  shap_explanations?: {
    features: Record<string, number>;
    base_value: number;
    contributions: Record<string, number>;
  };
  computed_at: string;
}

interface Mention {
  id: number;
  source: string;
  raw_text: string;
  language: string;
  sentiment_score: number;
  sentiment_label: string;
  url: string;
  published_date: string;
}

interface SchemeDetailProps {
  schemeId: number;
  onClose: () => void;
}

export const SchemeDetailModal: React.FC<SchemeDetailProps> = ({ schemeId, onClose }) => {
  const [detail, setDetail] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/schemes/${schemeId}`)
      .then(res => res.json())
      .then(data => {
        setDetail(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching detail:', err);
        setLoading(false);
      });
  }, [schemeId]);

  if (loading) {
    return (
      <div style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.85)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
        <div style={{ color: '#38bdf8', fontWeight: 600 }}>Loading detailed metrics & SHAP analysis...</div>
      </div>
    );
  }

  if (!detail) return null;

  // Process mentions for the trend chart
  const mentionsData = [...(detail.recent_mentions || [])]
    .sort((a, b) => new Date(a.published_date).getTime() - new Date(b.published_date).getTime());

  // Aggregate by date
  const sentimentByDate: Record<string, { date: string; Positive: number; Neutral: number; Negative: number; avgScore: number; count: number }> = {};
  
  mentionsData.forEach(mention => {
    const dateStr = new Date(mention.published_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    if (!sentimentByDate[dateStr]) {
      sentimentByDate[dateStr] = {
        date: dateStr,
        Positive: 0,
        Neutral: 0,
        Negative: 0,
        avgScore: 0,
        count: 0
      };
    }
    
    const label = mention.sentiment_label || 'Neutral';
    if (label === 'Positive') sentimentByDate[dateStr].Positive += 1;
    else if (label === 'Negative') sentimentByDate[dateStr].Negative += 1;
    else sentimentByDate[dateStr].Neutral += 1;
    
    sentimentByDate[dateStr].avgScore += mention.sentiment_score || 0;
    sentimentByDate[dateStr].count += 1;
  });

  const chartData = Object.values(sentimentByDate).map(d => ({
    ...d,
    avgScore: Number((d.avgScore / d.count).toFixed(2))
  }));

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(15, 23, 42, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem',
      zIndex: 1000,
      overflowY: 'auto'
    }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '900px', maxHeight: '90vh', overflowY: 'auto', padding: '2rem', position: 'relative' }}>
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1.5rem',
            right: '1.5rem',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '50%',
            width: '36px',
            height: '36px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#f8fafc',
            cursor: 'pointer'
          }}
        >
          <X size={18} />
        </button>

        <span style={{ fontSize: '0.8rem', color: '#38bdf8', fontWeight: 700, textTransform: 'uppercase' }}>
          {detail.category}
        </span>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f8fafc', margin: '0.25rem 0 0.5rem 0' }}>
          {detail.name}
        </h2>
        <p style={{ fontSize: '0.9rem', color: '#94a3b8', marginBottom: '1.5rem' }}>
          {detail.description}
        </p>

        {/* District Impact Scores & SHAP Explainability */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <Activity size={20} color="#38bdf8" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
              District-Level Impact Breakdown & SHAP Explainability
            </h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
            {detail.impact_scores.map((iscore: ImpactScoreDetail) => (
              <div key={iscore.id} className="glass-card" style={{ padding: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>
                    District: {iscore.district_name}
                  </h4>
                  <span style={{ fontSize: '1.1rem', fontWeight: 800, color: iscore.score >= 65 ? '#34d399' : '#fbbf24' }}>
                    {iscore.score.toFixed(1)} / 100
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8rem', marginBottom: '1rem' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: '#cbd5e1', marginBottom: '0.15rem' }}>
                      <span>Reach Component (40%):</span>
                      <strong>{iscore.reach_component}%</strong>
                    </div>
                    <div style={{ height: '4px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '2px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${iscore.reach_component}%`, background: '#38bdf8' }} />
                    </div>
                  </div>

                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: '#cbd5e1', marginBottom: '0.15rem' }}>
                      <span>Budget Adoption (30%):</span>
                      <strong>{iscore.adoption_component}%</strong>
                    </div>
                    <div style={{ height: '4px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '2px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${iscore.adoption_component}%`, background: '#6366f1' }} />
                    </div>
                  </div>

                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: '#cbd5e1', marginBottom: '0.15rem' }}>
                      <span>Public Sentiment (30%):</span>
                      <strong>{iscore.sentiment_component}%</strong>
                    </div>
                    <div style={{ height: '4px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '2px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${iscore.sentiment_component}%`, background: '#10b981' }} />
                    </div>
                  </div>
                </div>

                {/* SHAP contributions */}
                {iscore.shap_explanations && (
                  <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem', borderRadius: '8px', fontSize: '0.75rem' }}>
                    <div style={{ fontWeight: 700, color: '#f8fafc', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <HelpCircle size={12} color="#38bdf8" />
                      SHAP Feature Contributions:
                    </div>
                    {Object.entries(iscore.shap_explanations.contributions).map(([feat, contrib]) => (
                      <div key={feat} style={{ display: 'flex', justifyContent: 'space-between', color: contrib >= 0 ? '#34d399' : '#f87171' }}>
                        <span>{feat.replace(/_/g, ' ')}:</span>
                        <span>{contrib >= 0 ? `+${contrib}` : contrib} pts</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Public Sentiment & Scraped Mentions */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <MessageSquare size={20} color="#38bdf8" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
              Public Sentiment & Scraped Mentions (Hindi / Hinglish / English)
            </h3>
          </div>

          {/* Sentiment Trend Chart */}
          {chartData.length > 0 ? (
            <div style={{ height: '220px', width: '100%', marginTop: '0.5rem', marginBottom: '1.5rem', background: 'rgba(15, 23, 42, 0.4)', padding: '1rem', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorPositive" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.0}/>
                    </linearGradient>
                    <linearGradient id="colorNegative" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="date" stroke="#94a3b8" fontSize={10} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} />
                  <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '8px', color: '#f8fafc', fontSize: '0.85rem' }} />
                  <Legend wrapperStyle={{ fontSize: '0.75rem', color: '#94a3b8' }} />
                  <Area type="monotone" dataKey="Positive" stroke="#10b981" fillOpacity={1} fill="url(#colorPositive)" strokeWidth={2} name="Positive Mentions" />
                  <Area type="monotone" dataKey="Negative" stroke="#f43f5e" fillOpacity={1} fill="url(#colorNegative)" strokeWidth={2} name="Negative Mentions" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8', fontSize: '0.85rem' }}>
              No sentiment history available to plot.
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {detail.recent_mentions.map((mention: Mention) => (
              <div key={mention.id} className="glass-card" style={{ padding: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.85rem', color: '#f8fafc' }}>{mention.source}</span>
                    <span style={{ fontSize: '0.7rem', color: '#94a3b8', background: 'rgba(255, 255, 255, 0.05)', padding: '0.1rem 0.4rem', borderRadius: '4px' }}>
                      {mention.language.toUpperCase()}
                    </span>
                  </div>

                  <span className={`sentiment-${mention.sentiment_label.toLowerCase()}`} style={{ fontSize: '0.75rem', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '6px' }}>
                    {mention.sentiment_label} ({mention.sentiment_score > 0 ? `+${mention.sentiment_score}` : mention.sentiment_score})
                  </span>
                </div>

                <p style={{ fontSize: '0.85rem', color: '#cbd5e1', fontStyle: 'italic', marginBottom: '0.4rem' }}>
                  "{mention.raw_text}"
                </p>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748b' }}>
                  <span>Scraped on: {new Date(mention.published_date).toLocaleDateString()}</span>
                  {mention.url && (
                    <a href={mention.url} target="_blank" rel="noreferrer" style={{ color: '#38bdf8', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                      Source Link <ExternalLink size={10} />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

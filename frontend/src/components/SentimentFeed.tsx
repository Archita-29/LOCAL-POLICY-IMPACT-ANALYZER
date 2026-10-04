import React, { useEffect, useState } from 'react';
import { MessageSquare, Filter } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface Mention {
  id: number;
  scheme_id: number;
  source: string;
  raw_text: string;
  language: string;
  sentiment_score: number;
  sentiment_label: string;
  url?: string;
  published_date: string;
}

interface Scheme {
  id: number;
  name: string;
}

export const SentimentFeed: React.FC = () => {
  const [mentions, setMentions] = useState<Mention[]>([]);
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  
  const [selectedScheme, setSelectedScheme] = useState<string>('');
  const [selectedSentiment, setSelectedSentiment] = useState<string>('');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('');

  useEffect(() => {
    fetch('http://localhost:8000/api/schemes')
      .then(res => res.json())
      .then(data => setSchemes(data))
      .catch(err => console.error('Error fetching schemes:', err));
  }, []);

  const fetchMentions = () => {
    setLoading(true);
    let url = 'http://localhost:8000/api/mentions';
    const params = new URLSearchParams();
    if (selectedScheme) params.append('scheme_id', selectedScheme);
    if (selectedSentiment) params.append('sentiment_label', selectedSentiment);
    if (params.toString()) url += `?${params.toString()}`;

    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (selectedLanguage) {
          setMentions(data.filter((m: Mention) => m.language === selectedLanguage));
        } else {
          setMentions(data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching mentions:', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchMentions();
  }, [selectedScheme, selectedSentiment, selectedLanguage]);

  const sentimentCounts = mentions.reduce((acc, m) => {
    const label = m.sentiment_label || 'Neutral';
    acc[label] = (acc[label] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const pieData = Object.entries(sentimentCounts).map(([name, value]) => ({
    name: `${name} (${value})`,
    value
  }));

  const COLORS = {
    Positive: '#10b981',
    Neutral: '#94a3b8',
    Negative: '#f43f5e'
  };

  const getSchemeName = (id: number) => {
    const s = schemes.find(x => x.id === id);
    return s ? s.name : 'Unknown Scheme';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <MessageSquare color="#38bdf8" size={24} />
            Public Sentiment & Ingestion Feed
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.6' }}>
            Real-time feed aggregating comments, social mentions, and state news reviews in Hindi, English, and Hinglish. 
            The system runs these texts through our MuRIL/IndicBERT pipeline to compute sentiment scores.
          </p>
        </div>

        <div className="glass-panel" style={{ padding: '1rem', height: '180px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.25rem' }}>
            Sentiment Distribution Volume
          </span>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height="80%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={35}
                  outerRadius={55}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry) => {
                    const label = entry.name.split(' ')[0] as keyof typeof COLORS;
                    return <Cell key={entry.name} fill={COLORS[label] || '#cbd5e1'} />;
                  })}
                </Pie>
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', color: '#f8fafc', fontSize: '0.75rem' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <span style={{ fontSize: '0.75rem', color: '#94a3b8', padding: '2rem' }}>No data</span>
          )}
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '1rem 1.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Filter size={16} color="#94a3b8" />
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#f8fafc' }}>Filters:</span>
        </div>

        <select
          value={selectedScheme}
          onChange={e => setSelectedScheme(e.target.value)}
          style={{ background: 'rgba(30, 41, 59, 0.9)', color: '#f8fafc', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px', padding: '0.5rem 0.75rem', fontSize: '0.8rem', cursor: 'pointer' }}
        >
          <option value="">All Schemes</option>
          {schemes.map(s => (
            <option key={s.id} value={s.id}>{s.name.slice(0, 30)}...</option>
          ))}
        </select>

        <select
          value={selectedSentiment}
          onChange={e => setSelectedSentiment(e.target.value)}
          style={{ background: 'rgba(30, 41, 59, 0.9)', color: '#f8fafc', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px', padding: '0.5rem 0.75rem', fontSize: '0.8rem', cursor: 'pointer' }}
        >
          <option value="">All Sentiments</option>
          <option value="Positive">Positive</option>
          <option value="Neutral">Neutral</option>
          <option value="Negative">Negative</option>
        </select>

        <select
          value={selectedLanguage}
          onChange={e => setSelectedLanguage(e.target.value)}
          style={{ background: 'rgba(30, 41, 59, 0.9)', color: '#f8fafc', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px', padding: '0.5rem 0.75rem', fontSize: '0.8rem', cursor: 'pointer' }}
        >
          <option value="">All Languages</option>
          <option value="hi">Hindi (hi)</option>
          <option value="en">English (en)</option>
          <option value="hi-en">Hinglish (hi-en)</option>
        </select>
      </div>

      {loading ? (
        <div style={{ padding: '4rem 0', textAlign: 'center', color: '#94a3b8' }}>
          Loading public sentiment feed...
        </div>
      ) : mentions.length === 0 ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>
          No mentions found matching the filters.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {mentions.map(m => (
            <div key={m.id} className="glass-card" style={{ padding: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', marginBottom: '0.5rem' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', color: '#38bdf8', fontWeight: 700 }}>
                    {getSchemeName(m.scheme_id)}
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.2rem' }}>
                    <span style={{ fontWeight: 800, fontSize: '0.85rem', color: '#f8fafc' }}>{m.source}</span>
                    <span style={{ fontSize: '0.65rem', color: '#94a3b8', background: 'rgba(255,255,255,0.05)', padding: '0.1rem 0.4rem', borderRadius: '4px' }}>
                      {m.language.toUpperCase()}
                    </span>
                  </div>
                </div>

                <span className={`sentiment-${m.sentiment_label.toLowerCase()}`} style={{ fontSize: '0.75rem', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '6px' }}>
                  {m.sentiment_label} ({m.sentiment_score > 0 ? `+${Number(m.sentiment_score).toFixed(2)}` : Number(m.sentiment_score).toFixed(2)})
                </span>
              </div>

              <p style={{ fontSize: '0.85rem', color: '#cbd5e1', fontStyle: 'italic', marginBottom: '0.6rem' }}>
                "{m.raw_text}"
              </p>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.7rem', color: '#64748b' }}>
                <span>Scraped: {new Date(m.published_date).toLocaleString()}</span>
                {m.url && (
                  <a href={m.url} target="_blank" rel="noreferrer" style={{ color: '#38bdf8', textDecoration: 'none', display: 'flex', alignItems: 'center' }}>
                    Source Link
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

import React, { useEffect, useState } from 'react';
import { Scale, ArrowRightLeft } from 'lucide-react';
import type { SchemeData } from './SchemeCard';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export const ComparisonView: React.FC = () => {
  const [schemes, setSchemes] = useState<SchemeData[]>([]);
  const [scheme1Id, setScheme1Id] = useState<number | null>(null);
  const [scheme2Id, setScheme2Id] = useState<number | null>(null);
  const [comparison, setComparison] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const [loadingChart, setLoadingChart] = useState<boolean>(false);

  useEffect(() => {
    fetch('http://localhost:8000/api/schemes')
      .then(res => res.json())
      .then(data => {
        setSchemes(data);
        if (data.length >= 2) {
          setScheme1Id(data[0].id);
          setScheme2Id(data[1].id);
        }
      })
      .catch(err => console.error('Error fetching schemes:', err));
  }, []);

  useEffect(() => {
    if (!scheme1Id || !scheme2Id) return;

    setLoadingChart(true);
    fetch(`http://localhost:8000/api/comparison?scheme1_id=${scheme1Id}&scheme2_id=${scheme2Id}`)
      .then(res => res.json())
      .then(data => setComparison(data))
      .catch(err => console.error('Error fetching comparison:', err));

    Promise.all([
      fetch(`http://localhost:8000/api/schemes/${scheme1Id}`).then(res => res.json()),
      fetch(`http://localhost:8000/api/schemes/${scheme2Id}`).then(res => res.json())
    ])
      .then(([s1, s2]) => {
        const getAvgComponents = (scores: any[]) => {
          if (!scores || scores.length === 0) return { reach: 0, sentiment: 0, adoption: 0 };
          let sumReach = 0, sumSentiment = 0, sumAdoption = 0;
          scores.forEach(s => {
            sumReach += s.reach_component || 0;
            sumSentiment += s.sentiment_component || 0;
            sumAdoption += s.adoption_component || 0;
          });
          return {
            reach: Number((sumReach / scores.length).toFixed(1)),
            sentiment: Number((sumSentiment / scores.length).toFixed(1)),
            adoption: Number((sumAdoption / scores.length).toFixed(1))
          };
        };

        const s1Avg = getAvgComponents(s1.impact_scores);
        const s2Avg = getAvgComponents(s2.impact_scores);

        const s1Name = s1.name.length > 25 ? s1.name.slice(0, 25) + '...' : s1.name;
        const s2Name = s2.name.length > 25 ? s2.name.slice(0, 25) + '...' : s2.name;

        setChartData([
          {
            metric: 'Reach %',
            [s1Name]: s1Avg.reach,
            [s2Name]: s2Avg.reach,
          },
          {
            metric: 'Public Sentiment %',
            [s1Name]: s1Avg.sentiment,
            [s2Name]: s2Avg.sentiment,
          },
          {
            metric: 'Budget Adoption %',
            [s1Name]: s1Avg.adoption,
            [s2Name]: s2Avg.adoption,
          }
        ]);
        setLoadingChart(false);
      })
      .catch(err => {
        console.error('Error fetching scheme details for comparison chart:', err);
        setLoadingChart(false);
      });
  }, [scheme1Id, scheme2Id]);

  const getGlowClass = (score: number) => {
    if (score >= 70) return 'glow-accent-emerald';
    if (score >= 50) return 'glow-accent-amber';
    return 'glow-accent-rose';
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Scale color="#38bdf8" size={20} />
          NGO & Journalist Side-by-Side Scheme Comparison
        </h2>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
          Compare performance, budget utilization efficiency, and public sentiment between two schemes.
        </p>
      </div>

      {/* Dropdown selectors */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '1rem', alignItems: 'center' }}>
        <div>
          <label style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 600, display: 'block', marginBottom: '0.3rem' }}>
            Scheme A:
          </label>
          <select
            value={scheme1Id ?? ''}
            onChange={(e) => setScheme1Id(Number(e.target.value))}
            style={{
              width: '100%',
              background: 'rgba(30, 41, 59, 0.9)',
              color: '#f8fafc',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              borderRadius: '8px',
              padding: '0.6rem 1rem',
              fontSize: '0.9rem',
              fontWeight: 600
            }}
          >
            {schemes.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>

        <div style={{ padding: '0.5rem', background: 'rgba(56, 189, 248, 0.1)', borderRadius: '50%', color: '#38bdf8' }}>
          <ArrowRightLeft size={20} />
        </div>

        <div>
          <label style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 600, display: 'block', marginBottom: '0.3rem' }}>
            Scheme B:
          </label>
          <select
            value={scheme2Id ?? ''}
            onChange={(e) => setScheme2Id(Number(e.target.value))}
            style={{
              width: '100%',
              background: 'rgba(30, 41, 59, 0.9)',
              color: '#f8fafc',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              borderRadius: '8px',
              padding: '0.6rem 1rem',
              fontSize: '0.9rem',
              fontWeight: 600
            }}
          >
            {schemes.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Comparison Grid */}
      {comparison && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '1rem' }}>
          {/* Card Scheme A */}
          <div className={`glass-card ${getGlowClass(comparison.scheme1.average_impact_score)}`} style={{ padding: '1.5rem', borderLeft: '4px solid #6366f1' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#6366f1', textTransform: 'uppercase' }}>
              {comparison.scheme1.category}
            </span>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc', marginTop: '0.25rem' }}>
              {comparison.scheme1.name}
            </h3>

            <div style={{ margin: '1.5rem 0', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Impact Score</span>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: '#38bdf8' }}>
                  {comparison.scheme1.average_impact_score} / 100
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Budget Allocated</span>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
                  ₹{(comparison.scheme1.budget_allocated / 10000000).toFixed(2)} Cr
                </div>
              </div>
            </div>
          </div>

          {/* Card Scheme B */}
          <div className={`glass-card ${getGlowClass(comparison.scheme2.average_impact_score)}`} style={{ padding: '1.5rem', borderLeft: '4px solid #38bdf8' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase' }}>
              {comparison.scheme2.category}
            </span>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc', marginTop: '0.25rem' }}>
              {comparison.scheme2.name}
            </h3>

            <div style={{ margin: '1.5rem 0', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Impact Score</span>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: '#10b981' }}>
                  {comparison.scheme2.average_impact_score} / 100
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Budget Allocated</span>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
                  ₹{(comparison.scheme2.budget_allocated / 10000000).toFixed(2)} Cr
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Component Chart Comparison */}
      {comparison && chartData.length > 0 && (
        <div style={{ marginTop: '1.5rem', background: 'rgba(15, 23, 42, 0.4)', padding: '1.5rem', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1rem' }}>
            Detailed Performance Metrics Comparison (%)
          </h3>
          {loadingChart ? (
            <div style={{ height: '260px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#94a3b8' }}>
              Loading performance breakdown...
            </div>
          ) : (
            <div style={{ height: '300px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: -10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
                  <XAxis dataKey="metric" stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} domain={[0, 100]} />
                  <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '8px', color: '#f8fafc', fontSize: '0.85rem' }} />
                  <Legend wrapperStyle={{ fontSize: '0.75rem', paddingTop: '10px' }} />
                  {Object.keys(chartData[0])
                    .filter(key => key !== 'metric')
                    .map((schemeName, idx) => (
                      <Bar
                        key={schemeName}
                        dataKey={schemeName}
                        fill={idx === 0 ? '#6366f1' : '#38bdf8'}
                        radius={[4, 4, 0, 0]}
                        maxBarSize={40}
                      />
                    ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

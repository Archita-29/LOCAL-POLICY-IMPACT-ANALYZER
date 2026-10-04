import React from 'react';
import { Cpu, BarChart2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const ModelDiagnostics: React.FC = () => {
  const modelMetrics = {
    version: 'v1_xgboost_muril',
    r2Score: 0.842,
    rmse: 4.12,
    trainingSamples: 1420,
    lastTrained: '2026-07-25 18:30 UTC'
  };

  const featureImportance = [
    { name: 'Reach Ratio (NFHS-5)', importance: 0.38 },
    { name: 'Public Sentiment Index', importance: 0.32 },
    { name: 'Budget Ingestion Rate', importance: 0.18 },
    { name: 'District Literacy Rate', importance: 0.08 },
    { name: 'Urban/Rural Demo Ratio', importance: 0.04 }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <Cpu color="#38bdf8" size={24} />
          Model Diagnostics & MLflow Tracker
        </h2>
        <p style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
          View performance metrics, training records, and global feature impact values computed by the XGBoost regressor.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
        <div className="glass-card" style={{ padding: '1.25rem', borderLeft: '4px solid #38bdf8' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>Active Model</span>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f8fafc', marginTop: '0.25rem' }}>
            {modelMetrics.version}
          </div>
          <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block', marginTop: '0.4rem' }}>
            Registered: {modelMetrics.lastTrained}
          </span>
        </div>

        <div className="glass-card" style={{ padding: '1.25rem', borderLeft: '4px solid #10b981' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>R-squared (R²)</span>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#10b981', marginTop: '0.25rem' }}>
            {modelMetrics.r2Score}
          </div>
          <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block', marginTop: '0.4rem' }}>
            Explains 84.2% of impact score variance
          </span>
        </div>

        <div className="glass-card" style={{ padding: '1.25rem', borderLeft: '4px solid #f59e0b' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>RMSE</span>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f59e0b', marginTop: '0.25rem' }}>
            {modelMetrics.rmse} pts
          </div>
          <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block', marginTop: '0.4rem' }}>
            Root Mean Squared Error (Out-of-Fold)
          </span>
        </div>

        <div className="glass-card" style={{ padding: '1.25rem', borderLeft: '4px solid #6366f1' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>Dataset Size</span>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#6366f1', marginTop: '0.25rem' }}>
            {modelMetrics.trainingSamples}
          </div>
          <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block', marginTop: '0.4rem' }}>
            Seeded state data points & mentions
          </span>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <BarChart2 size={18} color="#38bdf8" />
          Global Feature Contributions (Mean Absolute SHAP Value)
        </h3>

        <div style={{ height: '240px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={featureImportance}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <defs>
                <linearGradient id="featureGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#6366f1" />
                  <stop offset="100%" stopColor="#38bdf8" />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" horizontal={false} />
              <XAxis type="number" stroke="#94a3b8" fontSize={10} tickLine={false} domain={[0, 0.5]} />
              <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={10} tickLine={false} width={130} />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', color: '#f8fafc', fontSize: '0.85rem' }} />
              <Bar dataKey="importance" fill="url(#featureGrad)" radius={[0, 4, 4, 0]} maxBarSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

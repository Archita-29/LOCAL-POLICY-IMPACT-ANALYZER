import React from 'react';
import { Play, TrendingUp } from 'lucide-react';

export const PolicySimulator: React.FC = () => {
  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Play color="#38bdf8" size={24} />
          Policy Impact Simulator (What-If Analysis)
        </h2>
        <p style={{ fontSize: '0.85rem', color: '#cbd5e1', marginTop: '0.5rem' }}>
          Adjust budget allocations and outreach parameters to simulate projected changes in scheme impact scores.
        </p>
      </div>
      <div style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8', border: '1px dashed rgba(255,255,255,0.1)', borderRadius: '10px' }}>
        <TrendingUp size={48} color="#64748b" style={{ margin: '0 auto 1rem' }} />
        <h3 style={{ fontSize: '1.1rem', color: '#f8fafc', marginBottom: '0.5rem' }}>Simulator Engine Offline</h3>
        <p>The predictive simulation engine is currently being trained. Check back after ML Phase 3 is completed.</p>
      </div>
    </div>
  );
};

import React from 'react';
import { AlertTriangle } from 'lucide-react';

export const DisclaimerBanner: React.FC = () => {
  return (
    <div style={{
      background: 'linear-gradient(90deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.15) 100%)',
      borderBottom: '1px solid rgba(245, 158, 11, 0.3)',
      padding: '0.6rem 1.5rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '0.75rem',
      fontSize: '0.85rem',
      color: '#fef3c7'
    }}>
      <AlertTriangle size={16} color="#fbbf24" style={{ flexShrink: 0 }} />
      <span>
        <strong>Notice:</strong> Impact scores are <em>estimated, model-generated rankings</em> combining ground reach, sentiment, and budget adoption. They are not official government ground truth.
      </span>
    </div>
  );
};

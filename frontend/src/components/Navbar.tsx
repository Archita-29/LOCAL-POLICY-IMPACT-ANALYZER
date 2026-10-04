import React from 'react';
import { ShieldCheck, Map, BarChart3, Layers, MessageSquare, Cpu, Play } from 'lucide-react';

interface NavbarProps {
  activeTab: 'schemes' | 'map' | 'comparison' | 'feed' | 'ml_details' | 'simulator';
  setActiveTab: (tab: 'schemes' | 'map' | 'comparison' | 'feed' | 'ml_details' | 'simulator') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <nav style={{
      background: 'rgba(15, 23, 42, 0.8)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
      padding: '1rem 2rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{
          width: '40px',
          height: '40px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #6366f1 0%, #38bdf8 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 12px rgba(56, 189, 248, 0.3)'
        }}>
          <ShieldCheck size={24} color="#ffffff" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}>
            Local Policy Impact Analyzer
          </h1>
          <p style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
            Data-Driven Ground Impact Tracking • Maharashtra State
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(30, 41, 59, 0.6)', padding: '0.25rem', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.05)', flexWrap: 'wrap' }}>
        <button
          onClick={() => setActiveTab('schemes')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            border: 'none',
            background: activeTab === 'schemes' ? 'linear-gradient(135deg, #6366f1 0%, #38bdf8 100%)' : 'transparent',
            color: activeTab === 'schemes' ? '#ffffff' : '#94a3b8',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
        >
          <Layers size={16} />
          Schemes
        </button>

        <button
          onClick={() => setActiveTab('map')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            border: 'none',
            background: activeTab === 'map' ? 'linear-gradient(135deg, #6366f1 0%, #38bdf8 100%)' : 'transparent',
            color: activeTab === 'map' ? '#ffffff' : '#94a3b8',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
        >
          <Map size={16} />
          Choropleth Map
        </button>

        <button
          onClick={() => setActiveTab('comparison')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            border: 'none',
            background: activeTab === 'comparison' ? 'linear-gradient(135deg, #6366f1 0%, #38bdf8 100%)' : 'transparent',
            color: activeTab === 'comparison' ? '#ffffff' : '#94a3b8',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
        >
          <BarChart3 size={16} />
          NGO Comparison
        </button>

        <button
          onClick={() => setActiveTab('feed')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            border: 'none',
            background: activeTab === 'feed' ? 'linear-gradient(135deg, #6366f1 0%, #38bdf8 100%)' : 'transparent',
            color: activeTab === 'feed' ? '#ffffff' : '#94a3b8',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
        >
          <MessageSquare size={16} />
          Sentiment Feed
        </button>

        <button
          onClick={() => setActiveTab('ml_details')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            border: 'none',
            background: activeTab === 'ml_details' ? 'linear-gradient(135deg, #6366f1 0%, #38bdf8 100%)' : 'transparent',
            color: activeTab === 'ml_details' ? '#ffffff' : '#94a3b8',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
        >
          <Cpu size={16} />
          Model Diagnostics
        </button>

        <button
          onClick={() => setActiveTab('simulator')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            border: 'none',
            background: activeTab === 'simulator' ? 'linear-gradient(135deg, #6366f1 0%, #38bdf8 100%)' : 'transparent',
            color: activeTab === 'simulator' ? '#ffffff' : '#94a3b8',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
        >
          <Play size={16} />
          Policy Simulator
        </button>
      </div>
    </nav>
  );
};

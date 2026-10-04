import React, { useEffect, useState } from 'react';
import { DisclaimerBanner } from './components/DisclaimerBanner';
import { Navbar } from './components/Navbar';
import { SchemeCard } from './components/SchemeCard';
import type { SchemeData } from './components/SchemeCard';
import { SchemeDetailModal } from './components/SchemeDetailModal';
import { DistrictMap } from './components/DistrictMap';
import { ComparisonView } from './components/ComparisonView';
import { SentimentFeed } from './components/SentimentFeed';
import { ModelDiagnostics } from './components/ModelDiagnostics';
import { PolicySimulator } from './components/PolicySimulator';
import { Search, Filter, RefreshCw, Layers } from 'lucide-react';
import { API_BASE } from './api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'schemes' | 'map' | 'comparison' | 'feed' | 'ml_details' | 'simulator'>('schemes');
  const [schemes, setSchemes] = useState<SchemeData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [debouncedSearch, setDebouncedSearch] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedSchemeId, setSelectedSchemeId] = useState<number | null>(null);
  const [schemeLevel, setSchemeLevel] = useState<'state' | 'central'>('state');

  // Debounce search query to prevent continuous network requests on keystrokes
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);
    return () => clearTimeout(handler);
  }, [searchQuery]);

  const fetchSchemes = () => {
    setLoading(true);
    let url = `${API_BASE}/api/schemes`;
    const params = new URLSearchParams();
    if (debouncedSearch) params.append('search', debouncedSearch);
    if (selectedCategory) params.append('category', selectedCategory);
    if (schemeLevel) params.append('level', schemeLevel);
    if (params.toString()) url += `?${params.toString()}`;

    fetch(url)
      .then(res => res.json())
      .then(data => {
        setSchemes(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching schemes:', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchSchemes();
  }, [debouncedSearch, selectedCategory, schemeLevel]);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <DisclaimerBanner />
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main style={{ flex: 1, padding: '2rem', maxWidth: '1280px', width: '100%', margin: '0 auto' }}>
        {activeTab === 'schemes' && (
          <div>
            {/* Search & Filter Bar */}
            <div className="glass-panel" style={{ padding: '1.25rem', marginBottom: '2rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: 1, minWidth: '280px', background: 'rgba(30, 41, 59, 0.6)', padding: '0.6rem 1rem', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
                <Search size={18} color="#94a3b8" />
                <input
                  type="text"
                  placeholder="Search schemes by name or keywords..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    outline: 'none',
                    color: '#f8fafc',
                    fontSize: '0.9rem',
                    width: '100%'
                  }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Filter size={18} color="#94a3b8" />
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  style={{
                    background: 'rgba(30, 41, 59, 0.9)',
                    color: '#f8fafc',
                    border: '1px solid rgba(255, 255, 255, 0.15)',
                    borderRadius: '8px',
                    padding: '0.6rem 1rem',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  <option value="">All Categories</option>
                  {Array.from(new Set(schemes.map(s => s.category).filter(Boolean))).map(cat => (
                    <option key={String(cat)} value={String(cat)}>{String(cat)}</option>
                  ))}
                </select>

                <button
                  onClick={fetchSchemes}
                  style={{
                    background: 'rgba(56, 189, 248, 0.1)',
                    border: '1px solid rgba(56, 189, 248, 0.2)',
                    color: '#38bdf8',
                    padding: '0.6rem',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                  title="Refresh data"
                >
                  <RefreshCw size={16} />
                </button>
              </div>
            </div>

            {/* Scheme List Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
                  <Layers color="#38bdf8" size={20} />
                  {schemeLevel === 'state' ? 'State Schemes' : 'Central Schemes'} ({schemes.length})
                </h2>
                
                <div style={{ display: 'flex', background: 'rgba(30, 41, 59, 0.6)', borderRadius: '8px', padding: '0.2rem' }}>
                  <button
                    onClick={() => setSchemeLevel('state')}
                    style={{
                      background: schemeLevel === 'state' ? 'rgba(56, 189, 248, 0.2)' : 'transparent',
                      color: schemeLevel === 'state' ? '#38bdf8' : '#94a3b8',
                      border: 'none',
                      padding: '0.4rem 1rem',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontWeight: 600,
                      fontSize: '0.85rem'
                    }}
                  >
                    State
                  </button>
                  <button
                    onClick={() => setSchemeLevel('central')}
                    style={{
                      background: schemeLevel === 'central' ? 'rgba(56, 189, 248, 0.2)' : 'transparent',
                      color: schemeLevel === 'central' ? '#38bdf8' : '#94a3b8',
                      border: 'none',
                      padding: '0.4rem 1rem',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontWeight: 600,
                      fontSize: '0.85rem'
                    }}
                  >
                    Central
                  </button>
                </div>
              </div>
              <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                Sorted by computed Impact Score
              </span>
            </div>

            {loading ? (
              <div style={{ textAlign: 'center', padding: '4rem 0', color: '#94a3b8' }}>
                Loading schemes and computing impact metrics...
              </div>
            ) : schemes.length === 0 ? (
              <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>
                No schemes found matching your search criteria.
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '1.5rem' }}>
                {schemes.map(s => (
                  <SchemeCard
                    key={s.id}
                    scheme={s}
                    onSelect={(selected) => setSelectedSchemeId(selected.id)}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'map' && <DistrictMap />}
        {activeTab === 'comparison' && <ComparisonView />}
        {activeTab === 'feed' && <SentimentFeed />}
        {activeTab === 'ml_details' && <ModelDiagnostics />}
        {activeTab === 'simulator' && <PolicySimulator />}
      </main>

      {/* Scheme Detail Modal */}
      {selectedSchemeId && (
        <SchemeDetailModal
          schemeId={selectedSchemeId}
          onClose={() => setSelectedSchemeId(null)}
        />
      )}
    </div>
  );
};

export default App;

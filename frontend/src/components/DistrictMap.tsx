import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Popup, CircleMarker } from 'react-leaflet';
import { Layers } from 'lucide-react';

interface RegionData {
  id: number;
  state: string;
  district: string;
  population: number;
  demographic_stats?: {
    literacy_rate?: number;
    sex_ratio?: number;
    urban_ratio?: number;
  };
}

interface SchemeOption {
  id: number;
  name: string;
  average_impact_score: number;
}

// Center coordinates for districts in Maharashtra
const DISTRICT_COORDS: Record<string, [number, number]> = {
  Pune: [18.5204, 73.8567],
  Mumbai: [19.0760, 72.8777],
  Nagpur: [21.1458, 79.0882]
};

export const DistrictMap: React.FC = () => {
  const [regions, setRegions] = useState<RegionData[]>([]);
  const [schemes, setSchemes] = useState<SchemeOption[]>([]);
  const [selectedSchemeId, setSelectedSchemeId] = useState<number | null>(null);
  const [regionScores, setRegionScores] = useState<Record<number, any>>({});

  useEffect(() => {
    // Fetch regions
    fetch('http://localhost:8000/api/regions')
      .then(res => res.json())
      .then(data => setRegions(data))
      .catch(err => console.error('Error fetching regions:', err));

    // Fetch schemes
    fetch('http://localhost:8000/api/schemes')
      .then(res => res.json())
      .then(data => {
        setSchemes(data);
        if (data.length > 0) {
          setSelectedSchemeId(data[0].id);
        }
      })
      .catch(err => console.error('Error fetching schemes:', err));
  }, []);

  useEffect(() => {
    if (!selectedSchemeId) return;

    fetch(`http://localhost:8000/api/schemes/${selectedSchemeId}`)
      .then(res => res.json())
      .then(data => {
        const scoreMap: Record<number, any> = {};
        data.impact_scores.forEach((iscore: any) => {
          scoreMap[iscore.region_id] = iscore;
        });
        setRegionScores(scoreMap);
      })
      .catch(err => console.error('Error fetching scheme scores:', err));
  }, [selectedSchemeId]);

  const getColor = (score?: number) => {
    if (!score) return '#94a3b8';
    if (score >= 70) return '#10b981'; // Green
    if (score >= 60) return '#38bdf8'; // Blue
    if (score >= 50) return '#f59e0b'; // Amber
    return '#f43f5e'; // Red
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Layers color="#38bdf8" size={20} />
            Maharashtra District Choropleth Map
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
            Visualizing district-level Impact Scores (Estimated, Model-Generated)
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <label style={{ fontSize: '0.85rem', color: '#cbd5e1', fontWeight: 600 }}>Select Scheme:</label>
          <select
            value={selectedSchemeId ?? ''}
            onChange={(e) => setSelectedSchemeId(Number(e.target.value))}
            style={{
              background: 'rgba(30, 41, 59, 0.9)',
              color: '#f8fafc',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              borderRadius: '8px',
              padding: '0.5rem 1rem',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            {schemes.map(s => (
              <option key={s.id} value={s.id}>
                {s.name} (Avg: {s.average_impact_score})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Map Container */}
      <MapContainer
        center={[19.25, 75.5]}
        zoom={6}
        scrollWheelZoom={false}
        style={{ height: '480px', width: '100%', borderRadius: '12px', overflow: 'hidden' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {regions.map(r => {
          const coords = DISTRICT_COORDS[r.district];
          if (!coords) return null;

          const iscore = regionScores[r.id];
          const scoreVal = iscore?.score;
          const markerColor = getColor(scoreVal);

          return (
            <CircleMarker
              key={r.id}
              center={coords}
              radius={24}
              pathOptions={{
                fillColor: markerColor,
                fillOpacity: 0.85,
                color: '#ffffff',
                weight: 2
              }}
            >
              <Popup>
                <div style={{ color: '#f8fafc', fontSize: '0.85rem' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#38bdf8', marginBottom: '0.4rem' }}>
                    {r.district} District
                  </h3>
                  <div style={{ marginBottom: '0.4rem', fontWeight: 700 }}>
                    Impact Score: <span style={{ color: markerColor }}>{scoreVal ? `${scoreVal.toFixed(1)} / 100` : 'N/A'}</span>
                  </div>
                  {iscore && (
                    <div style={{ fontSize: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.2rem', marginBottom: '0.4rem', color: '#cbd5e1' }}>
                      <div>• Reach Component: <strong>{iscore.reach_component}%</strong></div>
                      <div>• Budget Adoption: <strong>{iscore.adoption_component}%</strong></div>
                      <div>• Public Sentiment: <strong>{iscore.sentiment_component}%</strong></div>
                    </div>
                  )}
                  <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '0.4rem', fontSize: '0.7rem', color: '#94a3b8' }}>
                    <div>Population: {r.population.toLocaleString()}</div>
                    {r.demographic_stats && <div>Literacy Rate: {r.demographic_stats.literacy_rate}%</div>}
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {/* Map Legend */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1.5rem', fontSize: '0.8rem', color: '#cbd5e1', paddingTop: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#10b981' }} />
          <span>High Impact (&ge; 70)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#38bdf8' }} />
          <span>Moderate (60 - 69)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#f59e0b' }} />
          <span>Low (50 - 59)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#f43f5e' }} />
          <span>Needs Intervention (&lt; 50)</span>
        </div>
      </div>
    </div>
  );
};

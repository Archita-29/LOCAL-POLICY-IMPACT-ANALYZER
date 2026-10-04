/**
 * Mock Data & API Interceptor
 * ---------------------------
 * Provides realistic dummy data for every API endpoint so the frontend
 * can be previewed without the FastAPI backend running.
 *
 * Usage: import './mockData' in main.tsx (before App mount).
 */

// ─── Scheme Data ────────────────────────────────────────────────────────────

export interface MockScheme {
  id: number;
  name: string;
  launching_authority: string;
  category: string;
  launch_date: string;
  budget_allocated: number;
  description: string;
  source_url: string;
  average_impact_score: number;
  created_at: string;
}

const schemes: MockScheme[] = [
  {
    id: 1,
    name: 'Majhi Ladki Bahin Yojana',
    launching_authority: 'Department of Women & Child Development, Maharashtra',
    category: 'Social Welfare & Pension',
    launch_date: '2024-06-28',
    budget_allocated: 460000000000,
    description: 'Monthly financial assistance of ₹1,500 to eligible women aged 21-65 years across Maharashtra to promote economic independence and social security. Covers approximately 2.5 crore women beneficiaries.',
    source_url: 'https://womenchild.maharashtra.gov.in',
    average_impact_score: 78.4,
    created_at: '2026-07-20T12:00:00Z'
  },
  {
    id: 2,
    name: 'Maharashtra Swadhar Yojana',
    launching_authority: 'Department of Social Justice, Maharashtra',
    category: 'Education & Scholarship',
    launch_date: '2003-01-15',
    budget_allocated: 12000000000,
    description: 'Scholarship and hostel expense support for SC/NB/DT/VJ/SBC students pursuing post-matriculation education in Maharashtra. Covers tuition fees, exam fees, and maintenance allowance.',
    source_url: 'https://sjsa.maharashtra.gov.in',
    average_impact_score: 72.1,
    created_at: '2026-07-20T12:00:00Z'
  },
  {
    id: 3,
    name: 'Mukhyamantri Vayoshri Yojana',
    launching_authority: 'Department of Social Justice, Maharashtra',
    category: 'Social Welfare & Pension',
    launch_date: '2023-03-01',
    budget_allocated: 8500000000,
    description: 'Monthly pension of ₹1,000 to senior citizens (above 65) from BPL families across all districts of Maharashtra. Aims to provide financial security to the elderly population.',
    source_url: 'https://sjsa.maharashtra.gov.in',
    average_impact_score: 65.7,
    created_at: '2026-07-20T12:00:00Z'
  },
  {
    id: 4,
    name: 'Jalyukt Shivar Abhiyan 2.0',
    launching_authority: 'Water Conservation Department, Maharashtra',
    category: 'Agriculture & Rural Dev',
    launch_date: '2024-12-01',
    budget_allocated: 65000000000,
    description: 'Water conservation and drought-proofing programme targeting rain-fed districts. Includes deepening of farm ponds, nala bunding, cement check dams, and compartment bunding across 5,000+ villages.',
    source_url: 'https://water.maharashtra.gov.in',
    average_impact_score: 58.3,
    created_at: '2026-07-20T12:00:00Z'
  },
  {
    id: 5,
    name: 'Pradhan Mantri Awas Yojana – Gramin',
    launching_authority: 'Ministry of Rural Development, Government of India',
    category: 'Housing & Infrastructure',
    launch_date: '2016-04-01',
    budget_allocated: 480000000000,
    description: 'Central scheme providing financial assistance for construction of pucca houses with basic amenities to houseless and those living in kutcha/dilapidated houses in rural areas.',
    source_url: 'https://pmayg.nic.in',
    average_impact_score: 81.2,
    created_at: '2026-07-20T12:00:00Z'
  },
  {
    id: 6,
    name: 'PM Kisan Samman Nidhi',
    launching_authority: 'Ministry of Agriculture, Government of India',
    category: 'Agriculture & Rural Dev',
    launch_date: '2019-02-01',
    budget_allocated: 600000000000,
    description: 'Direct benefit transfer of ₹6,000 per year in three equal installments to small and marginal farmer families having cultivable land holding up to 2 hectares.',
    source_url: 'https://pmkisan.gov.in',
    average_impact_score: 74.9,
    created_at: '2026-07-20T12:00:00Z'
  },
  {
    id: 7,
    name: 'Ayushman Bharat - PMJAY',
    launching_authority: 'Ministry of Health, Government of India',
    category: 'Healthcare',
    launch_date: '2018-09-23',
    budget_allocated: 640000000000,
    description: 'Flagship health insurance scheme providing coverage of ₹5 lakh per family per year for secondary and tertiary hospitalization. Covers over 1,950 medical procedures across empaneled hospitals.',
    source_url: 'https://pmjay.gov.in',
    average_impact_score: 69.5,
    created_at: '2026-07-20T12:00:00Z'
  },
  {
    id: 8,
    name: 'Maharashtra Lek Ladki Yojana',
    launching_authority: 'Department of Women & Child Development, Maharashtra',
    category: 'Education & Scholarship',
    launch_date: '2023-04-01',
    budget_allocated: 25000000000,
    description: 'Staged financial assistance for girls from ₹5,000 at birth to ₹1,00,000 at age 18 to families with yellow/orange ration cards, incentivizing girl child education and reducing dropout rates.',
    source_url: 'https://womenchild.maharashtra.gov.in',
    average_impact_score: 44.8,
    created_at: '2026-07-20T12:00:00Z'
  }
];

// ─── Region Data ────────────────────────────────────────────────────────────

export interface MockRegion {
  id: number;
  state: string;
  district: string;
  population: number;
  demographic_stats: {
    literacy_rate: number;
    sex_ratio: number;
    urban_ratio: number;
  };
  geo_boundary: string | null;
}

const regions: MockRegion[] = [
  { id: 1, state: 'Maharashtra', district: 'Pune', population: 9429408, demographic_stats: { literacy_rate: 86.15, sex_ratio: 910, urban_ratio: 60.9 }, geo_boundary: null },
  { id: 2, state: 'Maharashtra', district: 'Mumbai', population: 12442373, demographic_stats: { literacy_rate: 89.73, sex_ratio: 838, urban_ratio: 100.0 }, geo_boundary: null },
  { id: 3, state: 'Maharashtra', district: 'Nagpur', population: 4653570, demographic_stats: { literacy_rate: 89.53, sex_ratio: 948, urban_ratio: 68.4 }, geo_boundary: null }
];

// ─── Impact Scores ──────────────────────────────────────────────────────────

interface MockImpactScore {
  id: number;
  scheme_id: number;
  region_id: number;
  district_name: string;
  score: number;
  reach_component: number;
  sentiment_component: number;
  adoption_component: number;
  shap_explanations: {
    base_value: number;
    contributions: Record<string, number>;
  };
  computed_at: string;
  model_version: string;
}

function generateImpactScores(): MockImpactScore[] {
  const scores: MockImpactScore[] = [];
  let id = 1;

  const districtVariances: Record<number, { reachMod: number; sentMod: number; adoptMod: number }> = {
    1: { reachMod: 5, sentMod: 3, adoptMod: 2 },   // Pune – slightly better
    2: { reachMod: -2, sentMod: 8, adoptMod: 5 },   // Mumbai – higher sentiment
    3: { reachMod: -5, sentMod: -3, adoptMod: -4 },  // Nagpur – slightly lower
  };

  const baseMetrics: Record<number, { reach: number; sent: number; adopt: number }> = {
    1: { reach: 82, sent: 70, adopt: 72 },
    2: { reach: 75, sent: 68, adopt: 65 },
    3: { reach: 60, sent: 62, adopt: 58 },
    4: { reach: 55, sent: 50, adopt: 52 },
    5: { reach: 85, sent: 78, adopt: 75 },
    6: { reach: 80, sent: 72, adopt: 68 },
    7: { reach: 70, sent: 65, adopt: 60 },
    8: { reach: 45, sent: 42, adopt: 38 },
  };

  for (const scheme of schemes) {
    for (const region of regions) {
      const base = baseMetrics[scheme.id] || { reach: 55, sent: 50, adopt: 50 };
      const variance = districtVariances[region.id] || { reachMod: 0, sentMod: 0, adoptMod: 0 };

      const reach = Math.min(100, Math.max(0, base.reach + variance.reachMod));
      const sentiment = Math.min(100, Math.max(0, base.sent + variance.sentMod));
      const adoption = Math.min(100, Math.max(0, base.adopt + variance.adoptMod));
      const score = Number(((0.4 * reach) + (0.3 * sentiment) + (0.3 * adoption)).toFixed(2));

      scores.push({
        id: id++,
        scheme_id: scheme.id,
        region_id: region.id,
        district_name: region.district,
        score,
        reach_component: reach,
        sentiment_component: sentiment,
        adoption_component: adoption,
        shap_explanations: {
          base_value: 60.0,
          contributions: {
            reach_level: Number((reach - 60).toFixed(2)),
            budget_utilization: Number((adoption - 60).toFixed(2)),
            sentiment_rating: Number((sentiment - 50).toFixed(2))
          }
        },
        computed_at: '2026-07-25T18:30:00Z',
        model_version: 'v1_xgboost_muril'
      });
    }
  }

  return scores;
}

const impactScores = generateImpactScores();

// ─── Mentions / Sentiment Data ──────────────────────────────────────────────

interface MockMention {
  id: number;
  scheme_id: number;
  source: string;
  raw_text: string;
  language: string;
  sentiment_score: number;
  sentiment_label: string;
  url: string;
  published_date: string;
}

const mentions: MockMention[] = [
  // Scheme 1 – Majhi Ladki Bahin
  { id: 1, scheme_id: 1, source: 'Times of India', raw_text: 'Majhi Ladki Bahin Yojana has reached over 1.5 crore women within the first year, a remarkable achievement in social welfare.', language: 'en', sentiment_score: 0.82, sentiment_label: 'Positive', url: 'https://timesofindia.com/mly-1', published_date: '2026-07-10T09:00:00Z' },
  { id: 2, scheme_id: 1, source: 'Lokmat', raw_text: 'माझी लाडकी बहीण योजनेमुळे ग्रामीण भागातील महिलांना मोठा आधार मिळाला आहे. महिन्याला ₹1500 मिळतात.', language: 'hi', sentiment_score: 0.75, sentiment_label: 'Positive', url: 'https://lokmat.com/mly-2', published_date: '2026-07-12T14:00:00Z' },
  { id: 3, scheme_id: 1, source: 'NDTV', raw_text: 'Some reports suggest the verification process for Ladki Bahin is too slow, with pendency rates as high as 40% in rural talukas.', language: 'en', sentiment_score: -0.45, sentiment_label: 'Negative', url: 'https://ndtv.com/mly-3', published_date: '2026-07-15T11:00:00Z' },
  { id: 4, scheme_id: 1, source: 'Twitter/X User', raw_text: 'Ladki Bahin ka paisa aaya kya? Mujhe toh abhi tak nahi mila. #MajhiLadkiBahin', language: 'hi-en', sentiment_score: -0.30, sentiment_label: 'Negative', url: '', published_date: '2026-07-18T16:00:00Z' },
  { id: 5, scheme_id: 1, source: 'Maharashtra Times', raw_text: 'सरकारने या योजनेसाठी ₹46,000 कोटींचे बजेट ठेवले आहे जे गेल्या वर्षीच्या दुप्पट आहे.', language: 'hi', sentiment_score: 0.55, sentiment_label: 'Positive', url: 'https://maharashtratimes.com/mly-5', published_date: '2026-07-20T08:00:00Z' },

  // Scheme 2 – Swadhar
  { id: 6, scheme_id: 2, source: 'Indian Express', raw_text: 'Swadhar Yojana has improved higher education enrollment among SC students by 15% in Marathwada region.', language: 'en', sentiment_score: 0.68, sentiment_label: 'Positive', url: 'https://indianexpress.com/swy-1', published_date: '2026-06-25T10:00:00Z' },
  { id: 7, scheme_id: 2, source: 'Sakal', raw_text: 'स्वाधार योजनेचे अनुदान उशिरा मिळत असल्याने विद्यार्थ्यांना अडचणी येत आहेत.', language: 'hi', sentiment_score: -0.35, sentiment_label: 'Negative', url: 'https://sakal.com/swy-2', published_date: '2026-07-02T13:00:00Z' },
  { id: 8, scheme_id: 2, source: 'Hindustan Times', raw_text: 'Swadhar students can now track their scholarship status on the new digital portal launched by SJSA.', language: 'en', sentiment_score: 0.40, sentiment_label: 'Neutral', url: 'https://ht.com/swy-3', published_date: '2026-07-08T15:00:00Z' },

  // Scheme 3 – Vayoshri
  { id: 9, scheme_id: 3, source: 'Loksatta', raw_text: 'वयोश्री योजनेत पेन्शनची रक्कम अजूनही कमी आहे, सरकारने ती वाढवावी अशी ज्येष्ठ नागरिकांची मागणी.', language: 'hi', sentiment_score: -0.20, sentiment_label: 'Neutral', url: 'https://loksatta.com/vy-1', published_date: '2026-07-05T11:00:00Z' },
  { id: 10, scheme_id: 3, source: 'The Hindu', raw_text: 'Vayoshri pension has been a lifeline for elderly widows in drought-prone Vidarbha, says NGO report.', language: 'en', sentiment_score: 0.65, sentiment_label: 'Positive', url: 'https://thehindu.com/vy-2', published_date: '2026-07-14T09:00:00Z' },

  // Scheme 4 – Jalyukt Shivar
  { id: 11, scheme_id: 4, source: 'Down To Earth', raw_text: 'Jalyukt Shivar 2.0 shows mixed results: water table rose in Marathwada but soil erosion concerns persist in Western Ghats zone.', language: 'en', sentiment_score: 0.10, sentiment_label: 'Neutral', url: 'https://downtoearth.org.in/js-1', published_date: '2026-06-30T10:00:00Z' },
  { id: 12, scheme_id: 4, source: 'Twitter/X User', raw_text: 'Hamare gaon mein Jalyukt Shivar ka kaam rok diya gaya hai, contractor bhaag gaya. #JalyuktShivar', language: 'hi-en', sentiment_score: -0.60, sentiment_label: 'Negative', url: '', published_date: '2026-07-08T18:00:00Z' },

  // Scheme 5 – PMAY-G
  { id: 13, scheme_id: 5, source: 'PIB', raw_text: 'PMAY-Gramin has completed 3.5 crore houses nationally. Maharashtra ranks 4th with 12 lakh houses sanctioned and 9 lakh completed.', language: 'en', sentiment_score: 0.85, sentiment_label: 'Positive', url: 'https://pib.gov.in/pmay-1', published_date: '2026-07-01T10:00:00Z' },
  { id: 14, scheme_id: 5, source: 'Divya Marathi', raw_text: 'PMAY-G अंतर्गत पुणे जिल्ह्यात ८,००० हून अधिक घरे पूर्ण झाली आहेत. लाभार्थी समाधानी.', language: 'hi', sentiment_score: 0.72, sentiment_label: 'Positive', url: 'https://divyamarathi.com/pmay-2', published_date: '2026-07-12T14:00:00Z' },

  // Scheme 6 – PM Kisan
  { id: 15, scheme_id: 6, source: 'Economic Times', raw_text: 'PM Kisan 18th installment of ₹2,000 credited to 9.5 crore farmers. Maharashtra disbursement rate at 92%.', language: 'en', sentiment_score: 0.70, sentiment_label: 'Positive', url: 'https://economictimes.com/pmk-1', published_date: '2026-07-20T08:00:00Z' },
  { id: 16, scheme_id: 6, source: 'ABP Majha', raw_text: 'काही शेतकऱ्यांना eKYC न केल्याने PM किसानचा हप्ता मिळालेला नाही.', language: 'hi', sentiment_score: -0.25, sentiment_label: 'Negative', url: 'https://abpmajha.com/pmk-2', published_date: '2026-07-22T16:00:00Z' },

  // Scheme 7 – Ayushman Bharat
  { id: 17, scheme_id: 7, source: 'Mint', raw_text: 'Ayushman Bharat covered 6.2 crore hospital admissions since inception. Maharashtra hospitals report 35% increase in empanelment.', language: 'en', sentiment_score: 0.60, sentiment_label: 'Positive', url: 'https://livemint.com/ab-1', published_date: '2026-07-05T09:00:00Z' },
  { id: 18, scheme_id: 7, source: 'Twitter/X User', raw_text: 'Ayushman card hai lekin hospital wale mana kar rahe hain. Kya faayda aise scheme ka? #AyushmanBharat', language: 'hi-en', sentiment_score: -0.55, sentiment_label: 'Negative', url: '', published_date: '2026-07-16T20:00:00Z' },

  // Scheme 8 – Lek Ladki
  { id: 19, scheme_id: 8, source: 'Free Press Journal', raw_text: 'Lek Ladki Yojana disbursements remain below target with only 28% of eligible families registered so far.', language: 'en', sentiment_score: -0.40, sentiment_label: 'Negative', url: 'https://fpj.com/lly-1', published_date: '2026-07-10T11:00:00Z' },
  { id: 20, scheme_id: 8, source: 'Pudhari', raw_text: 'लेक लाडकी योजनेसाठी कागदपत्रांची यादी खूप मोठी आहे. गरीब कुटुंबांना अर्ज करणे कठीण.', language: 'hi', sentiment_score: -0.50, sentiment_label: 'Negative', url: 'https://pudhari.com/lly-2', published_date: '2026-07-18T14:00:00Z' },
];

// ─── Helper Functions ───────────────────────────────────────────────────────

function getSchemeScores(schemeId: number) {
  return impactScores.filter(s => s.scheme_id === schemeId);
}

function getSchemeDetail(schemeId: number) {
  const scheme = schemes.find(s => s.id === schemeId);
  if (!scheme) return null;

  return {
    ...scheme,
    impact_scores: getSchemeScores(schemeId),
    recent_mentions: mentions.filter(m => m.scheme_id === schemeId)
  };
}

// ─── Fetch Interceptor ──────────────────────────────────────────────────────

const originalFetch = window.fetch;

window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
  const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;

  // Only intercept our API calls
  if (!url.includes('localhost:8000/api')) {
    return originalFetch(input, init);
  }

  // Simulate network delay
  await new Promise(r => setTimeout(r, 300 + Math.random() * 400));

  const makeResponse = (data: unknown) =>
    new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

  // ── GET /api/schemes ──
  if (url.includes('/api/schemes') && !url.includes('/api/schemes/')) {
    const urlObj = new URL(url);
    let filtered = [...schemes];

    const search = urlObj.searchParams.get('search');
    if (search) {
      const q = search.toLowerCase();
      filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(q) || s.description.toLowerCase().includes(q)
      );
    }

    const category = urlObj.searchParams.get('category');
    if (category) {
      filtered = filtered.filter(s => s.category === category);
    }

    const level = urlObj.searchParams.get('level');
    if (level === 'central') {
      filtered = filtered.filter(s => s.launching_authority.includes('Government of India'));
    } else if (level === 'state') {
      filtered = filtered.filter(s => !s.launching_authority.includes('Government of India'));
    }

    filtered.sort((a, b) => (b.average_impact_score ?? 0) - (a.average_impact_score ?? 0));

    return makeResponse(filtered);
  }

  // ── GET /api/schemes/:id ──
  const schemeDetailMatch = url.match(/\/api\/schemes\/(\d+)/);
  if (schemeDetailMatch) {
    const schemeId = parseInt(schemeDetailMatch[1]);
    const detail = getSchemeDetail(schemeId);
    if (!detail) return new Response(JSON.stringify({ detail: 'Not found' }), { status: 404 });
    return makeResponse(detail);
  }

  // ── GET /api/regions ──
  if (url.includes('/api/regions') && !url.includes('/schemes')) {
    return makeResponse(regions);
  }

  // ── GET /api/regions/:id/schemes ──
  const regionSchemesMatch = url.match(/\/api\/regions\/(\d+)\/schemes/);
  if (regionSchemesMatch) {
    const regionId = parseInt(regionSchemesMatch[1]);
    return makeResponse(impactScores.filter(s => s.region_id === regionId));
  }

  // ── GET /api/mentions ──
  if (url.includes('/api/mentions')) {
    const urlObj = new URL(url);
    let filtered = [...mentions];

    const schemeId = urlObj.searchParams.get('scheme_id');
    if (schemeId) filtered = filtered.filter(m => m.scheme_id === parseInt(schemeId));

    const sentimentLabel = urlObj.searchParams.get('sentiment_label');
    if (sentimentLabel) filtered = filtered.filter(m => m.sentiment_label === sentimentLabel);

    filtered.sort((a, b) => new Date(b.published_date).getTime() - new Date(a.published_date).getTime());

    return makeResponse(filtered);
  }

  // ── GET /api/comparison ──
  if (url.includes('/api/comparison')) {
    const urlObj = new URL(url);
    const s1Id = parseInt(urlObj.searchParams.get('scheme1_id') || '0');
    const s2Id = parseInt(urlObj.searchParams.get('scheme2_id') || '0');
    const s1 = schemes.find(s => s.id === s1Id);
    const s2 = schemes.find(s => s.id === s2Id);

    if (!s1 || !s2) {
      return new Response(JSON.stringify({ detail: 'One or both schemes not found' }), { status: 404 });
    }

    return makeResponse({
      scheme1: {
        id: s1.id,
        name: s1.name,
        category: s1.category,
        budget_allocated: s1.budget_allocated,
        average_impact_score: s1.average_impact_score
      },
      scheme2: {
        id: s2.id,
        name: s2.name,
        category: s2.category,
        budget_allocated: s2.budget_allocated,
        average_impact_score: s2.average_impact_score
      },
      disclaimer: 'Impact scores are model-assisted estimates for policy ranking.'
    });
  }

  // Fallback – pass through to original fetch
  return originalFetch(input, init);
};

console.log('[MockData] 🔌 API interceptor active — all /api/* calls are served from dummy data.');

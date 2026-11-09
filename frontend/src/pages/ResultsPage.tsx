import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { fetchRecommendations } from '../services/recommendationService';
import { RecommendationResult, StudentProfile } from '../types';
import ChoiceTable from '../components/ChoiceTable';

const emptyResult: RecommendationResult = {
  dreamChoices: [],
  targetChoices: [],
  safeChoices: [],
  finalOrder: []
};

type FilterTab = 'all' | 'dream' | 'target' | 'safe';

export default function ResultsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [data, setData] = useState<RecommendationResult>(emptyResult);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<FilterTab>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const profile = (location.state as { profile?: StudentProfile })?.profile;

  useEffect(() => {
    if (!profile) {
      navigate('/profile');
      return;
    }

    const load = async () => {
      try {
        const result = await fetchRecommendations(profile);
        setData(result);
      } catch (err) {
        setError('Unable to reach the recommendation engine. Please ensure the backend is running and refresh the page.');
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [navigate, profile]);

  const displayedItems = useMemo(() => {
    let list = data.finalOrder;
    if (activeTab === 'dream') list = data.dreamChoices;
    else if (activeTab === 'target') list = data.targetChoices;
    else if (activeTab === 'safe') list = data.safeChoices;

    if (!searchQuery.trim()) return list;

    const query = searchQuery.toLowerCase();
    return list.filter(
      item =>
        item.institute.toLowerCase().includes(query) ||
        item.branch.toLowerCase().includes(query)
    );
  }, [data, activeTab, searchQuery]);

  if (!profile) {
    return null;
  }

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-6 py-10 lg:px-10">
      {/* Top Header Card */}
      <div className="mb-8 flex flex-col gap-4 rounded-[2.5rem] border border-slate-200 bg-white p-8 shadow-soft transition-colors dark:border-slate-800 dark:bg-slate-900 lg:flex-row lg:items-center lg:justify-between lg:p-10">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.24em] text-sky-600 dark:text-sky-400">Recommendation Results</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">Your CSAB Choice Filling Order</h1>
          <div className="mt-3 flex flex-wrap gap-2 text-xs font-medium text-slate-600 dark:text-slate-400">
            <span className="rounded-full bg-slate-100 px-3 py-1 dark:bg-slate-800 dark:text-slate-300">CRL: {profile.crlRank.toLocaleString('en-IN')}</span>
            <span className="rounded-full bg-slate-100 px-3 py-1 dark:bg-slate-800 dark:text-slate-300">Category: {profile.category}</span>
            <span className="rounded-full bg-slate-100 px-3 py-1 dark:bg-slate-800 dark:text-slate-300">Gender: {profile.gender}</span>
            <span className="rounded-full bg-slate-100 px-3 py-1 dark:bg-slate-800 dark:text-slate-300">Home State: {profile.homeState}</span>
            <span className="rounded-full bg-slate-100 px-3 py-1 dark:bg-slate-800 dark:text-slate-300">State Pref: {profile.statePreference}</span>
          </div>
        </div>
        <button
          onClick={() => navigate('/profile')}
          className="inline-flex shrink-0 items-center justify-center rounded-full bg-sky-600 px-6 py-2.5 text-sm font-semibold text-white shadow-md shadow-sky-600/20 transition hover:bg-sky-500"
        >
          Edit Profile
        </button>
      </div>

      {loading ? (
        <div className="rounded-[2.5rem] border border-slate-200 bg-white p-12 text-center text-slate-700 shadow-soft transition-colors dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300">
          <p className="text-lg font-bold">Evaluating historical cutoffs & scoring choices...</p>
          <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">Processing 3,300+ CSAB cutoff records across NITs, IIITs, and GFTIs.</p>
        </div>
      ) : error ? (
        <div className="rounded-[2.5rem] border border-rose-200 bg-rose-50 p-10 text-rose-900 shadow-soft dark:border-rose-900/50 dark:bg-rose-950/40 dark:text-rose-200">
          <h2 className="text-lg font-bold">Backend Connection Error</h2>
          <p className="mt-2 text-sm leading-6">{error}</p>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Summary Metric Cards */}
          <section className="grid gap-4 md:grid-cols-3">
            <div
              onClick={() => setActiveTab('dream')}
              className={`cursor-pointer rounded-[2rem] border p-6 transition shadow-soft ${
                activeTab === 'dream'
                  ? 'border-purple-500 bg-purple-50/60 ring-2 ring-purple-400 dark:border-purple-600 dark:bg-purple-950/30'
                  : 'border-slate-200 bg-white hover:border-purple-300 dark:border-slate-800 dark:bg-slate-900 dark:hover:border-purple-800'
              }`}
            >
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-purple-700 dark:text-purple-400">Dream Choices</p>
                <span className="rounded-full bg-purple-100 px-2.5 py-0.5 text-xs font-bold text-purple-800 dark:bg-purple-950 dark:text-purple-300">Top Priority</span>
              </div>
              <p className="mt-4 text-4xl font-extrabold text-slate-900 dark:text-white">{data.dreamChoices.length}</p>
              <p className="mt-2 text-xs text-slate-600 dark:text-slate-400">Aspirational top-tier seats where cutoffs are within reach.</p>
            </div>

            <div
              onClick={() => setActiveTab('target')}
              className={`cursor-pointer rounded-[2rem] border p-6 transition shadow-soft ${
                activeTab === 'target'
                  ? 'border-sky-500 bg-sky-50/60 ring-2 ring-sky-400 dark:border-sky-600 dark:bg-sky-950/30'
                  : 'border-slate-200 bg-white hover:border-sky-300 dark:border-slate-800 dark:bg-slate-900 dark:hover:border-sky-800'
              }`}
            >
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-sky-700 dark:text-sky-400">Target Choices</p>
                <span className="rounded-full bg-sky-100 px-2.5 py-0.5 text-xs font-bold text-sky-800 dark:bg-sky-950 dark:text-sky-300">Realistic</span>
              </div>
              <p className="mt-4 text-4xl font-extrabold text-slate-900 dark:text-white">{data.targetChoices.length}</p>
              <p className="mt-2 text-xs text-slate-600 dark:text-slate-400">Balanced options with realistic historical admission chances.</p>
            </div>

            <div
              onClick={() => setActiveTab('safe')}
              className={`cursor-pointer rounded-[2rem] border p-6 transition shadow-soft ${
                activeTab === 'safe'
                  ? 'border-emerald-500 bg-emerald-50/60 ring-2 ring-emerald-400 dark:border-emerald-600 dark:bg-emerald-950/30'
                  : 'border-slate-200 bg-white hover:border-emerald-300 dark:border-slate-800 dark:bg-slate-900 dark:hover:border-emerald-800'
              }`}
            >
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-emerald-700 dark:text-emerald-400">Safe Choices</p>
                <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-bold text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">Guaranteed</span>
              </div>
              <p className="mt-4 text-4xl font-extrabold text-slate-900 dark:text-white">{data.safeChoices.length}</p>
              <p className="mt-2 text-xs text-slate-600 dark:text-slate-400">Solid fallback options ensuring you are guaranteed a seat.</p>
            </div>
          </section>

          {/* Main Table Section */}
          <section className="rounded-[2.5rem] border border-slate-200 bg-white p-8 shadow-soft transition-colors dark:border-slate-800 dark:bg-slate-900">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Choice List</p>
                <h2 className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">
                  {activeTab === 'all' && 'Recommended Choice Order (Dream → Target → Safe)'}
                  {activeTab === 'dream' && 'Dream Choices (Aspirational)'}
                  {activeTab === 'target' && 'Target Choices (Realistic Chances)'}
                  {activeTab === 'safe' && 'Safe Choices (Backup Fallbacks)'}
                </h2>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                {(['all', 'dream', 'target', 'safe'] as FilterTab[]).map(tab => (
                  <button
                    key={tab}
                    type="button"
                    onClick={() => setActiveTab(tab)}
                    className={`rounded-full px-4 py-1.5 text-xs font-bold transition ${
                      activeTab === tab
                        ? 'bg-sky-600 text-white shadow-sm'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'
                    }`}
                  >
                    {tab === 'all' ? `All (${data.finalOrder.length})` : `${tab.toUpperCase()} (${data[`${tab}Choices`].length})`}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-4">
              <input
                type="text"
                placeholder="Search by institute name or branch (e.g. Warangal, Computer Science, ECE)..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 transition focus:border-sky-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              />
            </div>

            <ChoiceTable items={displayedItems} />
          </section>

          {/* Simple Compact Explainer & Instructions at End of Page */}
          <div className="grid gap-6 md:grid-cols-2">
            {/* Simple Score Explanation Card */}
            <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition-colors dark:border-slate-800 dark:bg-slate-900">
              <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-white">
                <span className="text-base">⚡</span> What is the Desirability Score?
              </h3>
              <p className="mt-2 text-xs leading-relaxed text-slate-600 dark:text-slate-400">
                The <strong>Desirability Score (0 – 100)</strong> rates how ideal each choice is for your profile. Rather than ordering purely by raw cutoffs, it combines:
              </p>
              <ul className="mt-2.5 space-y-1 text-xs text-slate-600 dark:text-slate-400">
                <li>• <strong>Branch Preference (50%)</strong> — Prioritizes the engineering branch you want most.</li>
                <li>• <strong>College Quality (40%)</strong> — Evaluates NIRF ranking & placement reputation.</li>
                <li>• <strong>Admission Odds (10%)</strong> — Tie-breaker giving a slight boost to safer seats.</li>
                <li>• <strong>Home State Bonus (+5 pts)</strong> — Added if college is in your home state.</li>
              </ul>
              <p className="mt-3 text-[11px] font-mono text-sky-700 dark:text-sky-400">
                Score = (0.5×Branch) + (0.4×College) + (0.1×Odds) + HomeStateBonus
              </p>
            </section>

            {/* How to Use in CSAB */}
            <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition-colors dark:border-slate-800 dark:bg-slate-900">
              <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-white">
                <span className="text-base">📋</span> How to use this sheet in CSAB
              </h3>
              <div className="mt-2.5 space-y-2 text-xs leading-relaxed text-slate-600 dark:text-slate-400">
                <p>
                  1. <strong>Fill from Top to Bottom:</strong> Copy this exact order into the CSAB portal. Choices are ordered from highest desirability to lowest.
                </p>
                <p>
                  2. <strong>Dream Choices at Top:</strong> Gives you a risk-free shot at aspirational seats if vacancies open up in Round 1/2.
                </p>
                <p>
                  3. <strong>Safe Choices at Bottom:</strong> Guarantees you will not walk away empty-handed even during cutoff fluctuations.
                </p>
              </div>
            </section>
          </div>
        </div>
      )}
    </main>
  );
}

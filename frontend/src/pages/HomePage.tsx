import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-[calc(100vh-73px)] max-w-6xl flex-col justify-center px-6 py-12 lg:px-10">
      <section className="rounded-[2.5rem] border border-slate-200 bg-white p-10 shadow-soft transition-colors dark:border-slate-800 dark:bg-slate-900 lg:p-16">
        <div className="max-w-3xl">
          <span className="inline-flex rounded-full bg-sky-100 px-4 py-1 text-xs font-bold uppercase tracking-wider text-sky-700 dark:bg-sky-950/70 dark:text-sky-300">
            CSAB Special Rounds 2024–2025
          </span>
          <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-5xl">
            Build your ideal CSAB choice filling list with counsellor intelligence.
          </h1>
          <p className="mt-5 text-base leading-7 text-slate-600 dark:text-slate-300">
            Enter your JEE Main rank and preferences to generate a ranked preference list designed by real counselling algorithms — balancing branch preference, institute tier reputation, and admission probability.
          </p>
          <div className="mt-8 flex flex-col gap-4 sm:flex-row">
            <Link
              to="/profile"
              className="inline-flex items-center justify-center rounded-full bg-sky-600 px-7 py-3.5 text-sm font-semibold text-white shadow-lg shadow-sky-600/20 transition hover:bg-sky-500"
            >
              Start Choice Filling →
            </Link>
          </div>
        </div>

        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 transition-colors dark:border-slate-800 dark:bg-slate-800/50">
            <span className="text-2xl">🎯</span>
            <h2 className="mt-3 text-base font-bold text-slate-900 dark:text-white">Counsellor Scoring</h2>
            <p className="mt-2 text-xs leading-5 text-slate-600 dark:text-slate-400">
              50% branch priority + 40% college quality + 10% admission odds.
            </p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 transition-colors dark:border-slate-800 dark:bg-slate-800/50">
            <span className="text-2xl">🌟</span>
            <h2 className="mt-3 text-base font-bold text-slate-900 dark:text-white">3 Distinct Tiers</h2>
            <p className="mt-2 text-xs leading-5 text-slate-600 dark:text-slate-400">
              Dream, Target, and Safe choice buckets arranged for maximum safety.
            </p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 transition-colors dark:border-slate-800 dark:bg-slate-800/50">
            <span className="text-2xl">🏛️</span>
            <h2 className="mt-3 text-base font-bold text-slate-900 dark:text-white">All 108 Colleges</h2>
            <p className="mt-2 text-xs leading-5 text-slate-600 dark:text-slate-400">
              Complete coverage of NITs, IIITs, and GFTIs across all 32 Indian States & UTs.
            </p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 transition-colors dark:border-slate-800 dark:bg-slate-800/50">
            <span className="text-2xl">⚡</span>
            <h2 className="mt-3 text-base font-bold text-slate-900 dark:text-white">Home State Quota</h2>
            <p className="mt-2 text-xs leading-5 text-slate-600 dark:text-slate-400">
              Precise quota matching rules for local and other-state candidates.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}

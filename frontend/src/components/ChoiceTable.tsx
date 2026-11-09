import { RecommendationItem } from '../types';

interface ChoiceTableProps {
  items: RecommendationItem[];
}

export default function ChoiceTable({ items }: ChoiceTableProps) {
  function getBadgeClass(classification: string) {
    switch (classification.toUpperCase()) {
      case 'DREAM':
        return 'bg-purple-50 text-purple-700 border border-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:border-purple-800';
      case 'TARGET':
        return 'bg-sky-50 text-sky-700 border border-sky-200 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-800';
      case 'SAFE':
        return 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800';
      default:
        return 'bg-slate-100 text-slate-700 border border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700';
    }
  }

  if (items.length === 0) {
    return (
      <div className="mt-6 rounded-3xl border border-dashed border-slate-300 p-10 text-center text-slate-500 dark:border-slate-700 dark:text-slate-400">
        No choices found in this category.
      </div>
    );
  }

  return (
    <div className="mt-6 overflow-x-auto rounded-3xl border border-slate-200 bg-white shadow-soft transition-colors dark:border-slate-800 dark:bg-slate-900">
      <table className="min-w-full divide-y divide-slate-200 text-left text-sm dark:divide-slate-800">
        <thead className="bg-slate-50 text-slate-600 dark:bg-slate-800/80 dark:text-slate-300">
          <tr>
            <th className="px-4 py-3.5 font-bold text-center w-16">Choice #</th>
            <th className="px-4 py-3.5 font-bold">Institute</th>
            <th className="px-4 py-3.5 font-bold">Academic Program</th>
            <th className="px-4 py-3.5 font-bold text-center">Category Tier</th>
            <th className="px-4 py-3.5 font-bold text-right">Desirability Score</th>
            <th className="px-4 py-3.5 font-bold text-right">Last Year Cutoff (CR)</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white text-slate-700 dark:divide-slate-800/60 dark:bg-slate-900 dark:text-slate-300">
          {items.map((item, index) => (
            <tr
              key={`${item.institute}-${item.branch}-${index}`}
              className="hover:bg-slate-50/80 transition dark:hover:bg-slate-800/50"
            >
              <td className="px-4 py-3.5 font-bold text-center text-slate-900 dark:text-white">{index + 1}</td>
              <td className="px-4 py-3.5 font-medium text-slate-900 dark:text-slate-100">{item.institute}</td>
              <td className="px-4 py-3.5 text-slate-600 dark:text-slate-300">{item.branch}</td>
              <td className="px-4 py-3.5 text-center">
                <span className={`inline-block px-3 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${getBadgeClass(item.classification)}`}>
                  {item.classification}
                </span>
              </td>
              <td className="px-4 py-3.5 text-right font-bold text-sky-600 dark:text-sky-400">
                {item.finalScore.toFixed(2)}
              </td>
              <td className="px-4 py-3.5 text-right font-mono text-slate-600 dark:text-slate-400">
                {item.closingRank.toLocaleString('en-IN')}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

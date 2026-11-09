import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BranchOption, InstituteTypeOption, StatePreferenceOption, StudentProfile, CategoryOption, GenderOption } from '../types';

const categories: CategoryOption[] = ['GN', 'EWS', 'OBC-NCL', 'SC', 'ST'];
const genders: GenderOption[] = ['M', 'F'];
const instituteTypes: InstituteTypeOption[] = ['NIT', 'IIIT', 'GFTI'];

export const branchMetadata: { id: BranchOption; label: string }[] = [
  { id: 'CSE', label: 'Computer Science & AI / Data Science (CSE)' },
  { id: 'IT', label: 'Information Technology (IT)' },
  { id: 'ECE', label: 'Electronics & Communication / VLSI (ECE)' },
  { id: 'EE', label: 'Electrical & Electronics Engineering (EE)' },
  { id: 'ME', label: 'Mechanical & Automation Engineering (ME)' },
  { id: 'Civil', label: 'Civil & Infrastructure Engineering' },
  { id: 'Chemical', label: 'Chemical Engineering' },
  { id: 'MME', label: 'Metallurgical & Materials Engineering (MME)' },
  { id: 'Biotech', label: 'Biotechnology & Biomedical Engineering' },
];

export const allStates: string[] = [
  'Andhra Pradesh',
  'Arunachal Pradesh',
  'Assam',
  'Bihar',
  'Chandigarh (UT)',
  'Chhattisgarh',
  'Delhi',
  'Goa',
  'Gujarat',
  'Haryana',
  'Himachal Pradesh',
  'Jammu & Kashmir',
  'Jharkhand',
  'Karnataka',
  'Kerala',
  'Madhya Pradesh',
  'Maharashtra',
  'Manipur',
  'Meghalaya',
  'Mizoram',
  'Nagaland',
  'Odisha',
  'Puducherry (UT)',
  'Punjab',
  'Rajasthan',
  'Sikkim',
  'Tamil Nadu',
  'Telangana',
  'Tripura',
  'Uttar Pradesh',
  'Uttarakhand',
  'West Bengal'
];

const statePreferences: StatePreferenceOption[] = ['Home State Only', 'Home State Priority', 'Any State'];

interface FormState extends Omit<StudentProfile, 'crlRank'> {
  crlRank: number | string;
}

export default function ProfileFormPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState<FormState>({
    crlRank: 100000,
    category: 'OBC-NCL',
    gender: 'F',
    homeState: 'Maharashtra',
    instituteTypes: ['NIT', 'IIIT', 'GFTI'],
    branchPreference: ['CSE', 'ECE', 'ME', 'Civil'],
    minimumBranch: 'Civil',
    statePreference: 'Any State'
  });

  function updateField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm(prev => ({ ...prev, [key]: value }));
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    const rank = Math.max(1, Number(form.crlRank) || 1);
    const finalProfile: StudentProfile = {
      ...form,
      crlRank: rank
    };
    navigate('/results', { state: { profile: finalProfile } });
  }

  function toggleInstituteType(type: InstituteTypeOption) {
    setForm(prev => {
      const selected = prev.instituteTypes.includes(type)
        ? prev.instituteTypes.filter(item => item !== type)
        : [...prev.instituteTypes, type];
      return { ...prev, instituteTypes: selected.length ? selected : [type] };
    });
  }

  function addBranchPreference(branch: BranchOption) {
    if (form.branchPreference.includes(branch)) return;
    const next = [...form.branchPreference, branch];
    setForm(prev => ({
      ...prev,
      branchPreference: next,
      minimumBranch: next[next.length - 1]
    }));
  }

  function removeBranchPreference(index: number) {
    if (form.branchPreference.length <= 1) return;
    const next = form.branchPreference.filter((_, i) => i !== index);
    setForm(prev => ({
      ...prev,
      branchPreference: next,
      minimumBranch: next.includes(prev.minimumBranch) ? prev.minimumBranch : next[next.length - 1]
    }));
  }

  function updatePreference(index: number, value: BranchOption) {
    setForm(prev => {
      const next = [...prev.branchPreference];
      next[index] = value;
      return {
        ...prev,
        branchPreference: next,
        minimumBranch: next.includes(prev.minimumBranch) ? prev.minimumBranch : next[next.length - 1]
      };
    });
  }

  return (
    <main className="mx-auto min-h-screen max-w-5xl px-6 py-10 lg:px-10">
      <section className="rounded-[2.5rem] border border-slate-200 bg-white p-8 shadow-soft transition-colors dark:border-slate-800 dark:bg-slate-900 lg:p-12">
        <div className="mb-8">
          <p className="text-xs font-bold uppercase tracking-[0.24em] text-sky-600 dark:text-sky-400">Student Profile</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            Build your profile for CSAB recommendation.
          </h1>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            Fill in your rank, category, and preferences so the counsellor engine can generate dream, target, and safe choices.
          </p>
        </div>

        <form onSubmit={onSubmit} className="space-y-8">
          <div className="grid gap-6 md:grid-cols-2">
            <label className="space-y-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
              CRL Rank (Common Rank List)
              <input
                type="number"
                min={1}
                required
                placeholder="e.g. 45000"
                value={form.crlRank}
                onChange={event => {
                  const val = event.target.value;
                  setForm(prev => ({
                    ...prev,
                    crlRank: val === '' ? '' : Number(val)
                  }));
                }}
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 transition focus:border-sky-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              />
            </label>
            <label className="space-y-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
              Category
              <select
                value={form.category}
                onChange={event => updateField('category', event.target.value as CategoryOption)}
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 transition focus:border-sky-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              >
                {categories.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
            <label className="space-y-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
              Gender
              <select
                value={form.gender}
                onChange={event => updateField('gender', event.target.value as GenderOption)}
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 transition focus:border-sky-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              >
                {genders.map(option => (
                  <option key={option} value={option}>
                    {option === 'F' ? 'Female (Eligible for Female-only Supernumerary)' : 'Male / Gender-Neutral'}
                  </option>
                ))}
              </select>
            </label>
            <label className="space-y-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
              Home State (12th Schooling State)
              <select
                value={form.homeState}
                onChange={event => updateField('homeState', event.target.value)}
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 transition focus:border-sky-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              >
                {allStates.map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
            </label>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 transition-colors dark:border-slate-800 dark:bg-slate-800/40">
            <p className="text-sm font-bold text-slate-900 dark:text-white">Preferred Institute Types</p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Toggle the college categories you wish to include.</p>
            <div className="mt-4 flex flex-wrap gap-3">
              {instituteTypes.map(type => (
                <button
                  type="button"
                  key={type}
                  onClick={() => toggleInstituteType(type)}
                  className={`rounded-full px-5 py-2.5 text-sm font-bold transition ${
                    form.instituteTypes.includes(type)
                      ? 'bg-sky-600 text-white shadow-md shadow-sky-600/20'
                      : 'border border-slate-300 bg-white text-slate-700 hover:border-slate-400 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 transition-colors dark:border-slate-800 dark:bg-slate-800/40">
            <div>
              <p className="text-sm font-bold text-slate-900 dark:text-white">Branch Preference Order</p>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Ranked from highest (1st preference) to lowest.</p>
            </div>

            <div className="mt-4 space-y-3">
              {form.branchPreference.map((branch, index) => (
                <div key={index} className="flex items-center gap-3">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-sky-100 text-xs font-extrabold text-sky-800 dark:bg-sky-950 dark:text-sky-300">
                    {index + 1}
                  </span>
                  <select
                    value={branch}
                    onChange={event => updatePreference(index, event.target.value as BranchOption)}
                    className="flex-1 rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 transition focus:border-sky-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                  >
                    {branchMetadata.map(b => (
                      <option key={b.id} value={b.id}>{b.label}</option>
                    ))}
                  </select>
                  {form.branchPreference.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeBranchPreference(index)}
                      className="rounded-full border border-red-200 px-3 py-1 text-xs font-semibold text-red-600 hover:bg-red-50 dark:border-red-900/50 dark:text-red-400 dark:hover:bg-red-950/40"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
            </div>

            {form.branchPreference.length < branchMetadata.length && (
              <div className="mt-4 flex flex-wrap items-center gap-2">
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Add branch to preferences:</span>
                {branchMetadata
                  .filter(b => !form.branchPreference.includes(b.id))
                  .map(b => (
                    <button
                      type="button"
                      key={b.id}
                      onClick={() => addBranchPreference(b.id)}
                      className="rounded-full border border-dashed border-sky-300 bg-sky-50/50 px-3 py-1 text-xs font-medium text-sky-700 hover:bg-sky-100 dark:border-sky-800 dark:bg-sky-950/30 dark:text-sky-400 dark:hover:bg-sky-950/70"
                    >
                      + {b.id}
                    </button>
                  ))}
              </div>
            )}
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <label className="space-y-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
              Minimum Acceptable Branch
              <p className="text-xs font-normal text-slate-500 dark:text-slate-400">Branches ranked lower than this will not be recommended.</p>
              <select
                value={form.minimumBranch}
                onChange={event => updateField('minimumBranch', event.target.value as BranchOption)}
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 transition focus:border-sky-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              >
                {form.branchPreference.map(option => {
                  const meta = branchMetadata.find(b => b.id === option);
                  return (
                    <option key={option} value={option}>
                      {meta ? meta.label : option}
                    </option>
                  );
                })}
              </select>
            </label>
            <label className="space-y-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
              State Preference
              <p className="text-xs font-normal text-slate-500 dark:text-slate-400">Choose how Home State quota should be prioritized.</p>
              <select
                value={form.statePreference}
                onChange={event => updateField('statePreference', event.target.value as StatePreferenceOption)}
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 transition focus:border-sky-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              >
                {statePreferences.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
          </div>

          <div className="flex flex-col items-start justify-between gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition-colors dark:border-slate-800 dark:bg-slate-800/60 sm:flex-row sm:items-center">
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Ready to calculate choice filling order?</h2>
              <p className="mt-1 text-xs text-slate-600 dark:text-slate-400">
                Evaluates cutoffs across {allStates.length} states to generate your Dream, Target, and Safe choice list.
              </p>
            </div>
            <button
              type="submit"
              className="inline-flex shrink-0 rounded-full bg-sky-600 px-7 py-3 text-sm font-semibold text-white shadow-md shadow-sky-600/20 transition hover:bg-sky-500"
            >
              Generate Recommendations →
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}

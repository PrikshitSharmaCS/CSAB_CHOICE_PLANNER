export type CategoryOption = 'GN' | 'EWS' | 'OBC-NCL' | 'SC' | 'ST';
export type GenderOption = 'M' | 'F';
export type InstituteTypeOption = 'NIT' | 'IIIT' | 'GFTI';
export type StatePreferenceOption = 'Home State Only' | 'Home State Priority' | 'Any State';
export type BranchOption =
  | 'CSE'
  | 'IT'
  | 'ECE'
  | 'EE'
  | 'ME'
  | 'Civil'
  | 'Chemical'
  | 'MME'
  | 'Biotech';

export interface StudentProfile {
  crlRank: number;
  category: CategoryOption;
  gender: GenderOption;
  homeState: string;
  instituteTypes: InstituteTypeOption[];
  branchPreference: BranchOption[];
  minimumBranch: BranchOption;
  statePreference: StatePreferenceOption;
}

export interface RecommendationItem {
  institute: string;
  branch: string;
  classification: string;
  finalScore: number;
  closingRank: number;
}

export interface RecommendationResult {
  dreamChoices: RecommendationItem[];
  targetChoices: RecommendationItem[];
  safeChoices: RecommendationItem[];
  finalOrder: RecommendationItem[];
}

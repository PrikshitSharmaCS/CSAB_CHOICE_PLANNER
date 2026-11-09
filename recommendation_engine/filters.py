"""
Filtering logic for CSAB recommendation engine.
"""

from typing import List
from .models import UserProfile, CutoffRecord, Category


def is_same_state(state1: str, state2: str) -> bool:
    """Compare two state names after normalizing formatting differences."""
    if not state1 or not state2:
        return False
    clean1 = (
        state1.lower()
        .replace("(ut)", "")
        .replace("(nct)", "")
        .replace("&", "and")
        .strip()
    )
    clean2 = (
        state2.lower()
        .replace("(ut)", "")
        .replace("(nct)", "")
        .replace("&", "and")
        .strip()
    )
    return clean1 == clean2


def get_eligible_seat_types(category: Category) -> List[str]:
    """
    Get eligible seat types for a category.
    
    Reserved categories can use their reserved seat + OPEN seats.
    General category can only use OPEN seats.
    """
    eligible = {
        Category.GN: ['OPEN'],
        Category.EWS: ['EWS', 'OPEN'],
        Category.OBC_NCL: ['OBC-NCL', 'OPEN'],
        Category.SC: ['SC', 'OPEN'],
        Category.ST: ['ST', 'OPEN'],
    }
    return eligible.get(category, ['OPEN'])


def category_filter(cutoff: CutoffRecord, user_category: Category) -> bool:
    """
    Check if cutoff's seat_type matches user's category.
    
    Args:
        cutoff: Cutoff record
        user_category: User's category
    
    Returns:
        True if eligible, False otherwise
    """
    eligible_seat_types = get_eligible_seat_types(user_category)
    return cutoff.seat_type in eligible_seat_types


def gender_filter(cutoff: CutoffRecord, user_gender: str) -> bool:
    """
    Check if cutoff is eligible for user's gender.
    
    Args:
        cutoff: Cutoff record
        user_gender: User's gender ('M' or 'F')
    
    Returns:
        True if eligible, False otherwise
    """
    # 'GN' means general/gender-neutral (open to all)
    # 'F' means female-only (supernumerary)
    # 'M' means male-only (rare)
    if cutoff.gender == 'GN':
        return True
    elif cutoff.gender == 'F' and user_gender.upper() == 'F':
        return True
    elif cutoff.gender == 'M' and user_gender.upper() == 'M':
        return True
    return False


def quota_filter(cutoff: CutoffRecord, user: UserProfile, institute_state_map: dict) -> bool:
    """
    Check if cutoff's quota is valid for the user under CSAB counselling rules
    and their state preference.
    
    CSAB Quota Rules:
    - HS (Home State): ONLY available if institute is in candidate's home state.
    - OS (Other State): Available for NITs outside candidate's home state.
    - AI (All India): Available for IIITs and GFTIs for candidates from any state.
    - JK: Available only for candidates whose home state is Jammu & Kashmir.
    - DASA: Excluded for domestic CSAB candidates.
    
    Args:
        cutoff: Cutoff record
        user: User profile
        institute_state_map: Mapping of institute name to state
    
    Returns:
        True if eligible, False otherwise
    """
    quota = cutoff.quota.upper().strip()
    
    # Exclude non-domestic DASA quotas
    if quota in ('DASA_CIWG', 'DASA_NON_CIWG'):
        return False
    
    # Regional J&K quota check
    if quota == 'JK':
        return is_same_state(user.home_state, 'Jammu & Kashmir')
    
    institute_state = institute_state_map.get(cutoff.institute_name, cutoff.institute_state or '')
    is_home = is_same_state(institute_state, user.home_state)
    
    if user.state_preference == "Home State Only":
        # Candidate only wants colleges in their home state
        return is_home and (quota in ('HS', 'AI'))
    
    elif user.state_preference == "Home State Priority":
        # Prefers home state, but considers outside states too
        if is_home:
            return quota in ('HS', 'AI')
        else:
            return quota in ('OS', 'AI')
    
    elif user.state_preference == "Any State":
        # Open to all states, but quota eligibility rules MUST be respected:
        # A candidate can NEVER claim another state's HS quota!
        if quota == 'HS':
            return is_home
        elif quota == 'OS':
            return not is_home
        elif quota == 'AI':
            return True
        return False
    
    return False


def rank_filter(cutoff: CutoffRecord, user_rank: int, max_dream_reach: float = 0.75) -> bool:
    """
    Check if cutoff is within a realistic rank range for the user.
    
    Counselling Logic:
    1. A choice is eligible if closing_rank >= user_rank * max_dream_reach (default 0.75).
       - closing_rank >= 1.10 * user_rank: SAFE
       - 0.91 * user_rank <= closing_rank < 1.10 * user_rank: TARGET
       - 0.75 * user_rank <= closing_rank < 0.91 * user_rank: DREAM
       - closing_rank < 0.75 * user_rank: Filtered out (< 10% admission probability)
    2. Opening rank does NOT disqualify candidates with better ranks.
       A candidate whose rank is better (lower number) than opening_rank is fully eligible.
    
    Args:
        cutoff: Cutoff record
        user_rank: User's CRL rank
        max_dream_reach: Minimum ratio of cutoff closing rank to user rank (default 0.75)
    
    Returns:
        True if within realistic range, False otherwise
    """
    if cutoff.closing_rank <= 0 or user_rank <= 0:
        return False
    
    return cutoff.closing_rank >= int(user_rank * max_dream_reach)


def get_acceptable_branches(user: UserProfile) -> List[str]:
    """
    Get the list of acceptable branches taking minimum_acceptable_branch into account.
    """
    prefs = user.branch_preference
    min_branch = user.minimum_acceptable_branch
    
    if min_branch in prefs:
        cutoff_index = prefs.index(min_branch)
        return prefs[:cutoff_index + 1]
    
    return prefs


def branch_filter(cutoff: CutoffRecord, user: UserProfile) -> bool:
    """
    Check if branch matches user's preferences at or above minimum acceptable branch.
    
    Args:
        cutoff: Cutoff record
        user: User profile
    
    Returns:
        True if branch is acceptable, False otherwise
    """
    program_name = cutoff.program_name.lower()
    acceptable_branches = get_acceptable_branches(user)
    
    branch_keywords = {
        'CSE': [
            'computer science', 'computer engineering', 'cse', 'data science',
            'artificial intelligence', 'information technology', 'software',
            'computational'
        ],
        'ECE': [
            'electronics and communication', 'electronics & communication', 'ece',
            'electronics and telecommunication', 'electronics and vlsi', 'vlsi',
            'electronics and instrumentation', 'electronics engineering'
        ],
        'EE': [
            'electrical engineering', 'electrical and electronics',
            'electrical & electronics', 'electrical'
        ],
        'ME': [
            'mechanical', 'production', 'industrial and production',
            'manufacturing', 'automobile', 'mechatronics'
        ],
        'CIVIL': [
            'civil engineering', 'civil and infrastructure', 'civil'
        ],
        'CE': [
            'civil engineering', 'civil'
        ],
        'IT': [
            'information technology', 'it'
        ],
        'CHEMICAL': [
            'chemical engineering', 'petrochemical', 'biochemical'
        ],
        'MME': [
            'metallurg', 'materials engineering', 'materials science'
        ],
        'BIOTECH': [
            'bio technology', 'biotechnology', 'biomedical'
        ]
    }
    
    for branch in acceptable_branches:
        branch_upper = branch.upper().strip()
        keywords = branch_keywords.get(branch_upper, [branch.lower().strip()])
        
        for keyword in keywords:
            if keyword in program_name:
                return True
    
    return False


def institute_type_filter(cutoff: CutoffRecord, user: UserProfile) -> bool:
    """
    Check if institute type matches user's preference.
    
    Args:
        cutoff: Cutoff record
        user: User profile
    
    Returns:
        True if institute type is in user's preference, False otherwise
    """
    return cutoff.institute_type in user.preferred_institute_types


def combined_filter(
    cutoff: CutoffRecord,
    user: UserProfile,
    institute_state_map: dict
) -> bool:
    """
    Apply all counselling filters to a cutoff record.
    
    Args:
        cutoff: Cutoff record
        user: User profile
        institute_state_map: Mapping of institute name to state
    
    Returns:
        True if cutoff passes all filters, False otherwise
    """
    checks = [
        category_filter(cutoff, user.category),
        gender_filter(cutoff, user.gender),
        quota_filter(cutoff, user, institute_state_map),
        rank_filter(cutoff, user.crl_rank),
        branch_filter(cutoff, user),
        institute_type_filter(cutoff, user),
    ]
    
    return all(checks)

"""
Ranking and scoring logic for recommendations.
"""

from typing import List, Optional
from .models import UserProfile, CutoffRecord, Classification, Recommendation
from .classifier import get_probability_score


def calculate_branch_score(
    program_name: str,
    user_branch_preference: list,
    minimum_acceptable_branch: Optional[str] = None
) -> float:
    """
    Calculate branch preference score (0-100).
    
    Scoring:
    - 1st preference: 100
    - Subsequent preferences drop progressively down to 40
    - Below minimum acceptable branch: 0 (excluded)
    
    Args:
        program_name: Program name from cutoff
        user_branch_preference: User's ordered branch list
        minimum_acceptable_branch: Optional cutoff branch threshold
    
    Returns:
        Score (0-100)
    """
    program_lower = program_name.lower()
    
    # Determine allowed preferences up to minimum acceptable branch
    allowed_preferences = user_branch_preference
    if minimum_acceptable_branch and minimum_acceptable_branch in user_branch_preference:
        min_idx = user_branch_preference.index(minimum_acceptable_branch)
        allowed_preferences = user_branch_preference[:min_idx + 1]
    
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
    
    # Pre-calculated scale for top preferences
    standard_scores = [100.0, 80.0, 60.0, 40.0, 30.0, 20.0]
    
    for idx, branch in enumerate(allowed_preferences):
        branch_upper = branch.upper().strip()
        keywords = branch_keywords.get(branch_upper, [branch.lower().strip()])
        
        for keyword in keywords:
            if keyword in program_lower:
                if idx < len(standard_scores):
                    return standard_scores[idx]
                return max(15.0, 100.0 - idx * 15.0)
    
    return 0.0


def calculate_institute_score(counselor_priority_rank: int, total_institutes: int = 90) -> float:
    """
    Calculate institute quality score (0-100) from metadata.
    
    Formula: Institute_Score = 100 - ((priority_rank - 1) / (total_institutes - 1)) * 100
    
    Args:
        counselor_priority_rank: Counselor priority rank from metadata (1-90)
        total_institutes: Total institutes benchmark
    
    Returns:
        Score (0-100)
    """
    if counselor_priority_rank <= 0:
        return 0.0
    
    score = 100.0 - ((counselor_priority_rank - 1) / (total_institutes - 1)) * 100.0
    return max(0.0, min(100.0, score))


def calculate_probability_score(classification: Classification) -> float:
    """
    Calculate probability score based on classification (0-100).
    """
    return get_probability_score(classification)


def calculate_final_score(
    branch_score: float,
    institute_score: float,
    probability_score: float,
    branch_weight: float = 0.5,
    institute_weight: float = 0.4,
    probability_weight: float = 0.1,
    home_state_bonus: float = 0.0
) -> float:
    """
    Calculate final recommendation score.
    
    Formula:
    Final_Score = (0.5 * Branch) + (0.4 * Institute) + (0.1 * Probability) + Bonus
    
    Args:
        branch_score: Branch preference score (0-100)
        institute_score: Institute quality score (0-100)
        probability_score: Admission probability score (0-100)
        branch_weight: Weight for branch (default 0.5)
        institute_weight: Weight for institute (default 0.4)
        probability_weight: Weight for probability (default 0.1)
        home_state_bonus: Bonus if Home State Priority applies
    
    Returns:
        Final score (0-100)
    """
    final = (
        branch_weight * branch_score +
        institute_weight * institute_score +
        probability_weight * probability_score +
        home_state_bonus
    )
    return min(100.0, max(0.0, final))


def rank_recommendations(recommendations_list: List[Recommendation]) -> List[Recommendation]:
    """
    Sort recommendations by final score (descending).
    """
    return sorted(recommendations_list, key=lambda r: r.final_score, reverse=True)


def categorize_by_classification(recommendations_list: List[Recommendation]) -> dict:
    """
    Categorize recommendations by Dream/Target/Safe and sort each bucket by final score.
    
    Args:
        recommendations_list: List of Recommendation objects
    
    Returns:
        Dict with keys 'safe', 'target', 'dream' containing sorted lists
    """
    categorized = {
        'safe': [],
        'target': [],
        'dream': [],
    }
    
    for rec in recommendations_list:
        if rec.classification == Classification.SAFE:
            categorized['safe'].append(rec)
        elif rec.classification == Classification.TARGET:
            categorized['target'].append(rec)
        else:  # DREAM
            categorized['dream'].append(rec)
    
    for category in categorized:
        categorized[category].sort(key=lambda r: r.final_score, reverse=True)
    
    return categorized

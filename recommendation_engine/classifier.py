"""
Dream/Target/Safe classification for cutoffs.
"""

from .models import Classification


def classify_cutoff(user_rank: int, closing_rank: int) -> Classification:
    """
    Classify a cutoff as SAFE, TARGET, or DREAM.
    
    Formula: Probability = closing_rank / user_rank
    
    - SAFE: Probability >= 1.10 (closing rank is 10%+ worse)
    - TARGET: 0.91 <= Probability < 1.10 (closing rank within 10%)
    - DREAM: Probability < 0.91 (closing rank is 10%+ better)
    
    Args:
        user_rank: User's CRL rank
        closing_rank: Cutoff's closing rank
    
    Returns:
        Classification enum (SAFE, TARGET, or DREAM)
    """
    probability = closing_rank / user_rank
    
    if probability >= 1.10:
        return Classification.SAFE
    elif probability >= 0.91:
        return Classification.TARGET
    else:
        return Classification.DREAM


def get_probability_score(classification: Classification) -> float:
    """
    Get probability score based on classification.
    
    Used as tie-breaker in final scoring (10% weight).
    
    Args:
        classification: Classification enum
    
    Returns:
        Score (0-100)
    """
    scores = {
        Classification.SAFE: 100,
        Classification.TARGET: 60,
        Classification.DREAM: 20,
    }
    return scores.get(classification, 0)


def get_probability_value(user_rank: int, closing_rank: int) -> float:
    """
    Calculate probability value.
    
    Args:
        user_rank: User's CRL rank
        closing_rank: Cutoff's closing rank
    
    Returns:
        Probability as float
    """
    return closing_rank / user_rank

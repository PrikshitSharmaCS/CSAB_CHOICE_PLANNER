"""
Data models for CSAB recommendation engine.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class Category(str, Enum):
    """Candidate categories."""
    GN = "GN"        # General
    EWS = "EWS"      # Economically Weaker Section
    OBC_NCL = "OBC-NCL"
    SC = "SC"        # Scheduled Caste
    ST = "ST"        # Scheduled Tribe


class Classification(str, Enum):
    """Dream/Target/Safe classification."""
    SAFE = "SAFE"
    TARGET = "TARGET"
    DREAM = "DREAM"


@dataclass
class UserProfile:
    """User's profile for recommendation."""
    crl_rank: int
    category: Category
    gender: str  # 'M' or 'F'
    home_state: str
    preferred_institute_types: List[str]  # ['NIT', 'IIIT', 'GFTI']
    branch_preference: List[str]  # Ordered list, e.g., ['CSE', 'ECE', 'ME', 'Civil']
    minimum_acceptable_branch: str  # e.g., 'ME'
    state_preference: str  # 'Home State Only', 'Home State Priority', 'Any State'


@dataclass
class CutoffRecord:
    """A cutoff record from database."""
    cutoff_id: int
    institute_name: str
    institute_type: str  # NIT, IIIT, GFTI
    institute_state: str
    program_name: str
    quota: str  # 'HS' or 'OS'
    seat_type: str  # 'OPEN', 'OBC-NCL', 'SC', 'ST', 'EWS', 'PWD', etc.
    gender: str  # 'GN' or 'F'
    opening_rank: int
    closing_rank: int
    counselor_priority_rank: int


@dataclass
class Recommendation:
    """A recommendation choice."""
    cutoff: CutoffRecord
    branch_score: float
    institute_score: float
    probability: float
    classification: Classification
    probability_score: float
    final_score: float

    def __repr__(self):
        return (
            f"{self.cutoff.institute_name} - {self.cutoff.program_name} "
            f"({self.classification.value}, Score: {self.final_score:.2f})"
        )


@dataclass
class RecommendationResult:
    """Final recommendation result."""
    safe_choices: List[Recommendation]
    target_choices: List[Recommendation]
    dream_choices: List[Recommendation]
    final_order: List[Recommendation]

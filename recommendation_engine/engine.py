"""
Main CSAB recommendation engine.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from .models import (
    UserProfile, CutoffRecord, Category, Recommendation, 
    RecommendationResult, Classification
)
from .filters import combined_filter, is_same_state
from .classifier import classify_cutoff, get_probability_value, get_probability_score
from .ranker import (
    calculate_branch_score, calculate_institute_score, 
    calculate_final_score, rank_recommendations, categorize_by_classification
)


class RecommendationEngine:
    """Main recommendation engine for CSAB choice filling."""
    
    def __init__(self, db_path: str, metadata_path: str):
        """
        Initialize the engine with database and metadata.
        
        Args:
            db_path: Path to csab.db
            metadata_path: Path to csab_institute_metadata.json
        """
        self.db_path = db_path
        self.metadata_path = metadata_path
        self.metadata = None
        self.institute_state_map = {}
        self.institute_priority_map = {}
        self.institute_type_map = {}
        
        self._load_metadata()
    
    def _load_metadata(self):
        """Load institute metadata from JSON file."""
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.metadata = data.get('metadata', {})
        
        # Build maps for quick lookup
        for inst in data.get('institutes', []):
            name = inst['name']
            self.institute_state_map[name] = inst.get('state', '')
            self.institute_priority_map[name] = inst.get('counselor_priority_rank', 90)
            self.institute_type_map[name] = inst.get('type', 'GFTI')
    
    def _get_eligible_cutoffs(self, user: UserProfile) -> List[CutoffRecord]:
        """
        Query database for all eligible cutoffs.
        
        Args:
            user: User profile
        
        Returns:
            List of CutoffRecord objects that pass filtering
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Query all cutoff records with joins
        cursor.execute("""
            SELECT 
                c.id,
                i.name,
                p.name,
                c.quota,
                c.seat_type,
                c.gender,
                c.opening_rank,
                c.closing_rank
            FROM cutoffs c
            JOIN institutes i ON c.institute_id = i.id
            JOIN programs p ON c.program_id = p.id
            ORDER BY i.name, p.name
        """)
        
        cutoffs = []
        for row in cursor.fetchall():
            institute_name = row[1]
            cutoff = CutoffRecord(
                cutoff_id=row[0],
                institute_name=institute_name,
                institute_type=self.institute_type_map.get(institute_name, 'GFTI'),
                institute_state=self.institute_state_map.get(institute_name, ''),
                program_name=row[2],
                quota=row[3],
                seat_type=row[4],
                gender=row[5],
                opening_rank=row[6],
                closing_rank=row[7],
                counselor_priority_rank=self.institute_priority_map.get(institute_name, 90)
            )
            cutoffs.append(cutoff)
        
        conn.close()
        
        # Apply filters
        eligible = [
            c for c in cutoffs
            if combined_filter(c, user, self.institute_state_map)
        ]
        
        return eligible
    
    def generate_recommendations(self, user: UserProfile) -> RecommendationResult:
        """
        Generate recommendations for a user following JoSAA/CSAB counselling principles.
        
        Args:
            user: User profile
        
        Returns:
            RecommendationResult with safe/target/dream/final_order lists
        """
        # Get eligible cutoffs
        eligible_cutoffs = self._get_eligible_cutoffs(user)
        
        if not eligible_cutoffs:
            return RecommendationResult(
                safe_choices=[],
                target_choices=[],
                dream_choices=[],
                final_order=[]
            )
        
        # Score each cutoff
        recommendations = []
        for cutoff in eligible_cutoffs:
            # Calculate component scores
            branch_score = calculate_branch_score(
                cutoff.program_name,
                user.branch_preference,
                user.minimum_acceptable_branch
            )
            
            # Skip if branch score is 0 (not in acceptable list or below minimum branch)
            if branch_score == 0:
                continue
            
            institute_score = calculate_institute_score(
                cutoff.counselor_priority_rank
            )
            
            # Classify and get probability score
            classification = classify_cutoff(user.crl_rank, cutoff.closing_rank)
            probability = get_probability_value(user.crl_rank, cutoff.closing_rank)
            probability_score = get_probability_score(classification)
            
            # Calculate Home State Priority bonus if applicable
            home_state_bonus = 0.0
            if user.state_preference == "Home State Priority":
                if is_same_state(cutoff.institute_state, user.home_state):
                    home_state_bonus = 5.0
            
            # Calculate final score
            final_score = calculate_final_score(
                branch_score,
                institute_score,
                probability_score,
                home_state_bonus=home_state_bonus
            )
            
            # Create recommendation
            rec = Recommendation(
                cutoff=cutoff,
                branch_score=branch_score,
                institute_score=institute_score,
                probability=probability,
                classification=classification,
                probability_score=probability_score,
                final_score=final_score
            )
            
            recommendations.append(rec)
        
        # Deduplicate by (institute_name, program_name):
        # In JoSAA/CSAB portal, a student chooses each unique institute + program once.
        # If candidate qualifies under multiple pools (e.g. OPEN and reserved, or GN and Female),
        # keep the cutoff that gives the student the highest closing rank (most favorable).
        unique_recs = {}
        for rec in recommendations:
            key = (rec.cutoff.institute_name, rec.cutoff.program_name)
            if key not in unique_recs or rec.cutoff.closing_rank > unique_recs[key].cutoff.closing_rank:
                unique_recs[key] = rec
        
        final_recs = list(unique_recs.values())
        
        # Categorize by Dream / Target / Safe
        categorized = categorize_by_classification(final_recs)
        
        # JoSAA/CSAB Choice-Filling Order:
        # Always place Dream choices at top, followed by Target choices,
        # with Safe choices at bottom as guaranteed fallback backups.
        final_choice_order = (
            categorized['dream'] +
            categorized['target'] +
            categorized['safe']
        )
        
        return RecommendationResult(
            safe_choices=categorized['safe'],
            target_choices=categorized['target'],
            dream_choices=categorized['dream'],
            final_order=final_choice_order
        )


def create_engine(workspace_dir: str) -> RecommendationEngine:
    """
    Create and initialize the recommendation engine.
    
    Args:
        workspace_dir: Root workspace directory
    
    Returns:
        Initialized RecommendationEngine
    """
    db_path = str(Path(workspace_dir) / "csab.db")
    metadata_path = str(Path(workspace_dir) / "DATA" / "csab_institute_metadata.json")
    
    return RecommendationEngine(db_path, metadata_path)

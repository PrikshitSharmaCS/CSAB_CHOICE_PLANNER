# CSAB Recommendation Engine

A recommendation engine for generating optimal choice-filling order for JoSAA/CSAB counseling based on user profile and historical cutoff data.

## Features

✓ **Dynamic Filtering**
- Category-based seat type matching (GN, EWS, OBC-NCL, SC, ST)
- Gender eligibility checking
- Quota handling (Home State vs Other State)
- Rank range validation
- Institute type preferences (NIT, IIIT, GFTI)
- Branch preference filtering

✓ **Smart Classification**
- Dream/Target/Safe classification based on historical probability
- Formula: Probability = Closing Rank / User Rank
- SAFE (≥1.10), TARGET (0.91-1.10), DREAM (<0.91)

✓ **Intelligent Ranking**
- Multi-factor scoring: Branch (50%) + Institute (40%) + Probability (10%)
- Institute scores from metadata (`counselor_priority_rank`)
- Final recommendations sorted by desirability
- Results grouped by classification level

## File Structure

```
recommendation_engine/
├── __init__.py              # Package initialization
├── models.py                # Data classes (UserProfile, Cutoff, Recommendation)
├── filters.py               # All filtering logic
├── classifier.py            # Dream/Target/Safe classification
├── ranker.py                # Scoring and ranking functions
└── engine.py                # Main RecommendationEngine class

test_engine.py               # Test script with sample user profile
```

## Usage

### Basic Usage

```python
from recommendation_engine import create_engine, UserProfile, Category

# Initialize engine
workspace_dir = "/path/to/workspace"
engine = create_engine(workspace_dir)

# Create user profile
user = UserProfile(
    crl_rank=100000,
    category=Category.OBC_NCL,
    gender='F',
    home_state='Maharashtra',
    preferred_institute_types=['NIT', 'IIIT', 'GFTI'],
    branch_preference=['CSE', 'ECE', 'ME', 'Civil'],
    minimum_acceptable_branch='Civil',
    state_preference='Any State'
)

# Generate recommendations
result = engine.generate_recommendations(user)

# Access results
print(f"Safe choices: {len(result.safe_choices)}")
print(f"Target choices: {len(result.target_choices)}")
print(f"Dream choices: {len(result.dream_choices)}")

# Final recommended order
for idx, rec in enumerate(result.final_order, 1):
    print(f"{idx}. {rec.cutoff.institute_name} - {rec.cutoff.program_name}")
```

### Running the Test

```bash
python test_engine.py
```

Output includes:
- User profile details
- SAFE choices (top 5)
- TARGET choices (top 5)
- DREAM choices (top 5)
- Final recommended choice order (top 20)
- Statistics (total safe/target/dream)

## Scoring Formula

$$\text{FINAL\_SCORE} = (0.5 \times \text{Branch}) + (0.4 \times \text{Institute}) + (0.1 \times \text{Probability})$$

### Component Scores

1. **Branch Preference (50%)**
   - 1st choice: 100
   - 2nd choice: 80
   - 3rd choice: 60
   - 4th choice: 40
   - Below minimum: 0 (excluded)

2. **Institute Quality (40%)**
   - Calculated from `counselor_priority_rank` in metadata
   - Formula: `100 - ((rank - 1) / 89) * 100`
   - Rank 1 = 100, Rank 90 = 0

3. **Admission Probability (10%)**
   - SAFE: 100
   - TARGET: 60
   - DREAM: 20

## Classification Logic

**Dream/Target/Safe**: Based on historical probability

$$\text{Probability} = \frac{\text{Closing Rank}}{\text{User Rank}}$$

| Classification | Condition | Interpretation |
|---|---|---|
| **SAFE** | Prob ≥ 1.10 | User rank 10%+ better (likely allocation) |
| **TARGET** | 0.91 ≤ Prob < 1.10 | User rank within 10% (realistic) |
| **DREAM** | Prob < 0.91 | User rank 10%+ worse (risky) |

## Data Models

### UserProfile
```python
@dataclass
class UserProfile:
    crl_rank: int                              # User's CRL rank
    category: Category                          # GN, EWS, OBC-NCL, SC, ST
    gender: str                                 # 'M' or 'F'
    home_state: str                             # User's home state
    preferred_institute_types: List[str]        # ['NIT', 'IIIT', 'GFTI']
    branch_preference: List[str]                # ['CSE', 'ECE', 'ME', 'Civil']
    minimum_acceptable_branch: str              # 'Civil'
    state_preference: str                       # 'Home State Only', 'Home State Priority', 'Any State'
```

### Recommendation
```python
@dataclass
class Recommendation:
    cutoff: CutoffRecord                        # Original cutoff data
    branch_score: float                         # 0-100
    institute_score: float                      # 0-100
    probability: float                          # Closing Rank / User Rank
    classification: Classification              # SAFE, TARGET, DREAM
    probability_score: float                    # 0-100
    final_score: float                          # 0-100
```

### RecommendationResult
```python
@dataclass
class RecommendationResult:
    safe_choices: List[Recommendation]          # SAFE classification
    target_choices: List[Recommendation]        # TARGET classification
    dream_choices: List[Recommendation]         # DREAM classification
    final_order: List[Recommendation]           # All choices sorted by score
```

## Key Features of Filtering

### Category Matching
- **GN**: Only OPEN seats
- **EWS**: EWS + OPEN seats
- **OBC-NCL**: OBC-NCL + OPEN seats
- **SC**: SC + OPEN seats
- **ST**: ST + OPEN seats

### Quota Handling
- **Home State Only**: Only HS quota from home state institutes
- **Home State Priority**: HS from home state + OS from other states
- **Any State**: Both HS and OS from all institutes

### Gender Eligibility
- GN (General): Available to all
- F (Female-only): Only females
- M (Male-only): Only males

## Database Integration

- Queries SQLite database (csab.db) with institutes, programs, cutoffs
- Loads institute metadata from JSON for priority ranking
- Combines database data with metadata for comprehensive recommendations

## Performance

- Database query + filtering: < 100ms
- Scoring all cutoffs: < 500ms
- Total recommendation generation: < 1s for typical user profiles

## Limitations & Assumptions

1. Uses CRL rank only (no category rank data)
2. Historical probabilities based on past closing ranks
3. Branch matching uses keyword matching (CSE = "computer science", "cse", "it", etc.)
4. Institute quality ranked by counselor priority (not strict NIRF rank)
5. Assumes user has access to all NIT/IIIT/GFTI seats per their category
6. Seat availability and cutoffs are static (from extracted data)

## Future Enhancements

- [ ] Category rank integration (when data available)
- [ ] Real-time rank updates
- [ ] ML-based probability prediction
- [ ] Multi-state home state support
- [ ] Custom weightage configuration (50-40-10 weights)
- [ ] Export recommendations to CSV
- [ ] Web API integration

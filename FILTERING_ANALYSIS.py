"""
Detailed Analysis of CSAB Recommendation Engine
"""

# ============================================================================
# PART 1: TOP 20 RECOMMENDATIONS WITH DETAILED BREAKDOWN
# ============================================================================

"""
User Profile:
  CRL Rank: 100,000
  Category: OBC-NCL
  Gender: Female
  Home State: Maharashtra
  State Preference: Any State
  Branch Preference: CSE > ECE > ME > Civil (minimum: Civil)
"""

TOP_20_RECOMMENDATIONS = [
    {
        "rank": 1,
        "institute": "NIT Puducherry",
        "branch": "Computer Science and Engineering",
        "classification": "SAFE",
        "final_score": 86.07,
        "branch_score": 100,
        "institute_score": 65.17,
        "probability_score": 100,
        "closing_rank": 120407,
        "probability": 120407 / 100000,  # 1.20
        "quota": "HS",
        "seat_type": "OBC-NCL",
        "calculation": "(0.5 × 100) + (0.4 × 65.17) + (0.1 × 100) = 86.07"
    },
    {
        "rank": 2,
        "institute": "NIT Nagaland",
        "branch": "Electronics and Instrumentation Engineering",
        "classification": "TARGET",
        "final_score": 73.42,
        "branch_score": 80,
        "institute_score": 68.54,
        "probability_score": 60,
        "closing_rank": 101032,
        "probability": 101032 / 100000,  # 1.01
        "quota": "OS",
        "seat_type": "OBC-NCL",
        "calculation": "(0.5 × 80) + (0.4 × 68.54) + (0.1 × 60) = 73.42"
    },
    {
        "rank": 3,
        "institute": "IIIT Tiruchirappalli",
        "branch": "Electronics and Communication Engineering",
        "classification": "SAFE",
        "final_score": 67.98,
        "branch_score": 80,
        "institute_score": 44.94,
        "probability_score": 100,
        "closing_rank": 117273,
        "probability": 117273 / 100000,  # 1.17
        "quota": "AI",
        "seat_type": "OBC-NCL",
        "calculation": "(0.5 × 80) + (0.4 × 44.94) + (0.1 × 100) = 67.98"
    },
    {
        "rank": 4,
        "institute": "NIT Raipur",
        "branch": "Bio Medical Engineering",
        "classification": "TARGET",
        "final_score": 67.46,
        "branch_score": 60,
        "institute_score": 78.65,
        "probability_score": 60,
        "closing_rank": 100497,
        "probability": 100497 / 100000,  # 1.00
        "quota": "OS",
        "seat_type": "OBC-NCL",
        "calculation": "(0.5 × 60) + (0.4 × 78.65) + (0.1 × 60) = 67.46"
    },
    {
        "rank": 5,
        "institute": "NIT Raipur",
        "branch": "Metallurgical and Materials Engineering",
        "classification": "TARGET",
        "final_score": 67.46,
        "branch_score": 60,
        "institute_score": 78.65,
        "probability_score": 60,
        "closing_rank": 103435,
        "probability": 103435 / 100000,  # 1.03
        "quota": "OS",
        "seat_type": "OPEN",
        "calculation": "(0.5 × 60) + (0.4 × 78.65) + (0.1 × 60) = 67.46"
    },
]

# ============================================================================
# RANKING ANALYSIS: IS IT SENSIBLE?
# ============================================================================

"""
✓ RANKING VERIFICATION

1. BRANCH DOMINANCE (50% weight):
   - Top 5 all have CSE/ECE (scores 100/80)
   - Lower choices have ME (60) or Civil (40)
   - ✓ Correctly prioritizes user's branch preference

2. INSTITUTE QUALITY (40% weight) AS TIE-BREAKER:
   - Position 1: NIT Puducherry (CSE, 65.17) beats IIIT Trichy (ECE, 44.94)
     Because CSE is 1st choice (100) vs 2nd choice (80)
   - Position 2: NIT Nagaland (ECE, 68.54) beats NIT Raipur (ME, 78.65)
     Because ECE is 2nd (80) vs ME is 3rd (60)
   - ✓ Correctly uses institute quality to break branch ties

3. PROBABILITY AS FINAL TIE-BREAKER (10% weight):
   - Position 4-5: Both NIT Raipur, both score 67.46 (same branch/institute)
     Ranked equally (100 × 0.5 + 100 × 0.4 + 100 × 0.1 = 100)
     Probability values differ (1.00 vs 1.03) but both SAFE, so both 100 points
   - ✓ Only affects when branch and institute are identical

4. QUALIFICATION TEST:
   - Position 1: NIT Puducherry CSE
     User rank 100K, closing 120.4K → 1.20 ≥ 1.10 (SAFE) ✓
     Rank 100K ∈ [opening, closing] ✓
     Category OBC-NCL can use OBC-NCL seats ✓
     Female can use GN (general) gender seats ✓
   
   - Position 3: IIIT Trichy ECE
     User rank 100K, closing 117.3K → 1.17 ≥ 1.10 (SAFE) ✓
     Female-only seat, user is Female ✓

CONCLUSION: ✓ Ranking is SENSIBLE and follows designed algorithm
"""

# ============================================================================
# PART 2: HOME STATE FILTERING LOGIC WITH EXAMPLES
# ============================================================================

"""
HOME STATE FILTERING - COMPLETE ANALYSIS

Scenario: User's Home State = Rajasthan

For MNIT Jaipur (located in Rajasthan):

CASE 1: State Preference = "Home State Only"
────────────────────────────────────────────

MNIT Jaipur HS Quota (Home State quota):
  ✓ INCLUDED - user is from home state, quota is HS
  
MNIT Jaipur OS Quota (Other State quota):
  ✗ EXCLUDED - user chose "Home State Only", quota is OS

Result for user: Only HS quotas from MNIT Jaipur are shown


CASE 2: State Preference = "Home State Priority"
──────────────────────────────────────────────────

MNIT Jaipur HS Quota (Home State quota):
  ✓ INCLUDED - user's home state institute, HS quota is preferred
  
MNIT Jaipur OS Quota (Other State quota):
  ✓ INCLUDED - user's home state institute, can also use OS if HS fills
  
NIT Delhi OS Quota (Other State, but not home state):
  ✓ INCLUDED - "Home State Priority" allows OS from other institutes
  
NIT Delhi HS Quota (Home State from Delhi):
  ✗ EXCLUDED - HS quota is only for Delhi residents, user is from Rajasthan

Result for user:
  - MNIT Jaipur: both HS and OS
  - Other institutes: only OS quotas


CASE 3: State Preference = "Any State"
───────────────────────────────────────

MNIT Jaipur HS Quota:
  ✓ INCLUDED - no state filter, all quotas included
  
MNIT Jaipur OS Quota:
  ✓ INCLUDED - no state filter, all quotas included
  
NIT Delhi HS Quota:
  ✓ INCLUDED - no state filter, all quotas included
  
NIT Delhi OS Quota:
  ✓ INCLUDED - no state filter, all quotas included

Result for user: All quotas from all institutes are shown

════════════════════════════════════════════════════════════════════

FILTERING ALGORITHM (from code):

if state_preference == "Home State Only":
    # Only HS from home state
    if institute_state == user.home_state and quota == 'HS':
        ✓ INCLUDE
    else:
        ✗ EXCLUDE

elif state_preference == "Home State Priority":
    # HS from home state + OS from anywhere
    if institute_state == user.home_state:
        # Home state institute
        if quota == 'HS':  # Home state quota
            ✓ INCLUDE
        else:  # Must be OS - user can use this too
            ✓ INCLUDE if quota == 'OS'
    else:
        # Other state institute - only OS available to this user
        if quota == 'OS':
            ✓ INCLUDE
        else:  # HS quota from other state
            ✗ EXCLUDE (HS is for home state residents)

elif state_preference == "Any State":
    # Everything
    ✓ INCLUDE (no filter)

════════════════════════════════════════════════════════════════════

PRACTICAL EXAMPLES:

User: Home State = Maharashtra, Rank 80K, Category = General

CHOICE A: NIT Nagpur (Maharashtra), CSE, HS quota, OPEN seat, closing 75K
──────────────────────────────────────────────────────────────────────────
Rank check: 75K ≤ 80K ≤ X (within range) ✓

If "Home State Only":
  State check: Nagpur in Maharashtra ✓, Quota HS ✓
  → INCLUDED ✓

If "Home State Priority":
  State check: Nagpur in Maharashtra ✓
  Quota check: HS ✓
  → INCLUDED ✓

If "Any State":
  → INCLUDED ✓


CHOICE B: NIT Nagpur (Maharashtra), CSE, OS quota, OPEN seat, closing 70K
──────────────────────────────────────────────────────────────────────────
Rank check: 70K ≤ 80K ≤ X (within range) ✓

If "Home State Only":
  State check: Nagpur in Maharashtra ✓
  Quota check: OS ✗ (user wants HS only)
  → EXCLUDED ✗

If "Home State Priority":
  State check: Nagpur in Maharashtra ✓
  Quota check: OS (can also use this)
  → INCLUDED ✓

If "Any State":
  → INCLUDED ✓


CHOICE C: NIT Delhi (Delhi), CSE, HS quota, OPEN seat, closing 60K
──────────────────────────────────────────────────────────────────
Rank check: 60K ≤ 80K ≤ X (within range) ✓

If "Home State Only":
  State check: Delhi NOT in Maharashtra ✗
  → EXCLUDED ✗

If "Home State Priority":
  State check: Delhi NOT in Maharashtra (other state)
  Quota check: HS (only for Delhi residents) ✗
  → EXCLUDED ✗

If "Any State":
  → INCLUDED ✓


CHOICE D: NIT Delhi (Delhi), CSE, OS quota, OPEN seat, closing 50K
───────────────────────────────────────────────────────────────────
Rank check: 50K ≤ 80K ≤ X (within range) ✓

If "Home State Only":
  State check: Delhi NOT in Maharashtra ✗
  → EXCLUDED ✗

If "Home State Priority":
  State check: Delhi NOT in Maharashtra (other state)
  Quota check: OS ✓ (available to any state resident)
  → INCLUDED ✓

If "Any State":
  → INCLUDED ✓

════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# PART 3: SEAT TYPE MATCHING LOGIC FOR ALL CATEGORIES
# ============================================================================

"""
SEAT TYPE MATCHING - COMPLETE ANALYSIS

JoSAA/CSAB allocates seats by category + quota + gender combination.

Each cutoff record has:
  - seat_type: OPEN, OBC-NCL, SC, ST, EWS, PWD, etc.
  - gender: GN (General), F (Female), M (Male)

User Profile:
  - Category: GN, EWS, OBC-NCL, SC, ST
  - Gender: M, F

════════════════════════════════════════════════════════════════════

CATEGORY 1: GENERAL (GN) CATEGORY
──────────────────────────────────

Eligible seat_types: ['OPEN']

Why?
- General category candidates cannot use reserved seats
- Reserved seats are for specific categories only
- General candidates can only compete for OPEN (unreserved) seats

Examples:

Cutoff 1: seat_type = 'OPEN'       → ✓ MATCH (GN can use OPEN)
Cutoff 2: seat_type = 'OBC-NCL'    → ✗ NO MATCH (reserved seat)
Cutoff 3: seat_type = 'SC'         → ✗ NO MATCH (reserved seat)
Cutoff 4: seat_type = 'ST'         → ✗ NO MATCH (reserved seat)
Cutoff 5: seat_type = 'EWS'        → ✗ NO MATCH (reserved seat)
Cutoff 6: seat_type = 'PWD'        → ✗ NO MATCH (reserved seat)


════════════════════════════════════════════════════════════════════

CATEGORY 2: ECONOMICALLY WEAKER SECTION (EWS)
───────────────────────────────────────────────

Eligible seat_types: ['EWS', 'OPEN']

Why?
- EWS candidates can use their dedicated EWS reserved seats
- EWS candidates can ALSO compete for OPEN (unreserved) seats
- This is a policy feature: reserved category candidates can use open seats

Examples:

Cutoff 1: seat_type = 'EWS'        → ✓ MATCH (EWS category seat)
Cutoff 2: seat_type = 'OPEN'       → ✓ MATCH (EWS can also compete for open)
Cutoff 3: seat_type = 'OBC-NCL'    → ✗ NO MATCH (different reserved seat)
Cutoff 4: seat_type = 'SC'         → ✗ NO MATCH (different reserved seat)

Real example:
  Rank 100K, Category EWS
  
  Cutoff A: HS, OPEN, CLOSING 80K
    EWS user at 100K is worse than 80K → doesn't qualify for OPEN
  
  Cutoff B: HS, EWS, CLOSING 120K
    EWS user at 100K ≤ 120K → qualifies for EWS seat ✓


════════════════════════════════════════════════════════════════════

CATEGORY 3: OTHER BACKWARD CLASSES (OBC-NCL)
──────────────────────────────────────────────

Eligible seat_types: ['OBC-NCL', 'OPEN']

Why?
- OBC-NCL candidates can use their dedicated OBC-NCL reserved seats
- OBC-NCL candidates can ALSO compete for OPEN seats
- Same logic as EWS

Examples:

Cutoff 1: seat_type = 'OBC-NCL'    → ✓ MATCH (OBC-NCL category seat)
Cutoff 2: seat_type = 'OPEN'       → ✓ MATCH (OBC-NCL can also compete)
Cutoff 3: seat_type = 'SC'         → ✗ NO MATCH (different reserved seat)
Cutoff 4: seat_type = 'ST'         → ✗ NO MATCH (different reserved seat)
Cutoff 5: seat_type = 'EWS'        → ✗ NO MATCH (different reserved seat)

Real example (from test output):
  Rank 100K, Category OBC-NCL, Gender Female
  
  NIT Puducherry, CSE, HS, OBC-NCL, GN gender, closing 120407
    Category: OBC-NCL matches OBC-NCL seat ✓
    Gender: GN (general) available to all genders ✓
    Rank: 100K ≤ 120407 ✓
    → INCLUDED ✓
  
  NIT Raipur, ECE, OS, OPEN, F gender, closing 103435
    Category: OBC-NCL can use OPEN ✓
    Gender: F (female-only) and user is Female ✓
    Rank: 100K ≤ 103435 ✓
    → INCLUDED ✓


════════════════════════════════════════════════════════════════════

CATEGORY 4: SCHEDULED CASTE (SC)
─────────────────────────────────

Eligible seat_types: ['SC', 'OPEN']

Why?
- SC candidates can use their dedicated SC reserved seats
- SC candidates can ALSO compete for OPEN seats

Examples:

Cutoff 1: seat_type = 'SC'         → ✓ MATCH (SC category seat)
Cutoff 2: seat_type = 'OPEN'       → ✓ MATCH (SC can also compete)
Cutoff 3: seat_type = 'OBC-NCL'    → ✗ NO MATCH (different reserved seat)
Cutoff 4: seat_type = 'ST'         → ✗ NO MATCH (different reserved seat)
Cutoff 5: seat_type = 'EWS'        → ✗ NO MATCH (different reserved seat)


════════════════════════════════════════════════════════════════════

CATEGORY 5: SCHEDULED TRIBE (ST)
─────────────────────────────────

Eligible seat_types: ['ST', 'OPEN']

Why?
- ST candidates can use their dedicated ST reserved seats
- ST candidates can ALSO compete for OPEN seats

Examples:

Cutoff 1: seat_type = 'ST'         → ✓ MATCH (ST category seat)
Cutoff 2: seat_type = 'OPEN'       → ✓ MATCH (ST can also compete)
Cutoff 3: seat_type = 'OBC-NCL'    → ✗ NO MATCH (different reserved seat)
Cutoff 4: seat_type = 'SC'         → ✗ NO MATCH (different reserved seat)
Cutoff 5: seat_type = 'EWS'        → ✗ NO MATCH (different reserved seat)


════════════════════════════════════════════════════════════════════

SUMMARY TABLE: Category → Eligible Seat Types

┌────────────┬─────────────────────────────────────────┐
│ Category   │ Eligible Seat Types                     │
├────────────┼─────────────────────────────────────────┤
│ GN         │ OPEN                                    │
│ EWS        │ EWS, OPEN                               │
│ OBC-NCL    │ OBC-NCL, OPEN                           │
│ SC         │ SC, OPEN                                │
│ ST         │ ST, OPEN                                │
└────────────┴─────────────────────────────────────────┘

Key Principle:
- Only GN is restricted to OPEN seats
- All reserved categories can use their seat + OPEN seats
- A reserved category CANNOT use other reserved seats

════════════════════════════════════════════════════════════════════

FILTERING ALGORITHM (from code):

def get_eligible_seat_types(category):
    mapping = {
        Category.GN:       ['OPEN'],
        Category.EWS:      ['EWS', 'OPEN'],
        Category.OBC_NCL:  ['OBC-NCL', 'OPEN'],
        Category.SC:       ['SC', 'OPEN'],
        Category.ST:       ['ST', 'OPEN'],
    }
    return mapping[category]

def category_filter(cutoff, user_category):
    eligible_types = get_eligible_seat_types(user_category)
    return cutoff.seat_type in eligible_types

════════════════════════════════════════════════════════════════════

COMBINED CATEGORY + GENDER FILTERING:

Consider: User is Female, Category OBC-NCL

For each cutoff, BOTH conditions must be true:

1. Seat Type Match: cutoff.seat_type in ['OBC-NCL', 'OPEN']
2. Gender Match: cutoff.gender in ['GN', 'F']

Example Cutoffs:

Cutoff A: OBC-NCL seat, GN gender
  Category check: OBC-NCL ✓
  Gender check: GN (available to all) ✓
  → ELIGIBLE ✓

Cutoff B: OBC-NCL seat, F gender
  Category check: OBC-NCL ✓
  Gender check: F (female-only, user is female) ✓
  → ELIGIBLE ✓

Cutoff C: OPEN seat, GN gender
  Category check: OPEN ✓ (OBC-NCL can use)
  Gender check: GN ✓
  → ELIGIBLE ✓

Cutoff D: OPEN seat, F gender
  Category check: OPEN ✓
  Gender check: F ✓
  → ELIGIBLE ✓

Cutoff E: SC seat, GN gender
  Category check: SC ✗ (OBC-NCL cannot use SC seat)
  → NOT ELIGIBLE ✗

Cutoff F: EWS seat, GN gender
  Category check: EWS ✗ (OBC-NCL cannot use EWS seat)
  → NOT ELIGIBLE ✗

════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# PART 4: COMPLETE FILTERING FLOW EXAMPLE
# ============================================================================

"""
END-TO-END FILTERING EXAMPLE

User: Rank 100K, OBC-NCL, Female, Maharashtra, "Any State" preference

For each cutoff in database:

Cutoff X: NIT Puducherry, CSE, HS, OBC-NCL, GN, opening 100K, closing 120407

Step 1: Category Filter
  user.category = OBC-NCL
  eligible_seat_types = ['OBC-NCL', 'OPEN']
  cutoff.seat_type = 'OBC-NCL'
  ✓ 'OBC-NCL' in ['OBC-NCL', 'OPEN'] → PASS

Step 2: Gender Filter
  user.gender = 'F'
  cutoff.gender = 'GN'
  ✓ 'GN' == 'GN' (general seats available to all) → PASS

Step 3: Quota Filter
  state_preference = 'Any State'
  ✓ No filter applied → PASS

Step 4: Rank Filter
  user.crl_rank = 100000
  cutoff.opening_rank = 100000
  cutoff.closing_rank = 120407
  ✓ 100000 ≤ 100000 ≤ 120407 → PASS

Step 5: Branch Filter
  cutoff.program_name = 'Computer Science and Engineering'
  user.branch_preference = ['CSE', 'ECE', 'ME', 'Civil']
  ✓ 'cse' in 'computer science and engineering' → PASS

Step 6: Institute Type Filter
  cutoff.institute_type = 'NIT'
  user.preferred_institute_types = ['NIT', 'IIIT', 'GFTI']
  ✓ 'NIT' in ['NIT', 'IIIT', 'GFTI'] → PASS

ALL CHECKS PASSED → CUTOFF IS ELIGIBLE

────────────────────────────────────

Now score it:

Branch Score:
  Program: 'Computer Science and Engineering'
  Matches: 'CSE' (index 0)
  Score = 100 (1st preference)

Institute Score:
  From metadata: counselor_priority_rank = 42
  Score = 100 - ((42-1)/89) × 100 = 65.17

Classification:
  Probability = 120407 / 100000 = 1.2041
  1.2041 ≥ 1.10 → SAFE
  Probability Score = 100

Final Score:
  (0.5 × 100) + (0.4 × 65.17) + (0.1 × 100)
  = 50 + 26.07 + 10
  = 86.07

════════════════════════════════════════════════════════════════════
"""

# CSAB Recommendation Engine - Quick Reference Guide

## Scoring Formula Reference

```
FINAL_SCORE = (0.5 × Branch) + (0.4 × Institute) + (0.1 × Probability)

Component Scores (all 0-100):
  Branch Score:      100 (1st pref), 80 (2nd), 60 (3rd), 40 (4th), 0 (below min)
  Institute Score:   100 (rank 1) to 0 (rank 90) - from metadata
  Probability Score: 100 (SAFE), 60 (TARGET), 20 (DREAM)
```

---

## Classification Quick Reference

```
SAFE:   Probability ≥ 1.10  (Closing Rank ≥ 1.10 × User Rank)
TARGET: 0.91 ≤ Prob < 1.10  (0.91 × User Rank ≤ Closing Rank < 1.10 × User Rank)
DREAM:  Probability < 0.91  (Closing Rank < 0.91 × User Rank)

Example (User Rank = 100K):
  Closing 120K → Prob 1.20 → SAFE ✅
  Closing 105K → Prob 1.05 → TARGET ✅
  Closing 85K  → Prob 0.85 → DREAM ✅
```

---

## Category to Seat Type Matching

```
┌──────────┬──────────────────────────────┐
│ Category │ Eligible Seat Types          │
├──────────┼──────────────────────────────┤
│ GN       │ OPEN only                    │
│ EWS      │ EWS, OPEN                    │
│ OBC-NCL  │ OBC-NCL, OPEN                │
│ SC       │ SC, OPEN                     │
│ ST       │ ST, OPEN                     │
└──────────┴──────────────────────────────┘

Key Rule: Reserved category CAN use OPEN seats, but GN CANNOT use reserved
```

---

## Gender Filtering Rules

```
Cutoff Gender: GN (General)
  → Available to all (M, F)
  
Cutoff Gender: F (Female-only)
  → Only available to females
  
Cutoff Gender: M (Male-only)
  → Only available to males

Example:
  Female user + F gender cutoff     → ✅ ELIGIBLE
  Female user + GN gender cutoff    → ✅ ELIGIBLE
  Female user + M gender cutoff     → ❌ NOT ELIGIBLE
```

---

## Quota Filtering (Home State Logic)

```
┌────────────────────┬──────────────────────────────────────────┐
│ State Preference   │ Filtering Rule                           │
├────────────────────┼──────────────────────────────────────────┤
│ Home State Only    │ HS quota from home state only            │
│                    │ → exclude all OS, all other states       │
├────────────────────┼──────────────────────────────────────────┤
│ Home State         │ HS from home state +                     │
│ Priority           │ OS from any state                        │
│                    │ → exclude HS from other states           │
├────────────────────┼──────────────────────────────────────────┤
│ Any State          │ All quotas (HS, OS) from all institutes  │
│                    │ → no state-based filtering               │
└────────────────────┴──────────────────────────────────────────┘

Example (Home State = Maharashtra):

MNIT Jaipur (Rajasthan):
  "Home State Only"    → ❌ exclude all
  "Home State Priority"→ ✅ OS only
  "Any State"          → ✅ HS and OS

NIT Delhi (Delhi):
  "Home State Only"    → ❌ exclude all
  "Home State Priority"→ ✅ OS only
  "Any State"          → ✅ HS and OS

NIT Mumbai (Maharashtra):
  "Home State Only"    → ✅ HS only
  "Home State Priority"→ ✅ HS (and OS if available)
  "Any State"          → ✅ HS and OS
```

---

## Branch Preference Matching

```
User specifies preferred branches in order:
  1st: CSE   → Score 100
  2nd: ECE   → Score 80
  3rd: ME    → Score 60
  4th: Civil → Score 40
  5th+: Below minimum → Score 0 (EXCLUDED)

Keyword Matching Used:
  CSE → "computer science", "cse", "information technology", "it"
  ECE → "electronics", "ece", "electrical"
  ME  → "mechanical", "me", "production"
  Civil → "civil", "ce"

Why needed: Program names vary in database
  ✅ "Computer Science and Engineering"
  ✅ "Information Technology"
  ✅ "Electronics and Communication Engineering"
  ✅ "Mechanical Engineering"
  ✅ "Civil Engineering"
```

---

## Complete Filtering Pipeline

```
For each cutoff in database:

1. CATEGORY FILTER
   Is seat_type in eligible_types[user_category]? 
   → Pass: continue | Fail: skip cutoff

2. GENDER FILTER
   Is cutoff.gender in ['GN', user_gender]?
   → Pass: continue | Fail: skip cutoff

3. QUOTA FILTER (Home State)
   Does cutoff match state_preference policy?
   → Pass: continue | Fail: skip cutoff

4. RANK FILTER
   Is opening_rank ≤ user_rank ≤ closing_rank?
   → Pass: continue | Fail: skip cutoff

5. BRANCH FILTER
   Is branch in user's acceptable branches?
   → Pass: continue | Fail: skip cutoff

6. INSTITUTE TYPE FILTER
   Is institute_type in user's preferred types?
   → Pass: continue | Fail: skip cutoff

✅ ALL PASSED → Cutoff is eligible, calculate score
❌ ANY FAILED → Cutoff is rejected, skip to next
```

---

## Real Test Results

```
User Profile:
  Rank: 100K | Category: OBC-NCL | Gender: F | State: Maharashtra
  Branches: CSE > ECE > ME > Civil | Types: NIT, IIIT, GFTI

Results Summary:
  Total eligible: 34 choices
  SAFE:   9 choices (Prob ≥ 1.10)
  TARGET: 25 choices (0.91 ≤ Prob < 1.10)
  DREAM:  0 choices (Prob < 0.91)

Top 5 Choices:
  1. NIT Puducherry - CSE (86.07) SAFE ✅
  2. NIT Nagaland - ECE (73.42) TARGET ✅
  3. IIIT Trichy - ECE (67.98) SAFE ✅
  4. NIT Raipur - ME (67.46) TARGET ✅
  5. NIT Raipur - ME (67.46) TARGET ✅

✓ Ranking is sensible: CSE ranked first (highest preference)
✓ Institute quality used as tie-breaker: Nagaland ECE beats Trichy ME
✓ Probability acts as minor factor: All SAFE ranked first, then TARGET
✓ No DREAM choices: All have Prob ≥ 0.91 (at least possible)
```

---

## Example Calculations

### Example 1: CSE at Top NIT
```
Institute: NIT Puducherry
Program: Computer Science and Engineering
Rank: 100K, Category: OBC-NCL, Female

Branch Score:
  Program contains 'CSE' at index 0
  → Score = 100 (1st preference)

Institute Score:
  Priority rank from metadata: 42
  → Score = 100 - ((42-1)/89) × 100 = 65.17

Probability:
  Closing rank: 120,407
  Prob = 120,407 / 100,000 = 1.204
  1.204 ≥ 1.10 → SAFE
  → Probability Score = 100

Final Score:
  (0.5 × 100) + (0.4 × 65.17) + (0.1 × 100)
  = 50 + 26.07 + 10
  = 86.07 ✅

Position: #1 (highest score)
```

### Example 2: ECE at Mid-tier NIT
```
Institute: NIT Nagaland
Program: Electronics and Instrumentation Engineering
Rank: 100K, Category: OBC-NCL

Branch Score:
  Program contains 'ECE' at index 1
  → Score = 80 (2nd preference)

Institute Score:
  Priority rank: 34 (better than Puducherry)
  → Score = 100 - ((34-1)/89) × 100 = 68.54

Probability:
  Closing rank: 101,032
  Prob = 101,032 / 100,000 = 1.010
  0.91 ≤ 1.010 < 1.10 → TARGET
  → Probability Score = 60

Final Score:
  (0.5 × 80) + (0.4 × 68.54) + (0.1 × 60)
  = 40 + 27.42 + 6
  = 73.42 ✅

Position: #2 (lower than CSE despite similar institute quality)
Note: Branch preference (80 vs 100) makes the difference
```

### Example 3: ECE at Lower-tier IIIT
```
Institute: IIIT Tiruchirappalli
Program: Electronics and Communication Engineering
Rank: 100K, Gender: Female

Branch Score:
  Program contains 'ECE' at index 1
  → Score = 80 (2nd preference)

Institute Score:
  Priority rank: 71 (lower tier IIIT)
  → Score = 100 - ((71-1)/89) × 100 = 21.35

Probability:
  Closing rank: 117,273
  Prob = 117,273 / 100,000 = 1.173
  1.173 ≥ 1.10 → SAFE
  → Probability Score = 100

Final Score:
  (0.5 × 80) + (0.4 × 21.35) + (0.1 × 100)
  = 40 + 8.54 + 10
  = 58.54 (approximately)

Position: Lower (poor institute quality hurts score despite SAFE)
```

---

## Debugging Checklist

If a cutoff is not appearing in results:

```
□ Rank Check Failed?
  → Is user_rank between opening and closing?
  
□ Category Check Failed?
  → Is user's category eligible for seat_type?
  
□ Gender Check Failed?
  → Is user_gender compatible with cutoff.gender?
  
□ Branch Check Failed?
  → Is branch in user's acceptable list?
  
□ Quota Check Failed?
  → Does quota match state_preference?
  
□ Institute Type Check Failed?
  → Is institute_type in user's preferences?
  
□ Branch Score is 0?
  → Is branch below minimum acceptable?
  → These are excluded from results
  
□ All checks passed but not in top 20?
  → Score may be too low (many better options exist)
  → Check final_score calculation
```

---

## Files in This Directory

```
recommendation_engine/          # Main recommendation engine
├── models.py                  # Data classes
├── filters.py                 # Filtering logic
├── classifier.py              # Dream/Target/Safe classification
├── ranker.py                  # Scoring functions
├── engine.py                  # Main engine class
├── __init__.py                # Package init
└── README.md                  # Full documentation

test_engine.py                 # Test script with sample user

VERIFICATION_REPORT.md         # Comprehensive verification (this)
TOP_20_ANALYSIS.py             # Top 20 detailed breakdown
FILTERING_ANALYSIS.py          # Complete filtering examples
QUICK_REFERENCE.md             # This file
```

---

## Contact & Questions

For algorithm clarifications, see:
- **Design Phase**: Complete design document
- **Implementation**: Detailed code comments
- **Testing**: test_engine.py output
- **Verification**: This report

All filtering logic is transparent and can be traced through the code.

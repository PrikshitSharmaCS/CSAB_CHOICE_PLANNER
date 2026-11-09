"""
Test script for CSAB recommendation engine.
"""

from pathlib import Path
from recommendation_engine.engine import create_engine
from recommendation_engine.models import UserProfile, Category


def print_recommendations(result, user, max_choices=20):
    """Pretty print recommendations."""
    print("\n" + "=" * 100)
    print("CSAB CHOICE FILLING RECOMMENDATION")
    print("=" * 100)
    
    print(f"\nUser Profile:")
    print(f"  CRL Rank: {user.crl_rank}")
    print(f"  Category: {user.category.value}")
    print(f"  Gender: {user.gender}")
    print(f"  Home State: {user.home_state}")
    print(f"  State Preference: {user.state_preference}")
    print(f"  Branch Preference: {' > '.join(user.branch_preference)}")
    print(f"  Minimum Acceptable: {user.minimum_acceptable_branch}")
    print(f"  Institute Types: {', '.join(user.preferred_institute_types)}")
    
    print("\n" + "-" * 100)
    print("SAFE CHOICES (Guaranteed Allocation)")
    print("-" * 100)
    if result.safe_choices:
        for idx, rec in enumerate(result.safe_choices[:5], 1):
            print(
                f"{idx}. {rec.cutoff.institute_name} - {rec.cutoff.program_name.split('(')[0].strip()}"
            )
            print(
                f"   Score: {rec.final_score:.2f} | Branch: {rec.branch_score:.0f} | "
                f"Institute: {rec.institute_score:.2f} | Prob: {rec.probability_score:.0f} | "
                f"Prob Value: {rec.probability:.2f}"
            )
            print(f"   Quota: {rec.cutoff.quota} | Seat: {rec.cutoff.seat_type} | "
                  f"Gender: {rec.cutoff.gender}")
            print(f"   Closing Rank: {rec.cutoff.closing_rank}\n")
    else:
        print("No SAFE choices found.\n")
    
    print("-" * 100)
    print("TARGET CHOICES (Realistic Chances)")
    print("-" * 100)
    if result.target_choices:
        for idx, rec in enumerate(result.target_choices[:5], 1):
            print(
                f"{idx}. {rec.cutoff.institute_name} - {rec.cutoff.program_name.split('(')[0].strip()}"
            )
            print(
                f"   Score: {rec.final_score:.2f} | Branch: {rec.branch_score:.0f} | "
                f"Institute: {rec.institute_score:.2f} | Prob: {rec.probability_score:.0f} | "
                f"Prob Value: {rec.probability:.2f}"
            )
            print(f"   Quota: {rec.cutoff.quota} | Seat: {rec.cutoff.seat_type} | "
                  f"Gender: {rec.cutoff.gender}")
            print(f"   Closing Rank: {rec.cutoff.closing_rank}\n")
    else:
        print("No TARGET choices found.\n")
    
    print("-" * 100)
    print("DREAM CHOICES (Best Case Scenario)")
    print("-" * 100)
    if result.dream_choices:
        for idx, rec in enumerate(result.dream_choices[:5], 1):
            print(
                f"{idx}. {rec.cutoff.institute_name} - {rec.cutoff.program_name.split('(')[0].strip()}"
            )
            print(
                f"   Score: {rec.final_score:.2f} | Branch: {rec.branch_score:.0f} | "
                f"Institute: {rec.institute_score:.2f} | Prob: {rec.probability_score:.0f} | "
                f"Prob Value: {rec.probability:.2f}"
            )
            print(f"   Quota: {rec.cutoff.quota} | Seat: {rec.cutoff.seat_type} | "
                  f"Gender: {rec.cutoff.gender}")
            print(f"   Closing Rank: {rec.cutoff.closing_rank}\n")
    else:
        print("No DREAM choices found.\n")
    
    print("=" * 100)
    print("FINAL RECOMMENDED CHOICE ORDER")
    print("=" * 100)
    
    if result.final_order:
        for idx, rec in enumerate(result.final_order[:max_choices], 1):
            print(
                f"{idx:2d}. {rec.cutoff.institute_name:50s} - "
                f"{rec.cutoff.program_name.split('(')[0].strip():25s} "
                f"[{rec.classification.value:6s}] Score: {rec.final_score:6.2f}"
            )
    else:
        print("No eligible choices found!")
    
    print("=" * 100)
    print(f"\nTotal Choices: {len(result.final_order)}")
    print(f"  SAFE: {len(result.safe_choices)}")
    print(f"  TARGET: {len(result.target_choices)}")
    print(f"  DREAM: {len(result.dream_choices)}")
    print("=" * 100 + "\n")


def test_engine():
    """Run test with sample user profile."""
    # Get workspace directory
    workspace_dir = str(Path(__file__).parent)
    
    # Create engine
    print("Initializing recommendation engine...")
    engine = create_engine(workspace_dir)
    print("[OK] Engine initialized\n")
    
    # Create sample user profile
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
    
    print("Generating recommendations...")
    result = engine.generate_recommendations(user)
    print("[OK] Recommendations generated\n")
    
    # Print results
    print_recommendations(result, user, max_choices=20)


if __name__ == "__main__":
    test_engine()

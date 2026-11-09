from pathlib import Path
import traceback
from typing import List, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from recommendation_engine import Category, create_engine
from recommendation_engine.models import Recommendation, UserProfile


class RecommendationRequest(BaseModel):
    crlRank: int = Field(..., gt=0)
    category: Literal["GN", "EWS", "OBC-NCL", "SC", "ST"]
    gender: Literal["M", "F"]
    homeState: str
    instituteTypes: List[Literal["NIT", "IIIT", "GFTI"]]
    branchPreference: List[str]
    minimumBranch: str
    statePreference: Literal["Home State Only", "Home State Priority", "Any State"]

    model_config = {
        "json_schema_extra": {
            "example": {
                "crlRank": 100000,
                "category": "OBC-NCL",
                "gender": "F",
                "homeState": "Maharashtra",
                "instituteTypes": ["NIT", "IIIT", "GFTI"],
                "branchPreference": ["CSE", "IT", "ECE", "EE", "ME", "Civil"],
                "minimumBranch": "Civil",
                "statePreference": "Any State"
            }
        }
    }


def serialize_recommendation(rec: Recommendation) -> dict:
    return {
        "institute": rec.cutoff.institute_name,
        "branch": rec.cutoff.program_name,
        "classification": rec.classification.value,
        "finalScore": rec.final_score,
        "closingRank": rec.cutoff.closing_rank,
    }


app = FastAPI(
    title="CSAB Recommendation API",
    description="FastAPI wrapper for CSAB choice filling recommendation engine.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

workspace_dir = Path(__file__).resolve().parent
engine = create_engine(str(workspace_dir))


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "institutes": len(engine.institute_state_map),
        "engine": "active"
    }


@app.post("/api/recommend")
def recommend(request: RecommendationRequest):
    try:
        user_profile = UserProfile(
            crl_rank=request.crlRank,
            category=Category(request.category),
            gender=request.gender,
            home_state=request.homeState,
            preferred_institute_types=request.instituteTypes,
            branch_preference=request.branchPreference,
            minimum_acceptable_branch=request.minimumBranch,
            state_preference=request.statePreference,
        )
        result = engine.generate_recommendations(user_profile)
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Recommendation engine failed.") from exc

    serialized = [serialize_recommendation(item) for item in result.final_order]
    return {
        "dreamChoices": [serialize_recommendation(item) for item in result.dream_choices],
        "targetChoices": [serialize_recommendation(item) for item in result.target_choices],
        "safeChoices": [serialize_recommendation(item) for item in result.safe_choices],
        "finalOrder": serialized,
        "final_choice_order": serialized,
    }


# Mount and serve built frontend static files if present
frontend_dist = workspace_dir / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        # Do not intercept API calls
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")


if __name__ == "__main__":
    import uvicorn
    print("\n=======================================================")
    print("  CSAB Choice Filling Assistant is launching...")
    print("  Open in browser: http://localhost:8000")
    print("=======================================================\n")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

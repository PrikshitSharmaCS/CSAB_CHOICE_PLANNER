# 🎓 CSAB Choice Filling Assistant

[![Live Demo](https://img.shields.io/badge/Demo-Live%20on%20Vercel-success?style=for-the-badge&logo=vercel)](https://csab-choice-planner.vercel.app/)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React + Vite](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB.svg)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC.svg)](https://tailwindcss.com/)

> **Live Application**: 🚀 **[csab-choice-planner.vercel.app](https://csab-choice-planner.vercel.app/)**

An algorithmic, counsellor-grade choice-filling advisor for **CSAB Special Rounds & JoSAA Counselling** (NITs, IIITs, and GFTIs). 

It evaluates historical CSAB cutoff trends, category reservations, quotas (Home State, Other State, All India), and personal branch preferences to compute an optimal, risk-balanced choice list categorized into **Dream**, **Target**, and **Safe** tiers.

---

## 🌟 Key Features

- **🎯 3-Tier Smart Classification**:
  - **Dream (Ambitious)**: High-tier aspirational choices where the closing rank is slightly above your rank (up to 25% tighter).
  - **Target (Realistic)**: Balanced options right in your competitive admission zone.
  - **Safe (Guaranteed Backups)**: Reliable safety choices to ensure you secure a seat.
- **⚡ Desirability Scoring**: Ranks colleges using a balanced composite score:
  - **Branch Preference (50%)** + **Institute Reputation (40%)** + **Admission Odds (10%)** + **Home State Quota Bonus (+5 pts)**.
- **🏛️ Comprehensive Cutoff Database**: Over **3,300+ CSAB official cutoff data points** across **108 Institutes** (NITs, IIITs, GFTIs) and **185 Programs**.
- **🌓 Modern Web UI**: Fast React interface with Light/Dark theme toggle, instant search, branch re-ordering, and mobile responsiveness.
- **☁️ Zero-Install Cloud Ready**: Configured with `vercel.json`, `render.yaml`, and `Dockerfile` for instant free web deployment.

---

## 🔗 Try It Live

You don't need to install anything on your machine. Access the live web app directly:

👉 **[https://csab-choice-planner.vercel.app/](https://csab-choice-planner.vercel.app/)**

---

## 💻 Local Installation & Setup

If you want to run the project locally on your computer:

### 1. Clone the repository
```bash
git clone https://github.com/PrikshitSharmaCS/CSAB_CHOICE_PLANNER.git
cd CSAB_CHOICE_PLANNER
```

### 2. Set up Python backend
```bash
# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Build the React frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

### 4. Start the server
```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser!

*(On Windows, you can also just double-click `run_app.bat` to launch everything with one click).*

---

## 📊 How the Score is Calculated

Every eligible college-branch option receives a score from **0 to 105** calculated as:

$$\text{Final Score} = (0.50 \times S_{\text{branch}}) + (0.40 \times S_{\text{institute}}) + (0.10 \times S_{\text{probability}}) + B_{\text{homestate}}$$

| Factor | Weight | Explanation |
| :--- | :---: | :--- |
| **Branch Score** ($S_{\text{branch}}$) | **50%** | Scored from 100 down to 40 based on your preference sequence. |
| **Institute Score** ($S_{\text{institute}}$) | **40%** | Reputational ranking (Top NITs: 90–98, Mid NITs / Top IIITs: 75–88, Newer GFTIs: 50–70). |
| **Admission Probability** ($S_{\text{probability}}$) | **10%** | Higher scores for colleges where your rank is safely above the cutoff. |
| **Home State Bonus** ($B_{\text{homestate}}$) | **+5 pts** | Applied when the college is within your home state. |

### CSAB Choice Ordering Strategy
The algorithm orders your final list strictly by:
1. **Dream Options (Top)**: Maximizes chances of securing an aspirational seat with zero downside.
2. **Target Options (Middle)**: Strong, realistic options matching your merit rank.
3. **Safe Options (Bottom)**: Solid fallback choices to ensure you don't exit counselling unallocated.

---

## 📁 Project Structure

```text
├── api/
│   └── index.py                      # Vercel serverless entrypoint
├── DATA/
│   └── csab_institute_metadata.json  # Institute ranking & state metadata
├── frontend/
│   ├── src/
│   │   ├── components/               # ChoiceTable & UI components
│   │   ├── pages/                    # Home, Profile Form, Results pages
│   │   ├── services/                 # Frontend API client
│   │   └── types.ts                  # Data models & interfaces
│   ├── package.json
│   └── vite.config.ts
├── recommendation_engine/
│   ├── classifier.py                 # Dream / Target / Safe classifier
│   ├── engine.py                     # Recommendation & deduplication logic
│   ├── filters.py                    # Quota, rank, category, branch filters
│   ├── models.py                     # Pydantic schemas
│   └── ranker.py                     # Desirability scoring algorithms
├── app.py                            # FastAPI app & static file host
├── csab.db                           # SQLite database with cutoff data
├── Dockerfile                        # Multi-stage production container
├── render.yaml                       # Render deployment blueprint
├── vercel.json                       # Vercel serverless configuration
├── requirements.txt                  # Python dependencies
├── run_app.bat                       # Windows 1-click launcher
└── README.md
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

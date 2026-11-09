# 🎓 CSAB Choice Filling Assistant

An intelligent, data-driven choice-filling advisor for **CSAB Special Rounds & JoSAA Counselling** for admissions into **NITs, IIITs, and GFTIs**.

It analyzes official CSAB cutoff archives, matches student ranks, categories, quotas, and branch preferences, and automatically generates an optimal, counselor-grade choice list categorized into **Dream**, **Target**, and **Safe** options.

---

## ✨ Features

- **🎯 Intelligent Categorization**:
  - **Dream (Ambitious)**: High-tier branches where closing ranks are slightly above user rank (cutoff up to 25% tighter).
  - **Target (Realistic)**: Balanced options where the student is well within the competitive zone.
  - **Safe (Guaranteed Backups)**: High-probability safety colleges to ensure the student never leaves counselling empty-handed.
- **⚡ Desirability Score Engine**: Ranks choices combining **Branch Preference (50%)**, **Institute Reputation (40%)**, **Admission Probability (10%)**, and **Home State Quota Bonus (+5 pts)**.
- **🏛️ Comprehensive Database**: Pre-indexed SQLite database covering **108 Institutes**, **185 Programs**, and **3,300+ CSAB Cutoff data points** across all quotas (OS, HS, AI, GO).
- **🌓 Modern Web UI**: Built with React, TypeScript, and Tailwind CSS, featuring dark mode, category filtering, search, and responsive mobile layout.
- **🚀 One-Click Cloud Deployment**: Configured for instant deployment on **Render**, **Vercel**, or **Docker** so users can access it without installing Python or Node.js locally!

---

## 🌐 Deploy to the Web (Free Online Access)

To let anyone access your assistant online through their browser without installing anything on their desktop, choose either **Render** (easiest for full-stack) or **Vercel**:

### Option 1: Deploy with Render (Recommended — 100% Free Full-Stack)

Render runs both the Python FastAPI backend and the React frontend together seamlessly on a single URL.

1. Push this repository to your **GitHub** account.
2. Sign in to [Render.com](https://render.com) (free).
3. Click **New +** → **Web Service**.
4. Connect your GitHub repository.
5. Fill in the following settings:
   - **Name**: `csab-choice-filling`
   - **Language / Environment**: `Python 3`
   - **Build Command**:
     ```bash
     npm --prefix frontend install && npm --prefix frontend run build && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn app:app --host 0.0.0.0 --port $PORT
     ```
6. Click **Deploy Web Service**.
7. Once finished, Render gives you a live public URL (e.g. `https://csab-choice-filling.onrender.com`) that anyone can open in their browser!

---

### Option 2: Deploy with Vercel (Serverless Python + Vite Frontend)

This repository includes pre-configured `vercel.json` and `api/index.py` serverless functions.

1. Push your repository to **GitHub**.
2. Go to [Vercel](https://vercel.com) and click **Add New** → **Project**.
3. Import your GitHub repository.
4. Keep the Framework Preset as **Vite** or **Other**.
5. Click **Deploy**. Vercel will automatically build the frontend and host the Python serverless API.

---

### Option 3: Deploy with Docker

```bash
# Build the container image
docker build -t csab-assistant .

# Run the container
docker run -p 8000:8000 csab-assistant
```
Visit `http://localhost:8000` in your browser.

---

## ❓ Why did GitHub Deployment show "Internal Server Error"?

If you previously deployed only to **GitHub Pages** (or standard static web hosting):
- **GitHub Pages only hosts static files (HTML, CSS, JS)**. It **cannot run Python scripts** or host the SQLite database (`csab.db`).
- When a user entered their rank and clicked "Check Options", the frontend made a request to `/api/recommend`.
- Because there was no Python server running to answer that request, the browser received an **Internal Server Error (500)** or **404 Not Found**.
- **Fix**: Deploying to **Render** or **Vercel** (using the instructions above) runs the Python backend (`app.py`) in the cloud alongside the frontend so `/api/recommend` works flawlessly.

---

## 💻 Local Setup & Development

If you wish to run or develop the project locally on your machine:

### Quick Start on Windows

Double-click `run_app.bat` or run:
```powershell
.\run_app.ps1
```
This automatically starts the backend server and opens `http://localhost:8000` in your browser.

---

### Manual Setup

#### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd "CSAB Choice filling order"
```

#### 2. Set up Python backend
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt
```

#### 3. Build React frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

#### 4. Run the server
```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser!

---

## 📊 How the Desirability Score is Calculated

Every eligible college and branch combination is scored on a scale of **0 to 105** using a 4-part formula:

$$\text{Final Score} = (0.50 \times S_{\text{branch}}) + (0.40 \times S_{\text{institute}}) + (0.10 \times S_{\text{probability}}) + B_{\text{homestate}}$$

| Component | Weight | How it works |
| :--- | :---: | :--- |
| **Branch Score** ($S_{\text{branch}}$) | **50%** | Ranked from 100 down to 40 based on the order in your branch preference list. |
| **Institute Score** ($S_{\text{institute}}$) | **40%** | Based on counsellor reputation tiers (Top NITs: 90–98, Mid NITs / Top IIITs: 75–88, Newer GFTIs: 50–70). |
| **Admission Probability** ($S_{\text{probability}}$) | **10%** | Higher scores for safe choices with closing ranks well above your rank. |
| **Home State Bonus** ($B_{\text{homestate}}$) | **+5 pts** | Added when the college is in your home state (if you prioritize Home State). |

### Choice Ordering Philosophy
In official JoSAA / CSAB counselling, choices must **always** be ordered from most ambitious to safest:
1. **Dream Choices (Top)**: Aim for higher-tier institutes/branches with lower risk.
2. **Target Choices (Middle)**: Realistic admissions matching your exact rank range.
3. **Safe Choices (Bottom)**: Guaranteed fallbacks to secure your seat.

---

## 📁 Repository Structure

```text
├── api/
│   └── index.py                      # Vercel serverless entrypoint
├── DATA/
│   └── csab_institute_metadata.json  # Institute reputation & state mapping
├── frontend/
│   ├── src/
│   │   ├── components/               # React UI components (ChoiceTable, etc.)
│   │   ├── pages/                    # Home, Profile Form, Results pages
│   │   ├── services/                 # API client for /api/recommend
│   │   └── types.ts                  # TypeScript types & interfaces
│   ├── package.json
│   └── vite.config.ts
├── recommendation_engine/
│   ├── classifier.py                 # Dream / Target / Safe classifier
│   ├── engine.py                     # Main engine pipeline & deduplication
│   ├── filters.py                    # Quota, rank, category, branch filtering
│   ├── models.py                     # Pydantic data schemas
│   └── ranker.py                     # Desirability scoring algorithm
├── app.py                            # FastAPI application & static file server
├── csab.db                           # SQLite database with all cutoff records
├── Dockerfile                        # Universal container definition
├── render.yaml                       # Render.com 1-click blueprint
├── vercel.json                       # Vercel cloud deployment routing
├── requirements.txt                  # Python dependencies
├── run_app.bat                       # Windows one-click launcher
└── README.md                         # Documentation
```

---

## 📤 How to Push this Repository to GitHub

Run these commands in your project folder to push to GitHub:

```bash
# 1. Initialize git (if not already done)
git init

# 2. Add all files (the .gitignore will automatically skip virtual environments & node_modules)
git add .

# 3. Create your first commit
git commit -m "feat: complete CSAB choice filling assistant with cloud deployment support"

# 4. Set default branch to main
git branch -M main

# 5. Link to your GitHub repository
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>.git

# 6. Push to GitHub
git push -u origin main
```

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

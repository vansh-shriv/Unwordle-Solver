# 🟩🟨⬛ Unwordle Solver (Logic Engine)

A full-stack algorithmic Wordle solver that reconstructs valid word attempt ladders targeting a secret word given row-by-row tile feedback patterns (Green, Yellow, Gray).

Powered by a high-performance **FastAPI (Python)** backend utilizing graph search/pruning algorithms, and a sleek **Cyber-Pixel Glass UI** built with **Next.js 15, React, & Tailwind CSS**.

---

## ✨ Features

- 🎯 **Target Word Matching**: Solve Wordle/Unwordle boards by defining target word lengths (4 to 8 letters) and specifying feedback patterns.
- 🟩🟨⬛ **Interactive Pattern Selector**: Click-to-cycle letter feedback colors:
  - **Green**: Letter is correct and in the right position.
  - **Yellow**: Letter is present in the target word but in the wrong position.
  - **Gray**: Letter is excluded from the word (accounting for duplicate letter frequency rules).
- ⚡ **Multi-Row Solver Engine**: Evaluates multiple guess attempts in sequence to find valid word candidate paths.
- 🔀 **Distinct Words Filter**: Option to enforce unique candidate words across rows or allow repeat words.
- 🎨 **Retro Cyberpunk UI**: CRT scanlines, neon pixel grids, responsive layout, custom typography (`Silkscreen`, `VT323`), and dynamic row management.

---

## 🛠️ Architecture & Tech Stack

```
Unwordle/
├── backend/          # Python FastAPI Solver Engine
│   ├── app/          # API routes, core solver algorithms & model specs
│   ├── data/         # Word dictionaries & pre-calculated lookup tables
│   ├── tests/        # Pytest test suite for feedback logic and endpoints
│   └── requirements.txt
└── frontend/         # Next.js 15 + React + Tailwind CSS Web Application
    ├── src/app/      # App Router, Layout, Cyberpunk CSS theme
    ├── src/components/# Tile row selectors, Header, Presets
    └── src/lib/      # API client for backend integration
```

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Data Structures**: Graph / Constraint Satisfaction Search using `NetworkX` & `Pydantic` validation.
- **Testing**: `pytest`

### Frontend
- **Framework**: [Next.js 15](https://nextjs.org/) (App Router) + React 19 + TypeScript
- **Styling**: Vanilla CSS custom variables, Tailwind CSS, Google Fonts (`Silkscreen`, `VT323`)
- **HTTP Client**: `fetch` API wrapper with strict TypeScript interfaces

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: `3.10` or higher
- **Node.js**: `18.x` or higher (`npm` / `pnpm` / `yarn`)

---

### 1. Running the Backend (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment (optional but recommended)
python -m venv venv
# Activate on Windows:
venv\Scripts\activate
# Activate on macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI development server
uvicorn app.main:app --reload --port 8000
```

The backend server will run at: **`http://localhost:8000`**  
Interactive API docs (Swagger UI): **`http://localhost:8000/docs`**

---

### 2. Running the Frontend (Next.js)

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Next.js development server
npm run dev -- -p 3001
```

The web client will be available at: **`http://localhost:3001`**

---

## 🛰️ API Endpoint Reference

### `POST /api/solve`

Solves the puzzle ladder based on target solution word and row patterns.

#### Request Body Example
```json
{
  "solution": "CRANE",
  "rows": [
    { "id": "row_1", "pattern": ["gray", "yellow", "gray", "gray", "green"] },
    { "id": "row_2", "pattern": ["green", "green", "green", "green", "green"] }
  ],
  "options": {
    "max_candidates_per_row": 20,
    "distinct_words_across_rows": true
  }
}
```

#### Response Example
```json
{
  "solution": "CRANE",
  "word_length": 5,
  "rows": [
    {
      "id": "row_1",
      "pattern": ["gray", "yellow", "gray", "gray", "green"],
      "best_guess": "SLATE",
      "candidates": ["SLATE", "STARE", "SHARE"]
    },
    {
      "id": "row_2",
      "pattern": ["green", "green", "green", "green", "green"],
      "best_guess": "CRANE",
      "candidates": ["CRANE"]
    }
  ],
  "unsolvable_row_ids": []
}
```

---

## 🧪 Testing

To run the backend test suite:

```bash
cd backend
pytest
```

---

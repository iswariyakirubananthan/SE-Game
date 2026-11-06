# 🍌 Banana Quest – Brain Challenge

A web-based mathematical puzzle game developed using **Python (Flask)**, **SQLite**, **HTML5/CSS3/JavaScript**, and the **University of Bedfordshire Banana Game API**.

---

## 📌 Table of Contents
1. [System Architecture](#system-architecture)
2. [Project Folder Structure](#project-folder-structure)
3. [The Four Core Computer Science Themes](#the-four-core-computer-science-themes)
   - [A. Version Control (Git & GitHub)](#a-version-control)
   - [B. Interoperability (REST API Communication)](#b-interoperability)
   - [C. Event-Driven Programming (Client-Side Interactions)](#c-event-driven-programming)
   - [D. Virtual Identity (Authentication & State Management)](#d-virtual-identity)
4. [Database Design & Schema](#database-design--schema)
5. [Required Modules Overview](#required-modules-overview)
6. [Game Rules & Difficulty Tiers](#game-rules--difficulty-tiers)
7. [Installation & Setup in Visual Studio Code](#installation--setup-in-visual-studio-code)
8. [Running the Application](#running-the-application)
9. [Running Automated Unit Tests](#running-automated-unit-tests)
10. [10-Minute Video Presentation & Demonstration Guide](#10-minute-video-presentation-guide)
11. [Academic Attribution & Integrity](#academic-attribution)

---

## 🏗️ 1. System Architecture

The application adopts a **3-tier Distributed Client-Server Architecture**:

```
+-------------------------------------------------------------+
|                     Client Browser Layer                    |
|   - HTML5 Semantic Structure                                |
|   - CSS3 Glassmorphic Gaming UI (Purple / Blue / Yellow)    |
|   - Vanilla JavaScript Event Engine (Timer, Fetch, Keys)    |
+------------------------------+------------------------------+
                               |
                        HTTP / JSON (REST)
                               v
+-------------------------------------------------------------+
|                  Python (Flask) Backend Layer               |
|   - Application Factory (app.py)                            |
|   - Modular Blueprints (auth, game, dashboard, leaderboard) |
|   - Secure Session Management (Signed Cookies)              |
|   - Backend Rule Enforcement & Score Calculation            |
+---------------+-----------------------------+---------------+
                |                             |
      SQL Parameterized Queries         HTTP GET / JSON
                v                             v
+-------------------------------+ +---------------------------+
|      SQLite Database          | |   Banana Game API (UoB)   |
|   - users table               | |   http://marcconrad.com/  |
|   - scores table              | |   uob/banana/api.php      |
|   - Foreign Keys & Cascading  | |   (Live image & solution) |
+-------------------------------+ +---------------------------+
```

### Critical Security Rule
The correct puzzle solution is **never** sent to the client browser while the puzzle is active. When the Python backend calls the external API, it saves the target integer answer strictly inside Flask's server-side session. The browser only receives the image URL. Player answers are verified exclusively on the Python backend to prevent cheating or client-side inspection.

---

## 📁 2. Project Folder Structure

```
banana-quest/
│
├── app.py                      # Flask application factory and entry point
├── database.py                 # SQLite database manager & connection pool
├── requirements.txt            # Python dependencies (Flask, requests, Werkzeug)
├── test_app.py                 # Automated unit test suite (8 passing test suites)
├── README.md                   # Full documentation & presentation guide
├── .gitignore                  # Git ignore rules for venv, database, and cache
│
├── models/
│   ├── __init__.py
│   ├── user.py                 # User model (creation, hashing, auth, stats)
│   └── score.py                # Score model (persistence, leaderboard, history)
│
├── services/
│   ├── __init__.py
│   └── banana_service.py       # Banana API interoperability service & fallback
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Registration, login, logout, session cookies
│   ├── dashboard.py            # User dashboard & stats aggregation
│   ├── game.py                 # Game arena, difficulty, submit, timeout, quit
│   ├── home.py                 # Public landing page
│   ├── leaderboard.py          # Top 10 rankings query & view
│   └── profile.py              # User profile & full gameplay history
│
├── templates/
│   ├── base.html               # Master layout (navbar, alerts, footer)
│   ├── index.html              # Module 1: Home page
│   ├── register.html           # Module 2: User registration form
│   ├── login.html              # Module 3: User login form
│   ├── dashboard.html          # Module 4: Game dashboard
│   ├── difficulty.html         # Module 5: Difficulty selection
│   ├── game.html               # Module 6 & 7: Interactive game arena
│   ├── leaderboard.html        # Module 8: Hall of champions
│   ├── profile.html            # Module 9: User profile & history
│   ├── 404.html                # Error page: Not found
│   └── 500.html                # Error page: Server error
│
├── static/
│   ├── css/
│   │   └── style.css           # Modern gaming UI (Purple/Blue/Yellow gradients)
│   └── js/
│       ├── main.js             # Global alert dismissals & UI helpers
│       └── game.js             # Event-driven game engine (Timer, DOM, Fetch)
│
└── instance/
    └── database.db             # Local SQLite database file (created on runtime)
```

---

## 🎯 3. The Four Core Computer Science Themes

### A. Version Control (Git & GitHub)
- **Repository Initialization**: Git was initialized from the start with a clean `.gitignore` excluding temporary files and binary databases.
- **Meaningful Commit History**: Commits follow the Conventional Commits standard (`feat(...)`, `chore(...)`, `test(...)`).
- **Feature Branching**: Development was organized across dedicated feature branches:
  - `feature/database-auth`: Implementation of database tables, Werkzeug hashing, and session authentication.
  - `feature/game-engine`: Implementation of Banana API service, difficulty rules, scoring, and route controllers.
  - `feature/frontend-ui`: Implementation of responsive UI, Jinja2 templates, CSS styling, and event-driven JavaScript.
- **Merging**: Feature branches were merged into `main` systematically.
- **Collaboration Value**: In industry, Git prevents overwrite conflicts, preserves full audit trails of who made what change, enables rollback to stable releases, and allows teams to work on independent modules in parallel via pull requests.

### B. Interoperability (REST API Communication)
- **Communication Protocol**: Communicates with the external University of Bedfordshire REST service (`http://marcconrad.com/uob/banana/api.php?out=json`) via HTTP `GET` requests using Python `requests`.
- **JSON Serialization & Deserialization**: The dynamic JSON payload is parsed on the server:
  ```json
  {
    "question": "https://www.sanfoh.com/uob/banana/data/tb....png",
    "solution": 8
  }
  ```
- **Resilient Fault Tolerance**: Network requests are bound by a 6-second timeout. If the external university server experiences downtime or connection drops, the service catches `requests.exceptions.RequestException` and seamlessly serves verified fallback puzzles. The player never experiences a crash.

### C. Event-Driven Programming
- **Client-Side Event Engine (`static/js/game.js`)**:
  - `DOMContentLoaded`: Initializes the game engine instance upon page readiness.
  - `click` Events: Answer submission, saving & quitting, play again, and navigation.
  - `keydown` (Enter Key): Allows the player to submit answers using the Enter key for rapid arcade gameplay.
  - `setInterval` & `clearInterval`: 1-second countdown clock that ticks down, with dynamic visual cues (timer turns red and pulses below 10 seconds).
  - `fetch` Asynchronous Promises (`async/await`): Dispatches HTTP `POST` requests to `/game/api/submit` and `/game/api/timeout` without reloading the webpage.
  - **Dynamic DOM Updates**: Updates score, lives, question numbers, feedback banners, and image sources in place.

### D. Virtual Identity
- **User Account Registration**: Captures username and email with input validation (length, character sets, valid email format).
- **Cryptographic Security**: Passwords are never stored in plaintext. They are salted and hashed using **Werkzeug**'s scrypt/pbkdf2 implementation (`generate_password_hash` and `check_password_hash`).
- **Session-Based Authentication**: Authenticated player identities are stored inside cryptographically signed Flask session cookies (`session['user_id']`).
- **Access Control**: A custom `@login_required` Python decorator prevents unauthenticated visitors from accessing `/dashboard`, `/game/play`, or `/profile`.
- **Identity Association**: Saved scores and historical game metrics are tied to the player's primary key (`user_id`) using SQLite Foreign Keys.

---

## 🗄️ 4. Database Design & Schema

### `users` Table
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique user identifier |
| `username` | TEXT | UNIQUE NOT NULL COLLATE NOCASE | Display name |
| `email` | TEXT | UNIQUE NOT NULL COLLATE NOCASE | Login credential |
| `password_hash` | TEXT | NOT NULL | Werkzeug hashed password |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account registration date |

### `scores` Table
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique score entry ID |
| `user_id` | INTEGER | NOT NULL, FOREIGN KEY → `users(id)` ON DELETE CASCADE | Associated player ID |
| `score` | INTEGER | NOT NULL | Final points achieved |
| `difficulty` | TEXT | NOT NULL | Easy, Medium, or Hard |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date and time achieved |

*Note: Foreign key constraints are enforced using `PRAGMA foreign_keys = ON;`.*

---

## 🎮 5. Required Modules Overview

- **Module 1: Home Page (`/`)**: Hero banner, visual puzzle showcase, navigation buttons.
- **Module 2: User Registration (`/register`)**: Account creation with validation and duplicate email check.
- **Module 3: User Login (`/login`)**: Secure credential verification and session initiation.
- **Module 4: Game Dashboard (`/dashboard`)**: Player statistics (Highest Score, Games Played, Total Points, Average Score) and recent matches.
- **Module 5: Difficulty Selection (`/game/difficulty`)**: Three distinct game modes with backend rule enforcement.
- **Module 6: Main Gameplay (`/game/play`)**: Interactive arena displaying live API puzzles, countdown clock, hearts for lives, and answer input.
- **Module 7: Score Management**: Server-side verification, points accumulation, and database persistence.
- **Module 8: Leaderboard (`/leaderboard`)**: Top 10 rankings highlighting the top 3 with Gold, Silver, and Bronze badges.
- **Module 9: User Profile (`/profile`)**: Virtual identity overview with complete chronological match logs.
- **Module 10: Logout (`/logout`)**: Session termination, flash confirmation, and redirect to home.

---

## ⚙️ 6. Game Rules & Difficulty Tiers

| Difficulty Tier | Time per Question | Starting Lives | Points per Correct Answer |
|---|---|---|---|
| **Easy** | 60 seconds | 3 Lives (❤️❤️❤️) | +10 Points |
| **Medium** | 40 seconds | 3 Lives (❤️❤️❤️) | +20 Points |
| **Hard** | 25 seconds | 2 Lives (❤️❤️) | +30 Points |

- **Wrong Answer**: Deducts 1 life. Reveals correct answer and loads the next puzzle.
- **Timeout**: Deducts 1 life. Reveals correct answer and loads the next puzzle.
- **Game Over**: Triggered when lives reach 0. Final score is automatically committed to SQLite.

---

## 💻 7. Installation & Setup in Visual Studio Code

### Prerequisites
- Python 3.10 or newer
- Git

### Step-by-Step Instructions

1. **Open the project in VS Code**:
   ```powershell
   cd c:\Users\iswar\Desktop\SE_GAME
   code .
   ```

2. **Activate the Virtual Environment**:
   - In PowerShell:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - In Command Prompt:
     ```cmd
     .\venv\Scripts\activate.bat
     ```

3. **Install Dependencies** (if setting up on a fresh machine):
   ```powershell
   pip install -r requirements.txt
   ```

---

## 🚀 8. Running the Application

Execute the main application file:
```powershell
.\venv\Scripts\python.exe app.py
```

Open your web browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🧪 9. Running Automated Unit Tests

A comprehensive unit test suite (`test_app.py`) is included to verify all functionality:
```powershell
.\venv\Scripts\python.exe -m unittest test_app.py -v
```

All 8 test suites validate registration, duplicate email rejection, password hashing, session cookies, difficulty rules, route protection, scoring, and leaderboard updates.

---

## 🎙️ 10. 10-Minute Video Presentation & Demonstration Guide

Use this structured presentation plan for your assignment video:

| Timestamp | Section | Key Discussion Points |
|---|---|---|
| **0:00 - 1:30** | **Introduction & Architecture** | Introduce *Banana Quest*. Explain the 3-tier distributed architecture (Browser Frontend → Python Flask Backend → SQLite Database + Banana API). Emphasize that the backend keeps the answer secret to prevent cheating. |
| **1:30 - 3:30** | **Theme D: Virtual Identity & Auth** | Demonstrate Registration (`/register`) and Login (`/login`). Show input validation and explain Werkzeug password hashing. Show session cookie handling and the `@login_required` decorator guarding the Dashboard. |
| **3:30 - 5:30** | **Theme B: Interoperability & Live Gameplay** | Start a Medium game. Explain how Python `requests` sends an HTTP GET request to `marcconrad.com`, parses the JSON payload, and loads the image. Mention the 6-second timeout and fallback mechanism for fault tolerance. |
| **5:30 - 7:30** | **Theme C: Event-Driven Programming** | Show the game arena: explain DOM click events, the Enter key submission, the `setInterval` countdown timer, and the Fetch API asynchronous state transitions without page reload. Intentionally answer incorrectly to demonstrate life deduction and Game Over. |
| **7:30 - 8:45** | **Modules 7, 8, 9: Scores, Leaderboard & Profile** | Show the Leaderboard (`/leaderboard`) updating with the new score. Open the Profile (`/profile`) showing total games, highest score, and full chronological match logs. Demonstrate Logout (`/logout`). |
| **8:45 - 10:00** | **Theme A: Version Control & Conclusion** | Open terminal / Git log. Show the feature branch workflow (`feature/database-auth`, `feature/game-engine`, `feature/frontend-ui`) and conventional commits. Summarize how software engineering best practices were fulfilled. |

---

## 📚 11. Academic Attribution & Integrity

- **External REST API**: University of Bedfordshire Banana Game API by Marc Conrad (`http://marcconrad.com/uob/banana/api.php?out=json`).
- **Icons & Visuals**: UTF-8 Emoji graphics and Google Fonts (Plus Jakarta Sans).
- **Backend & Frontend Code**: Authored for the Computer Science undergraduate assignment at the University of Bedfordshire following modern software engineering principles.

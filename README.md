# FitLife - Production-Ready Django Nutrition & Fitness Tracking Web App

FitLife is a complete, secure, responsive, and database-backed calorie, macro, weight, caffeine, and sugar tracking application. It features automated target calorie calculations using Mifflin-St Jeor and TDEE, timezone-aware daily tracking streaks, data analytics trends (7/30/90 days), and seamless standard + Google OAuth sign-in.

---

## Technical Stack
- **Core Framework**: Python 3.12+ & Django 5.x
- **Frontend**: HTML5, Tailwind CSS (via play CDN), JavaScript
- **Database**: SQLite (Local development), PostgreSQL (Production)
- **Deployment**: Gunicorn, WhiteNoise, Render/Railway-ready
- **Authentication**: Django standard auth + Google OAuth 2.0 (Continue with Google)

---

## Features
- **Modern Landing Page**: Dynamic feature summary, active CTA blocks.
- **Authentication & User Data Isolation**: Account security, preventing IDOR (unauthorized logs views/edits).
- **Onboarding Setup**: Establishes body measurements and BMR/TDEE goals (Lose/Gain/Maintain weight).
- **Streak Tracker**: Timezone-aware consecutive day tracker counting days where calories and protein are entered.
- **Nutrition Log**: Interactive daily form containing calorie, protein, carbs, fat, fiber, sugar, sodium, water, and notes.
- **Dynamic Calculators**:
  - *Calorie Calculator*: Interactive JS food list itemizer. Sums values and logs totals.
  - *Caffeine Calculator*: Select beverage servings and sizes. Standardizes to mg and updates daily log.
  - *Sugar Calculator*: Convert teaspoons, tablespoons, or packets into grams, logging them in today's summaries.
- **Weight Tracking Logs**: Regular logs tracking start weight, current weight, target, and overall changes.
- **Analytics Dashboard**: 7/30/90-day progress trends utilizing Chart.js.

---

## Local Setup & Installation

Follow these steps to run FitLife on your local computer:

### 1. Clone & Set Up Directory
Navigate to the project root directory:
```bash
cd fitness_tracker
```

### 2. Set Up Virtual Environment
**Windows**:
```powershell
python -m venv venv
venv\Scripts\activate
```
**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env     # Windows
cp .env.example .env       # macOS/Linux
```
Configure your `.env` variables (e.g. `SECRET_KEY`, `GOOGLE_CLIENT_ID`, etc.).

### 5. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 7. Run Server
```bash
python manage.py runserver
```
Visit the application at `http://127.0.0.1:8000/`.

---

## Google OAuth 2.0 Integration
To enable "Continue with Google":
1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project, navigate to **APIs & Services** > **Credentials**.
3. Configure the OAuth Consent Screen (External, specify application name and support emails).
4. Go to **Credentials** > **Create Credentials** > **OAuth Client ID**.
5. Select application type as **Web application**.
6. Under **Authorized Redirect URIs**, add:
   - For local development: `http://localhost:8000/auth/google/callback/`
   - For production: `https://your-domain.com/auth/google/callback/`
7. Copy the client ID and Client Secret into your `.env` file (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`).

---

## Production Deployment (Render Example)

Render provides direct support for Django web services:

1. **Create Web Service**: Connect your GitHub repository to Render.
2. **Setup PostgreSQL Database**: Create a Render PostgreSQL database instance and copy the `Internal Database URL` / `External Database URL`.
3. **Configure Environment Variables on Render**:
   - `SECRET_KEY` = (A secure random string)
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `your-render-subdomain.onrender.com`
   - `DATABASE_URL` = (Paste your PostgreSQL connection URI)
   - `GOOGLE_CLIENT_ID` = (Google developer client ID)
   - `GOOGLE_CLIENT_SECRET` = (Google developer client secret)
   - `CSRF_TRUSTED_ORIGINS` = `https://your-render-subdomain.onrender.com`
4. **Build & Start Commands on Render**:
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `python manage.py migrate && gunicorn config.wsgi --log-file -`

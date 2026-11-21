# 🌾 CropCare AI (क्रॉपकेयर एआई)
### Production-Grade AI Agricultural Expert System & Precision Advisory Web Application

CropCare AI is a full-stack, AI-powered agricultural web application built with **Python Flask**, **SQLite**, **Computer Vision**, and **Machine Learning**. It assists farmers, agronomists, and agricultural students with instant plant pathology diagnosis, multi-modal evidence reconciliation, ML-driven crop recommendation, precision fertilizer planning, irrigation budgeting, and bilingual interactive guidance in **English and Hindi (हिंदी)**.

---

## 🚀 Key Modules & Capabilities

### 1. 📸 Multi-Modal AI Crop Disease Diagnosis
- **Dual-Engine Vision Pipeline:**
  - **Local Offline Vision Classifier:** Fast multi-spectral color segmentation (HSV/RGB) and connected-component morphology analysis (`scipy.ndimage`) detecting spot clusters, necrosis percentage, chlorotic halo overlap, and margin decay with zero external internet dependencies.
  - **Cloud Vision Multimodal AI (Optional):** Optional integration with Google Gemini 2.5 Flash Vision for advanced leaf pathology when an API key is configured.
- **Symptom-Based Forward-Chaining Inference Engine:** Agricultural production rules (`IF-THEN`) evaluating observed symptoms, growth stages, and weather triggers with calibrated certainty factors.
- **Multi-Modal Evidence Fusion & Conflict Resolution:**
  - **Mutual Corroboration:** When visual lesion morphology and farmer-reported symptoms agree, certainty is elevated via multi-modal corroboration.
  - **Uncertain / Conflict Diagnosis State:** When modalities diverge (e.g. discrete target spots detected visually at 90.1% while farmer reports water-soaking symptoms yielding partial 40.8% rule confidence), the system avoids premature overrides. It presents both candidate diseases side-by-side, explains the biological basis of the tension, and prescribes a discriminating field inspection test.
  - **Source-Separated Symptoms:** User-selected observations and image-detected lesions are strictly segregated with distinct badges and quantitative metrics.
  - **Deduplicated Differential Diagnoses:** Uses stable disease IDs to ensure clean, non-duplicate candidate comparisons.

### 2. 🌾 Machine Learning Crop Recommendation
- Evaluates soil macronutrients (**Nitrogen, Phosphorus, Potassium**), soil **pH**, and environmental climate (**Temperature, Humidity, Rainfall**).
- Statistically predicts the optimal crop with suitability percentages across 26+ crops (Rice, Wheat, Maize, Chickpea, Cotton, Potato, Tomato, Mustard, Pulses, Fruits, and Plantation crops).
- Uses a pure NumPy Gaussian Maximum Likelihood and agronomic distance engine without platform-specific binary dependencies.

### 3. 🧪 Precision Soil Health & Fertilizer Calculator
- Analyzes soil test values against crop-specific target ranges.
- Formulates a customized fertilizer application plan converting nutrient deficits into commercial bags per acre:
  - **Urea (46% N)**
  - **DAP (18% N, 46% P₂O₅)**
  - **MOP / Potash (60% K₂O)**
- Features an interactive **pH meter gauge** with lime (for acidic soils) and gypsum (for alkaline soils) correction advice.

### 4. 💧 Crop Water & Irrigation Scheduler
- Computes watering intervals based on crop type, growth stage, soil texture (Sandy, Loamy, Clayey), and season (Rabi, Kharif, Zaid).
- Highlights critical moisture-sensitive stages (e.g., Crown Root Initiation in wheat, flowering in tomato).
- Recommends optimal water-saving irrigation methods (Drip, Sprinkler, AWD, Furrow).

### 5. 🤖 Kisan Mitra (AI Agri-Bot)
- Conversational farming assistant powered by Google Gemini (when configured) or an extensive offline agronomic semantic knowledge base covering 35+ topics (organic bio-pesticides, Jeevamrut, Nano Urea, PM-KISAN, crop insurance PMFBY, drip subsidies).
- Available in both English and Hindi.

### 6. 🌐 1-Click Bilingual Language Switcher
- Instant toggle between **English** and **Hindi (हिंदी)** across all UI elements, disease names, symptoms, treatments, crop recommendations, and chat replies.

### 7. 🗄️ SQLite Database Persistence & Audit Logging
- Stores full audit logs for diagnoses, crop recommendations, soil tests, and chat interactions across 5 structured tables.
- Allows farmers to view, filter, print, and delete historical records.

---

## 📁 Project Architecture & Directory Structure

```text
CropCare-Ai/
│
├── app.py                     # Main Flask web server & REST API controller
├── database.py                # SQLite database management (5 tables & CRUD)
├── cropcare.db                # Local SQLite runtime database (auto-created on startup)
├── requirements.txt           # Production Python dependencies (includes gunicorn, scipy, etc.)
├── Procfile                   # Process file for cloud web services (Render, Heroku)
├── render.yaml                # Render Infrastructure-as-Code deployment blueprint
├── .env.example               # Template for environment variables
├── .gitignore                 # Excludes venvs, caches, db, secrets, and temp uploads
├── README.md                  # Comprehensive project documentation
│
├── run_all_tests.py           # Unified regression test runner (all 3 test suites)
├── test_cropcare.py           # Core production system test suite (8 subsystems)
├── tests/
│   └── test_diagnosis_fusion.py # Diagnostic evidence fusion & conflict resolution tests
│
├── expert_system/             # 🧠 AI & Expert System Core
│   ├── __init__.py
│   ├── vision_ai.py           # Local Computer Vision & Gemini Vision classifier
│   ├── crop_recommender.py    # NumPy Gaussian ML crop recommendation model
│   ├── rules.py               # Production rule base for 9 major crops
│   ├── engine.py              # Forward-chaining inference engine & Explanation Facility
│   ├── advisories.py          # Soil NPK calculator, Irrigation guide, & Kisan Mitra Bot
│   └── image_analyzer.py      # Vision AI adapter & image pre-processing
│
├── static/                    # 🎨 Frontend Assets
│   ├── css/
│   │   └── style.css          # Modern green theme, glassmorphism, pH gauge, print styles
│   ├── js/
│   │   ├── i18n.js            # English & Hindi (हिंदी) bilingual translation engine
│   │   └── app.js             # Client controller, API client, & dynamic UI interactions
│   └── uploads/               # Directory for uploaded leaf photos (contains sample test image)
│
└── templates/
    └── index.html             # Responsive single-page application dashboard
```

---

## 🛠️ Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/CropCare-Ai.git
cd CropCare-Ai
```

### 2. Create and Activate a Virtual Environment
```bash
# On Linux / macOS:
python3 -m venv venv
source venv/bin/activate

# On Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)
```bash
# Copy the template to .env
cp .env.example .env
```
*(The application works 100% offline out-of-the-box. A `GEMINI_API_KEY` is optional.)*

### 5. Run the Automated Test Suite
```bash
# Run all tests together (Production suite + Diagnostic Fusion + Validation):
python run_all_tests.py
```

### 6. Start the Local Server
```bash
python app.py
```
Open [**http://127.0.0.1:5000**](http://127.0.0.1:5000) in your browser.

---

## 🚀 Deployment Guide: Vercel (https://vercel.com)

CropCare AI is fully configured for zero-config serverless deployment on **Vercel** via [`vercel.json`](vercel.json), [`api/index.py`](api/index.py), and Edge CDN static asset delivery (`public/static`).

### Option 1: Deploy via GitHub (Recommended)
1. Push this repository to **GitHub**.
2. Go to [Vercel Dashboard](https://vercel.com/dashboard) and click **"Add New..."** $\rightarrow$ **"Project"**.
3. Import your **CropCare-Ai** GitHub repository.
4. Vercel automatically detects the project configuration via `vercel.json` and `.python-version` (Python 3.12).
5. (Optional) In **Environment Variables**, you can add:
   - `GEMINI_API_KEY`: *(Your Google Gemini API key if using multimodal cloud AI)*
   - `SECRET_KEY`: *(A secret key for Flask sessions)*
6. Click **Deploy**. Your app will be live on `https://<your-project>.vercel.app`!

### Option 2: Deploy via Vercel CLI / Folder Upload
1. If you have Node.js installed, open terminal in this folder and run:
   ```bash
   npx vercel
   ```
2. Follow the prompt instructions (default options for all prompts).
3. To deploy to production:
   ```bash
   npx vercel --prod
   ```

---

## ☁️ Deployment Guide: Render (https://render.com)

CropCare AI is pre-configured for Render deployment with Gunicorn, dynamic port binding, and cache-busting headers.

### Method A: One-Click Render Blueprint (Recommended)
1. Push your repository to **GitHub**.
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** $\rightarrow$ **Blueprint**.
4. Connect your GitHub repository. Render will automatically read [`render.yaml`](render.yaml) and configure:
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 2 --threads 2 -b 0.0.0.0:$PORT --timeout 120 app:app`
5. Click **Apply**. Your web app will build and deploy live!

---

### Method B: Manual Web Service Setup on Render
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** $\rightarrow$ **Web Service**.
3. Connect your **CropCare-Ai** GitHub repository.
4. Configure the service settings:
   - **Name:** `cropcare-ai`
   - **Region:** Any region close to your users (e.g. Singapore, Oregon, Frankfurt)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 2 --threads 2 -b 0.0.0.0:$PORT --timeout 120 app:app`
   - **Instance Type:** `Free` (or higher)
5. **Environment Variables:**
   - `PYTHON_VERSION`: `3.11.9`
   - `SECRET_KEY`: *(Generate a secure random string or click Generate)*
   - `GEMINI_API_KEY`: *(Optional - leave blank if running offline)*
6. Click **Create Web Service**.

---

## 💾 Storage & Persistence on Cloud Hosting

- **Ephemeral Storage Notice:** On Render's Free tier, the filesystem is ephemeral (resets on deploy or container sleep). CropCare AI automatically initializes the SQLite schema on startup via `init_db()`.
- **Persistent Disk (Optional):** If you attach a Persistent Disk on Render (e.g. mounted at `/var/data`), set these environment variables in Render Dashboard:
  - `DATABASE_PATH`: `/var/data/cropcare.db`
  - `UPLOAD_FOLDER`: `/var/data/uploads`
  Both `app.py` and `database.py` will automatically read these paths.

---

## 🧪 Testing Summary

To run individual or combined test suites:

```bash
# 1. Complete Regression Test Suite (Runs all 3 suites)
python run_all_tests.py

# 2. Production System Test Suite (CRUD, ML, Soil, Irrigation, Chatbot)
python test_cropcare.py

# 3. Diagnostic Evidence Fusion Test Suite (Conflict reconciliation & morphology)
python tests/test_diagnosis_fusion.py
```

---

## 👥 Authors & License
Developed for precision agriculture, farmer decision-support, and agronomic education.  
Distributed under the **MIT License**.

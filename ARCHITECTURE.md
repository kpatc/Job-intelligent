# Architecture Job Intelligent

## 📐 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                              │
│  LinkedIn | Indeed | Welcome to the Jungle | France Travail     │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│               INGESTION LAYER (ETL Phase 1)                      │
│  - LinkedInIngester, IndeedIngester, WTTJIngester              │
│  - Methods: API, Web Scraping, CSV                              │
│  - Orchestrator: Coordonne l'ingestion                           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│             PROCESSING LAYER (Nettoyage & Normalisation)        │
│  - Déduplication (external_job_id)                              │
│  - Nettoyage texte (regex, stopwords)                           │
│  - Normalisation des intitulés (JobTitleMapping)                │
│  - Extraction compétences (STANDARDIZED_SKILLS)                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│            STORAGE LAYER (Base de Données PostgreSQL)           │
│                                                                   │
│  ┌─ Dimension Tables:                                           │
│  │  - dim_locations (city, country, region, coordinates)        │
│  │  - dim_skills (skill_name, category, level)                  │
│  │  - dim_companies (company_name, industry, size)              │
│  │  - dim_sources (source_name, type, url)                      │
│  │                                                               │
│  ├─ Fact Tables:                                                │
│  │  - fact_jobs (job_title, description, salary, date...)      │
│  │  - job_skills (many-to-many avec dim_skills)               │
│  │  - job_embeddings (vectors pour NLP)                         │
│  │                                                               │
│  └─ Views (pour BI):                                            │
│     - vw_top_job_titles, vw_top_skills                          │
│     - vw_jobs_by_location, vw_source_comparison                │
│     - vw_job_market_overview                                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│          NLP & ANALYSIS LAYER (Phase 4 - À implémenter)        │
│  - Sentence-BERT embeddings (description_embedding)             │
│  - Semantic similarity (cosine distance)                         │
│  - Skills extraction (spaCy)                                     │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│      RECOMMENDATION ENGINE (Phase 4 - À implémenter)           │
│  - Content-Based Filtering                                      │
│  - Score = Similarity + Skills Match + Location Weight          │
│  - Output: Top N recommendations per candidate                  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│            DATA MART (Phase 5 - À implémenter)                  │
│  - Cube OLAP pour Power BI                                      │
│  - Optimisation des requêtes analytiques                        │
│  - Aggregation des métriques (count, avg salary, etc.)          │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              POWER BI DASHBOARD (Phase 6)                       │
│  - Job Market Overview                                           │
│  - Skills Analysis                                               │
│  - Personalized Recommendations                                 │
│  - Platform Comparison                                           │
└─────────────────────────────────────────────────────────────────┘
```

## 📂 Structure des fichiers

```
job-intelligent/
│
├── config/
│   ├── __init__.py
│   ├── settings.py                    # Configuration centralisée
│   └── .env                           # Variables d'environnement
│
├── src/
│   ├── __init__.py
│   │
│   ├── database/
│   │   ├── __init__.py               # Classe Database (connexion)
│   │   └── models.py                 # Modèles ORM SQLAlchemy
│   │
│   ├── ingestion/
│   │   ├── __init__.py               # BaseIngester (classe abstraite)
│   │   ├── indeed_ingester.py        # Web scraping Indeed
│   │   ├── linkedin_ingester.py      # API LinkedIn
│   │   ├── welcome_jungle_ingester.py # API WTTJ
│   │   └── orchestrator.py           # IngestionOrchestrator
│   │
│   ├── processing/
│   │   └── __init__.py               # DataCleaner, DataProcessor
│   │
│   ├── nlp/
│   │   └── __init__.py               # À faire: Embeddings, Similarity
│   │
│   └── recommandation/
│       └── __init__.py               # À faire: RecommendationEngine
│
├── scripts/
│   ├── setup_database.sql            # Schéma PostgreSQL
│   └── run_ingestion.py              # Script principal d'exécution
│
├── data/
│   ├── raw/                          # Données brutes (git-ignored)
│   └── processed/                    # Données traitées (git-ignored)
│
├── requirements.txt                  # Dépendances Python
├── .env.example                      # Template .env
├── .gitignore
├── README.md
└── ARCHITECTURE.md                   # Ce fichier
```

## 🔄 Pipeline d'ingestion

### Phase 1: Ingestion

**Classe abstraite: `BaseIngester`**
```python
class BaseIngester:
    def fetch_jobs() -> List[Dict]     # À implémenter par chaque source
    def validate_job(job) -> bool      # Validation
    def normalize_job(job) -> Dict     # Normalisation
    def ingest() -> Dict               # Orchestration
```

**Ingesteurs implémentés:**
- `LinkedInIngester`: Données test simulées
- `IndeedIngester`: Web scraping BeautifulSoup
- `WelcomeToTheJungleIngester`: Données test simulées

**Orchestrateur:**
```python
orchestrator = IngestionOrchestrator()
result = orchestrator.run_all()
```

### Phase 2: Nettoyage & Normalisation

**`DataCleaner` class:**
- `clean_text()`: Supprime caractères spéciaux
- `normalize_job_title()`: Mappe intitulés vers normes (Data Scientist, Data Engineer, etc.)
- `extract_and_standardize_skills()`: Standardise compétences (ex: "python" → "Python")
- `deduplicate_jobs()`: Supprime doublons via external_job_id

**`DataProcessor` class:**
- Orchestre le pipeline complet: déduplicate → nettoie → valide

### Format de données normalisées

```json
{
  "job_title": "Data Scientist",
  "job_description": "Description nettoyée et normalisée...",
  "company_name": "Criteo",
  "location": "Paris, France",
  "experience_level": "Senior",
  "contract_type": "CDI",
  "job_url": "https://...",
  "external_job_id": "linkedin_12345",
  "published_at": "2024-01-03",
  "skills": ["Python", "SQL", "Machine Learning", "Spark"],
  "salary_min": 50000,
  "salary_max": 70000,
  "salary_currency": "EUR"
}
```

## 🗄️ Schéma Base de Données

### Tables de dimension (Slowly Changing Dimensions)

**`dim_locations`** - Localisation des offres
- id, city, country, region, latitude, longitude
- Index: UNIQUE(city, country)

**`dim_skills`** - Compétences standardisées
- id, skill_name (UNIQUE), category, skill_level
- 100+ skills préconfigurées

**`dim_companies`** - Entreprises
- id, company_name (UNIQUE), company_url, company_size, industry

**`dim_sources`** - Sources de données
- id, source_name (UNIQUE), source_type, base_url

### Fact Table (Grain: 1 offre d'emploi)

**`fact_jobs`** - Offres d'emploi (central repository)
- id (PK), job_title, job_description, location_id (FK), company_id (FK), source_id (FK)
- experience_level, contract_type, salary_min, salary_max, salary_currency
- job_url, external_job_id, published_at, created_at, updated_at, is_active
- UNIQUE(external_job_id, source_id) - Évite doublons

### Association Tables

**`job_skills`** (Many-to-many)
- job_id, skill_id, required (bool), proficiency_level
- UNIQUE(job_id, skill_id)

**`job_embeddings`** (Vectors pour NLP)
- job_id, description_embedding (FLOAT8[]), title_embedding (FLOAT8[])

### Tables de candidates (Recommandation)

**`candidate_profiles`**
- id, candidate_name, target_job_title, location_id, years_experience

**`candidate_skills`** (Many-to-many)
- candidate_id, skill_id, proficiency_level, years_of_experience

**`job_recommendations`** (Output du matching)
- candidate_id, job_id, match_score, semantic_similarity, skills_match_percentage
- location_match, matched_skills

### Logs & Monitoring

**`ingestion_logs`**
- source_name, status, jobs_count, errors_count
- started_at, ended_at, error_message

## 📊 Views pour Power BI

```sql
vw_job_market_overview      -- Total jobs, companies, locations
vw_top_job_titles           -- Jobs par titre et source
vw_top_skills               -- Skills les plus demandées
vw_jobs_by_location         -- Distribution géographique
vw_source_comparison        -- Comparaison sources
vw_best_recommendations     -- Top recommandations
```

## 🔐 Configuration & Secrets

**`.env`** (git-ignored)
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=job_intelligent
DB_USER=postgres
DB_PASSWORD=***
LINKEDIN_API_KEY=***
INDEED_API_KEY=***
LOG_LEVEL=INFO
```

Chargé via `python-dotenv` dans `config/settings.py`

## 🚀 Lancement

```bash
# 1. Setup environnement
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Initialiser BD PostgreSQL
psql -U postgres -f scripts/setup_database.sql

# 3. Lancer le pipeline
python scripts/run_ingestion.py
```

**Output:**
- Logs: `data/ingestion.log`
- Data: `data/processed/jobs_processed.json`
- BD: Tables populées

## 📈 Phases futures (À faire)

### Phase 3: NLP & Semantic Analysis
- Charger modèle Sentence-BERT
- Générer embeddings pour descriptions
- Calculer similarité cosinus

### Phase 4: Recommandation Engine
- Implémenter content-based filtering
- Scorer offres par candidat
- Exposer via API ou view

### Phase 5: Data Mart BI
- Créer cube OLAP
- Optimiser indexes
- Pré-aggréger métriques

### Phase 6: Power BI Dashboard
- Connecter PostgreSQL
- Créer 4 pages principales
- Publier Power BI Service

---

**Auteur**: Job Intelligent Project  
**Date**: Janvier 2026  
**Version**: 1.0 - Architecture Initiale

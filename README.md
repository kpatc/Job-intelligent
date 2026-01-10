# Job Intelligent - Complete Data Intelligence Platform

Plateforme data-driven pour l'analyse, l'extraction de skills, et la recommandation d'offres d'emploi Data/ML.

**Status**: ✅ Fully Functional (6 phases complete)

---

## 🏗️ Architecture

```
PHASE 1-2: DATA INGESTION
[ ReKrute Scraper ]  [ Indeed Scraper ]
         ↓                    ↓
      38 Jobs          +    41 Jobs        (Multi-region)

PHASE 3: DATA PROCESSING
         ↓
    [ Data Cleaner ] → 79 Jobs (deduplicated)
         ↓
   [ Skills Extractor ] → 370 Skills (61 unique)
         ↓
   [ Snowflake Loader ] → Star Schema
         ↓
    DIM_COMPANIES (55)  DIM_LOCATIONS (3)  DIM_SKILLS (61)
    FACT_JOBS (79)      FACT_JOB_SKILLS (370)

PHASE 5: DATA MART BI
         ↓
    9 Optimized Views (VW_*)
    
PHASE 4: RECOMMENDATIONS
         ↓
   [ Recommendation Engine ]
   (Semantic + Skill Matching)

PHASE 6: DASHBOARDS
         ↓
    [ Power BI ]
    (6 Dashboards)
```

## 📊 Project Status

| Phase | Component | Status | 
|-------|-----------|--------|
| 1-2 | Data Ingestion (ReKrute, Indeed) | ✅ Complete (79 jobs) |
| 3 | Data Processing & Cleaning | ✅ Complete |
| 3 | NLP Skills Extraction | ✅ Complete (370 extractions) |
| 3 | Snowflake Schema | ✅ Complete (star schema) |
| 3 | Data Loading | ✅ Complete |
| 4 | Recommendation Engine | ✅ Ready |
| 5 | BI Data Mart Views | ✅ Ready (9 views) |
| 6 | Power BI Dashboards | ✅ Configured |

## 📦 Structure du projet

```
job-intelligent/
├── src/
│   ├── ingestion/              # Phase 1-2: Web scrapers
│   │   ├── rekrute_ingester.py     # ReKrute (25 pages)
│   │   ├── indeed_ingester.py      # Indeed (3 regions)
│   │   └── remoteok_ingester.py    # RemoteOK (template)
│   ├── processing/             # Phase 3: Data cleaning
│   │   └── data_cleaner.py         # Harmonization
│   ├── nlp/                    # Phase 3: NLP
│   │   └── skills_extractor.py     # 200+ patterns, BERT
│   ├── database/               # Phase 3: Snowflake
│   │   ├── models.py               # ORM definitions
│   │   └── snowflake_loader.py     # Data loading
│   ├── recommandation/         # Phase 4: Recommendations
│   │   └── recommendation_engine.py # Semantic + Skills
│   └── powerbi_setup.py        # Phase 6: BI Config
├── config/                 # Environment & settings
├── data/                   # CSV exports
│   ├── indeed_jobs.csv
│   ├── rekrute_jobs.csv
│   ├── jobs_cleaned.csv        # Combined 79 jobs
│   ├── jobs_skills.csv         # 370 extractions
│   └── candidate_recommendations.csv
├── scripts/                # SQL & orchestration
│   ├── snowflake_schema.sql    # Phase 3: Schema
│   └── snowflake_datamart.sql  # Phase 5: BI views
├── PHASES_4_5_6.md        # Detailed phases docs
├── requirements.txt       # Dependencies
└── README.md
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
cd /home/josh/PowerBi/job-intelligent
source /home/josh/PowerBi/venv/bin/activate
```

### 2. View Data
```bash
# Jobs cleaned (79 total)
cat data/jobs_cleaned.csv | head -5

# Skills extracted (370 total)
cat data/jobs_skills.csv | head -10
```

### 3. Test Recommendations (Phase 4)
```bash
python src/recommandation/recommendation_engine.py
# Output: data/candidate_recommendations.csv
```

### 4. Query Data Mart (Phase 5)
```python
from src.database.snowflake_loader import SnowflakeLoader

loader = SnowflakeLoader()
loader.connect()

# Query a view
jobs = loader.execute_sql("SELECT * FROM VW_JOBS_FULL_CONTEXT LIMIT 5")
print(jobs)
```

### 5. Power BI (Phase 6)
See [PHASES_4_5_6.md](PHASES_4_5_6.md) for dashboard setup guide

4. **Configurer la base de données PostgreSQL**
```bash
# Voir scripts/setup_database.sql
psql -U postgres -f scripts/setup_database.sql
```

5. **Configuration ENV**
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

## 🎯 Phases du projet

- [ ] Phase 1 : Architecture & BD (en cours)
- [ ] Phase 2 : Ingestion données
- [ ] Phase 3 : Nettoyage & Normalisation
- [ ] Phase 4 : NLP & Recommandation
- [ ] Phase 5 : Data Mart BI
- [ ] Phase 6 : Dashboard Power BI

## 📝 Livrables

- Base de données centralisée
- Pipeline data documentée
- Système de recommandation
- Dashboard Power BI
- Rapport final

-- ============================================================
-- Job Intelligent - Schéma de Base de Données PostgreSQL
-- ============================================================

-- Table des localisations
CREATE TABLE IF NOT EXISTS dim_locations (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    region VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city, country)
);

-- Table des compétences
CREATE TABLE IF NOT EXISTS dim_skills (
    id SERIAL PRIMARY KEY,
    skill_name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100),
    skill_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des entreprises
CREATE TABLE IF NOT EXISTS dim_companies (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL UNIQUE,
    company_url VARCHAR(500),
    company_size VARCHAR(50),
    industry VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des sources de données
CREATE TABLE IF NOT EXISTS dim_sources (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL UNIQUE,
    source_type VARCHAR(50),
    base_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table principale des offres d'emploi
CREATE TABLE IF NOT EXISTS fact_jobs (
    id SERIAL PRIMARY KEY,
    job_title VARCHAR(255) NOT NULL,
    job_description TEXT NOT NULL,
    location_id INTEGER REFERENCES dim_locations(id),
    company_id INTEGER REFERENCES dim_companies(id),
    source_id INTEGER REFERENCES dim_sources(id),
    experience_level VARCHAR(100),
    contract_type VARCHAR(100),
    salary_min NUMERIC,
    salary_max NUMERIC,
    salary_currency VARCHAR(10),
    job_url VARCHAR(500),
    external_job_id VARCHAR(255),
    published_at DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(external_job_id, source_id)
);

-- Table de liaison job-skills (many-to-many)
CREATE TABLE IF NOT EXISTS job_skills (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES fact_jobs(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES dim_skills(id),
    required BOOLEAN DEFAULT TRUE,
    proficiency_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_id, skill_id)
);

-- Table pour stocker les embeddings/vecteurs
CREATE TABLE IF NOT EXISTS job_embeddings (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL UNIQUE REFERENCES fact_jobs(id) ON DELETE CASCADE,
    description_embedding FLOAT8[],
    title_embedding FLOAT8[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des profils candidats
CREATE TABLE IF NOT EXISTS candidate_profiles (
    id SERIAL PRIMARY KEY,
    candidate_name VARCHAR(255),
    target_job_title VARCHAR(255),
    location_id INTEGER REFERENCES dim_locations(id),
    years_experience INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table de liaison candidate-skills
CREATE TABLE IF NOT EXISTS candidate_skills (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES candidate_profiles(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES dim_skills(id),
    proficiency_level VARCHAR(50),
    years_of_experience INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(candidate_id, skill_id)
);

-- Table des recommandations
CREATE TABLE IF NOT EXISTS job_recommendations (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES candidate_profiles(id) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES fact_jobs(id) ON DELETE CASCADE,
    match_score FLOAT NOT NULL,
    semantic_similarity FLOAT,
    skills_match_percentage FLOAT,
    location_match BOOLEAN,
    matched_skills TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(candidate_id, job_id)
);

-- Table de logs pour le tracking
CREATE TABLE IF NOT EXISTS ingestion_logs (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100),
    status VARCHAR(50),
    jobs_count INTEGER,
    errors_count INTEGER,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES pour optimisation
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_jobs_location_id ON fact_jobs(location_id);
CREATE INDEX IF NOT EXISTS idx_fact_jobs_company_id ON fact_jobs(company_id);
CREATE INDEX IF NOT EXISTS idx_fact_jobs_source_id ON fact_jobs(source_id);
CREATE INDEX IF NOT EXISTS idx_fact_jobs_published_at ON fact_jobs(published_at);
CREATE INDEX IF NOT EXISTS idx_fact_jobs_external_id ON fact_jobs(external_job_id);
CREATE INDEX IF NOT EXISTS idx_job_skills_job_id ON job_skills(job_id);
CREATE INDEX IF NOT EXISTS idx_job_skills_skill_id ON job_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_candidate_skills_candidate_id ON candidate_skills(candidate_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_candidate_id ON job_recommendations(candidate_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_match_score ON job_recommendations(match_score);

-- ============================================================
-- VUES pour Power BI
-- ============================================================

-- Vue : Vue d'ensemble du marché
CREATE OR REPLACE VIEW vw_job_market_overview AS
SELECT 
    COUNT(DISTINCT f.id) as total_jobs,
    COUNT(DISTINCT f.company_id) as total_companies,
    COUNT(DISTINCT f.location_id) as total_locations,
    MAX(f.published_at) as latest_job_date
FROM fact_jobs f
WHERE f.is_active = TRUE;

-- Vue : Top métiers
CREATE OR REPLACE VIEW vw_top_job_titles AS
SELECT 
    f.job_title,
    COUNT(*) as job_count,
    d.source_name as source,
    MAX(f.published_at) as latest_date
FROM fact_jobs f
JOIN dim_sources d ON f.source_id = d.id
WHERE f.is_active = TRUE
GROUP BY f.job_title, d.source_name
ORDER BY job_count DESC;

-- Vue : Top compétences
CREATE OR REPLACE VIEW vw_top_skills AS
SELECT 
    s.skill_name,
    COUNT(js.job_id) as job_count,
    s.category,
    ROUND(100.0 * COUNT(js.job_id)::NUMERIC / 
        (SELECT COUNT(*) FROM fact_jobs WHERE is_active = TRUE), 2) as percentage
FROM dim_skills s
LEFT JOIN job_skills js ON s.id = js.skill_id
LEFT JOIN fact_jobs f ON js.job_id = f.id AND f.is_active = TRUE
GROUP BY s.id, s.skill_name, s.category
ORDER BY job_count DESC;

-- Vue : Distribution géographique
CREATE OR REPLACE VIEW vw_jobs_by_location AS
SELECT 
    l.city,
    l.country,
    l.region,
    COUNT(DISTINCT f.id) as job_count,
    COUNT(DISTINCT f.company_id) as company_count
FROM dim_locations l
LEFT JOIN fact_jobs f ON l.id = f.location_id AND f.is_active = TRUE
GROUP BY l.id, l.city, l.country, l.region
ORDER BY job_count DESC;

-- Vue : Source comparaison
CREATE OR REPLACE VIEW vw_source_comparison AS
SELECT 
    s.source_name,
    COUNT(DISTINCT f.id) as total_jobs,
    COUNT(DISTINCT f.company_id) as companies,
    MAX(f.published_at) as latest_job,
    ROUND(AVG(EXTRACT(DAY FROM (CURRENT_TIMESTAMP - f.published_at))), 1) as avg_days_old
FROM dim_sources s
LEFT JOIN fact_jobs f ON s.id = f.source_id AND f.is_active = TRUE
GROUP BY s.id, s.source_name
ORDER BY total_jobs DESC;

-- Vue : Recommandations
CREATE OR REPLACE VIEW vw_best_recommendations AS
SELECT 
    cp.candidate_name,
    f.job_title,
    f.job_description,
    dc.company_name,
    dl.city,
    jr.match_score,
    jr.skills_match_percentage,
    jr.matched_skills,
    f.job_url
FROM job_recommendations jr
JOIN candidate_profiles cp ON jr.candidate_id = cp.id
JOIN fact_jobs f ON jr.job_id = f.id
JOIN dim_companies dc ON f.company_id = dc.id
JOIN dim_locations dl ON f.location_id = dl.id
WHERE jr.match_score >= 0.7
ORDER BY cp.candidate_name, jr.match_score DESC;
